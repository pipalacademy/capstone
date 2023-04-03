import argparse
import json
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

import requests
from capstone_checker import run_check


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capstone-url', required=True)
    parser.add_argument('-t', '--capstone-token', required=True)
    parser.add_argument('-p', '--project-name', required=True)
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-o', '--output', required=False)

    return parser.parse_args()


def get_user_project(capstone_url, capstone_token, project_name, username):
    """Get user project by name.

    Return format:
    ```
    {
        "app_url": "...",
        "git_url": "..."
    }
    ```
    """
    user_project_url = f"{capstone_url}/api/users/{username}/projects/{project_name}"
    r = requests.get(
        user_project_url,
        headers={"Authorization": f"Bearer {capstone_token}"}
    )
    r.raise_for_status()

    response = r.json()
    return dict(
        response,
        app_url=response["app_url"],
        git_url=response["git_url"]
    )


def get_project(
    capstone_url: str, capstone_token: str, project_name: str
) -> dict[str, Any]:
    """Get project by name.

    Return format:
    ```
    {
        "name": ...,
        "title": ...,
        "git_url": ...,
        "tasks": [
            ...,
            "checks": [
                {
                    "name": "...",
                    "title": "...",
                    "args": {
                        "str": "any"
                    }
                }
            ]
        ]
        ...
    }
    ```
    """
    url = f"{capstone_url}/api/projects/{project_name}"
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {capstone_token}"}
    )
    r.raise_for_status()

    response = r.json()
    return dict(
        response,
        name=response["name"],
        title=response["title"],
        git_url=response["git_url"],
        tasks=response["tasks"]
    )


def clone_repository(git_url: str, dest_dir: str) -> None:
    subprocess.check_call(["git", "clone", git_url, dest_dir])


def install_requirements(filepath: str) -> None:
    subprocess.check_call(["pip", "install", "-r", filepath])


def run_checks_until_task_fails(
    capstone_url: str, capstone_token: str, project_name: str, username: str
) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_dir = Path(tmp_dir) / "project"
        user_project_dir = Path(tmp_dir) / "user_project"

        project = get_project(
            capstone_url=capstone_url,
            capstone_token=capstone_token,
            project_name=project_name
        )
        clone_repository(git_url=project["git_url"], dest_dir=str(project_dir))
        install_requirements(str(project_dir / "requirements.txt"))

        user_project = get_user_project(
            capstone_url=capstone_url,
            capstone_token=capstone_token,
            project_name=project_name,
            username=username
        )
        app_url = user_project["app_url"]
        clone_repository(
            git_url=user_project["git_url"],
            dest_dir=str(user_project_dir)
        )

        task_results = []
        context = {"app_url": app_url, "app_dir": user_project_dir}
        for task in project["tasks"]:
            check_results = []
            for check in task["checks"]:
                check_status = run_check(
                    check["name"], context=context, args=check["args"]
                )
                check_results.append(
                    {
                        "status": check_status.status,
                        "message": check_status.message
                    }
                )

            task_results.append(
                {
                    "name": task["name"],
                    "checks": check_results
                },
            )
            if any(c["status"] != "pass" for c in check_results):
                # TODO: logger?
                break

        return task_results


def main():
    args = parse_args()

    capstone_url = args.capstone_url
    capstone_token = args.capstone_token
    project_name = args.project_name
    username = args.username
    output_stream = open(args.output, "w") if args.output else sys.stdout

    try:
        task_results = run_checks_until_task_fails(
            capstone_url, capstone_token, project_name, username
        )
    except Exception:
        result = {"ok": False, "log": traceback.format_exc(), "tasks": None}
        json.dump(result, output_stream)
    else:
        result = {"ok": True, "log": None, "tasks": task_results}
        json.dump(result, output_stream)
