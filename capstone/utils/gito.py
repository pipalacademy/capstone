from typing import Any

import requests

from capstone import config


class GitoException(Exception):
    pass


def create_repo(name: str) -> str:
    """Creates a repo in Gito, returns the ID"""
    url = config.gito_base_url + "/api/repos"
    r = requests.post(url, json={"name": name})
    try:
        r.raise_for_status()
    except Exception as e:
        raise GitoException("Non-OK status code") from e

    location = r.headers.get("location")
    if location is None:
        raise GitoException("No location header after OK response")

    return location.split("/")[-1]


def get_repo(id: str) -> dict[str, Any]:
    """Gets repo info from Gito, given the repo ID

    Repo info is like:
    {
        "id": "abcd12345678",
        "name": "rajdhani",
        "repo_name": "abcd12345678/rajdhani",
        "git_url": "https://git.pipal.in/abcd12345678/rajdhani"
    }
    """
    url = config.gito_base_url + f"/api/repos/{id}"
    r = requests.get(url)
    try:
        r.raise_for_status()
    except Exception as e:
        raise GitoException("Non-OK status code") from e

    return r.json()


def delete_repo(id: str) -> None:
    """Deletes a repository from Gito"""
    url = config.gito_base_url + f"/api/repos/{id}"
    r = requests.delete(url)
    try:
        r.raise_for_status()
    except Exception as e:
        raise GitoException("Non-OK status code") from e


def get_webhook(id: str) -> str | None:
    """Gets the webhook URL that is currently set.

    None if no webhook URL is set
    """
    url = config.gito_base_url + f"/api/repos/{id}/hook"
    r = requests.get(url)
    try:
        r.raise_for_status()
    except Exception as e:
        raise GitoException("Non-OK status code") from e

    return r.json()["url"]


def set_webhook(id: str, webhook_url: str) -> str | None:
    """Sets the webhook URL for a repo. Returns new webhook URL.
    """
    url = config.gito_base_url + f"/api/repos/{id}/hook"
    r = requests.post(url, json={"url": webhook_url})
    try:
        r.raise_for_status()
    except Exception as e:
        raise GitoException("Non-OK status code") from e

    return r.json()["url"]
