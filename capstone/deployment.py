"""Deployment interface for capstone.
"""

import contextlib
import importlib
import sys
from pathlib import Path
from jinja2 import Template
import nomad

from capstone import config
from capstone.db import db
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
            app_url=f"http://{app_domain}",
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
        ports = ["web"]
      }
    }
  }
}
"""

def get_nomad_job_hcl(name, host, docker_image):
    t = Template(NOMAD_JOB_TEMPLATE)
    return t.render(name=name, host=host, docker_image=docker_image)

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
        self.nomad.jobs.register_job({"job": job})
