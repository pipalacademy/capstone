import json
import logging
import subprocess
import tempfile
import traceback
import yaml
from pathlib import Path
from typing import Any

import docker
from pydantic import BaseModel
from toolkit import setup_logger

from . import config, db, tq
from .utils import files, git

setup_logger()
logger = logging.getLogger(__name__)


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
    is_published: bool | None = None


@tq.task_function
def update_project(project_id: int, changelog_id: int) -> None:
    logger.info(f"Task started: update_project(project_id={project_id}, changelog_id={changelog_id})")

    changelog = db.Changelog.find(id=changelog_id)
    if changelog is None:
        logger.error(f"Changelog not found: {changelog_id}")
        return

    changelog.details["status"] = "running"
    changelog.save()

    t = db.db.transaction()
    try:
        project = db.Project.find(id=project_id)
        if project is None:
            logger.error(f"Project not found: {project_id}")
            return

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
            project.update(**project_info)
            project.save()
            project.update_tasks(tasks)

            repo_dir = Path(tmp) / "repo"
            subprocess.check_call(["zip", "-r", "repo.zip", "."], cwd=repo_dir)
            with open(repo_dir / "repo.zip", "rb") as f:
                files.save_private_file(f"projects/{project.name}/repo.zip", f)
    except Exception:
        logger.error("Caught an exception. Rolling back transaction")
        t.rollback()
        changelog.details["status"] = "failed"
        changelog.details["log"] = traceback.format_exc()
        changelog.save()
        raise
    else:
        logger.info("Project updated without errors. Committing transaction")
        t.commit()
        changelog.details["status"] = "success"
        changelog.save()


@tq.task_function
def update_user_project(user_project_id: int, changelog_id: int) -> None:
    logger.info(f"Task started: update_user_project(user_project_id={user_project_id}, changelog_id={changelog_id})")

    changelog = db.Changelog.find(id=changelog_id)
    if changelog is None:
        logger.error(f"Changelog not found: {changelog_id}")
        return

    changelog.details["status"] = "running"
    changelog.save()

    try:
        user_project = db.UserProject.find(id=user_project_id)
        if user_project is None:
            logger.error(f"UserProject not found: {user_project_id}")
            return

        project = user_project.get_project()
        if project is None:
            raise Exception("Project not found")

        user = user_project.get_user()
        if user is None:
            raise Exception("User not found")

        client = docker.from_env()
        with tempfile.TemporaryDirectory() as tmp:
            result_file = str(Path(tmp) / "result.json")
            logger.info("Starting container")
            logs = client.containers.run(
                config.runner_docker_image,
                [
                    "--capstone-url", project.get_site().get_url(),
                    "--capstone-token", config.runner_capstone_token,
                    "--project-name", project.name,
                    "--username", user.username,
                    "--output", "/output/result.json",
                ],
                #auto_remove=True,
                network_mode="host",
                stdout=True,
                stderr=True,
                volumes={
                    tmp: {"bind": "/output", "mode": "rw"},
                },
            )
            logger.info(f"Container exited. Logs: {logs}")

            with open(result_file) as f:
                result = json.load(f)

            if not result["ok"]:
                logger.error("Runner failed with result not ok")
                changelog.details["status"] = "failed"
                changelog.details["log"] = result["log"]
                changelog.save()
                return

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
