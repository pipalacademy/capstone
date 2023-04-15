"""Deployment interface for capstone.
"""

import contextlib
import importlib
import sys
from pathlib import Path
from jinja2 import Template
import nomad
import subprocess
import logging
import uuid
import tempfile
import os

from capstone import config
from capstone.db import db, Site, UserProject
from capstone.utils import git


def write_deploy_changelog(site_id, user_id, project_id, type, git_commit_hash, app_url=None):
    return db.insert(
        "changelog",
        action="deploy",
        site_id=site_id,
        user_id=user_id,
        project_id=project_id,
        details={
            "type": type,
            "git_commit_hash": git_commit_hash,
            "app_url": app_url,
        }
    )


def get_deployments(site, user_id=None, project_id=None):
    filters = {"site_id": site.id}
    if user_id:
        filters["user_id"] = user_id
    if project_id:
        filters["project_id"] = project_id
    deployments = db.where("changelog", action="deploy", **filters)
    return [
        {
            "timestamp": deployment["timestamp"],
            "type": deployment["details"]["type"],
            "project": site.get_projects(id=deployment["project_id"])[0].name,
            "user": site.get_users(id=deployment["user_id"])[0].username,
            "git_hash": deployment["details"]["git_commit_hash"],
            "app_url": deployment["details"]["app_url"],
        }
        for deployment in deployments
    ]


def new_deployment(user_project, type="simple"):
    site = user_project.get_site()
    if type == "simple":
        return SimpleDeployment.run(site=site, user_project=user_project)
    else:
        raise ValueError(f"Unknown deployment type: {type}")


class Deployment:
    @classmethod
    def run(cls, site, user_project):
        raise NotImplementedError


class SimpleDeployment(Deployment):
    TYPE = "simple"

    @classmethod
    def run(cls, site, user_project):
        git_url = user_project.git_url
        app_domain = f"{user_project.user_id}.{site.domain}"
        deployment_dir = get_deployment_root() / app_domain
        deployment_dir.mkdir(parents=True, exist_ok=True)

        # copy contents of Git repo to deployment dir
        git.clone(git_url, ".", workdir=str(deployment_dir))

        commit_hash = git.rev_parse("HEAD", workdir=str(deployment_dir))

        write_deploy_changelog(
            site_id=site.id,
            user_id=user_project.user_id,
            project_id=user_project.project_id,
            type="simple",
            git_commit_hash=commit_hash,
            app_url=user_project.get_app_url(),
        )

    def can_serve_domain(self, domain):
        return (get_deployment_root() / domain).is_dir()

    def serve_domain(self, domain, env, start_response):
        deployment_dir = str(get_deployment_root() / domain)
        with add_sys_path(deployment_dir):
            return importlib.import_module("wsgi").app(env, start_response)


@contextlib.contextmanager
def add_sys_path(path):
    sys.path.insert(0, path)
    try:
        yield
    finally:
        sys.path.remove(path)


def get_deployment_root() -> Path:
    return Path(config.data_dir) / "deployments"

NOMAD_JOB_TEMPLATE = """
job "{{name}}" {
  type = "service"

  group "{{name}}" {
    count = 1

    network {
      port "web" {
        to = 8080
      }
    }

    service {
      name     = "{{name}}"
      port     = "web"

      tags = ["capstone-service"]

      meta {
        host = "{{host}}"
      }
    }

    task "{{name}}" {

      driver = "docker"

      config {
        image = "{{docker_image}}"
        force_pull = true
        ports = ["web"]
      }
    }
  }
}
"""

def get_nomad_job_hcl(name, host, docker_image):
    t = Template(NOMAD_JOB_TEMPLATE)
    return t.render(name=name, host=host, docker_image=docker_image)

class Task:
    def __init__(self, site: str):
        self.site = site
        self.task_id = uuid.uuid4().hex
        self.logger = self.make_logger(self.site, self.task_id)

    def make_logger(self, site: str, task_id: str) -> logging.Logger:
        '''Creates a logger for a particular upload and sets up relevant parameters
        '''
        log_root = Path(config.data_dir)

        logger = logging.Logger(task_id)
        logger.setLevel(logging.DEBUG)
        filename = f'{task_id}.log'
        logfile = log_root.joinpath("tasks", site, filename)
        logfile.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(str(logfile))
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        return logger

class DeployTask(Task):
    def __init__(self, site: str, name, hostname, git_url):
        super().__init__(site)
        self.name = name
        self.hostname = hostname
        self.git_url = git_url
        self.cwd = None

    def chdir(self, directory):
        self.logger.info("")
        self.logger.info("$ cd %s", directory)
        self.cwd = os.path.join(self.cwd or "", directory)

    def run(self):
        self.logger.info(f"Starting DeployTask {self.task_id} to deploy {self.hostname}")
        image = self.build_docker_image()
        self.logger.info("deploying the job to nomad")
        ok = NomadDeployer().deploy(self.name, self.hostname, image)
        if ok:
            self.logger.info("The webapp %s is deployed", self.hostname)
        else:
            self.logger.error("The webapp %s failed to deploy", self.hostname)
        return ok

    def run_command(self, *args, **kwargs):
        self.logger.info("")
        self.logger.info("$ %s", ' '.join(args))
        p = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=self.cwd, **kwargs)
        status = p.wait()
        self.logger.info(p.stdout.read())
        if status != 0:
            self.logger.error("Command failed with exit status: %s", status)
            return False
        else:
            self.logger.info("Command finished successfully.")
            return True

    def build_docker_image(self):
        with tempfile.TemporaryDirectory() as root:
            self.chdir(root)

            docker_image = f"{config.docker_registry}/capstone-{self.site}-{self.name}"
            self.run_command("git", "clone", self.git_url, "repo")

            self.chdir("repo")
            self.run_command("cat", "Dockerfile")
            self.run_command("docker", "build", ".", "-t", docker_image)
            self.run_command("docker", "push", docker_image)
            return docker_image


class NomadDeployer:
    """Creates a deployer based on Nomad.

    Uses env vars like NOMAD_ADDR to connect to Nomad.

    See documentation of python-nomad for more details.
    """
    def __init__(self):
        self.nomad = nomad.Nomad()

    def deploy(self, name, hostname, docker_image):
        job_hcl = get_nomad_job_hcl(name, hostname, docker_image)
        job = self.nomad.jobs.parse(job_hcl)

        # TODO: check the response for errors and return a handle to the deployment
        response = self.nomad.jobs.register_job({"job": job})
        print(response)

        return True


class NomadDeployment(Deployment):
    TYPE = "nomad"

    @classmethod
    def run(cls, site: Site, user_project: UserProject) -> None:
        if site.id != user_project.get_site().id:
            raise ValueError("Site and user_project must be from the same site")

        username = user_project.get_user().username
        project_name = user_project.get_project().name
        name = f"{username}-{project_name}"
        hostname = config.app_url_hostname_template.format(
            username=username,
            project_name=project_name,
            site_name=site.name
        )
        app_url = config.app_url_scheme + "://" + hostname
        if hostname.endswith(".local.pipal.in"):
            # running locally
            app_url += ":8080"

        task = DeployTask(site.name, name=name, hostname=hostname, git_url=user_project.git_url)
        deployment_ok = task.run()

        if deployment_ok:
            user_project.set_app_url(app_url)
            write_deploy_changelog(
                site_id=site.id,
                user_id=user_project.user_id,
                project_id=user_project.project_id,
                type=cls.TYPE,
                git_commit_hash=None,  # TODO: set commit hash
                app_url=app_url,
            )
