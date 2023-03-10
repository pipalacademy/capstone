import pytest
from datetime import datetime

from capstone import db

def test_query():
    assert db.db.query("SELECT 1 as x").list() == [{"x": 1}]


mock_site = {
    "name": "test-site",
    "title": "Test Site Title",
    "domain": "test-site.example.com"
}

mock_project = {
    "name": "test-project",
    "title": "Test Project",
    "short_description": "test short description",
    "description": "test description",
    "tags": ["test-tag-1", "test-tag-2"]
}


@pytest.fixture(scope="function")
def site_id():
    result = db.db.query("""\
        INSERT INTO site (name, title, domain)
        VALUES ('{name}', '{title}', '{domain}')
        RETURNING id;
    """.format(**mock_site))
    id = result[0]["id"]

    yield id

    db.db.query(f"""\
        DELETE FROM site WHERE id={id};
    """)


@pytest.fixture(scope="function")
def project_id(site_id):
    q = """\
        INSERT INTO
        project (site_id, name, title, short_description, description, tags)
        VALUES (
            %(site_id)d, '%(name)s', '%(title)s', '%(short_description)s',
            '%(description)s', '{"%(tag_0)s","%(tag_1)s"}'
        )
        RETURNING id;
    """ % {
        **mock_project, "tag_0": mock_project["tags"][0],
        "tag_1": mock_project["tags"][1], "site_id": site_id,
    }

    result = db.db.query(q)
    id = result[0]["id"]

    yield id

    db.db.query(f"""\
        DELETE FROM project WHERE id={id};
    """)


def test_db_array_type_is_fetched_correctly(project_id):
    project = db.Project.find(id=project_id)
    assert isinstance(project.tags, list)
    assert project.tags == mock_project["tags"]


def test_db_timestamp_type_is_fetched_correctly(project_id):
    project = db.Project.find(id=project_id)
    assert isinstance(project.created, datetime)


def test_db_default_is_set_correctly(project_id):
    project = db.Project.find(id=project_id)
    assert project.created is not None
    assert project.last_modified is not None
    assert project.is_published is False


def test_find_project_ok(project_id):
    project = db.Project.find(id=project_id)
    assert isinstance(project, db.Project)


def test_find_project_when_project_does_not_exist():
    assert db.Project.find(id=123456) is None


def test_insert_project_ok(site_id):
    project = db.Project(**mock_project, site_id=site_id)
    try:
        project.save()
        assert project.id is not None
        rows = db.db.query(f"SELECT * FROM project WHERE id={project.id}")
        assert len(rows) == 1
    finally:
        if project.id is not None:
            db.db.query(f"DELETE FROM project WHERE id={project.id}")


def test_update_project_ok(project_id):
    project = db.Project.find(id=project_id)
    project.title = "New Title"
    project.save()

    assert db.Project.find(id=project_id).title == "New Title"


def test_delete_project_ok(project_id):
    project = db.Project.find(id=project_id)
    project.delete()

    assert db.Project.find(id=project_id) is None
