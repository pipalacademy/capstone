from functools import wraps

from flask import Flask, abort, flash, redirect, request, session, url_for
from kutty import html, Markdown, Optional

from .api import api
from .db import Activity, Project, User, check_password
from .components import (
    AbsoluteCenter, AuthNavEntry, Breadcrumb, Form, Layout,
    LinkWithoutDecoration, LoginButton, LoginCard, Page,
    ProjectHero, ProjectCard, ProjectGrid, ProgressBar, TaskCard, LinkButton,
    SubmitButton
)

app = Flask(__name__)
app.secret_key = "hello, world!"  # TODO: change this
app.register_blueprint(api, url_prefix="/api")

layout = Layout("Capstone")
layout.navbar.right_entries.add(
    AuthNavEntry(
        login_link="/login", login_content=LoginButton("Login"),
        logout_link="/logout", logout_content="Logout",
        is_logged_in=lambda: is_authenticated(),
    )
)
layout.add_stylesheet('/static/style.css')

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


def TaskDetails(task, status, check_statuses=(), desc_formats={}):
    # TODO: desc_formats is not pretty, find another way
    if desc_formats:
        description = task.description.format(**desc_formats)
    else:
        description = task.description

    card = TaskCard(
        position=task.position,
        title=task.title,
        text=Markdown(description),
        status=status,
        collapsible_id=task.name,
        collapsed=False if status == "In Progress" else True,
    )
    # TODO: move this to another element, and make it part of the TaskCard
    if check_statuses:
        card.body.add_subtitle("Checks:")
        checks_list = card.body.add_check_list()
        for check, check_status in zip(task.checks, check_statuses):
            if check.name == check_status.name:
                checks_list.add_item(
                    title=check.title or check_status.name,
                    status=check_status.status,
                    message=check_status.message
                )
    return card

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


def is_authenticated():
    return get_authenticated_user() is not None


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

    page = Page(title="Projects")
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

    page = Page(title="Dashboard")
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


@app.route("/projects/<name>", methods=["GET", "POST"])
def project(name):
    user = get_authenticated_user()
    project = Project.find(name=name)
    is_authenticated = bool(user)
    has_started_project = is_authenticated and user.has_started_project(project.name)
    activity = user.get_activity(project.name) if has_started_project else None

    if request.method == "POST":
        if not is_authenticated:
            flash("You must login before starting a project", "error")
        elif has_started_project:
            flash("You have already started this project!", "error")
        else:
            user.start_project(project.name)
            flash("You have started this project. All the best!", "success")
            return redirect(request.url)

    page = Page(title="", container=html.div())
    hero = ProjectHero(
        title=project.title,
        subtitle=project.short_description,
        text=Markdown(project.description),
        app_url=activity and activity.vars.get("app_url"),
    )
    main = html.div(class_="container")
    page << hero
    page << main

    if not is_authenticated:
        hero.body.add(LinkButton("Start Project", href="/login", class_="btn-lg"))
    elif not has_started_project:
        hero.body.add(
            Form(SubmitButton("Start Project", class_="btn-lg"), method="POST")
        )

    activity = has_started_project and user.get_activity(project.name) or None
    for task in project.get_tasks():
        task_activity = activity and activity.get_task_activity(task.id)
        desc_formats = {
            "git_url": activity.git_url,
        } if activity is not None and task.position == 0 else {}
        main << TaskDetails(
            task,
            status=task_activity and task_activity.status or None,
            check_statuses=task_activity and task_activity.checks or None,
            desc_formats=desc_formats,
        )

    return layout.render_page(page)


@app.route("/activity")
@authenticated
def all_activity(user):
    page = Page(title="Activity")

    project_section_empty_state = html.div(html.em("No participants have started this project."))

    for project in Project.find_all(is_active=True):
        project_section = html.div(
            html.h3(project.title), id=project.name, class_="my-3")
        project_activities = html.div(class_="m-3")

        for activity in Activity.find_all(project_id=project.id):
            user = activity.get_user()
            progress = activity.get_progress()
            project_activities << html.div(class_="row").add(
                html.div(
                    html.a(
                        user.full_name,
                        " - ",
                        f"{progress['completed_tasks']}/{progress['total_tasks']}",
                        href=url_for(
                            "individual_activity",
                            username=activity.username,
                            project_name=activity.project_name),
                    ),
                    class_="col-12 col-sm-3 my-auto",
                ),
                html.div(
                    ProgressBar(
                        percentage=progress["percentage"],
                        height="25px",
                        label=f"{progress['percentage']}%"),
                    class_="col-12 col-sm-9 my-auto",
                ),
            )

        project_section << project_activities
        if project_activities.is_empty():
            project_section << project_section_empty_state

        page << project_section

    return layout.render_page(page)


@app.route("/users/<username>/projects/<project_name>")
@authenticated
def individual_activity(user, username, project_name):
    user = User.find(username=username)
    project = Project.find(name=project_name)
    activity = user.get_activity(project.name)

    breadcrumbs = Breadcrumb()
    breadcrumbs.add_item("All Activity", href=url_for("all_activity"))
    breadcrumbs.add_item(project.title, href=url_for("all_activity", _anchor=project.name)),
    breadcrumbs.add_item(user.full_name, active=True)
    breadcrumbs.add_class("p-0").breadcrumb_list.add_class("p-0")

    page = Page("", container=html.div())
    hero = ProjectHero(
        html.div(breadcrumbs, class_="container"),
        title=project.title,
        subtitle=project.short_description,
        text=Markdown(project.description),
        app_url=activity.vars.get("app_url"),
    )
    main = html.div(class_="container")

    page << hero
    page << main

    for task in project.get_tasks():
        task_activity = activity and activity.get_task_activity(task.id)
        main << TaskDetails(
            task,
            status=task_activity and task_activity.status or None,
            check_statuses=task_activity and task_activity.checks or None,
        )

    return layout.render_page(page)
