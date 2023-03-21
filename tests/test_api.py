import pytest

from capstone.app import app as _app
from capstone import db

@pytest.fixture(autouse=True)
def setup_db():
    """Fixture to start every test with a clean database.
    """
    db.db.query("TRUNCATE site CASCADE")

@pytest.fixture()
def api_client():
    return APIClient()

class APIClient:
    """Interface to acess the API."""
    def create_site(self, name, domain):
        site = db.Site(name=name, domain=domain, title=name).save()
        return APISite(domain)

class APISite:
    """"Site interface via the API.
    """
    def __init__(self, domain):
        self.domain = domain
        self.base_url = f"http://{domain}/"
        self.client = _app.test_client()
        self.headers = {"Authorization": "Bearer test123"}

    def request(self, path, method, check_status=True, **kwargs):
        kwargs.setdefault("headers", self.headers)
        response = self.client.open(path,
                            method=method,
                            base_url=self.base_url,
                            **kwargs)
        if check_status and response.status_code != 200:
            print(f"request failed with status code: {response.status_code}")
            print(response.text)
            assert response.status_code == 200, response.text

        return response

    def get(self, path, **kwargs):
        return self.request(path, method="GET", **kwargs)

    def post(self, path, **kwargs):
        return self.request(path, method="POST", **kwargs)

    def put(self, path, **kwargs):
        return self.request(path, method="PUT", **kwargs)

    def delete(self, path, **kwargs):
        return self.request(path, method="DELETE", **kwargs)

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
        "tags": ["test-tag-1", "test-tag-2"],
    },
    {
        "name": "test-project-2",
        "title": "Test Project Beta",
        "short_description": "test short description beta",
        "description": "test description beta",
        "tags": ["test-tag-1-beta", "test-tag-2-beta"],
    }
]

fake_checks = [
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

fake_tasks = [
    {
        "name": "foo",
        "title": "foo short desc",
        "description": "foo desc",
        "checks": fake_checks,
    },
    {
        "name": "bar",
        "title": "bar short desc",
        "description": "bar desc",
        "checks": []
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
    project.update_tasks(fake_tasks)
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
    response = client.put(
        endpoint, json={**fake_projects[0], "tasks": fake_tasks})
    assert response.status_code == 401


def test_update_project_when_user_not_authorized(client, fake_project):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint, json={**fake_projects[0], "tasks": fake_tasks})
    assert response.status_code == 401


def test_create_project(client, fake_site):
    project = db.Project.find(
        site_id=fake_site.id, name=fake_projects[0]["name"])
    assert project is None

    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
            endpoint, headers=get_test_headers(),
            json={**fake_projects[0], "tasks": fake_tasks})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_projects[0]["name"]

    project = db.Project.find(
        site_id=fake_site.id, name=fake_projects[0]["name"])
    assert isinstance(project, db.Project)
    assert project.name == fake_projects[0]["name"]
    assert project.site_id == fake_site.id

    project.delete()


def test_create_project_when_incomplete_data_is_given(
        client, fake_site):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
            endpoint, headers=get_test_headers(), json={"title": "test test"})
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
        json={**fake_projects[1], "tasks": []})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["name"] == fake_projects[1]["name"]
    assert len(response.json["tasks"]) == 1

    project_2 = db.Project.find(
        site_id=fake_site_2.id, name=fake_projects[1]["name"])
    assert isinstance(project_2, db.Project)
    assert project_2.name == fake_projects[1]["name"]
    assert project_2.site_id == fake_site_2.id
    assert project_2.get_tasks() != []

    project_2.delete()


def test_update_project(client, fake_project):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint,
        headers=get_test_headers(),
        json={**fake_projects[0], "title": "new test title",
              "tasks": fake_tasks})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["title"] == "new test title"
    assert len(response.json["tasks"]) == 3
    assert len(response.json["tasks"][1]["checks"]) == 2
    assert len(response.json["tasks"][2]["checks"]) == 0

    fake_project.refresh()
    assert fake_project.title == "new test title"

SAMPLE_PROJECT = {
    "title": "...",
    "short_description": "...",
    "description": "...",
    "tags": [],
    "tasks": []
}

def assert_dict(value, expected):
    """Checks only the keys present in expected, ignore additional keys in the value.
    """
    value = {k:v for k, v in value.items() if k in expected}
    assert value == expected

class TestProject:
    def test_create(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        p = site.put("/api/projects/fizzbuzz", json=data).json

        assert p['name'] == 'fizzbuzz'
        assert p['title'] == 'Fizz Buzz'

        p2 = site.get("/api/projects/fizzbuzz").json

        data.pop("tasks") # ignore tasks for now
        assert_dict(p2, data)

    def test_update_title(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site.put("/api/projects/fizzbuzz", json=data)

        data['title'] = "Fizz Buzz 2.0"
        response_data = site.put("/api/projects/fizzbuzz", json=data).json
        assert response_data['title'] == 'Fizz Buzz 2.0'


def test_update_project_when_project_is_on_different_site(
        client, fake_project, fake_site_2):
    endpoint = f"/api/projects/{fake_projects[0]['name']}"
    response = client.put(
        endpoint,
        base_url=get_base_url(fake_site_2.domain, endpoint),
        headers=get_test_headers(),
        json={**fake_projects[0], "title": "new test title",
              "tasks": fake_tasks})
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
