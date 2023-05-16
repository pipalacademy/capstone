from functools import wraps

from flask import Flask, abort, flash, g, redirect, request, send_from_directory, url_for
from kutty import html, Markdown, Optional
from kutty.bootstrap.hero import Hero, HeroContainer, HeroTitle, HeroSeparator, HeroSubtitle

from .api import api
from .auth import auth_bp, get_authenticated_user
from .db import Site
from .components import (
    AbsoluteCenter, Accordion, AuthNavEntry, Breadcrumb, Card, Form, HiddenInput,
    Layout, LinkWithoutDecoration, LoginButton, LoginCard, Page,
    ProjectHero, ProjectCard, ProjectGrid, ProgressBar, TaskCard, LinkButton,
    SubmitButton
)
from .utils.user_project import delete_user_project, start_user_project

app = Flask(__name__)
app.secret_key = "hello, world!"  # TODO: change this
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")

layout = Layout("Capstone")
layout.navbar.add_link("Projects", url="/projects")
layout.navbar.add_link("Courses", url="/courses")
layout.navbar.right_entries.add(
    AuthNavEntry(
        login_link="/auth/login", login_content=LoginButton("Login"),
        logout_link="/auth/logout", logout_content="Logout",
        is_logged_in=lambda: is_authenticated(),
    )
)
layout.add_stylesheet('/static/style.css')
layout.add_stylesheet('/static/codehilite-styles.css')


def is_authenticated():
    return get_authenticated_user() is not None


