from flask import Blueprint, make_response, request

from .db import Activity, Project, User, TaskActivityInput


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
    return Activity.find_all()


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
