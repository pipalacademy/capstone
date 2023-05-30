from typing import Any

from capstone.db import Site, UserProject


class Deployment:
    @classmethod
    def run(cls, site: Site, user_project: UserProject) -> dict[str, Any]:
        """
        Must return a result dict:
        {
            "ok": bool,
            "logs": str,
            "app_url": optional str  # only if ok is True
        }

        It is OK to have additional keys, but these^ must be there.
        """
        raise NotImplementedError
