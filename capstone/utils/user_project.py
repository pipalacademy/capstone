# TODO: ad-hoc module name, think of something better
import os
import subprocess
import uuid

from . import files
from capstone import config
from capstone import db


def start_user_project(project: db.Project, user: db.User) -> db.UserProject:
    assert user.id is not None and project.id is not None, "user and project must be saved"
    assert project.site_id == user.site_id, "project and user must be on the same site"
    assert project.get_user_project(user_id=user.id) is None, "user has already started the project"

    repo_name = generate_repo_name(project_name=project.name)
    repo_path = get_repo_path(repo_name=repo_name)
    template_repo_path = get_template_repo_as_zipfile(project=project)
    extract_zipfile(src=template_repo_path, dst=repo_path)

    git_url = get_git_url(repo_name=repo_name)

    return db.UserProject(
        user_id=user.id, project_id=project.id, git_url=git_url).save()


def delete_user_project(user_project: db.UserProject) -> None:
    assert user_project.id is not None, "user_project must be saved"

    repo_name = user_project.git_url.removeprefix(f"{config.git_base_url}/")
    repo_path = get_repo_path(repo_name=repo_name)

    # delete git repo
    subprocess.check_call(["rm", "-rf", repo_path])

    # delete from db
    user_project.delete()


def generate_repo_name(project_name: str) -> str:
    random_hash = uuid.uuid4().hex
    return f"{random_hash}/{project_name}.git"


def get_repo_path(repo_name: str) -> str:
    return os.path.join(config.git_root_directory, repo_name)


def get_template_repo_as_zipfile(project: db.Project) -> str:
    return files.get_private_file_path(
            project.get_private_file_key_for_zipball()
        )


def get_git_url(repo_name: str) -> str:
    return f"{config.git_base_url}/{repo_name}"


def extract_zipfile(src: str, dst: str) -> None:
    """Extracts a zip file to a destination.
    """
    os.makedirs(dst, exist_ok=True)
    subprocess.check_call(["unzip", "-d", dst, os.path.abspath(src)])
