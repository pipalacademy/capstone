from .conftest import APISite


def get_base_url(host, endpoint):
    return f"http://{host}{endpoint}"

def assert_dict(value, expected):
    """Checks only the keys present in expected, ignore additional keys in the value.
    """
    value = {k:v for k, v in value.items() if k in expected}
    assert value == expected

SAMPLE_PROJECT = {
    "title": "...",
    "short_description": "...",
    "description": "...",
    "tags": [],
    "tasks": []
}

SAMPLE_TASK = {
    "name": "...",
    "title": "...",
    "description": "...",
    "checks": []
}

class TestSite:
    def test_site_does_not_exist(self):
        endpoint = "/api/projects"
        response = APISite(domain="should-not-exist").get(endpoint, check_status=False)
        assert response.status_code == 404


class TestProject:
    def test_list(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        name, title = "fizzbuzz", "Fizz Buzz"
        data = dict(SAMPLE_PROJECT, title=title)
        site.put(f"/api/projects/{name}", json=data)

        ps = site.get("/api/projects").json

        assert isinstance(ps, list)
        assert len(ps) == 1
        assert ps[0]["name"] == name

    def test_list_when_two_sites_have_projects(self, api_client):
        site1 = api_client.create_site(name="alpha", domain="alpha")
        site2 = api_client.create_site(name="beta", domain="beta")

        name1, name2 = "lorem", "ipsum"
        project1 = dict(SAMPLE_PROJECT, title="Lorem")
        project2 = dict(SAMPLE_PROJECT, title="Ipsum")

        site1.put(f"/api/projects/{name1}", json=project1)
        site2.put(f"/api/projects/{name2}", json=project2)

        # project1 on site1
        ps1 = site1.get("/api/projects").json
        assert isinstance(ps1, list)
        assert len(ps1) == 1
        assert ps1[0]["name"] == name1

        # project2 on site2
        ps2 = site2.get("/api/projects").json
        assert isinstance(ps2, list)
        assert len(ps2) == 1
        assert ps2[0]["name"] == name2

    def test_list_with_no_projects(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")
        assert site.get("/api/projects").json == []

    def test_get(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site.put("/api/projects/fizzbuzz", json=data)

        p = site.get("/api/projects/fizzbuzz").json
        data.pop("tasks")
        assert_dict(p, data)

    def test_get_when_project_is_on_different_site(self, api_client):
        site1 = api_client.create_site(name="alpha", domain="alpha")
        site2 = api_client.create_site(name="beta", domain="beta")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site1.put("/api/projects/fizzbuzz", json=data)

        response = site2.get("/api/projects/fizzbuzz", check_status=False)
        assert response.status_code == 404

    def test_create(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        p = site.put("/api/projects/fizzbuzz", json=data).json

        assert p['name'] == 'fizzbuzz'
        assert p['title'] == 'Fizz Buzz'

        p2 = site.get("/api/projects/fizzbuzz").json

        data.pop("tasks") # ignore tasks for now
        assert_dict(p2, data)

    def test_create_with_task(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        task = dict(SAMPLE_TASK, name="test-task-1", title="Test Task 1")
        data = dict(SAMPLE_PROJECT, title="Fizz Buzz", tasks=[task])
        site.put("/api/projects/fizzbuzz", json=data)

        p = site.get("/api/projects/fizzbuzz").json
        assert p["tasks"] == [task]

    def test_create_when_user_is_unauthorized(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        p = site.put("/api/projects/fizzbuzz", json=data, headers={}, check_status=False)

        assert p.status_code == 401

    def test_create_with_incomplete_data(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        response = site.put("/api/projects/fizzbuzz", json={"title": "test test"}, check_status=False)
        assert response.status_code == 422

    def test_create_same_project_on_two_sites(self, api_client):
        site1 = api_client.create_site(name="alpha", domain="alpha")
        site2 = api_client.create_site(name="beta", domain="beta")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site1.put("/api/projects/fizzbuzz", json=data)
        site2.put("/api/projects/fizzbuzz", json=data)

        p1 = site1.get("/api/projects/fizzbuzz").json
        p2 = site2.get("/api/projects/fizzbuzz").json

        data.pop("tasks")
        assert_dict(p1, data)
        assert_dict(p2, data)

    def test_update_title(self, api_client):
        site = api_client.create_site(name="alpha", domain="alpha")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site.put("/api/projects/fizzbuzz", json=data)

        data['title'] = "Fizz Buzz 2.0"
        response_data = site.put("/api/projects/fizzbuzz", json=data).json
        assert response_data['title'] == 'Fizz Buzz 2.0'

    def test_update_title_when_projects_have_same_name_on_two_sites(self, api_client):
        site1 = api_client.create_site(name="alpha", domain="alpha")
        site2 = api_client.create_site(name="beta", domain="beta")

        data = dict(SAMPLE_PROJECT, title="Fizz Buzz")
        site1.put("/api/projects/fizzbuzz", json=data)
        site2.put("/api/projects/fizzbuzz", json=data)

        site1.put("/api/projects/fizzbuzz", json=dict(data, title="Fizz Buzz 2"))

        assert site1.get("/api/projects/fizzbuzz").json["title"] == "Fizz Buzz 2"
        assert site2.get("/api/projects/fizzbuzz").json["title"] == "Fizz Buzz"
