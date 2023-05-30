from typing import Any

from capstone.db import Site, UserProject
from .base import Deployment


class CustomDeployment(Deployment):
    TYPE = "custom"

    @classmethod
    def run(cls, site: Site, user_project: UserProject) -> dict[str, Any]:
        """
        Returns a result dict:
        {
            "ok": bool,
            "logs": str,
            "app_url": optional str  # only if ok is True
        }
        """
        return {}
