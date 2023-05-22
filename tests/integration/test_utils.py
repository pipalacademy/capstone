# these aren't exactly integration tests, but they need gitto and nomad
# to be there  to run  so they're here along with integration tests

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from capstone import config, db
from capstone.utils.user_project import delete_user_project, start_user_project

from ..test_db import site_id, project_id, user_id


def test_start_user_project(project_id, user_id, tmp_path):
    project = db.Project.find_or_fail(id=project_id)
    user = db.User.find_or_fail(id=user_id)

    # setup repo.zip for project
    with open(Path(tmp_path) / "test.txt", "w") as f:
        f.write("test\n")
    subprocess.check_call(["zip", "repo.zip", "test.txt"], cwd=tmp_path)
    with open(Path(tmp_path) / "repo.zip", "rb") as f:
        project.get_site().save_private_file(
            key=project.get_private_file_key_for_zipball(), stream=f,
        )

    user_project = start_user_project(project=project, user=user)

    subprocess.check_call(
        ["git", "clone", user_project.git_url], env={"PATH": os.getenv("PATH")}, cwd=tmp_path,
    )
    repo_dir = Path(tmp_path) / project.name
    assert repo_dir.is_dir()
    assert {p.name for p in repo_dir.iterdir()} == {".git", "test.txt"}
    with open(repo_dir / "test.txt") as f:
        assert f.read() == "test\n"


@patch("capstone.utils.user_project.gitto.delete_repo")
def test_delete_user_project(mock_delete_repo, project_id, user_id):
    repo_name = "random_hash/project_name.git"
    git_url = f"{config.gitto_base_url}/{repo_name}"
    user_project = db.UserProject(
        user_id=user_id,
        project_id=project_id,
        git_url=git_url,
        repo_id="random_hash"
    ).save()

    delete_user_project(user_project=user_project)

    assert mock_delete_repo.called_once_with(id="random_hash")
