from flask import Blueprint, make_response, request

from .db import Project, User


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
        return project.get_json()
    else:
        if not is_authorized(request):
            return Unauthorized()
        project = Project.find(name=name)
        if project is None:
            return NotFound("Project not found")

        new = request.json
        # TODO: validate body
        project.update(**new)
        project.save()
        return project.get_json()


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
