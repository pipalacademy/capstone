from textwrap import dedent

from flask import get_flashed_messages
from html import escape as html_escape
from kutty import html, Optional
from kutty.bootstrap import Layout as _Layout, Page as _Page, Card, Hero
from kutty.bootstrap.base import BootstrapElement
from kutty.bootstrap.card import CardBody, CardText, CardTitle
from kutty.components.navbar import NavEntry


class Page(_Page):
    def __init__(self, *args, title=None, **kwargs):
        super().__init__(title="", **kwargs)

        self.title = title
        if self.title:
            self.add(PageTitle(title))

        for category, message in get_flashed_messages(with_categories=True):
            alert_style = get_style_by_category(category)
            alert = Alert(message, style_as=alert_style, is_dismissible=True)
            alert.add_class("m-2")
            self << alert


def get_style_by_category(category):
    match category:
        case "error": return "danger"
        case "message": return "info"
        case _: return category


class Layout(_Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.footer = Footer()

    def render(self, content=None):
        doc = html.Document()

        doc.head.add(html.title(self.title))

        for link in self.stylesheets:
            doc.head.add(html.link(rel="stylesheet", href=link))

        doc.body.add(self.navbar)
        doc.body.add(content)
        doc.body.add(self.footer)

        for link in self.javascripts:
            doc.body.add(html.script(src=link))

        return doc.render()


class Footer(BootstrapElement):
    TAG = "footer"
    CLASS = "my-3 py-3"


class Breadcrumb(BootstrapElement):
    TAG = "nav"
    CLASS = "breadcrumb"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.breadcrumb_list = BreadcrumbList()
        self << self.breadcrumb_list

    def add_item(self, text, href=None, active=False):
        if href:
            content = html.a(text, href=href)
        else:
            content = text

        element = BreadcrumbItem(content, active=active)
        self.breadcrumb_list << element
        return element


class BreadcrumbList(BootstrapElement):
    TAG = "ol"
    CLASS = "breadcrumb"


class BreadcrumbItem(BootstrapElement):
    TAG = "li"
    CLASS = "breadcrumb-item"

    def __init__(self, *args, active=False, **kwargs):
        super().__init__(*args, **kwargs)
        if active:
            self.add_class("active")

class PageTitle(BootstrapElement):
    TAG = "h1"
    CLASS = "my-4"


class ProgressBar(BootstrapElement):
    TAG = "div"
    CLASS = "progress"

    def __init__(self, *args, percentage, label=None, height=None, **kwargs):
        if height:
            styles = f"height: {height};"
        super().__init__(*args, style=styles, **kwargs)

        self.progress_bar = html.div(style=f"width: {percentage}%;", class_="progress-bar")
        if label:
            self.progress_bar << label

        self << self.progress_bar


class LoginButton(BootstrapElement):
    TAG = "button"
    CLASS = "btn btn-dark"


class AuthNavEntry(BootstrapElement):
    TAG = "div"

    def __init__(
            self,
            *args,
            login_link, login_content,
            logout_link, logout_content,
            is_logged_in,
            **kwargs):
        super().__init__()
        self << Optional(
            NavEntry(login_content, login_link),
            render_condition=lambda _: not is_logged_in(),
        )
        self << Optional(
            NavEntry(logout_content, logout_link),
            render_condition=lambda _: is_logged_in(),
        )


class Alert(BootstrapElement):
    TAG = "div"
    CLASS = "alert"

    def __init__(self, *args, is_dismissible=False, style_as="primary", **kwargs):
        self.body = html.div()
        super().__init__(*args, **kwargs)
        self.add(self.body, in_body=False)

        self.is_dismissible = is_dismissible
        self.add_class(f"alert-{style_as}")

        if self.is_dismissible:
            self.add_class("alert-dismissible fade show")
            self.add(
                html.button(
                    "&times;",
                    type="button", class_="close", data_dismiss="alert",
                ),
                in_body=False,
            )

    def add(self, *args, in_body=True):
        if in_body:
            self.body.add(*args)
        else:
            super().add(*args)
        return self

    def add_heading(self, text):
        element = AlertHeading(text)
        self << element
        return element

    def add_link(self, title, href):
        element = AlertLink(title, href=href)
        self << element
        return element

    def is_empty(self):
        if self.is_dismissible:
            return len(self.children) > 1
        else:
            return super().is_empty()


class AlertHeading(BootstrapElement):
    TAG = "h4"
    CLASS = "alert-heading"


class AlertLink(BootstrapElement):
    TAG = "a"
    CLASS = "alert-link"


class Grid(BootstrapElement):
    TAG = "div"
    CLASS = "row"
    COL_CLASS = "col"

    def __init__(self, *args, col_class=None, **kwargs):
        self.col_class = col_class if col_class is not None else self.COL_CLASS
        super().__init__(*args, **kwargs)

    def add_column(self, *children):
        column = html.div(*children, class_=self.col_class)
        self.add(column)
        return column


class Badge(BootstrapElement):
    TAG = "span"
    CLASS = "badge badge-secondary"


class AbsoluteCenter(BootstrapElement):
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


class LoginCard(Card):
    EXTRA_CLASSES = "p-4"

    def __init__(
            self,
            *args, username_field, password_field,
            error_message=None, method=None, action=None, **kwargs):
        super().__init__(*args, title="Login", **kwargs)
        self.add_class(self.EXTRA_CLASSES)

        self.errors = Optional(html.div())
        if error_message:
            self.error << error_message

        form_kwargs = {"method": method, "action": action}
        form_kwargs = {k: v for k, v in form_kwargs.items() if v is not None}
        self.form = LoginCardForm(
            username_field=username_field, password_field=password_field,
            **form_kwargs,
        )

        self.body << self.errors
        self.body << self.form

    def add_error(self, content):
        element = LoginCardError(content)
        self.errors << element
        return element


class LoginCardError(Alert):
    STYLE_AS = "danger"
    IS_DISMISSIBLE = True

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            style_as=self.STYLE_AS, is_dismissible=self.IS_DISMISSIBLE,
            **kwargs,
        )