def authenticated(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            abort(401)
        return handler(*args, user=user, **kwargs)
    return wrapper


@app.before_request
def set_site():
    domain = request.host.split(":")[0]
    site = Site.find(domain=domain)
    if not site:
        page = Page(title="Site not found")
        page << f"The site <em>{domain}</em> is not found."
        html = layout.render_page(page)
        return html, 404
    else:
        g.site = site


@app.route("/")
def index():
    user = get_authenticated_user()
    if user:
        return redirect("/dashboard")
    else:
        return redirect("/home")


@app.route("/home")
def home():
    projects = g.site.get_projects(is_published=True)

    page = Page(title="", container=html.div(class_="pb-4 pb-md-5"))
    page << html.HTML("""
        <div class="jumbotron hero">
          <div class="container">
            <div class="hero-image">
              <img src="/static/images/undraw-programming-dark.svg" style="width: 100%;">
            </div>

            <div class="hero-body">
              <h1 class="hero-title">What would you like to build today?</h1>
              <p class="lead">Level up your coding skills by building something challenging.</p>

              <p>The capstone platform makes it easier to work with complex projects by taking care of deploying the application and validating it on every git push.</p>
              <p>Ready to start?</p>
            </div>

            <div style="clear: both;"></div>
          </div>
        </div>
    """)
    div = html.div(class_="container section")
    page << div

    if projects:
        div << html.h2("Featured Projects")

        div << ProjectGrid(
            class_="mt-3",
            columns=[
                ProjectTeaser(project, is_started=False) for project in projects
            ],
        )
        div << Optional(
            # empty state
            html.em("No projects available."),
            render_condition=lambda _: not projects,
        )
    return layout.render_page(page)



@app.route("/projects")
def projects():
    projects = g.site.get_projects(is_published=True)

    page = Page(title="Projects")
    page << ProjectGrid(
        class_="mt-3",
        columns=[
            ProjectTeaser(project, is_started=False) for project in projects
        ],
    )
    page << Optional(
        # empty state
        html.em("No projects available."),
        render_condition=lambda _: not projects,
    )
    return layout.render_page(page)


@app.route("/dashboard")
@authenticated
def dashboard(user):
    projects = g.site.get_projects(is_published=True)
    started_projects = [
        project for project in projects
        if project.get_user_project(user.id) is not None
    ]
    unstarted_projects = [
        project for project in projects if project not in started_projects
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
    page << Optional(
        # empty state
        html.em("No projects have been added."),
        render_condition=lambda _: not started_projects and not unstarted_projects,
    )

    return layout.render_page(page)


@app.route("/projects/<name>", methods=["GET", "POST"])
def project(name):
    project = g.site.get_project(name=name)
    if project is None:
        abort(404)

    user = get_authenticated_user()
    user_project = project.get_user_project(user.id) if user else None

    # TODO: split this into two methods

    if request.method == "POST":
        if not user:
            abort(401)
        action = request.form.get("action", "start")
        if action == "start":
            if user_project:
                flash("You have already started this project.")
            else:
                start_user_project(user=user, project=project)
                flash("You have started this project.")
        elif action == "reset":
            if not user_project:
                flash("You have not started this project yet.")
            else:
                delete_user_project(user_project)
                flash("Your progress has been reset.")
        return redirect(url_for("project", name=name))
    else:
        page = Page(title="", container=html.div(class_="pb-4 pb-md-5"))
        hero = ProjectHero(
            title=project.title,
            subtitle=project.short_description,
            text=Markdown(project.description),
            app_url=None,
        )
        if not user:
            hero.body.add(LinkButton("Start Project",
                                     class_="btn-lg", href=url_for("auth.login")))
        elif not user_project:
            hero.body << Form(method="POST").add(
                HiddenInput(name="action", value="start"),
                SubmitButton("Start Project", class_="btn-lg"),
            )
        else:
            hero.body << Form(method="POST").add(
                HiddenInput(name="action", value="reset"),
                SubmitButton(
                    "Reset Project",
                    class_="btn-lg btn-danger",
                    onclick="return confirm('Are you sure?');"
                )
            )

        main = html.div(class_="container")
        page << hero
        page << main
        for task in project.get_tasks():
            task_status = user_project and user_project.get_task_status(task)
            main << TaskDetails(
                task,
                status=task_status and task_status.status or None,
                description_vars=user_project and user_project.get_context_vars() or None,
                check_statuses=task_status and task_status.get_check_statuses() or (),
            )

        return layout.render_page(page)


@app.route("/projects/<name>/history")
@authenticated
def project_history(name, user):
    project = g.site.get_project(name=name)
    if not project:
        abort(404)

    page = Page(title="Project History")

    updates = project.get_history()
    if not updates:
        page << html.em("No updates have been made to this project.")
    else:
        accordion = Accordion()
        page << accordion

        for update in updates:
            accordion.add_card(
                header=html.div(class_="d-flex justify-content-between").add(
                    html.div(update["timestamp"].strftime("%a, %B %d %Y, %I:%M %p UTC")),
                    html.div(update["status"]),
                ),
                body=html.pre(update["log"]) if update["log"] else html.em("No logs"),
            )

    return layout.render_page(page)


@app.route("/projects/<name>/user/history")
@authenticated
def user_project_history(name, user):
    project = g.site.get_project(name=name)
    if not project:
        abort(404)
    user_project = project.get_user_project(user_id=user.id)

    page = Page(title="Project History")

    updates = user_project.get_history()
    if not updates:
        page << html.em("No updates have been made to this project.")
    else:
        accordion = Accordion()
        page << accordion

        for update in updates:
            accordion.add_card(
                header=html.div(class_="d-flex justify-content-between").add(
                    html.div(update["timestamp"].strftime("%a, %B %d %Y, %I:%M %p UTC")),
                    html.div(update["status"]),
                ),
                body=html.pre(update["log"]) if update["log"] else html.em("No logs"),
            )

    return layout.render_page(page)


@app.route("/courses")
def courses():
    page = Page(title="Courses")
    for course in g.site.get_courses():
        page << LinkWithoutDecoration(
            Card(
                title=course.title,
                text=html.div(course.description, class_="text-truncate"),
            ),
            href=course.get_url(),
        )
    return layout.render_page(page)


@app.route("/courses/<name>")
def course(name):
    course = g.site.get_course(name)
    if not course:
        abort(404)

    page = Page("", container=html.div())
    page << Hero(
        title=course.title,
    )

    container = html.div(class_="container")
    page << container

    container << html.tag("ol").add(
        *[
            html.li(
                html.div(
                    html.strong(module.title),
                    html.tag("ol", type_="a").add(
                        *[
                            html.li(html.a(lesson.title, href=lesson.get_url()))
                            for lesson in module.get_lessons()
                        ]
                    )
                )
            )
            for module in course.get_modules()
        ]
    )
    return layout.render_page(page)


@app.route("/courses/<name>/media/<path:filename>")
def course_media(name, filename):
    course = g.site.get_course(name)
    if not course:
        abort(404)
    return send_from_directory(course.get_media_dir().resolve(), filename)


@app.route("/courses/<name>/lessons/<module_name>/<lesson_name>")
def course_lesson(name, module_name, lesson_name):
    course = g.site.get_course(name)
    if not course:
        abort(404)
    module = course.get_module(module_name)
    if not module:
        abort(404)
    lesson = module.get_lesson(lesson_name)
    if not lesson:
        abort(404)

    prev_lesson, next_lesson = lesson.get_prev(), lesson.get_next()

    page = Page("", container=html.div(class_="bg-white pb-4 pb-md-5"))
    page << Hero(
        HeroContainer(
            HeroSubtitle(
                html.a(course.title, href=course.get_url()),
                " / ",
                html.a(module.title),
            ),
            HeroSeparator(),
            HeroTitle(lesson.title)
        ),
    )

    container = html.div(class_="container")
    container << html.div(html.HTML(lesson.get_html()), class_="mb-2")

    container << html.div(class_="my-3").add(
        Optional(
            html.a(
               "<< Prev",
               class_="btn btn-outline-primary px-2 float-left rounded-right-0",
               href=prev_lesson and prev_lesson.get_url() or "",
            ),
            render_condition=lambda _: bool(prev_lesson),
        ),
        Optional(
            html.a(
                "Next >>",
                class_="btn btn-outline-primary px-2 float-right rounded-left-0",
                href=next_lesson and next_lesson.get_url() or "",
            ),
            render_condition=lambda _: bool(next_lesson)
        ),
        html.div(style="clear: both")  # to fix the floating (ref https://css-tricks.com/all-about-floats/)
    )

    page << container
    return layout.render_page(page)


@app.route("/activity")
@authenticated
def all_activity(user):
    page = Page(title="Activity")

    project_section_empty_state = html.div(html.em("No participants have started this project."))

    for project in g.site.get_projects(is_published=True):
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
    user = g.site.get_user(username=username)
    project = g.site.get_project(name=project_name)
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


# Component makers

def ProjectTeaser(project, is_started):
    return LinkWithoutDecoration(
        ProjectCard(
            title=project.title,
            short_description=project.short_description,
            tags=project.tags,
            is_started=is_started,
            class_="teaser-card"
        ),
        href=f"/projects/{project.name}"
    )


def TaskDetails(task, status, check_statuses=(), description_vars=None):
    card = TaskCard(
        position=task.position,
        title=task.title,
        text=Markdown(task.render_description(description_vars)),
        status=status,
        collapsible_id=task.name,
        collapsed=False if status == "In Progress" else True,
    )
    # TODO: move this to another element, and make it part of the TaskCard
    if check_statuses:
        card.body.add_subtitle("Checks:")
        checks_list = card.body.add_check_list()
        for check, check_status in zip(task.get_checks(), check_statuses):
            checks_list.add_item(
                title=check.title or check_status.name,
                status=check_status.status,
                message=check_status.message
            )
    return card
