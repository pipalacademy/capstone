from functools import wraps

from flask import Flask, abort, request
from kutty import html, Markdown
from kutty.bootstrap import Layout, Page, Card, Hero
from kutty.bootstrap.card import CardBody, CardText, CardTitle

from .api import api
from .db import Activity, Project, User


app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

layout = Layout("Capstone")
layout.navbar.add_link("Login", "/login", right=True)


class Grid(html.HTMLElement):
    TAG = "div"
    CLASS = "row"

    def __init__(self, *args, col_class="col", **kwargs):
        self.col_class = col_class
        super().__init__(*args, **kwargs)

    def add_column(self, *children):
        column = html.div(*children, class_=self.col_class)
        self.add(column)
        return column


class Badge(html.HTMLElement):
    TAG = "span"
    CLASS = "badge badge-primary"


def make_project_card(title, short_description, tags, *extra):
    card = Card(
        title=title,
        text=short_description,
    )
    for tag in tags:
        badge = Badge(tag)
        badge.add_class("mr-2 p-2")
        card.body << badge
    card.body.add(*extra)
    return card


green_tick_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M243.8 339.8C232.9 350.7 215.1 350.7 204.2 339.8L140.2 275.8C129.3 264.9 129.3 247.1 140.2 236.2C151.1 225.3 168.9 225.3 179.8 236.2L224 280.4L332.2 172.2C343.1 161.3 360.9 161.3 371.8 172.2C382.7 183.1 382.7 200.9 371.8 211.8L243.8 339.8zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #28a745;", class_="px-2 mr-2")
red_x_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor"xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M175 175C184.4 165.7 199.6 165.7 208.1 175L255.1 222.1L303 175C312.4 165.7 327.6 165.7 336.1 175C346.3 184.4 346.3 199.6 336.1 208.1L289.9 255.1L336.1 303C346.3 312.4 346.3 327.6 336.1 336.1C327.6 346.3 312.4 346.3 303 336.1L255.1 289.9L208.1 336.1C199.6 346.3 184.4 346.3 175 336.1C165.7 327.6 165.7 312.4 175 303L222.1 255.1L175 208.1C165.7 199.6 165.7 184.4 175 175V175zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #dc3545;", class_="px-2 mr-2")
yellow_circle_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #ffc107;", class_="px-2 mr-2")


def make_task_card(position, title, text, status=None):
    status_marks = {
        "Completed": green_tick_mark,
        "Failing": red_x_mark,
        "In Progress": yellow_circle_mark,
    }
    status_mark = status_marks.get(status, "")
    collapsible_id = f"task-collapse-{position}"
    card = Card(
        CardBody(
            CardTitle(f"{position}. {title}").add_class("mb-0"),
            status_mark
        ).add_class("d-flex justify-content-between"),
        CardBody(
            CardText(text),
            class_="collapse py-0", id=collapsible_id,
        )
    ).add_class("my-3")
    return html.a(card,
                  class_="text-decoration-none text-reset",
                  href=f"#{collapsible_id}",
                  **{"data-toggle": "collapse"})


def authenticated(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        # TODO: implement this
        user = get_authenticated_user(request)
        if not user:
            return abort(404)
        return handler(*args, user=user, **kwargs)
    return wrapper


def get_authenticated_user(request):
    return User.find(username="test")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        page = html.div(id="page", class_="w-100 h-100")
        page.add(
            html.tag("style",
                     """\
body {
    background-color: #D3D3D3;
}

.center {
  position: absolute;
  left: 50%;
  top: 50%;
  -webkit-transform: translate(-50%, -50%);
  transform: translate(-50%, -50%);
}""")
        )
        card = Card(
            title="Login",
            class_="center",
        )
        card.body.add(
            html.tag(
                "form",
                html.div(class_="form-group").add(
                    html.tag("label", "Username", for_="username"),
                    html.input(type="email", class_="form-control", id="username", required="true"),
                ),
                html.div(class_="form-group").add(
                    html.tag("label", "Password", for_="password"),
                    html.input(type="password", class_="form-control", id="password", required="true"),
                ),
                html.button("Login", type="submit", class_="btn btn-primary")
            )
        )
        card.add_class("p-4")
        page << card
        return layout.render_page(page)
    elif request.method == "POST":
        # TODO: implement this
        pass
    else:
        abort(405)


@app.route("/projects")
def projects():
    projects = Project.find_all(is_active=True)

    page = Page("Projects")
    grid = Grid(col_class="col-6")
    grid.add_class("mt-3")
    for project in projects:
        card = make_project_card(
            title=project.title,
            short_description=project.short_description,
            tags=project.tags)
        grid.add_column(card)

    page << grid
    return layout.render_page(page)


@app.route("/dashboard")
@authenticated
def dashboard(user):
    projects = Project.find_all()
    page = Page("Dashboard")
    your_projects = Grid(col_class="col-6")
    explore = Grid(col_class="col-6")
    for project in projects:
        card = make_project_card(
            title=project.title,
            short_description=project.short_description,
            tags=project.tags,
        )

        continue_button = html.div(
            html.button("Continue ›", class_="btn btn-secondary"),
            class_="d-flex justify-content-end mt-3")
        if user.has_started_project(project.name):
            card.body.add(continue_button)
            your_projects.add_column(card)
        else:
            explore.add_column(card)

    if not your_projects.is_empty():
        page << html.div(class_="mt-3").add(html.h3("Your Projects"), your_projects)
    if not explore.is_empty():
        page << html.div(class_="mt-3").add(html.h3("Explore"), explore)

    return layout.render_page(page)


@app.route("/projects/<name>")
@authenticated
def project(name, user):
    project = Project.find(name=name)
    page = html.div()
    hero = Hero(
        title=project.title,
        subtitle=project.short_description,
        text=Markdown(project.description),
    )
    main = Page("")
    page << hero
    page << main

    if user.has_started_project(project.name):
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
        hero.add_cta("Start Project", href="#")
        for task in Project.find(name="build-your-own-shell").get_tasks():
            card = make_task_card(
                position=task.position, title=task.title, text=Markdown(task.description))
            main << card

    return layout.render_page(page)
