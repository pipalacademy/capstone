"""Module to run integration tests for projects.

Viewing, creating, updating projects should be tested here.
"""
import re
import subprocess
import yaml

from .conftest import create_site, create_project


def test_cli_command_exits_with_zero_code():
    create_site(name="test", domain="test")
    result = subprocess.run([
        "capstone-server", "projects", "new", "-s", "test",
        "-n", "test-project", "-t", "Test Project"
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_cli_command_creates_correct_git_repo(tmp_path):
    create_site(name="test", domain="test")
    result = subprocess.run([
        "capstone-server", "projects", "new", "-s", "test",
        "-n", "test-project", "-t", "Test Project"
    ], capture_output=True, text=True, check=True)

    git_url_match = re.search(r"^git_url: (.*)$", result.stdout, re.MULTILINE)
    assert git_url_match is not None

    git_url = git_url_match.group(1)
    p = subprocess.run(["git", "clone", git_url, "repo"], cwd=tmp_path)
    assert p.returncode == 0

    repo = tmp_path / "repo"
    assert repo.is_dir()
    assert (repo / "capstone.yml").is_file()

    metadata = yaml.safe_load((repo / "capstone.yml").read_text())
    assert metadata["title"] == "Test Project"
    assert "short_description" in metadata
    assert "description" in metadata
    assert "tags" in metadata
    assert "tasks" in metadata

    assert (repo / "checks.py").is_file()
    assert (repo / "requirements.txt").is_file()
    assert (repo / "repo").is_dir()


def test_cli_command_initial_metadata_is_consistent(capstone_app, tmp_path):
    """
    Project metadata (when created initially) must be consistent in the
    git repo's metadata file (capstone.yml) and the database.
    """
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    project.refresh()

    subprocess.check_call(["git", "clone", project.git_url, tmp_path])
    metadata = yaml.safe_load((tmp_path / "capstone.yml").read_text())
    assert metadata["title"] == project.title
    assert metadata["short_description"] == project.short_description
    assert metadata["description"].strip() == project.short_description
    assert metadata["tags"] == project.tags
    assert len(metadata["tasks"]) == len(project.get_tasks())


def test_new_project_is_unpublished_by_default(capstone_app):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    assert project.is_published is False


def test_cli_command_publishes_the_project(capstone_app):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    subprocess.check_call([
        "capstone-server", "projects", "publish", "-s", site.name, project.name,
    ])

    project.refresh()
    assert project.is_published is True


def test_metadata_is_updated_with_capstone_yml(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    subprocess.check_call(["git", "clone", project.git_url, tmp_path])

    metadata_file = tmp_path / "capstone.yml"
    metadata = yaml.safe_load(metadata_file.read_text())
    metadata.update(title="Updated title")
    metadata_file.write_text(yaml.safe_dump(metadata))

    subprocess.check_call(["git", "add", "capstone.yml"], cwd=tmp_path)
    subprocess.check_call(["git", "commit", "-m", "update title"], cwd=tmp_path)
    subprocess.check_call(["git", "push"], cwd=tmp_path)

    project.refresh()

    assert project.title == "Updated title"
