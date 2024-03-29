import string
import requests
from flask import Blueprint, g, request, redirect, request, session, url_for
from urllib.parse import urlencode

from . import config
from .db import db, Site, User
from .utils import get_random_string


auth_bp = Blueprint("auth", __name__)

CLIENT_ID = config.google_client_id
CLIENT_SECRET = config.google_client_secret

GOOGLE_OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@auth_bp.route("/login")
def login():
    next = request.args.get("next")
    return redirect(url_for("auth.google_oauth_login", next=next))


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@auth_bp.route("/google")
def google_oauth_login():
    auth_url = get_google_auth_url(CLIENT_ID, next=request.args.get("next"))
    return redirect(auth_url)


@auth_bp.route("/google/callback")
def google_oauth_callback():
    code = request.args.get("code")
    next = request.args.get("state")
    user_info = get_user_info(CLIENT_ID, CLIENT_SECRET, code)
    if not user_info:
        return "Error getting user info", 400
    else:
        # no longer needed
        revoke_token(CLIENT_SECRET, user_info["access_token"])

    email = user_info["email"]
    user = get_or_create_user(site=g.site, email=email, full_name=user_info["name"])
    login_user(user_id=user.id)
    return redirect(next or "/")


# create user

def get_or_create_user(site: Site, email: str, full_name: str) -> User:
    user = User.find(site_id=site.id, email=email)

    # user exists
    if user is not None:
        return user

    # user must be created
    with db.transaction():
        user = User(
            site_id=site.id,  # type: ignore
            email=email,
            username=get_random_username(site=site),
            full_name=full_name
        ).save()

        # set the actual username. try for email prefix, then
        # fallback to appending user id to this prefix
        new_username = get_username_from_email(user.email)
        if not is_username_available(site, new_username):
            new_username = get_fallback_username(user)

        user.update(username=new_username).save()

    return user


# extract username from email

def get_username_from_email(email: str) -> str:
    return email.split("@")[0]


def is_username_available(site: Site, username: str) -> bool:
    return site.get_user(username=username) is None


def get_random_username(site: Site) -> str:
    username = get_random_string(allowed_chars=string.ascii_lowercase)
    while not is_username_available(site, username):
        username = get_random_string(allowed_chars=string.ascii_lowercase)
    return username


def get_fallback_username(user: User) -> str:
    """Get a fallback username for a user.

    But, the user must be saved to database.
    """
    return get_username_from_email(user.email) + f"-{user.id}"


# authentication helpers

def get_authenticated_user():
    if "user_id" in session:
        return User.find(id=session["user_id"])
    else:
        return None


def login_user(user_id):
    session["user_id"] = user_id


def logout_user():
    session.pop("user_id", None)


# google oauth helpers

def get_google_auth_url(client_id, next=""):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": url_for("auth.google_oauth_callback", _external=True),
        "state": next or ""
    }
    return f"{GOOGLE_OAUTH_URL}?{urlencode(params)}"


def get_user_info(client_id, client_secret, code):
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": url_for("auth.google_oauth_callback", _external=True)
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    token_data = response.json()
    if "access_token" not in token_data:
        return None

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    user_info = response.json()
    user_info["access_token"] = token_data["access_token"]
    return user_info


def revoke_token(client_secret, access_token):
    payload = {"token": access_token, "client_secret": client_secret}
    requests.post(GOOGLE_REVOKE_URL, data=payload)
