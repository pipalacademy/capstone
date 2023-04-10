from typing import Any

import requests

from capstone import config


class GittoException(Exception):
    pass


def get_auth_headers():
    return {"Authorization": f"Bearer {config.gitto_api_token}"}


def create_repo(name: str) -> str:
    """Creates a repo in Gitto, returns the ID"""
    url = config.gitto_base_url + "/api/repos"
    r = requests.post(url, json={"name": name}, headers=get_auth_headers())
    try:
        r.raise_for_status()
    except Exception as e:
        raise GittoException("Non-OK status code") from e

    return r.json()["id"]


def get_repo(id: str) -> dict[str, Any]:
    """Gets repo info from Gitto, given the repo ID

    Repo info is like:
    {
        "id": "abcd12345678",
        "name": "rajdhani",
        "repo_name": "abcd12345678/rajdhani",
        "git_url": "https://git.pipal.in/abcd12345678/rajdhani"
    }
    """
    url = config.gitto_base_url + f"/api/repos/{id}"
    r = requests.get(url, headers=get_auth_headers())
    try:
        r.raise_for_status()
    except Exception as e:
        raise GittoException("Non-OK status code") from e

    return r.json()


def delete_repo(id: str) -> None:
    """Deletes a repository from Gitto"""
    url = config.gitto_base_url + f"/api/repos/{id}"
    r = requests.delete(url, headers=get_auth_headers())
    try:
        r.raise_for_status()
    except Exception as e:
        raise GittoException("Non-OK status code") from e


def get_webhook(id: str) -> str | None:
    """Gets the webhook URL that is currently set.

    None if no webhook URL is set
    """
    url = config.gitto_base_url + f"/api/repos/{id}/hook"
    r = requests.get(url, headers=get_auth_headers())
    try:
        r.raise_for_status()
    except Exception as e:
        raise GittoException("Non-OK status code") from e

    return r.json()["url"]


def set_webhook(id: str, webhook_url: str) -> str | None:
    """Sets the webhook URL for a repo. Returns new webhook URL.
    """
    url = config.gitto_base_url + f"/api/repos/{id}/hook"
    r = requests.post(url, json={"url": webhook_url}, headers=get_auth_headers())
    try:
        r.raise_for_status()
    except Exception as e:
        raise GittoException("Non-OK status code") from e

    return r.json()["url"]
