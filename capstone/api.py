import requests
import subprocess
import tempfile
import zipfile
from . import tq

from flask import Blueprint, make_response, request, url_for

from .db import Activity, Project, User, CheckStatus, TaskActivityInput
from .checks import run_check
from . import config
from .utils import git
from .utils.files import get_private_file, save_private_file


api = Blueprint("api", __name__)


def is_authorized(request):
    auth = request.headers.get("authorization")
    if not auth:
        return False

    token = auth[len("Bearer "):]
    return is_token_valid(token)


def is_token_valid(token):
    return token == "test123"


def Unauthorized(message="Unauthorized"):
    return make_response(({"message": message}, 401))


def NotFound(message="Not Found"):
    return make_response(({"message": message}, 404))


def ValidationFailed(message):
    return make_response(({"message": message}, 422))


def Conflict(message="Conflict"):
    return make_response(({"message": message}, 409))


# Resource: project

@api.route("/projects", methods=["GET"])
def list_projects():
    """List all projects

    Returns: array[project_teaser]
    """
    projects = Project.find_all()
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
        project = Project.find(name=name)
        if project is None:
            return NotFound("Project not found")
        return project.get_json()
    else:
        if not is_authorized(request):
            return Unauthorized()

        # TODO: validate body
        args = request.json
        tasks = args.pop("tasks")

        project = Project.find(name=name)
        if project is None:
            project = Project(**args)
        else:
            project.update(**args)

        project.update_tasks(tasks)
        project.save()
        return project.get_json()


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
            repo_git_zip = f"{tempdir}/repo-git.zip"
            repo_dir = f"{tempdir}/repo"

            with open(repo_zip, "wb") as f:
                for data in request.stream:
                    f.write(data)

            if not zipfile.is_zipfile(repo_zip):
                return {"message": "Not a valid zipfile"}, 400

            extract_and_setup_git(zip_file=repo_zip, extract_to=repo_dir)
            write_post_receive_hook(f"{repo_dir}/.git/hooks/post-receive")
            write_git_config(repo_dir=repo_dir)

            zip_directory(src=f"{repo_dir}/.git", dst=repo_git_zip)

            with open(repo_zip, "rb") as f:
                save_private_file(f"projects/{project_name}/repo.zip", f)

            with open(repo_git_zip, "rb") as f:
                save_private_file(f"projects/{project_name}/repo-git.zip", f)

        return {}, 201


@api.route("/projects/<project_name>/repo-git.zip")
def get_repo_git_zip(project_name):
    if not is_authorized(request):
        return Unauthorized()

    return get_private_file(f"projects/{project_name}/repo-git.zip")


# Resource: User

@api.route("/users/<username>", methods=["GET"])
def get_user(username):
    """Get a user

    Authenticated endpoint.

    Returns: user
    """
    if not is_authorized(request):
        return Unauthorized()
    user = User.find(username=username)
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


@api.route("/webhook/post_receive", methods=["POST"])
def post_receive_webhook():
    if not is_authorized(request):
        return Unauthorized()

    repo_path = request.json["repo_path"]
    _, username_and_more, project_and_more = repo_path.rsplit("/", maxsplit=2)
    _, username = username_and_more.split("-", maxsplit=1)
    project_name, _ = project_and_more.rsplit(".git", maxsplit=1)
    tq.add_task("post_receive_webhook_action", username=username, project_name=project_name)
    response = "\nTriggered the checks for new changes.\nPlease wait for a minute or two for it to complete....\n"
    return response

@tq.task_function
def post_receive_webhook_action(username, project_name):
    user = User.find(username=username)
    project = Project.find(name=project_name)
    if not user or not project:
        return NotFound("User or project not found")

    activity = user.get_activity(project.name)
    if project.commit_hook_url:
        json_body = commit_hook_build_body(activity=activity)
        if "git_commit_hash" in request.json:
            json_body.update(git_commit_hash=request.json["git_commit_hash"])
        r = requests.post(
            project.commit_hook_url,
            json=json_body,
        )
        if not r.ok:
            return {
                "ok": False,
                "message": f"commit_hook failed:\n{r.content.decode()}",
            }, 500
    if project.checks_url:
        r = requests.post(
            config.capstone_url + url_for(
                "activity_run_checks",
                username=username, project_name=project_name))
        if not r.ok:
            return {
                "ok": False,
                "message": f"checks_url failed:\n{r.content.decode()}",
            }, 500

    return {}


def checks_build_context(activity, **rest):
    return {
        "capstone_url": config.capstone_url,
        "username": activity.username,
        "project_name": activity.project_name,
        **rest,
    }


def commit_hook_build_body(activity, **rest):
    return {
        "username": activity.username,
        "project": activity.project_name,
        "git_url": activity.git_url,
        **rest,
    }


def write_post_receive_hook(filepath):
    post_receive_hook_content = f"""\
#! /bin/bash

exec {config.git_post_receive_script}
"""
    with open(filepath, "w") as f:
        f.write(post_receive_hook_content)

    subprocess.check_call(["chmod", "+x", filepath])


def write_git_config(repo_dir):
    git.config("--bool", "http.receivepack", "true", workdir=repo_dir)
    git.config("--bool", "core.bare", "true", workdir=repo_dir)


def zip_directory(src, dst):
    subprocess.check_call(f"cd '{src}'; zip -r {dst} .", shell=True)


def extract_and_setup_git(zip_file, extract_to):
    git.init(extract_to, b="main")
    subprocess.check_call(["unzip", "-d", extract_to, zip_file])
    git.add(".", workdir=extract_to)
    git.commit(
        m="initial commit", workdir=extract_to,
        author="Capstone <git@pipal.in>")
