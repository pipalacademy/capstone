"""Module to run integration tests for projects.

Viewing, creating, updating projects should be tested here.
"""
import re
import subprocess
import yaml

from .conftest import create_site


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
