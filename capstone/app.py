from functools import wraps

from flask import Flask, abort, request
from kutty import html
from kutty.bootstrap import Layout, Page, Card

from .api import api
from .db import Project, User


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


def authenticated(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        # TODO: implement this
        user = User.find(username="kaustubh")
        return handler(*args, user=user, **kwargs)
    return wrapper


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
            class_="d-flex justify-content-end mt-2")
        if user.has_started_project(project.name):
            card.body.add(continue_button)
            your_projects.add_column(card)
        else:
            explore.add_column(card)

    if not your_projects.is_empty():
        page << html.div(class_="mt-2").add(html.h2("Your Projects"), your_projects)
    if not explore.is_empty():
        page << html.div(class_="mt-2").add(html.h2("Explore"), explore)

    return layout.render_page(page)
