# TODO: ad-hoc module name, think of something better
import os
import subprocess
import tempfile

from . import files, git, gito
from capstone import db


def start_user_project(project: db.Project, user: db.User) -> db.UserProject:
    assert user.id is not None and project.id is not None, "user and project must be saved"
    assert project.site_id == user.site_id, "project and user must be on the same site"
    assert project.get_user_project(user_id=user.id) is None, "user has already started the project"

    # TODO: there is a race condition where there could be two gito repositories created
    # for the same user_project

    repo_id = gito.create_repo(name=project.name)
    repo_info = gito.get_repo(id=repo_id)
    git_url = repo_info["git_url"]

    template_zipfile = get_template_repo_as_zipfile(project=project)
    setup_remote_git_repo(git_url, template_zipfile=template_zipfile)

    with db.db.transaction():
        user_project = db.UserProject(
            user_id=user.id, project_id=project.id, git_url=git_url,
            gito_repo_id=repo_id
        ).save()
        gito.set_webhook(
            id=repo_id, webhook_url=user_project.get_webhook_url(),
        )

    return user_project


def delete_user_project(user_project: db.UserProject) -> None:
    assert user_project.id is not None, "user_project must be saved"

    # delete from gito
    gito.delete_repo(id=user_project.gito_repo_id)

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


def get_template_repo_as_zipfile(project: db.Project) -> str:
    return files.get_private_file_path(
            project.get_private_file_key_for_zipball()
        )


def extract_zipfile(src: str, dst: str) -> None:
    """Extracts a zip file to a destination.
    """
    os.makedirs(dst, exist_ok=True)
    subprocess.check_call(["unzip", "-d", dst, os.path.abspath(src)])
