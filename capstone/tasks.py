import logging
import subprocess
import tempfile
import traceback
import yaml
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from toolkit import setup_logger
from redis import Redis
from rq import Queue

from . import config, db
from .deployment import NomadDeployment
from .utils import git
from .utils.user_project import run_checks

setup_logger()
logger = logging.getLogger(__name__)

queue = Queue(connection=Redis.from_url(config.redis_url))


class CheckInputModel(BaseModel):
    name: str
    title: str
    args: dict[str, Any]


class TaskInputModel(BaseModel):
    name: str
    title: str
    description: str
    checks: list[CheckInputModel]


class ProjectUpsertModel(BaseModel):
    title: str
    short_description: str
    description: str
    tags: list[str]
    tasks: list[TaskInputModel]


def update_project(site_id: int, project_id: int, changelog_id: int) -> None:
    logger.info(f"Task started: update_project(site_id={site_id}, "
                f"project_id={project_id}, changelog_id={changelog_id})")

    site = db.Site.find_or_fail(id=site_id)

    changelog = site.get_changelog_or_fail(id=changelog_id)
    changelog.details["status"] = "running"
    changelog.save()

    try:
        project = site.get_project_by_id_or_fail(project_id)

        with tempfile.TemporaryDirectory() as tmp:
            git.clone(project.git_url, tmp, workdir=tmp)

            if not Path(f"{tmp}/capstone.yml").is_file():
                raise Exception("capstone.yml not found in the root of the repository")
            if not Path(f"{tmp}/checks.py").is_file():
                raise Exception("checks.py not found in the root of the repository")
            if not Path(f"{tmp}/requirements.txt").is_file():
                raise Exception("requirements.txt not found in the root of the repository")
            if not Path(f"{tmp}/repo").is_dir():
                raise Exception("repo directory not found in the root of the repository")

            with open(f"{tmp}/capstone.yml") as f:
                project_info = yaml.safe_load(f)

            project_info = ProjectUpsertModel.parse_obj(project_info).dict()
            tasks = project_info.pop("tasks")

            with db.db.transaction():
                project.update(**project_info)
                project.save()
                project.update_tasks(tasks)

                repo_dir = Path(tmp) / "repo"
                subprocess.check_call(
                    ["zip", "-r", "repo.zip", "."], cwd=repo_dir
                )
                with open(repo_dir / "repo.zip", "rb") as f:
                    site.save_private_file(
                        key=f"projects/{project.name}/repo.zip", stream=f,
                    )
    except Exception:
        logger.error("Caught an exception.")
        changelog.details["status"] = "failed"
        changelog.details["log"] = traceback.format_exc()
        changelog.save()
        raise
    else:
        logger.info("Project updated successfully.")
        changelog.details["status"] = "success"
        changelog.save()


def update_user_project(
    site_id: int, user_project_id: int, changelog_id: int
) -> None:
    logger.info(f"Task started: update_user_project(site_id={site_id}, "
                f"user_project_id={user_project_id}, "
                f"changelog_id={changelog_id})")

    site = db.Site.find_or_fail(id=site_id)

    changelog = site.get_changelog_or_fail(id=changelog_id)
    changelog.details["status"] = "running"
    changelog.save()

    try:
        user_project = site.get_user_project_by_id_or_fail(id=user_project_id)

        # run deployment
        changelog.details["stage"] = "deployment"
        result = run_deployer(site=site, user_project=user_project)
        logger.info(f"Deployment result:\n{result}")
        if not result["ok"]:
            logger.error("Deployment failed with result not ok")
            changelog.details["status"] = "failed"
            changelog.details["log"] = result["log"]
            changelog.save()
            return

        # run checks
        changelog.details["stage"] = "checks"
        result = run_checker(site=site, user_project=user_project)
        logger.info(f"Checker result:\n{result}")
        if not result["ok"]:
            logger.error("Checker failed with result not ok")
            changelog.details["status"] = "failed"
            changelog.details["log"] = result["log"]
            changelog.save()
            return

    except Exception:
        logger.error("Caught an exception")
        changelog.details["status"] = "failed"
        changelog.details["log"] = traceback.format_exc()
        changelog.save()
        raise
    else:
        logger.info("UserProject updated without errors")
        changelog.details["status"] = "success"
        changelog.save()


def run_deployer(site, user_project):
    result = NomadDeployment.run(site=site, user_project=user_project)
    if result["ok"]:
        user_project.set_app_url(result["app_url"])
    return result


def run_checker(site, user_project):
    project = user_project.get_project()
    user = user_project.get_user()

    result = run_checks(
        capstone_url=project.get_site().get_url(),
        capstone_token=config.runner_capstone_token,
        project_name=project.name,
        username=user.username,
    )

    task_results = result["tasks"]

    with db.db.transaction():
        for task, task_result in zip(project.get_tasks(), task_results):
            task_status = user_project.get_task_status(task=task)
            if task_status is None:
                task_status = user_project.update_task_status(task=task, status="Pending")
            for check, check_result in zip(task.get_checks(), task_result["checks"]):
                task_status.update_check_status(
                    check=check,
                    status=check_result["status"],
                    message=check_result["message"]
                )
            user_project.update_task_status(
                task=task,
                status=task_status.compute_status()
            )
        user_project.set_in_progress_task()

    return result
