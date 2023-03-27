"""gito - a lightweight service for creating anonymous git repos.


Gito provide an API to create git repos with a secret URL. Anyone
who has access to the URL can read and write to the repo.

Gito also supports commit hooks.
"""

from dataclasses import dataclass
import logging
import os
import subprocess
import uuid
from flask import Flask, abort, request
from pathlib import Path

__version__ = "0.1.0"

logger = logging.getLogger(__name__)

app = Flask(__name__)

ROOT = os.getenv("GITO_ROOT") or "git"

class Gito:
    def __init__(self, root):
        self.root = Path(root)

    def create_repo(self, name):
        id = uuid.uuid4().hex
        path = self.root.joinpath(id).joinpath(name + ".git")
        repo = Repo(root=self.root, id=id, name=name)
        repo.create()
        return repo

    def get_repo(self, id):
        """Returns repo if exists.
        """
        path = self.root / id
        repos = list(path.glob("*.git"))
        if repos:
            name = repos[0].stem
            return Repo(root=self.root, id=id, name=name)

@dataclass
class Repo:
    root: Path
    id: str
    name: str

    def create(self):
        """"Initializes the git repo.
        """
        path = self.get_path()
        logging.info("Creating new repo at %s", path)

        cmd = [
            "git", "init",
            "--bare",
            "--initial-branch", "main",
            str(path)
        ]
        # TODO: check the status and fail gracefully
        subprocess.run(cmd, check=True)

        # setup post-receive hook
        hook_path = Path(__file__).parent.absolute() / "scripts" / "post-receive"
        target = path / "hooks" / "post-receive"
        target.symlink_to(hook_path)

    def get_path(self):
        return self.root / self.id / (self.name + ".git")

    def get_webhook_path(self):
        return self.get_path() / "hooks" / "webhook.txt"

    def get_webhook(self):
        path = self.get_webhook_path()
        if path.exists():
            return path.read_text().strip()

    def set_webhook(self, url):
        logger.info("setting webhook of repo %s to %s", self.id, url)
        path = self.get_webhook_path()
        if url:
            path.write_text(url)
        else:
            path.unlink(missing_ok=True)

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": f"{request.url_root}api/repos/{self.id}",
            "git_url": f"{request.url_root}{self.id}/{self.name}.git"
        }

gito = Gito(ROOT)

@app.route("/")
def index():
    return {
        "app": "gito",
        "version": __version__
    }

@app.route("/api/repos", methods=["POST"])
def repos():
    data = request.get_json()
    name = data['name']
    repo = gito.create_repo(name)
    return repo.dict()

@app.route("/api/repos/<repo_id>")
def get_repo(repo_id):
    repo = gito.get_repo(repo_id)
    if not repo:
        abort(404)
    return repo.dict()

@app.route("/api/repos/<repo_id>/hook")
def get_webhook(repo_id):
    repo = gito.get_repo(repo_id)
    if repo is None:
        abort(404)

    return {
        "url": repo.get_webhook()
    }

@app.route("/api/repos/<repo_id>/hook", methods=["PUT"])
def set_webhook(repo_id):
    repo = gito.get_repo(repo_id)
    if repo is None:
        abort(404)

    data = request.get_json()
    url = data['url']

    repo.set_webhook(url)
    return {
        "url": url
    }

@app.route("/api/repos/<repo_id>/hook", methods=["DELETE"])
def delete_webhook(repo_id):
    repo = gito.get_repo(repo_id)
    if repo is None:
        abort(404)

    repo.set_webhook(None)
    return {
        "url": None
    }

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%d-%m %H:%M:%S')

if __name__ == "__main__":
    setup_logging()
    app.run(debug=True)