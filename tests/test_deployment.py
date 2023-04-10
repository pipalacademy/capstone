from pathlib import Path
import pytest
from .test_db import user_id, project_id, site_id, user_project_id

from capstone import config
from capstone import db
from capstone.deployment import SimpleDeployment
from capstone.utils import git


@pytest.fixture(autouse=True)
def setup_dir(monkeypatch, tmp_path):
    """Fixture to start every test with a clean deployment directory.
    """
    (tmp_path / "deployments").mkdir()
    (tmp_path / "private").mkdir()
    monkeypatch.setattr(config, "data_dir", str(tmp_path))


@pytest.fixture(autouse=True)
def setup_git(monkeypatch, tmp_path):
    (tmp_path / "git").mkdir()
    monkeypatch.setattr(config, "git_base_url", str(tmp_path / "git"))


def setup_sample_git_repo(dir):
    path = Path(dir)
    path.mkdir(parents=True, exist_ok=True)
    git.init(workdir=str(path))
    git.commit(message="Initial commit", allow_empty=True, workdir=str(path))


class TestSimpleDeployment:
    def test_simple_deployment_repo_is_being_copied(self, user_id, project_id, site_id):
        git_path = config.git_base_url + f"/{project_id}/{user_id}"
        setup_sample_git_repo(git_path)
        (Path(git_path) / "index.html").touch()
        git.add("index.html", workdir=git_path)
        git.commit(message="Add index.html", workdir=git_path)

        db_site = db.Site.find(id=site_id)
        user_project = db.UserProject(user_id=user_id, project_id=project_id, git_url=git_path, repo_id="abcd12345").save()

        SimpleDeployment.run(site=db_site, user_project=user_project)

        deployment_dir = Path(config.data_dir) / "deployments" / f"{user_id}.{db_site.domain}"
        assert deployment_dir.is_dir()
        assert (deployment_dir / ".git").is_dir()
        assert (deployment_dir / "index.html").is_file()

    def test_simple_deployment_changelog(self, user_id, project_id, site_id):
        git_path = config.git_base_url + f"/{project_id}/{user_id}"
        setup_sample_git_repo(git_path)

        db_site = db.Site.find(id=site_id)
        user_project = db.UserProject(user_id=user_id, project_id=project_id, git_url=git_path, repo_id="abcd12345").save()

        SimpleDeployment.run(site=db_site, user_project=user_project)

        changelog = db.Changelog.find(action="deploy", site_id=site_id)
        assert changelog is not None
        assert changelog.get_dict() == {
            "id": changelog.id,
            "timestamp": changelog.timestamp,
            "action": "deploy",
            "site_id": site_id,
            "user_id": user_id,
            "project_id": project_id,
            "details": {
                "type": "simple",
                "git_commit_hash": git.rev_parse("HEAD", workdir=git_path),
                "app_url": f"http://{user_id}.{db_site.domain}",
            },
        }
