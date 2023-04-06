import tempfile
import zipfile
import logging
from typing import Any
from pydantic import BaseModel, ValidationError
from . import tq

from flask import Blueprint, g, make_response, request

from .db import Changelog, Project
from .checks import run_check
from . import config
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

    PUT method is authenticated.

    Returns: project
    """
    if request.method == "GET":
        project = g.site.get_project(name=name)
        if project is None:
            return NotFound("Project not found")
        return project.get_detail()
    else:
        if not is_authorized(request):
            return Unauthorized()

        try:
            body = ProjectUpsertModel.parse_obj(request.json).dict()
        except ValidationError as e:
            return ValidationFailed(str(e))

        body["name"] = name
        body["site_id"] = g.site.id
        tasks = body.pop("tasks")

        project = g.site.get_project(name=name)
        if project is None:
            project = Project(**body)
        else:
            project.update(**body)

        project.save()
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


# Resource: Activity

@api.route("/activity")
def list_activity():
    """List all activity

    Authenticated endpoint

    Returns: array[activity_teaser]
    """
    # TODO: add pagination
    activities = Activity.find_all()
    return [a.get_teaser() for a in activities]


@api.route("/users/<username>/projects")
def list_activity_by_user(username):
    """List all activity for a user

    Authenticated endpoint.

    Returns: array[activity_teaser]
    """
    if not is_authorized(request):
        return Unauthorized()

    user_activity = Activity.find_all(username=username)
    return [a.get_teaser() for a in user_activity]


@api.route("/users/<username>/projects/<project_name>", methods=["GET", "PUT"])
def get_or_create_activity(username, project_name):
    """Get an activity for a user on a project, or create a new
    one (Sign Up for a project).

    Authenticated endpoint.

    Returns: activity
    """
    if not is_authorized(request):
        return Unauthorized()

    if request.method == "PUT":
        if Activity.find(username=username, project_name=project_name) is not None:
            return Conflict("User is already signed up for the project")
        activity = Activity(username=username, project_name=project_name)
        activity.save()
        return activity.get_json()
    else:
        activity = Activity.find(
            username=username, project_name=project_name,
        )
        if activity is None:
            return NotFound("Activity not found")
        return activity.get_json()


@api.route(
    "/users/<username>/projects/<project_name>/tasks", methods=["GET", "PUT"])
def get_or_update_activity_tasks(username, project_name):
    """Get/update all task activity for a user on a project

    Authenticated endpoint when updating.

    Returns: array[task_activity]
    """
    activity = Activity.find(username=username, project_name=project_name)
    if activity is None:
        return NotFound("Activity not found")

    if request.method == "PUT":
        if not is_authorized(request):
            return Unauthorized()

        raw_tasks = request.json
        tasks = [TaskActivityInput.from_json(**each) for each in raw_tasks]
        activity.update_tasks(tasks)

        return [t.get_json() for t in activity.get_task_activities()]
    else:
        return [t.get_json() for t in activity.get_task_activities()]


@api.route(
        "/users/<username>/projects/<project_name>/checks", methods=["POST"])
def activity_run_checks(username, project_name):
    """Run all checks for an activity and use them to update status.

    Returns: array[task_activity]
    """
    activity = Activity.find(username=username, project_name=project_name)
    if activity is None:
        return NotFound("Activity not found")

    project = activity.get_project()
    for task in project.get_tasks():
        check_statuses = []
        for check in task.checks:
            result = run_check(
                base_url=project.checks_url,
                context=checks_build_context(activity),
                check_name=check.name,
                arguments=check.args)
            check_statuses.append(
                CheckStatus(**result, name=check.name))
        task_activity_input = TaskActivityInput(name=task.name, checks=check_statuses)
        task_activity = activity.get_task_activity(task.id)
        old_status = task_activity.status
        task_activity.update_from_input(task_activity_input).save()
        if old_status not in {"Completed", "Failing"} and task_activity.status != "Completed":
            break

    activity.set_in_progress_task()
    return [t.get_json() for t in activity.get_task_activities()]


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
    )
    changelog.save()

    tq.add_task(
        "update_project",
        project_id=project.id, changelog_id=changelog.id,
    )

    return {
        "message": f"Task has been enqueued to update project {project.name}",
        "changelog_id": changelog.id,  # debug info
    }
