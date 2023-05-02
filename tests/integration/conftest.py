import subprocess
from contextlib import contextmanager
from multiprocessing import Queue, Process

import pytest

from capstone.app import app
from capstone import db


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
