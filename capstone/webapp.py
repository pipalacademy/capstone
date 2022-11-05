import functools
from dataclasses import asdict

import markdown
import web
from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, url_for
from jinja2 import Markup

from . import config
from . import form
from .auth import Github, login_user, logout_user, get_logged_in_user
from .db import User
from .tasks import TaskStatus


app = Flask(__name__)
app.secret_key = config.secret_key


def get_github():
    redirect_uri = url_for("github_callback", _external=True)
    return Github(config.github_client_id, config.github_client_secret, redirect_uri)


def auth_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.template_filter()
def markdown_to_html(md):
    return Markup(markdown.markdown(md))


@app.before_request
def before_request():
    g.user = get_logged_in_user()


@app.context_processor
def update_context():
    return {
        "datestr": web.datestr,
        "title": g.capstone.title,
        "subtitle": g.capstone.subtitle,
        "current_user": g.user,
        "make_input_html": form.make_input_html,
    }


@app.route("/")
def index():
    if get_logged_in_user():
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/leaderboard")
def leaderboard():
    sites = g.capstone.get_all_sites()
    return render_template("leaderboard.html", sites=sites)


@app.route("/dashboard", methods=["GET", "POST"])
@auth_required
def dashboard():
    """Renders dashboard (site page).

    `tasks` given to the template is a list of dict.

    task.status can be either of "pass", "fail", "current", "locked".
    """
    site = g.capstone.get_site(g.user.username)
    if not site:
        abort(404)

    if request.method == "POST":
        task_name = request.form["task_name"]
        task = g.capstone.get_task(task_name)
        if not task:
            abort(400)

        if task.form:
            try:
                task.form.validate(request.form)
            except form.ValidationError as e:
                flash(str(e), "error")
                return redirect(url_for("dashboard"))
            task.form.save(site, request.form)

        status = g.capstone.get_status(site)
        site.update_status(status)
        if status["tasks"][task.name]["status"] == TaskStatus.PASS:
            task.run_actions(site)

        return redirect(url_for("dashboard"))

    else:
        raw_tasks = g.capstone.get_tasks()
        tasks = []

        for raw_task in raw_tasks:
            task = asdict(raw_task)
            task_status = site.get_task_status(task["name"])
            task["status"] = task_status.status if task_status else "locked"
            task["checks"] = task_status.checks if task_status else []

            form_values = raw_task.form and raw_task.form.get_current_values(site)
            if form_values:
                task["form"]["values"] = form_values

            if task["name"] == site.current_task:
                task["status"] = "current"

            tasks.append(task)

        return render_template(
            "dashboard.html",
            tasks=tasks,
            progress=get_progress(tasks),
        )


@app.route("/site/<name>/refresh", methods=["POST"])
def site_refresh(name):
    """Refresh status of site (re-run deployment or checks)
    """
    site = g.capstone.get_site(name)
    if not site:
        abort(404)
    status = g.capstone.get_status(site)
    site.update_status(status)
    return jsonify(status)


@app.route("/auth/github")
def github_initiate():
    """Initiate github oauth flow
    """
    url = get_github().get_oauth_url()
    return redirect(url)


@app.route("/auth/github/callback")
def github_callback():
    """Callback for github oauth flow
    """
    code = request.args.get("code")
    if not code:
        abort(400)

    gh = get_github()
    token = gh.get_access_token(code)
    username = gh.get_username(token)

    user = User.find(username=username) or User.create(username=username)
    login_user(user)

    g.capstone.get_site(user.username) or g.capstone.new_site(user.username)

    flash(f"Welcome to Self Hosting 101, {user.username}", "info")
    return redirect(url_for("index"))


@app.route("/account/me")
@auth_required
def verify_auth():
    """Verify that user is logged in
    """
    return jsonify(
        username=g.user.username,
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logout")
@auth_required
def logout():
    logout_user()
    return redirect("/")


def get_progress(tasks):
    passed_tasks = sum(1 for task in tasks if task["status"] == TaskStatus.PASS)
    return round(passed_tasks * 100 / len(tasks))
