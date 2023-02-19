from textwrap import dedent

from kutty import html
from kutty.bootstrap import Layout, Page, Card
from kutty.bootstrap.card import CardBody, CardText, CardTitle


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


class AbsoluteCenter(html.HTMLElement):
    TAG = "div"
    CLASS = "absolute-center"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        absolute_center_style = html.tag(
          "style",
          dedent("""\
            .absolute-center {
              position: absolute;
              left: 50%;
              top: 50%;
              -webkit-transform: translate(-50%, -50%);
              transform: translate(-50%, -50%);
            }"""))
        self.add(absolute_center_style)


def make_login_card(username_id="username", password_id="password", **form_kwargs):
    card = Card(
        CardBody(
            CardTitle("Login"),
            html.tag(
                "form",
                html.div(class_="form-group").add(
                    html.tag("label", "Username", for_="username"),
                    html.input(type="text", class_="form-control",
                               id=username_id, name=username_id, required="true")
                ),
                html.div(class_="form-group").add(
                    html.tag("label", "Password", for_="password"),
                    html.input(type="password", class_="form-control",
                               id=password_id, name=password_id, required="true")
                ),
                html.button("Login", type="submit", class_="btn btn-primary"),
                **form_kwargs,
            )
        )
    )
    card.add_class("p-4")
    return card


def make_project_card(title, short_description, tags, url, show_continue_button=False):
    card = Card(
        title=title,
        text=short_description,
    )
    card.add_class("h-100")
    for tag in tags:
        badge = Badge(tag)
        badge.add_class("mr-2 p-2")
        card.body << badge
    if show_continue_button:
        card.body << html.div(class_="d-flex justify-content-end mt-3").add(
                html.button("Continue ›", class_="btn btn-secondary"))
    return html.a(card, class_="text-decoration-none text-reset", href=url)


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
                  data_toggle="collapse")


green_tick_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M243.8 339.8C232.9 350.7 215.1 350.7 204.2 339.8L140.2 275.8C129.3 264.9 129.3 247.1 140.2 236.2C151.1 225.3 168.9 225.3 179.8 236.2L224 280.4L332.2 172.2C343.1 161.3 360.9 161.3 371.8 172.2C382.7 183.1 382.7 200.9 371.8 211.8L243.8 339.8zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #28a745;", class_="px-2 mr-2")
red_x_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor"xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M175 175C184.4 165.7 199.6 165.7 208.1 175L255.1 222.1L303 175C312.4 165.7 327.6 165.7 336.1 175C346.3 184.4 346.3 199.6 336.1 208.1L289.9 255.1L336.1 303C346.3 312.4 346.3 327.6 336.1 336.1C327.6 346.3 312.4 346.3 303 336.1L255.1 289.9L208.1 336.1C199.6 346.3 184.4 346.3 175 336.1C165.7 327.6 165.7 312.4 175 303L222.1 255.1L175 208.1C165.7 199.6 165.7 184.4 175 175V175zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #dc3545;", class_="px-2 mr-2")
yellow_circle_mark = html.span(
        html.HTML("""<svg style="height: 100%;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #ffc107;", class_="px-2 mr-2")


