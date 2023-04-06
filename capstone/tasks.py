import logging
import subprocess
import tempfile
import traceback
import yaml
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from toolkit import setup_logger

from . import db, tq
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

    project = db.Project.find(id=project_id)
    if project is None:
        logger.error(f"Project not found: {project_id}")
        return

    changelog = db.Changelog.find(id=changelog_id)
    if changelog is None:
        logger.error(f"Changelog not found: {changelog_id}")
        return

    changelog.details["status"] = "running"
    changelog.save()

    t = db.db.transaction()
    try:
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
