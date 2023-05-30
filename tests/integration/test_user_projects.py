import re
import subprocess
import tempfile
import yaml
from pathlib import Path
from textwrap import dedent

import requests

from capstone.utils import git
from .conftest import capstone_app, create_site, create_project, create_user, create_user_project


def setup_project_for_deployment_and_checks(project):
    """
    Add tasks, and
    Set starter code to something that works -- anything

    two tasks are added:
    - first task has no checks, must pass
    - second task will always fail
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        repo = git.Repo.clone_from(project.git_url, path)

        (path / "checks.py").write_text(
            dedent("""
            from capstone_checker import ValidationError, main, register_check

            @register_check()
            def always_fail(context, args):
                raise ValidationError("this check always fails")

            if __name__ == "__main__":
                main()
            """)
        )

        metadata = yaml.safe_load((path / "capstone.yml").read_text())
        metadata["tasks"] = [
            dict(name="git-push", title="Git", description="commit, push", checks=[]),
            dict(name="must-fail", title="Must fail", description="fail...", checks=[
                dict(name="always_fail", title="Must fail", args={}),
            ]),
        ]
        (path / "capstone.yml").write_text(yaml.safe_dump(metadata))

        # do whatever needs to be done for starter code to have a flask app
        (path / "repo" / "Dockerfile").write_text(
            dedent("""
            FROM python:3.10-slim-buster
            COPY . /app
            WORKDIR /app
            RUN pip install flask
            CMD ["python", "app.py"]
            """)
        )
        (path / "repo" / "app.py").write_text(
            dedent("""
            from flask import Flask
            app = Flask(__name__)
            app.route("/")(lambda: "hello world")
            app.run(port=8080)
            """)
        )

        repo.add("capstone.yml", "checks.py", "repo/Dockerfile", "repo/app.py")
        repo.commit(message="setup project for deployment/checks")
        repo.push()


def test_project_can_be_started_by_learner(capstone_app):
    site = create_site(name="localhost", domain="localhost")
    user = create_user(site, email="learner@example.com")
    project = create_project(site, name="test-project", title="Test Project")
    project.publish()

    with capstone_app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = user.id

        response = client.post(f"/projects/test-project")
        # status code could be 302 (it is at the time of writing this test)
        # but i don't want to enforce that. any OK status code is fine.
        assert response.status_code < 400

    user_project = project.get_user_project(user_id=user.id)
    assert user_project is not None, "user project wasn't created"


def test_project_with_default_starter_code_can_be_cloned_by_learner(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    user = create_user(site, email="learner@example.com")
    project = create_project(site, name="test-project", title="Test Project")
    project.publish()
    user_project = create_user_project(site, user=user, project=project)

    repo = git.Repo.clone_from(user_project.git_url, tmp_path)
    assert repo.rev_parse("HEAD") is not None
    assert (tmp_path / "README.md").exists()


def test_user_project_gets_deployed_and_checked(capstone_app, tmp_path):
    """
    to test deployment,
    we run nomad cli command with `{username}-{project_name}` as job name

    to test checks,
    we see if the default task has passed, and a new task that will be added fails
    """
    site = create_site(name="localhost", domain="localhost")
    user = create_user(site, email="learner@example.com")
    project = create_project(site, name="test-project", title="Test Project")
    setup_project_for_deployment_and_checks(project)
    project.publish()
    user_project = create_user_project(site, user=user, project=project)

    repo = git.Repo.clone_from(user_project.git_url, tmp_path / "user-project")
    repo.commit(message="deploy and check", allow_empty=True)
    repo.push()

    # Test deployment:
    # TODO: find some more robust way to test deployment? 
    # both deployment method and the job-name format could change
    proc = subprocess.run(
        ["nomad", "job", "status", "-short", f"{user.username}-{project.name}"],
        stdout=subprocess.PIPE, text=True, check=True
    )
    assert re.search(r"^Status(\s+)= running$", proc.stdout, re.MULTILINE)

    # Test checks:
    task_statuses = user_project.get_task_statuses()
    assert len(task_statuses) == 2
    must_pass, must_fail = task_statuses
    assert must_pass.status == "Completed"
    assert must_fail.status == "In Progress"
    assert must_fail.get_check_statuses()[0].status == "fail"

    ## Test projects:
    # These tests must ideally be separated out, but running deployment and checks
    # takes >1min so we don't want to run it again and again.

    project_repo = git.Repo.clone_from(project.git_url, tmp_path / "project")
    metadata = yaml.safe_load((project_repo.path / "capstone.yml").read_text())

    # Test project: task title can be updated without losing user progress
    metadata["tasks"][0]["title"] = "Updated title"
    (project_repo.path / "capstone.yml").write_text(yaml.safe_dump(metadata))
    project_repo.add("capstone.yml")
    project_repo.commit(message="update task title")
    project_repo.push()

    project.refresh()
    assert project.get_tasks()[0].title == "Updated title"
    must_pass, _ = user_project.get_task_statuses()
    assert must_pass.status == "Completed"  # unchanged.

    # Test project, tasks can be reordered without losing user progress
    metadata["tasks"] = [metadata["tasks"][1], metadata["tasks"][0]]
    (project_repo.path / "capstone.yml").write_text(yaml.safe_dump(metadata))

    project_repo.add("capstone.yml")
    project_repo.commit(message="reorder tasks")
    project_repo.push()

    project.refresh()
    fst, snd = project.get_tasks()
    assert fst.name == metadata["tasks"][0]["name"]
    assert snd.name == metadata["tasks"][1]["name"]
    assert len(user_project.get_task_statuses()) == 2  # progress is not lost

    # Test project, tasks can be deleted
    metadata["tasks"] = []
    (project_repo.path / "capstone.yml").write_text(yaml.safe_dump(metadata))

    project_repo.add("capstone.yml")
    project_repo.commit(message="delete tasks")
    project_repo.push()

    project.refresh()
    assert len(project.get_tasks()) == 0
