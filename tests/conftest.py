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
