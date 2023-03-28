import subprocess
import sys

def init(*args, workdir=None, **kwargs):
    cmd = build_cmd("init", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def commit(*args, workdir=None, **kwargs):
    cmd = build_cmd("commit", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def push(*args, workdir=None, **kwargs):
    cmd = build_cmd("push", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def add(*args, workdir=None, **kwargs):
    cmd = build_cmd("add", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def config(*args, workdir=None, **kwargs):
    cmd = build_cmd("config", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def clone(*args, workdir=None, **kwargs):
    cmd = build_cmd("clone", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    return True


def rev_parse(*args, workdir=None, **kwargs):
    cmd = build_cmd("rev-parse", options=kwargs, workdir=workdir, args=args)

    # TODO: handle gracefully when proc fails
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=sys.stderr, check=True)
    return proc.stdout.decode("utf-8").strip()


def build_cmd(subcommand, args, options, workdir=None):
    pre_command = f"cd '{workdir}'; " if workdir else ""

    git_options = [f"-c user.name=Capstone", f"-c user.email=git@pipal.in"]

    command = " ".join([
        "git", *git_options, subcommand, *_build_options(**options), *args,
    ])
    return ["bash", "-c", pre_command+command]


def _build_options(**options):
    def build_option(key, value):
        match key.replace("_", "-"), value:
            case _, False: return ""
            case k, True if len(k) == 1: return f"-{k}"
            case k, True: return f"--{k}"
            case k, v if len(k) == 1: return f"-{k} '{v}'"
            case k, v: return f"--{k}='{v}'"

    return [
        build_option(k, v) for k, v in options.items()
    ]
