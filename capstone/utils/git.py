import os
import subprocess
import sys
from pathlib import Path


class Repo:
    @classmethod
    def clone_from(cls, url: str, path: os.PathLike, *args, **kwargs):
        clone(url, os.fspath(path), *args, **kwargs)
        return cls(path)

    def __init__(self, path: os.PathLike):
        self.path = Path(path)

    def init(self, *args, **kwargs):
        return init(*args, workdir=self.path, **kwargs)

    def commit(self, *args, **kwargs):
        return commit(*args, workdir=self.path, **kwargs)

    def push(self, *args, **kwargs):
        return push(*args, workdir=self.path, **kwargs)

    def add(self, *args, **kwargs):
        return add(*args, workdir=self.path, **kwargs)

    def config(self, *args, **kwargs):
        return config(*args, workdir=self.path, **kwargs)

    def rev_parse(self, *args, **kwargs):
        return rev_parse(*args, workdir=self.path, **kwargs)


def init(*args, workdir=None, **kwargs):
    cmd = build_cmd("init", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def commit(*args, workdir=None, **kwargs):
    cmd = build_cmd("commit", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def push(*args, workdir=None, **kwargs):
    cmd = build_cmd("push", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def add(*args, workdir=None, **kwargs):
    cmd = build_cmd("add", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def config(*args, workdir=None, **kwargs):
    cmd = build_cmd("config", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def clone(*args, workdir=None, **kwargs):
    cmd = build_cmd("clone", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True, cwd=workdir)
    return True


def rev_parse(*args, workdir=None, **kwargs):
    cmd = build_cmd("rev-parse", options=kwargs, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=sys.stderr, check=True, cwd=workdir)
    return proc.stdout.decode("utf-8").strip()


def build_cmd(
    subcommand: str,
    *,
    options: dict[str, str] | None = None,
    args: list[str] | None = None
) -> list[str]:
    """
    Builds the complete Git command from subcommand, args, and options.

    Also adds a generic username and email to the Git command, so that the
    commits are not associated with the system Git user.

    For example,

    ```
    >>> build_cmd("commit", options={"message": "initial commit"})
    ["git", "-c user.name=...", "-c user.email=...", "commit", "--message", "initial commit"]
    >>> build_cmd("add", args=["capstone.yml"])
    ["git", "-c user.name=...", "-c user.email=...", "add", "'capstone.yml'"]
    >>> build_cmd("commit", options={"m": "empty", "allow_empty": True})
    ["git", "-c user.name=...", "-c user.email=...", "commit", "-m='empty'", "--allow-empty"]

    ```

    It also handles:
    - single-letter options (notice that it only prepended one "-" to the "m"
     option in last example, but two hyphens "--" to "message" in second example).
    - boolean options ("allow_empty" in last example)
    - converting "_" to "-" in option names ("allow_empty"->"--allow-empty" in
     last example).
    """
    options = options or {}
    args = args or []

    # TODO: can this be removed?
    git_options = ["-c", "user.name=Capstone", "-c", "user.email=git@pipal.in"]

    # flatten result of build_options
    cmd_options = [
        s
        for built_option in build_options(options)
        for s in built_option
    ]

    return ["git", *git_options, subcommand, *cmd_options, *args]


def build_options(options: dict) -> list[list[str]]:
    def _build_option(key, value):
        match key.replace("_", "-"), value:
            case _, False: return []  # is this case needed?
            case k, True if len(k) == 1: return [f"-{k}"]
            case k, True: return [f"--{k}"]
            case k, v if len(k) == 1: return [f"-{k}", v]
            case k, v: return [f"--{k}", v]

    return [
        _build_option(k, v) for k, v in options.items()
    ]