class LoginCardForm(BootstrapElement):
    TAG = "form"

    def __init__(self, *args, username_field, password_field, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(
            html.div(class_="form-group").add(
                html.tag("label", "Username", for_="username"),
                html.input(
                    type="text", class_="form-control",
                    id=username_field, name=username_field, required="true"
                ),
            ),
            html.div(class_="form-group").add(
                html.tag("label", "Password", for_="password"),
                html.input(
                    type="password", class_="form-control",
                    id=password_field, name=password_field, required="true"
                ),
            ),
            html.button("Login", type="submit", class_="btn btn-primary"),
        )


class LinkButton(BootstrapElement):
    TAG = "a"
    CLASS = "btn"

    def __init__(self, *args, style_as="primary", **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(f"btn-{style_as}")


class SubmitButton(BootstrapElement):
    TAG = "button"
    CLASS = "btn"
    TYPE = "submit"

    def __init__(self, *args, style_as="primary", **kwargs):
        super().__init__(*args, type=self.TYPE, **kwargs)
        self.add_class(f"btn-{style_as}")


class Form(BootstrapElement):
    TAG = "form"


class HiddenInput(BootstrapElement):
    TAG = "input"
    TYPE = "hidden"

    def __init__(self, *args, name, value, **kwargs):
        super().__init__(*args, type=self.TYPE, name=name, value=value, **kwargs)


class ProjectHero(Hero):
    def __init__(self, *args, app_url=None, **kwargs):
        super().__init__(*args, **kwargs)
        if app_url:
            self.body.add(
                html.div(
                    html.strong(
                        "Your app has been deployed to ",
                        html.a(app_url, href=app_url, target="_blank"),
                    ),
                    class_="mt-3",
                ),
            )


class ProjectGrid(Grid):
    COL_CLASS = "col-12 col-md-6 mb-3"

    def __init__(self, *args, columns=(), **kwargs):
        super().__init__(*args, **kwargs)
        for column in columns:
            self.add_column(column)


class ProjectCard(Card):
    EXTRA_CLASSES = "h-100"

    def __init__(
        self, *args, title, short_description, tags, is_started, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.add_class(self.EXTRA_CLASSES)

        self.is_started = is_started

        self.body.add_title(title)
        self.body.add_text(short_description)
        self.body.add(*[ProjectCardTag(tag) for tag in tags])

        self.add(
            Optional(
                CardBody(
                    Right(
                        ProjectCardButton("Continue ›"),
                    ),
                    class_="d-flex align-items-end",
                ),
                render_condition=lambda _: self.is_started,
            )
        )


class ProjectCardTag(Badge):
    EXTRA_CLASSES = "m-1 p-2"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(self.EXTRA_CLASSES)


class ProjectCardButton(BootstrapElement):
    TAG = "button"
    CLASS = "btn btn-primary btn-md"


class LinkWithoutDecoration(BootstrapElement):
    TAG = "a"
    CLASS = "text-decoration-none text-reset"


class Right(BootstrapElement):
    TAG = "div"
    CLASS = "w-100 d-flex justify-content-end"


class TaskCard(BootstrapElement):
    TAG = "div"
    CLASS = "card"
    EXTRA_CLASSES = "my-3"

    def __init__(
            self,
            *args,
            position, title, text, status, collapsible_id,
            collapsed=True,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(self.EXTRA_CLASSES)

        self.heading = TaskCardHeading(
            f"{position}. {title}",
            get_status_mark(status),
        )
        self.body = TaskCardBody(
            id=collapsible_id, text=text, collapsed=collapsed)

        self << CollapsibleLink(self.heading, href=f"#{collapsible_id}")
        self << self.body

    def add_check_list(self):
        check_list = TaskCheckList()
        self << check_list
        return check_list


class TaskCardHeading(CardBody):
    EXTRA_CLASSES = "d-flex justify-content-between"

    def __init__(self, title, *args, **kwargs):
        super().__init__(TaskCardTitle(title), *args, **kwargs)
        self.add_class(self.EXTRA_CLASSES)


class TaskCardBody(CardBody):
    EXTRA_CLASSES = "collapse py-0"

    def __init__(self, *args, id, collapsed, **kwargs):
        super().__init__(*args, id=id, **kwargs)
        self.add_class(self.EXTRA_CLASSES)
        if not collapsed:
            self.add_class("show")

    def add_check_list(self):
        check_list = TaskCheckList()
        self << check_list
        return check_list


class TaskCardTitle(CardTitle):
    EXTRA_CLASSES = "mb-0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class(self.EXTRA_CLASSES)


class TaskCheckList(BootstrapElement):
    TAG = "ul"

    def add_item(self, title, status=None, message=None):
        item = TaskCheckListItem(title=title, status=status, message=message)
        self << item
        return item


class TaskCheckListItem(BootstrapElement):
    TAG = "li"

    def __init__(
            self,
            *args,
            title, status=None, message=None,
            **kwargs):
        super().__init__(*args, **kwargs)
        self << title
        if status:
            self << " - " + status
        if message:
            self << TaskCheckListMessage(html_escape(message))


class TaskCheckListMessage(BootstrapElement):
    TAG = "pre"


def get_status_mark(status):
    match status:
        case "Completed": return green_tick_mark
        case "Failing": return red_x_mark
        case "In Progress": return yellow_circle_mark
        case "Pending": return ""
        case None: return ""


class CollapsibleLink(LinkWithoutDecoration):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_toggle="collapse", **kwargs)


green_tick_mark = html.span(
        html.HTML("""<svg style="height: 100%; max-height: 24px;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M243.8 339.8C232.9 350.7 215.1 350.7 204.2 339.8L140.2 275.8C129.3 264.9 129.3 247.1 140.2 236.2C151.1 225.3 168.9 225.3 179.8 236.2L224 280.4L332.2 172.2C343.1 161.3 360.9 161.3 371.8 172.2C382.7 183.1 382.7 200.9 371.8 211.8L243.8 339.8zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #28a745;", class_="px-2 mr-2")
red_x_mark = html.span(
        html.HTML("""<svg style="height: 100%; max-height: 24px;" fill="currentColor"xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M175 175C184.4 165.7 199.6 165.7 208.1 175L255.1 222.1L303 175C312.4 165.7 327.6 165.7 336.1 175C346.3 184.4 346.3 199.6 336.1 208.1L289.9 255.1L336.1 303C346.3 312.4 346.3 327.6 336.1 336.1C327.6 346.3 312.4 346.3 303 336.1L255.1 289.9L208.1 336.1C199.6 346.3 184.4 346.3 175 336.1C165.7 327.6 165.7 312.4 175 303L222.1 255.1L175 208.1C165.7 199.6 165.7 184.4 175 175V175zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #dc3545;", class_="px-2 mr-2")
yellow_circle_mark = html.span(
        html.HTML("""<svg style="height: 100%; max-height: 24px;" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z"/></svg>"""),
        style="color: #ffc107;", class_="px-2 mr-2")
