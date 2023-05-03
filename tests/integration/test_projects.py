"""Module to run integration tests for projects.

Viewing, creating, updating projects should be tested here.
"""
import re
import subprocess
import yaml

from capstone.utils import git
from .conftest import create_site, create_project


example_check = {
    "name": "check_http_request",
    "title": "index page should return 200 OK",
    "args": {
        "endpoint": "/"
    }
}


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

    repo = git.Repo.clone_from(project.git_url, tmp_path)
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


def test_project_metadata_can_be_updated_by_author(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    repo = git.Repo.clone_from(project.git_url, tmp_path)

    metadata_file = tmp_path / "capstone.yml"
    metadata = yaml.safe_load(metadata_file.read_text())
    metadata.update(title="Updated title")
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="update title")
    repo.push()

    project.refresh()

    assert project.title == "Updated title"


def test_project_task_can_be_added_by_author(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    repo = git.Repo.clone_from(project.git_url, tmp_path)
    metadata_file = tmp_path / "capstone.yml"
    example_task = dict(name="foo", title="Foo!", description="foo, not bar\n", checks=[])

    metadata = yaml.safe_load(metadata_file.read_text())
    metadata["tasks"].append(example_task)
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="add task")
    repo.push()

    project.refresh()

    tasks = project.get_tasks()
    assert len(tasks) == len(metadata["tasks"])
    assert tasks[-1].name == example_task["name"]
    assert tasks[-1].title == example_task["title"]
    assert tasks[-1].get_checks() == []


def test_project_task_can_be_updated_by_author(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    repo = git.Repo.clone_from(project.git_url, tmp_path)
    metadata_file = tmp_path / "capstone.yml"
    example_task = dict(name="foo", title="Foo!", description="foo, not bar\n", checks=[])

    metadata = yaml.safe_load(metadata_file.read_text())
    metadata["tasks"].append(example_task)
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="add task")
    repo.push()

    # update title
    metadata["tasks"][-1].update(title="New Foo!")
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="update task")
    repo.push()

    project.refresh()
    tasks = project.get_tasks()
    assert len(tasks) == len(metadata["tasks"])
    assert tasks[-1].name == example_task["name"]
    assert tasks[-1].title == "New Foo!"


def test_project_task_can_be_deleted_by_author(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    repo = git.Repo.clone_from(project.git_url, tmp_path)
    metadata_file = tmp_path / "capstone.yml"
    example_task = dict(name="foo", title="Foo!", description="foo, not bar\n", checks=[dict(example_check)])

    metadata = yaml.safe_load(metadata_file.read_text())
    metadata["tasks"].append(example_task)
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="add task")
    repo.push()

    project.refresh()
    assert len(project.get_tasks()) == len(metadata["tasks"])

    # delete task(s) -- including maybe any default tasks
    metadata["tasks"] = []
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="delete task")
    repo.push()

    project.refresh()
    assert len(project.get_tasks()) == 0


def test_project_tasks_can_be_reordered_by_author(capstone_app, tmp_path):
    site = create_site(name="localhost", domain="localhost")
    project = create_project(site, name="test-project", title="Test Project")

    repo = git.Repo.clone_from(project.git_url, tmp_path)
    metadata_file = tmp_path / "capstone.yml"
    foo_task = dict(name="foo", title="Foo!", description="foo, not bar\n", checks=[dict(example_check)])
    bar_task = dict(name="bar", title="Bar!", description="bar, not foo\n", checks=[dict(example_check)])

    metadata = yaml.safe_load(metadata_file.read_text())
    default_tasks = list(metadata["tasks"])
    metadata["tasks"] = default_tasks + [foo_task, bar_task]
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="add tasks")
    repo.push()

    # switch order, foo_task, bar_task -> bar_task, foo_task
    metadata["tasks"] = default_tasks + [bar_task, foo_task]
    metadata_file.write_text(yaml.safe_dump(metadata))

    repo.add(metadata_file.name)
    repo.commit(message="reorder tasks")
    repo.push()

    project.refresh()
    tasks = project.get_tasks()
    expected_bar_task, expected_foo_task = tasks[-2:]

    assert expected_bar_task.name == "bar"
    assert expected_bar_task.title == "Bar!"
    assert len(expected_bar_task.get_checks()) == 1

    assert expected_foo_task.name == "foo"
    assert expected_foo_task.title == "Foo!"
    assert len(expected_foo_task.get_checks()) == 1
