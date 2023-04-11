import os
import platform
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from capstone.app import app as _app
from capstone import db


@pytest.fixture(autouse=True)
def setup_db():
    """Fixture to start every test with a clean database.
    """
    db.db.query("TRUNCATE site CASCADE")

@contextmanager
def safe_popen(*args, **kwargs):
    """Context manager that works exactly like subprocess.Popen, except that
    the process is killed at the end of the with statement.
        with safe_popen("python webapp.py 8080"):
            time.sleep(0.5) # wait for the app to start
            assert urlopen("http://localhost:8080/").code == 200
        # The webserver will be automatically killed here
    """
    p = subprocess.Popen(*args, **kwargs)
    try:
        yield p
    finally:
        p.kill()

def get_arch():
    return platform.machine()

@pytest.fixture()
def gitto(tmp_path):
    """Fixture to start a gitto server for testing."""
    gitto_executable_path = Path(__file__).parent.parent / "gitto" / f"gitto-{get_arch()}"
    with safe_popen(
        [gitto_executable_path],
        env={
            "GITTO_ROOT": str(tmp_path),
            "GITTO_PORT": "8080",
            "GITTO_API_TOKEN": "gitto",
            "PATH": os.getenv("PATH"),
        }
    ):
        time.sleep(0.5)  # wait for the app to start
        yield

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
