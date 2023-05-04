import subprocess
from contextlib import contextmanager
from multiprocessing import Queue, Process

import pytest

from capstone import auth
from capstone import db
from capstone.app import app
from capstone.utils.user_project import start_user_project


@contextmanager
def safe_producer_queue(target, *args, **kwargs):
    q = Queue()
    p = Process(target=target, args=(q, *args), kwargs=kwargs)
    p.start()
    try:
        yield q
    finally:
        p.kill()


@pytest.fixture
def capstone_app(port=5000):
    def producer(q):
        app.run(port=port)

    with safe_producer_queue(producer):
        yield app


def create_site(name, domain) -> db.Site:
    return db.Site(name=name, domain=domain, title=name).save()


def create_project(site: db.Site, name, title) -> db.Project:
    subprocess.check_call([
        "capstone-server", "projects", "new", "-s", site.name,
        "-n", name, "-t", title,
    ])
    return site.get_project_or_fail(name=name)


def create_user(site: db.Site, email: str, full_name: str = "Alice") -> db.User:
    username = email.split("@")[0]
    return auth.get_or_create_user(site=site, email=email, full_name=full_name)


def create_user_project(site, user, project):
    start_user_project(user=user, project=project)
    return project.get_user_project_or_fail(user_id=user.id)
