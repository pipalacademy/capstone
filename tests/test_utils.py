import os
from unittest.mock import patch

from capstone import config
from capstone import db
from capstone.utils.user_project import start_user_project

from .test_db import site_id, project_id, user_id


@patch("capstone.utils.user_project.extract_zipfile")
@patch(
    "capstone.utils.user_project.generate_repo_name",
    side_effect=lambda project_name: f"random_hash/{project_name}"
)
def test_start_user_project(_, mock_extract_zipfile, project_id, user_id):
    project = db.Project.find(id=project_id)
    user = db.User.find(id=user_id)

    user_project = start_user_project(project=project, user=user)

    assert user_project.project_id == project_id
    assert user_project.user_id == user_id

    expected_repo_path = f"random_hash/{project.name}"
    assert user_project.git_url == f"{config.git_base_url}/{expected_repo_path}"
    assert mock_extract_zipfile.called_once_with(
        src=f"private/projects/{project.name}/repo-git.zip",
        dst=os.path.join(config.git_root_directory, expected_repo_path)
    )
