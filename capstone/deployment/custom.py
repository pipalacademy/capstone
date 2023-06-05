import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, IO

import requests
from pydantic import BaseModel, validator

from capstone import config
from capstone.db import Site, UserProject
from .base import Deployment


class AppInfo(BaseModel):
    id: str
    user: str
    project: str
    links: dict[str, str]

    @validator("links")
    def app_url_must_be_in_links(cls, v):
        if "app" not in v:
            raise ValueError("app_url must be in links")
        else:
            return v


class DeploymentTeaser(BaseModel):
    id: int
    status: str
    timestamp: datetime
    links: dict[str, str]

    @validator("links")
    def self_url_must_be_in_links(cls, v):
        if "self" not in v:
            raise ValueError("self url must be in links")
        else:
            return v


class DeploymentInfo(DeploymentTeaser):
    app: str

    @validator("links")
    def logs_url_must_be_in_links(cls, v):
        if "logs" not in v:
            raise ValueError("logs url must be in links")
        else:
            return v


class DeploymentTeasers(BaseModel):
    __root__ = list[DeploymentTeaser]


class CustomDeployment(Deployment):
    TYPE = "custom"

    def __init__(self, url: str, token: str | None = None):
        self.url = url
        self.token = token

    def _get_request_headers(self):
        headers = {}
        if self.token:
            headers.update({"Authorization": f"Bearer {self.token}"})
        return headers

    def create_app(self, username: str, project_name: str) -> AppInfo:
        r = requests.post(
            f"{self.url}/apps",
            headers=self._get_request_headers(),
            json={
                "user": username,
                "project": project_name
            }
        )
        # TODO: handle errors
        r.raise_for_status()
        return AppInfo.parse_obj(r.json())

    def get_app(self, app_id: str) -> AppInfo:
        r = requests.get(
            f"{self.url}/apps/{app_id}", headers=self._get_request_headers()
        )
        # TODO: handle errors
        r.raise_for_status()
        return AppInfo.parse_obj(r.json())

    def list_deployments(self, app_id: str) -> DeploymentTeasers:
        r = requests.get(
            f"{self.url}/apps/{app_id}/deployments",
            headers=self._get_request_headers(),
        )
        # TODO: handle errors
        r.raise_for_status()
        return DeploymentTeasers.parse_obj(r.json())

    def get_deployment(self, app_id: str, deployment_id: int) -> DeploymentInfo:
        r = requests.get(
            f"{self.url}/apps/{app_id}/deployments/{deployment_id}",
            headers=self._get_request_headers(),
        )
        # TODO: handle errors
        r.raise_for_status()
        return DeploymentInfo.parse_obj(r.json())

    def create_deployment(self, app_id: str, payload_zipfile: IO[bytes]) -> DeploymentInfo:
        headers = self._get_request_headers()
        headers["Content-Type"] = "application/zip"

        # send binary data as application/zip
        r = requests.post(
            f"{self.url}/apps/{app_id}/deployments",
            headers=headers,
            data=payload_zipfile,
        )
        # TODO: handle errors
        r.raise_for_status()
        return DeploymentInfo.parse_obj(r.json())

    def get_deployment_logs(self, app_id: str, deployment_id: int) -> str:
        r = requests.get(
            f"{self.url}/apps/{app_id}/deployments/{deployment_id}/logs",
            headers=self._get_request_headers(),
        )
        # TODO: handle errors
        r.raise_for_status()
        return r.text

    def wait_for_status(self, app_id: str, deployment_id: int) -> DeploymentInfo:
        for _ in range(100):  # 100 retries (~100 seconds)
            deployment = self.get_deployment(app_id=app_id, deployment_id=deployment_id)
            if deployment.status == "IN-PROGRESS":
                time.sleep(1)

        return deployment

    def run(self, site: Site, user_project: UserProject) -> dict[str, Any]:
        """
        Returns a result dict:
        {
            "ok": bool,
            "logs": str,
            "app_url": optional str  # only if ok is True
        }
        """
        if "app_id" in user_project.app_settings:
            app_info = self.get_app(app_id=user_project.app_settings["app_id"])
        else:
            app_info = self.create_app(
                username=user_project.get_user().username,
                project_name=user_project.get_project().name
            )
            user_project.app_settings["app_id"] = app_info.id
            user_project.save()
        payload_zipfile = _make_zipfile_for_user_project(user_project=user_project)
        depl = self.create_deployment(
            app_id=app_info.id,
            payload_zipfile=payload_zipfile,
        )
        depl = self.wait_for_status(app_id=app_info.id, deployment_id=depl.id)
        return {
            "ok": depl.status == "SUCCESS",
            "logs": self.get_deployment_logs(app_id=app_info.id, deployment_id=depl.id),
            "app_url": depl.links["app"] if depl.status == "SUCCESS" else None,
        }


def _make_zipfile_for_user_project(user_project: UserProject) -> IO[bytes]:
    """
    Returns a file-like object containing the zipped user project.
    """
    with tempfile.TemporaryDirectory() as tmp:
        # project = user_project.get_project()
        # move project assets to this directory:
        subprocess.check_call(["mkdir", "project"], cwd=tmp)

        subprocess.check_call(["git", "clone", user_project.git_url, "app"], cwd=tmp)

        subprocess.check_call(["zip", "-r", "app.zip", "app", "project"], cwd=tmp)

        zipfile_path = Path(config.data_dir).joinpath(
            "custom_deployment_assets",
            user_project.get_site().name,
            f"{user_project.get_project().name}-{user_project.get_user().username}.zip",
        )
        zipfile_path.parent.mkdir(parents=True, exist_ok=True)

        subprocess.check_call(["mv", "app.zip", str(zipfile_path.resolve())], cwd=tmp)

    return zipfile_path.open("rb")
