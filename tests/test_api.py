import pytest

from capstone.app import app as _app
from capstone import db


fake_sites = [
    {
        "name": "test-site",
        "title": "Test Site Title",
        "domain": "localhost"
    },
    {
        "name": "beta-test-site",
        "title": "Beta Test Site Title",
        "domain": "beta.localhost"
    }
]

fake_projects = [
    {
        "name": "test-project",
        "title": "Test Project",
        "short_description": "test short description",
        "description": "test description",
        "tags": ["test-tag-1", "test-tag-2"]
    },
    {
        "name": "test-project-2",
        "title": "Test Project Beta",
        "short_description": "test short description beta",
        "description": "test description beta",
        "tags": ["test-tag-1-beta", "test-tag-2-beta"]
    }
]


@pytest.fixture()
def app():
    yield _app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def fake_site():
    site = db.Site(**fake_sites[0]).save()
    yield site
    site.delete()


@pytest.fixture(scope="function")
def fake_site_2():
    site = db.Site(**fake_sites[1]).save()
    yield site
    site.delete()


@pytest.fixture(scope="function")
def fake_project(fake_site):
    project = db.Project(**fake_projects[0], site_id=fake_site.id).save()
    yield project
    project.delete()


@pytest.fixture(scope="function")
def fake_project_2(fake_site_2):
    project = db.Project(**fake_projects[1], site_id=fake_site_2.id).save()
    yield project
    project.delete()


def get_base_url(host, endpoint):
    return f"http://{host}{endpoint}"


def get_test_headers(**extras):
    return {"Authorization": "Bearer test123"}


def test_get_all_projects_when_site_does_not_exist(client):
    endpoint = "/api/projects"
    response = client.get(endpoint)
    assert response.status_code == 404


def test_get_all_projects_when_there_is_only_one_project(client, fake_project):
    endpoint = "/api/projects"
    response = client.get(endpoint)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]["name"] == fake_project.name


def test_get_all_projects_when_there_are_projects_on_two_sites(
        client, fake_site, fake_project, fake_site_2, fake_project_2):
    endpoint = "/api/projects"

    # project 1 on site 1
    response = client.get(
        endpoint, base_url=get_base_url(fake_site.domain, endpoint))
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]["name"] == fake_project.name

    # project 2 on site 2
    response = client.get(
        endpoint, base_url=get_base_url(fake_site_2.domain, endpoint))
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]["name"] == fake_project_2.name


def test_get_all_projects_when_site_has_no_projects(
        client, fake_site, fake_project_2):
    endpoint = "/api/projects"
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json == []


def test_get_project(client, fake_project):
    endpoint = f"/api/projects/{fake_project.name}"
    response = client.get(endpoint)
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_project.name


def test_get_project_on_second_site(
        client, fake_project, fake_site_2, fake_project_2):
    endpoint = f"/api/projects/{fake_project_2.name}"
    response = client.get(
        endpoint, base_url=get_base_url(fake_site_2.domain, endpoint))
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_project_2.name


def test_get_project_when_project_is_on_different_site(
        client, fake_site_2, fake_project):
    endpoint = f"/api/project/{fake_project.name}"
    response = client.get(
        endpoint, base_url=get_base_url(fake_site_2.domain, endpoint))
    assert response.status_code == 404


def test_create_project_when_user_not_authorized(client, fake_site):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(endpoint, json=fake_projects[0])
    assert response.status_code == 401


def test_update_project_when_user_not_authorized(client, fake_project):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(endpoint, json=fake_projects[0])
    assert response.status_code == 401


def test_create_project(client, fake_site):
    project = db.Project.find(
        site_id=fake_site.id, name=fake_projects[0]["name"])
    assert project is None

    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
            endpoint, headers=get_test_headers(), json=fake_projects[0])
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_projects[0]["name"]

    project = db.Project.find(
        site_id=fake_site.id, name=fake_projects[0]["name"])
    assert isinstance(project, db.Project)
    assert project.name == fake_projects[0]["name"]
    assert project.site_id == fake_site.id

    project.delete()


def test_create_project_when_insufficient_data_is_given(
        client, fake_site):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
            endpoint, headers=get_test_headers(), json={'title': 'test test'})
    assert response.status_code == 422


def test_create_project_on_second_site(
        client, fake_project, fake_site_2):
    project_2 = db.Project.find(
        site_id=fake_site_2.id, name=fake_projects[1]["name"])
    assert project_2 is None

    endpoint = f"/api/projects/{fake_projects[1]['name']}"
    response = client.put(
        endpoint,
        headers=get_test_headers(),
        base_url=get_base_url(fake_site_2.domain, endpoint),
        json=fake_projects[1])
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_projects[1]["name"]

    project_2 = db.Project.find(
        site_id=fake_site_2.id, name=fake_projects[1]["name"])
    assert isinstance(project_2, db.Project)
    assert project_2.name == fake_projects[1]["name"]
    assert project_2.site_id == fake_site_2.id

    project_2.delete()


def test_update_project(client, fake_project):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint,
        headers=get_test_headers(),
        json={**fake_projects[0], "title": "new test title"})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["title"] == "new test title"

    fake_project.refresh()
    assert fake_project.title == "new test title"


def test_update_project_when_project_is_on_different_site(
        client, fake_project, fake_site_2):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint,
        base_url=get_base_url(fake_site_2.domain, endpoint),
        headers=get_test_headers(),
        json={**fake_projects[0], "title": "new test title"})
    assert response.status_code == 422

    fake_project.refresh()
    assert fake_project.title == fake_projects[0]["title"]


def test_update_project_when_incomplete_data_is_given(
        client, fake_project):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint,
        headers=get_test_headers(),
        json={"title": "new test title"})
    assert response.status_code == 422

    fake_project.refresh()
    assert fake_project.title == fake_projects[0]["title"]
