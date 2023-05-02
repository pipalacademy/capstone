import subprocess

from capstone.utils import gitto
from .conftest import safe_producer_queue


def test_gitto_set_webhook(tmp_path):
    port = 15000

    with safe_producer_queue(listen_on_webhook, port) as q:
        repo_id = gitto.create_repo(name="test-gitto-webhook")
        webhook_url = f"http://localhost:{port}/webhook"
        gitto.set_webhook(id=repo_id, webhook_url=webhook_url)

        repo_info = gitto.get_repo(repo_id)
        git_url = repo_info["git_url"]

        subprocess.check_call(["git", "clone", git_url, tmp_path])
        subprocess.check_call(["git", "commit", "-m", "test", "--allow-empty"], cwd=tmp_path)
        subprocess.check_call(["git", "push"], cwd=tmp_path)

        value = q.get(timeout=0.5)
        assert value is not None, "did not get a webhook callback"


def listen_on_webhook(q, port):
    from flask import Flask, request

    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        q.put(request.json)
        return ""

    app.run(port=port)
