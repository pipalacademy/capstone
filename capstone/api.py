import tempfile
import zipfile
import logging
from typing import Any
from pydantic import BaseModel, ValidationError
from . import tq

from flask import Blueprint, g, make_response, request

from . import config
from .db import Changelog, Project
from .utils.user_project import start_user_project
from .utils.files import get_private_file, save_private_file


logger = logging.getLogger(__name__)
api = Blueprint("api", __name__)


def is_authorized(request):
    auth = request.headers.get("authorization")
    if not auth:
        return False

    token = auth[len("Bearer "):]
    return is_token_valid(token)


def is_token_valid(token):
    return token == config.capstone_api_token


def Unauthorized(message="Unauthorized"):
    return make_response(({"message": message}, 401))


def NotFound(message="Not Found"):
    return make_response(({"message": message}, 404))


def ValidationFailed(message):
    return make_response(({"message": message}, 422))


def Conflict(message="Conflict"):
    return make_response(({"message": message}, 409))


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


# Resource: project

@api.route("/projects", methods=["GET"])
def list_projects():
    """List all projects

    Returns: array[project_teaser]
    """
    projects = g.site.get_projects()
    return [
        project.get_teaser() for project in projects
    ]


@api.route("/projects/<name>", methods=["GET", "PUT"])
def get_or_upsert_project(name):
    """Get or update or create project

    Methods:
    - GET: Get a project by name
    - PUT: Update a project, or create one if it doesn't exist

    Both methods are authenticated.

    Returns: project
    """
    if not is_authorized(request):
        return Unauthorized()

    if request.method == "GET":
        project = g.site.get_project(name=name)
        if project is None:
            return NotFound("Project not found")
        return project.get_detail()
    else:
        try:
            body = ProjectUpsertModel.parse_obj(request.json).dict()
        except ValidationError as e:
            return ValidationFailed(str(e))

        body["name"] = name
        body["site_id"] = g.site.id
        tasks = body.pop("tasks")

        project = g.site.get_project(name=name)
        if project is None:
            project = Project(**body).save()
        else:
            project.update(**body).save()

        project.update_tasks(tasks)

        return project.get_detail()


@api.route("/projects/<project_name>/repo.zip", methods=["GET", "PUT"])
def get_or_upsert_repo_zip(project_name):
    """Get or upsert zipfile with starter code.

    This starter code will be part of the repository
    that the participants will clone.
    """
    if not is_authorized(request):
        return Unauthorized()

    if request.method == "GET":
        gen = get_private_file(f"projects/{project_name}/repo.zip")
        response = make_response(gen)
        response.headers["Content-Type"] = "application/zip"
        return response

    elif request.method == "PUT":
        with tempfile.TemporaryDirectory() as tempdir:
            repo_zip = f"{tempdir}/repo.zip"

            with open(repo_zip, "wb") as f:
                for data in request.stream:
                    f.write(data)

            if not zipfile.is_zipfile(repo_zip):
                return {"message": "Not a valid zipfile"}, 400

            with open(repo_zip, "rb") as f:
                save_private_file(f"projects/{project_name}/repo.zip", f)

        return {}, 201


# Resource: User

@api.route("/users/<username>", methods=["GET"])
def get_user(username):
    """Get a user

    Authenticated endpoint.

    Returns: user
    """
    if not is_authorized(request):
        return Unauthorized()
    user = g.site.get_user(username=username)
    if user is None:
        return NotFound("User not found")
    return user.get_json()


# Resource: UserProject

@api.route("/activity")
def list_user_projects():
    """List all user projects

    Authenticated endpoint

    Returns: array[user_project_teaser]
    """
    # TODO: add pagination
    user_project = g.site.get_user_projects()
    return [up.get_teaser() for up in user_project]


@api.route("/users/<username>/projects")
def list_user_projects_by_user(username):
    """List all user projects for a user

    Authenticated endpoint.

    Returns: array[user_project_teaser]
    """
    if not is_authorized(request):
        return Unauthorized()

    user = g.site.get_user(username=username)
    if user is None:
        return NotFound("User not found")

    user_projects = user.get_user_projects()
    return [up.get_teaser() for up in user_projects]


@api.route("/users/<username>/projects/<project_name>", methods=["GET", "PUT"])
def get_or_create_user_project(username, project_name):
    """Get an activity for a user on a project, or create a new
    one (Sign Up for a project).

    Authenticated endpoint.

    Returns: user_project
    """
    if not is_authorized(request):
        return Unauthorized()

    user = g.site.get_user(username=username)
    if user is None:
        return NotFound("User not found")

    project = g.site.get_project(name=project_name)
    if project is None:
        return NotFound("Project not found")

    if request.method == "PUT":
        if project.get_user_project(user_id=user.id) is not None:
            return Conflict("User is already signed up for the project")

        user_project = start_user_project(project=project, user=user)
        return user_project.get_detail()
    else:
        user_project = project.get_user_project(user_id=user.id)
        if user_project is None:
            return NotFound("User Project not found")
        return user_project.get_detail()


# Webhooks

@api.route("/projects/<name>/hook/<gito_repo_id>", methods=["POST"])
def update_project_webhook(name, gito_repo_id):
    # NOTE: there is no other authentication, only gito_repo_id

    project = g.site.get_project(name=name)
    if project is None:
        return NotFound("Project not found")

    if project.gito_repo_id != gito_repo_id:
        return Unauthorized("Repo ID mismatch")

    changelog = Changelog(
        site_id=g.site.id,
        project_id=project.id,
        action="update_project",
        details={"status": "pending"}
    ).save()

    tq.add_task(
        "update_project",
        project_id=project.id, changelog_id=changelog.id,
    )

    return {
        "message": f"Task has been enqueued to update project {project.name}",
        "changelog_id": changelog.id,  # debug info
    }


@api.route(
    "/users/<username>/projects/<project_name>/hook/<gito_repo_id>",
    methods=["POST"]
)
def update_user_project_webhook(username, project_name, gito_repo_id):
    # NOTE: there is no other authentication, only gito repo id

    project = g.site.get_project(name=project_name)
    if project is None:
        return NotFound("Project not found")
    user = g.site.get_user(username=username)
    if user is None:
        return NotFound("User not found")

    user_project = project.get_user_project(user_id=user.id)
    if user_project is None:
        return NotFound("User project not found")

    if user_project.gito_repo_id != gito_repo_id:
        return Unauthorized("Repo ID mismatch")

    changelog = Changelog(
        site_id=g.site.id,
        user_id=user.id,
        project_id=project.id,
        action="update_user_project",
        details={
            "status": "pending",
            "user_project_id": user_project.id,
        }
    ).save()

    tq.add_task(
        "update_user_project",
        user_project_id=user_project.id, changelog_id=changelog.id,
    )

    return {
        "message": "Task has been enqueued to update user project "
                   f"(Project: {project_name}, Username: {username})",
        "changelog_id": changelog.id,  # debug info
    }
