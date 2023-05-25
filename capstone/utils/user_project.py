# TODO: ad-hoc module name, think of something better
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import docker
from toolkit import setup_logger

from . import git, gitto
from capstone import config, db

setup_logger()
logger = logging.getLogger(__name__)


def start_user_project(project: db.Project, user: db.User) -> db.UserProject:
    assert user.id is not None and project.id is not None, "user and project must be saved"
    assert project.site_id == user.site_id, "project and user must be on the same site"
    assert project.get_user_project(user_id=user.id) is None, "user has already started the project"

    # TODO: there is a race condition where there could be two gitto repositories created
    # for the same user_project

    repo_id = gitto.create_repo(name=project.name)
    repo_info = gitto.get_repo(id=repo_id)
    git_url = repo_info["git_url"]

    zipfile_path = get_template_repo_as_zipfile(project=project)
    setup_remote_git_repo(git_url, template_zipfile=str(zipfile_path))

    with db.db.transaction():
        user_project = db.UserProject(
            user_id=user.id, project_id=project.id, git_url=git_url,
            repo_id=repo_id
        ).save()
        gitto.set_webhook(
            id=repo_id, webhook_url=user_project.get_webhook_url(),
        )

        # set first task to be in progress
        tasks = project.get_tasks()
        if tasks:
            user_project.update_task_status(task=tasks[0], status="In Progress")

    return user_project


def delete_user_project(user_project: db.UserProject) -> None:
    assert user_project.id is not None, "user_project must be saved"

    # delete from gitto
    gitto.delete_repo(id=user_project.repo_id)

    # delete from db
    user_project.delete()


def setup_remote_git_repo(git_url: str, template_zipfile: str) -> None:
    """Sets up a remote git repo with the template repo as the initial commit.
    """
    with tempfile.TemporaryDirectory() as repo_path:
        git.clone(git_url, ".", workdir=repo_path)
        extract_zipfile(src=template_zipfile, dst=repo_path)
        git.add(".", workdir=repo_path)
        git.commit(message="Initial commit", workdir=repo_path)
        git.push(git_url, "main", workdir=repo_path)


def get_template_repo_as_zipfile(project: db.Project) -> Path:
    return project.get_site().get_private_file_path(
        project.get_private_file_key_for_zipball()
    )


def extract_zipfile(src: str, dst: str) -> None:
    """Extracts a zip file to a destination.
    """
    os.makedirs(dst, exist_ok=True)
    subprocess.check_call(["unzip", "-d", dst, os.path.abspath(src)])


def run_checks(
    capstone_url: str, capstone_token: str, project_name: str, username: str
) -> dict[str, Any]:
    """
    Returns result:
    {
        "ok": True|False,
        "log": str|None,
        "tasks": [
            {
                "checks": [
                    {
                        "status": "pass"|"fail"|"error",
                        "message": str|None
                    }
                ]
            }
        ]
    }
    """
    runner_path = Path(__file__).parent.parent.parent / "runner" / "run-checks.py"

    with tempfile.TemporaryDirectory() as tmp:
        result_file = str(Path(tmp) / "result.json")

        if config.capstone_dev:
            logger.info("Running checks in dev mode")
            subprocess.check_call(
                [
                    config.runner_devmode_python_executable,
                    str(runner_path),
                    "--capstone-url", capstone_url,
                    "--capstone-token", capstone_token,
                    "--project-name", project_name,
                    "--username", username,
                    "--output", result_file,
                ],
                cwd=tmp,
            )
        else:
            logger.info("Running checks in docker")
            client = docker.from_env()
            logs = client.containers.run(
                config.runner_docker_image,
                [
                    "--capstone-url", capstone_url,
                    "--capstone-token", capstone_token,
                    "--project-name", project_name,
                    "--username", username,
                    "--output", "/output/result.json",
                ],
                auto_remove=True,
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

    return result
