from unittest import mock
from unittest.mock import patch

from capstone import config
from capstone import db
from capstone.utils.user_project import delete_user_project, start_user_project

from .test_db import site_id, project_id, user_id


@patch("capstone.utils.user_project.extract_zipfile")
@patch("capstone.utils.user_project.git")
@patch("capstone.utils.user_project.gito.create_repo", return_value="testid1234")
@patch("capstone.utils.user_project.gito.set_webhook")
def test_start_user_project(
        mock_set_webhook,
        mock_create_repo,
        mock_git,
        mock_extract_zipfile,
        project_id,
        user_id):
    project = db.Project.find(id=project_id)
    user = db.User.find(id=user_id)

    with patch("capstone.utils.user_project.gito.get_repo",
               return_value={"id": "testid1234",
                             "git_url": f"{config.git_base_url}/testid1234/{project.name}",
                             "name": project.name,
                             "repo_name": f"testid1234/{project.name}"}):
        user_project = start_user_project(project=project, user=user)

    assert user_project.project_id == project_id
    assert user_project.user_id == user_id
    assert user_project.git_url == f"{config.git_base_url}/testid1234/{project.name}"
    assert user_project.gito_repo_id == "testid1234"

    assert mock_extract_zipfile.called_once_with(
        src=f"private/projects/{project.name}/repo-git.zip",
        dst=mock.ANY
    )
    assert mock_set_webhook.called_once_with(
        id="testid1234",
        webhook_url=f"{project.get_site().get_url()}/api/users/{user.username}/projects/{project.name}/hook/test1234",
    )


@patch("capstone.utils.user_project.gito.delete_repo")
@patch("capstone.utils.user_project.db.UserProject.delete")
def test_delete_user_project(mock_db_delete, mock_delete_repo, project_id, user_id):
    repo_name = "random_hash/project_name.git"
    git_url = f"{config.git_base_url}/{repo_name}"
    user_project = db.UserProject(
        user_id=user_id, project_id=project_id, git_url=git_url, gito_repo_id="random_hash").save()

    delete_user_project(user_project=user_project)

    assert mock_db_delete.called_once_with(user_project)
    assert mock_delete_repo.called_once_with(id="random_hash")
