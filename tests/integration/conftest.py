import pytest
from rq import SimpleWorker

from capstone import db
from capstone import tasks


def create_site(name, domain):
    return db.Site(name=name, domain=domain, title=name).save()


@pytest.fixture
def clear_queue(autouse=True):
    tasks.queue.empty()


@pytest.fixture
def worker():
    yield SimpleWorker([tasks.queue], connection=tasks.queue.connection)
