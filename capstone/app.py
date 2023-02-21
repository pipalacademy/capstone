from functools import wraps

from flask import Flask, abort, flash, redirect, request, session, url_for
from kutty import html, Markdown, Optional
from kutty.bootstrap import Layout, Hero

from .api import api
from .db import Activity, Project, User, check_password
from .components import (
    AbsoluteCenter, LinkWithoutDecoration, LoginCard,
    Page, ProjectCard, ProjectGrid, make_task_card,
)

app = Flask(__name__)
app.secret_key = "hello, world!"  # TODO: change this
app.register_blueprint(api, url_prefix="/api")

layout = Layout("Capstone")


def ProjectTeaser(project, is_started):
    return LinkWithoutDecoration(
        ProjectCard(
            title=project.title,
            short_description=project.short_description,
            tags=project.tags,
            is_started=is_started,
        ),
        href=project.html_url,
    )


@app.before_request
def add_auth_button():
    login_button = html.button("Login", class_="btn btn-dark")

    def set_auth_link(content, url):
        layout.navbar.right_entries.children = []
        layout.navbar.add_link(content, url, right=True)

    if get_authenticated_user() is not None:
        set_auth_link("Logout", "/logout")
    else:
        set_auth_link(login_button, "/login")


def authenticated(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            abort(401)
        return handler(*args, user=user, **kwargs)
    return wrapper


def get_authenticated_user():
    if "username" in session:
        return User.find(username=session["username"])
    else:
        return None


def login_user(username):
    session["username"] = username


def logout_user():
    session.pop("username")


@app.route("/")
def index():
    user = get_authenticated_user()
    if user:
        return redirect("/dashboard")
    else:
        return redirect("/projects")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", "/")

    page = Page(
        "",
        container=html.div(class_="w-100 h-100"),
    )
    page << html.tag("style", "body { background-color: #D3D3D3; }")

    center = AbsoluteCenter()
    page << center

    login_card = LoginCard(
        username_field="username", password_field="password",
        method="POST", action=url_for("login", next=next_page),
    )
    center << login_card

    if request.method == "GET":
        return layout.render_page(page)

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            login_card.add_error("Missing username or password")
            return layout.render_page(page)

        user = User.find(username=username)
        if (not user or not check_password(password, user.password)):
            login_card.add_error("Invalid username or password")
            return layout.render_page(page)

        login_user(user.username)
        flash("Logged in successfully", "success")
        return redirect(next_page)
    else:
        abort(405)


@app.route("/logout")
@authenticated
def logout(user):
    logout_user()
    return redirect("/")


@app.route("/projects")
def projects():
    projects = Project.find_all(is_active=True)

    page = Page("Projects")
    page << ProjectGrid(
        class_="mt-3",
        columns=[
            ProjectTeaser(project, is_started=False) for project in projects
        ]
    )
    return layout.render_page(page)


@app.route("/dashboard")
@authenticated
def dashboard(user):
    projects = Project.find_all(is_active=True)
    started_projects = [
        project
        for project in projects
        if user.has_started_project(project.name)
    ]
    unstarted_projects = [
        project
        for project in projects
        if not user.has_started_project(project.name)
    ]

    page = Page("Dashboard")
    page << Optional(
        html.div(class_="my-3").add(
            html.h2("Your Projects"),
            ProjectGrid(columns=[
                ProjectTeaser(project, is_started=True)
                for project in started_projects
            ]),
        ),
        render_condition=lambda _: bool(started_projects),
    )
    page << Optional(
        html.div(class_="my-3").add(
            html.h2("Explore..."),
            ProjectGrid(columns=[
                ProjectTeaser(project, is_started=False)
                for project in unstarted_projects
            ]),
        ),
        render_condition=lambda _: bool(unstarted_projects),
    )

    return layout.render_page(page)


@app.route("/projects/<name>")
def project(name):
    user = get_authenticated_user()
    project = Project.find(name=name)

    page = Page("", container=html.div())
    hero = Hero(
        title=project.title,
        subtitle=project.short_description,
        text=Markdown(project.description),
    )
    main = html.div(class_="container")
    page << hero
    page << main

    if user and user.has_started_project(project.name):
        activity = Activity.find(
            username=user.username, project_name=project.name)

        task_activities_list = activity.get_tasks()
        task_activities = {ta.task_id: ta for ta in task_activities_list}
        for task in project.get_tasks():
            task_activity = task_activities.get(task.id)
            card = make_task_card(
                position=task.position,
                title=task.title,
                text=Markdown(task.description),
                status=task_activity and task_activity.status)
            main << card
    else:
        href = "#" if user else url_for("login", next=request.path)
        hero.add_cta("Start Project", href=href)

        for task in project.get_tasks():
            card = make_task_card(
                position=task.position, title=task.title, text=Markdown(task.description))
            main << card

    return layout.render_page(page)
