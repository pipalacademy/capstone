import subprocess
from contextlib import contextmanager
from multiprocessing import Queue, Process

from capstone.utils import gitto


@contextmanager
def safe_producer_queue(target, *args):
    q = Queue()
    p = Process(target=target, args=(q, *args))
    p.start()
    try:
        yield q
    finally:
        p.kill()


def test_safe_producer_queue():
    def producer(q):
        q.put("foo")
        return

    with safe_producer_queue(producer) as q:
        assert q.get(timeout=0.5) == "foo"


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
