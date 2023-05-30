"""Deployment interface for capstone.
"""

from typing import Any, Type

from capstone import db
from capstone.db import Site, UserProject
from .base import Deployment
from .custom import CustomDeployment
from .nomad import NomadDeployment


def get_deployments(
        site: Site, user_id: int | None = None, project_id: int | None = None
) -> list[dict[str, Any]]:
    """
    Returns a list of deployments for a given site, and optionally a user or
    project.

    Each deployment is a dict with the following keys:
    - timestamp: datetime
    - type: str
    - project: str
    - user: str
    - app_url: str
    - git_hash: str
    """
    filters = {"site_id": site.id}
    if user_id:
        filters["user_id"] = user_id
    if project_id:
        filters["project_id"] = project_id
    deployments = db.db.where("changelog", action="deploy", **filters)
    return [
        {
            "timestamp": deployment["timestamp"],
            "type": deployment["details"]["type"],
            "project": site.get_projects(id=deployment["project_id"])[0].name,
            "user": site.get_users(id=deployment["user_id"])[0].username,
            "git_hash": deployment["details"]["git_commit_hash"],
            "app_url": deployment["details"]["app_url"],
        }
        for deployment in deployments
    ]


def get_deployment_class(type: str) -> Type[Deployment]:
    if type == "nomad":
        return NomadDeployment
    elif type == "custom":
        return CustomDeployment
    else:
        raise ValueError(f"Unknown deployment type: {type}")
