import requests

from capstone.utils import git
from .conftest import capstone_app, create_site, create_project, create_user, create_user_project


def test_project_can_be_started_by_learner(capstone_app):
    site = create_site(name="localhost", domain="localhost")
    user = create_user(site, email="learner@example.com")
    project = create_project(site, name="test-project", title="Test Project")
    project.publish()

    with capstone_app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = user.id

        response = client.post(f"/projects/test-project")
        # status code could be 302 (it is at the time of writing this test)
        # but i don't want to enforce that. any OK status code is fine.
        assert response.status_code < 400

    user_project = project.get_user_project(user_id=user.id)
    assert user_project is not None, "user project wasn't created"


def test_project_with_default_starter_code_can_be_cloned_by_learner(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    user = create_user(site, email="learner@example.com")
    project = create_project(site, name="test-project", title="Test Project")
    project.publish()
    user_project = create_user_project(site, user=user, project=project)

    repo = git.Repo.clone_from(user_project.git_url, tmp_path)
    assert repo.rev_parse("HEAD") is not None
    assert (tmp_path / "README.md").exists()
