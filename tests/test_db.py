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

mock_projects = [
    {
        "name": "test-project",
        "title": "Test Project",
        "short_description": "test short description",
        "description": "test description",
        "tags": ["test-tag-1", "test-tag-2"]
    },
    {
        "name": "test-project-2",
        "title": "Test Project 2",
        "short_description": "test short description 2",
        "description": "test description 2",
        "tags": ["test-2-tag-1", "test-2-tag-2"]
    },
]

mock_tasks = [
    {
        "name": "foo",
        "title": "Foo",
        "description": "foo desc"
    },
    {
        "name": "bar",
        "title": "Bar",
        "description": "bar desc"
    }
]


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
        **mock_projects[0], "tag_0": mock_projects[0]["tags"][0],
        "tag_1": mock_projects[0]["tags"][1], "site_id": site_id,
    }

    result = db.db.query(q)
    id = result[0]["id"]

    yield id

    db.db.query(f"DELETE FROM task WHERE project_id={id};")
    db.db.query(f"DELETE FROM project WHERE id={id};")


@pytest.fixture(scope="function")
def project_id_2(site_id):
    q = """\
        INSERT INTO
        project (site_id, name, title, short_description, description, tags)
        VALUES (
            %(site_id)d, '%(name)s', '%(title)s', '%(short_description)s',
            '%(description)s', '{"%(tag_0)s","%(tag_1)s"}'
        )
        RETURNING id;
    """ % {
        **mock_projects[1], "tag_0": mock_projects[1]["tags"][0],
        "tag_1": mock_projects[1]["tags"][1], "site_id": site_id,
    }

    result = db.db.query(q)
    id = result[0]["id"]

    yield id

    db.db.query(f"DELETE FROM task WHERE project_id={id};")
    db.db.query(f"DELETE FROM project WHERE id={id};")


def test_db_array_type_is_fetched_correctly(project_id):
    project = db.Project.find(id=project_id)
    assert isinstance(project.tags, list)
    assert project.tags == mock_projects[0]["tags"]


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
    project = db.Project(**mock_projects[0], site_id=site_id)
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


def test_delete_project_when_project_has_tasks(project_id):
    project = db.Project.find(id=project_id)
    db.db.query(f"""\
        INSERT INTO
            task (name, title, description, position, project_id)
        VALUES
            ('{mock_tasks[0]['name']}', '{mock_tasks[0]['title']}',
             '{mock_tasks[0]['description']}', 0, {project_id}),
            ('{mock_tasks[1]['name']}', '{mock_tasks[1]['title']}',
             '{mock_tasks[1]['description']}', 1, {project_id});
    """)

    project.delete()
    assert db.Project.find(id=project_id) is None
    assert db.Task.find_all(project_id=project_id) == []


def test_get_tasks_when_project_has_tasks(project_id):
    project = db.Project.find(id=project_id)
    db.db.query(f"""\
        INSERT INTO
            task (name, title, description, position, project_id)
        VALUES
            ('{mock_tasks[0]['name']}', '{mock_tasks[0]['title']}',
             '{mock_tasks[0]['description']}', 0, {project_id}),
            ('{mock_tasks[1]['name']}', '{mock_tasks[1]['title']}',
             '{mock_tasks[1]['description']}', 1, {project_id});
    """)

    tasks = project.get_tasks()
    assert len(tasks) == 2
    assert tasks[0].name == mock_tasks[0]["name"]
    assert tasks[0].position == 0
    assert tasks[1].name == mock_tasks[1]["name"]
    assert tasks[1].position == 1


def test_update_tasks_ok(project_id):
    project = db.Project.find(id=project_id)
    project.update_tasks(mock_tasks)

    tasks = project.get_tasks()
    assert len(tasks) == 2
    assert tasks[0].name == mock_tasks[0]["name"]
    assert tasks[0].position == 0
    assert tasks[1].name == mock_tasks[1]["name"]
    assert tasks[1].position == 1


def test_update_tasks_when_two_tasks_have_same_name(project_id, project_id_2):
    project_1 = db.Project.find(id=project_id)
    project_2 = db.Project.find(id=project_id_2)

    project_1.update_tasks(mock_tasks)
    project_2.update_tasks(mock_tasks)

    p1_tasks = project_1.get_tasks()
    p2_tasks = project_2.get_tasks()

    assert len(p1_tasks) == 2
    assert len(p2_tasks) == 2
    assert p1_tasks[0].id != p2_tasks[0].id
    assert p1_tasks[0].name == mock_tasks[0]["name"]
    assert p2_tasks[0].name == mock_tasks[0]["name"]
    assert p1_tasks[1].id != p2_tasks[1].id
    assert p1_tasks[1].name == mock_tasks[1]["name"]
    assert p2_tasks[1].name == mock_tasks[1]["name"]


def test_update_tasks_when_task_inputs_is_empty(
        project_id):
    project = db.Project.find(id=project_id)
    project.update_tasks(mock_tasks)
    project.update_tasks([])

    assert len(project.get_tasks()) == 0
