import pytest
import json
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
        "tags": ["test-tag-1", "test-tag-2"],
        "project_type": "web",
        "deployment_type": "nomad",
    },
    {
        "name": "test-project-2",
        "title": "Test Project 2",
        "short_description": "test short description 2",
        "description": "test description 2",
        "tags": ["test-2-tag-1", "test-2-tag-2"],
        "project_type": "cli",
        "deployment_type": "custom",
    },
]

mock_tasks = [
    {
        "name": "foo",
        "title": "Foo",
        "description": "foo desc",
        "checks": []
    },
    {
        "name": "bar",
        "title": "Bar",
        "description": "bar desc",
        "checks": []
    }
]

mock_checks = [
    {
        "name": "spam",
        "title": "spam check",
        "args": {
            "a": 1,
            "b": "s",
            "c": [1, 2, 3],
            "d": {"a": 1, "b": 2}
        }
    },
    {
        "name": "ham",
        "title": "ham check",
        "args": {
            "a": 1,
            "b": "s",
            "c": [1, 2, 3],
            "d": {"a": 1, "b": 2}
        }
    },
]

mock_user = {
    "username": "test-user",
    "email": "user@example.test",
    "full_name": "Test User",
    "enc_password": "test-password",
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

    db.db.query("TRUNCATE site CASCADE")


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


@pytest.fixture(scope="function")
def task_id(project_id):
    q = """\
        INSERT INTO
        task (project_id, position, name, title, description)
        VALUES (%(project_id)d, %(position)d, '%(name)s', '%(title)s', '%(description)s')
        RETURNING id;
    """ % {
        **mock_tasks[0], "project_id": project_id, "position": 0,
    }

    result = db.db.query(q)
    id = result[0]["id"]

    yield id


@pytest.fixture(scope="function")
def task_check_id(task_id):
    q = db.db.query("""\
        INSERT INTO
        task_check (task_id, name, title, args, position)
        VALUES (%(task_id)d, '%(name)s', '%(title)s', '%(args)s', %(position)d)
        RETURNING id;
    """ % {
        "task_id": task_id, **mock_checks[0], "args": json.dumps(mock_checks[0]["args"]),
        "position": 0
    })
    id = q[0]["id"]

    yield id


@pytest.fixture(scope="function")
def user_id(site_id):
    q = db.db.query("""\
        INSERT INTO
        user_account (site_id, username, email, full_name, enc_password)
        VALUES (
            %(site_id)d, '%(username)s', '%(email)s', '%(full_name)s',
            '%(enc_password)s'
        )
        RETURNING id;
    """ % {
        "site_id": site_id, **mock_user
    })
    id = q[0]["id"]

    yield id



@pytest.fixture(scope="function")
def user_project_id(user_id, project_id):
    q = db.db.query("""\
        INSERT INTO
        user_project (user_id, project_id, git_url, repo_id)
        VALUES (%(user_id)d, %(project_id)d, '%(git_url)s', '%(repo_id)s')
        RETURNING id;
    """ % {
        "user_id": user_id, "project_id": project_id,
        "repo_id": "abcd123456",
        "git_url": "http://example.com/abcd123456/git"
    })
    id = q[0]["id"]

    yield id


@pytest.fixture(scope="function")
def user_task_status_id(user_project_id, task_id):
    q = db.db.query("""\
        INSERT INTO
        user_task_status (user_project_id, task_id, status)
        VALUES (%(user_project_id)d, %(task_id)d, '%(status)s')
        RETURNING id;
    """ % {
        "user_project_id": user_project_id, "task_id": task_id,
        "status": "Pending"
    })
    id = q[0]["id"]

    yield id


@pytest.fixture(scope="function")
def user_check_status_id(user_task_status_id, task_check_id):
    q = db.db.query("""\
        INSERT INTO
        user_check_status (user_task_status_id, task_check_id, status)
        VALUES (%(user_task_status_id)d, %(task_check_id)d, '%(status)s')
        RETURNING id;
    """ % {
        "user_task_status_id": user_task_status_id, "task_check_id": task_check_id,
        "status": "Pending"
    })
    id = q[0]["id"]

    yield id


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


def test_db_none_value_is_set_correctly(project_id):
    project = db.Project.find(id=project_id)
    assert project.git_url is None


def test_find_project_ok(project_id):
    project = db.Project.find(id=project_id)
    assert isinstance(project, db.Project)


def test_find_project_when_project_does_not_exist():
    assert db.Project.find(id=123456) is None


def test_insert_project_ok(site_id):
    project = db.Project(**mock_projects[0], site_id=site_id)

    project.save()
    assert project.id is not None

    rows = db.db.query(f"SELECT * FROM project WHERE id={project.id}")
    assert len(rows) == 1


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


def test_update_tasks_zeroth_task_is_added(project_id):
    project = db.Project.find(id=project_id)
    project.update_tasks([])

    assert project.get_tasks() == []


def test_task_render_description_without_formatting(project_id):
    git_url = "http://example.com/test-dir/test-repo.git"
    project = db.Project.find(id=project_id)
    project.update_tasks(mock_tasks)
    task = project.get_tasks()[0]
    assert task.render_description({"git_url": git_url}) == mock_tasks[0]["description"]
    assert task.render_description({}) == mock_tasks[0]["description"]


def test_task_render_description_with_formatting(project_id):
    git_url = "http://example.com/test-dir/test-repo.git"
    project = db.Project.find(id=project_id)
    project.update_tasks([dict(mock_tasks[0], description="`{git_url}`")])
    assert project.get_tasks()[0].render_description({"git_url": git_url}) == f"`{git_url}`"


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


def test_get_checks_when_task_has_checks(task_id):
    task = db.Task.find(id=task_id)
    db.db.query(f"""\
        INSERT INTO
            task_check (name, title, args, position, task_id)
        VALUES
            ('{mock_checks[0]['name']}', '{mock_checks[0]['title']}',
             '{json.dumps(mock_checks[0]['args'])}', 0, {task_id}),
            ('{mock_checks[1]['name']}', '{mock_checks[1]['title']}',
             '{json.dumps(mock_checks[1]['args'])}', 1, {task_id});
    """)

    checks = task.get_checks()
    assert len(checks) == 2
    assert checks[0].name == mock_checks[0]["name"]
    assert checks[0].position == 0
    assert checks[0].args == mock_checks[0]["args"]
    assert checks[1].name == mock_checks[1]["name"]
    assert checks[1].position == 1
    assert checks[1].args == mock_checks[1]["args"]


def test_delete_task_when_task_has_checks(task_id):
    task = db.Task.find(id=task_id)
    db.db.query(f"""\
        INSERT INTO
            task_check (name, title, args, position, task_id)
        VALUES
            ('{mock_checks[0]['name']}', '{mock_checks[0]['title']}',
             '{json.dumps(mock_checks[0]['args'])}', 0, {task_id}),
            ('{mock_checks[1]['name']}', '{mock_checks[1]['title']}',
             '{json.dumps(mock_checks[1]['args'])}', 1, {task_id});
    """)

    task.delete()
    assert db.Task.find(id=task_id) is None
    assert db.TaskCheck.find_all(task_id=task_id) == []


def test_update_checks_ok(task_id):
    task = db.Task.find(id=task_id)
    task.update_checks(mock_checks)

    checks = task.get_checks()
    assert len(checks) == 2
    assert checks[0].name == mock_checks[0]["name"]
    assert checks[0].position == 0
    assert checks[0].args == mock_checks[0]["args"]
    assert checks[1].name == mock_checks[1]["name"]
    assert checks[1].position == 1
    assert checks[1].args == mock_checks[1]["args"]


def test_update_checks_when_check_inputs_is_empty(
        task_id):
    task = db.Task.find(id=task_id)
    task.update_checks(mock_checks)
    task.update_checks([])

    assert len(task.get_checks()) == 0


class TestUserProject:
    def test_update_task_status(self, user_project_id, task_id):
        user_project = db.UserProject.find(id=user_project_id)
        task = db.Task.find(id=task_id)
        user_project.update_task_status(task, "Completed")
        assert user_project.get_task_status(task).status == "Completed"

    def test_update_task_status_when_task_status_already_exists(self, user_project_id, task_id):
        user_project = db.UserProject.find(id=user_project_id)
        task = db.Task.find(id=task_id)
        user_project.update_task_status(task, "Completed")
        assert user_project.get_task_status(task).status == "Completed"

        user_project.update_task_status(task, "In Progress")
        assert user_project.get_task_status(task).status == "In Progress"


class TestUserTaskStatus:
    def test_update_check_status(self, user_task_status_id, task_check_id):
        user_task_status = db.UserTaskStatus.find(id=user_task_status_id)
        task_check = db.TaskCheck.find(id=task_check_id)
        user_task_status.update_check_status(task_check, "pass")
        assert user_task_status.get_check_status(task_check).status == "pass"

        user_task_status.update_check_status(task_check, "fail")
        assert user_task_status.get_check_status(task_check).status == "fail"
