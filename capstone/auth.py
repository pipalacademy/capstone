import requests
from flask import session

from .db import User


class Github:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.oauth_base_url = "https://github.com/login/oauth"
        self.api_base_url = "https://api.github.com"

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_oauth_url(self):
        return f"{self.oauth_base_url}/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}"

    def get_access_token(self, code):
        """Get access token from github
        """
        print("params: ", {"client_id": self.client_id,
                            "client_secret": self.client_secret, "code": code})
        token_url = f"{self.oauth_base_url}/access_token"
        r = requests.post(
            token_url,
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
            })
        r.raise_for_status()
        print(r.json())
        return r.json()["access_token"]

    def get_username(self, token):
        """Get username from github
        """
        user_url = f"{self.api_base_url}/user"
        r = requests.get(
            user_url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            })
        r.raise_for_status()
        return r.json()["login"]


def login_user(user):
    session["user"] = user.username


def logout_user():
    session.pop("user", None)


def get_logged_in_user():
    username = session.get("user")
    return username and User.find(username=username)
