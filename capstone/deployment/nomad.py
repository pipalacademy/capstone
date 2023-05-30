import logging
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

import nomad
from jinja2 import Template

from capstone import config
from capstone.db import Site, UserProject
from .base import Deployment


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

      resources {
        cpu   = 100
        memory = 128
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

    def run(self):
        self.logger.info(f"Starting DeployTask {self.task_id} to deploy {self.hostname}")

        with tempfile.TemporaryDirectory() as root:
            repo = Path(root) / "repo"
            repo.mkdir()
            self.chdir(str(repo))

            commit_hash, logs, ok = self.clone_repo(repo)
            if not ok:
                self.logger.error(f"INTERNAL ERROR: Failed to clone repo\n{logs}")
                return {
                    "ok": False,
                    "log": f"Failed to clone Git repo\n{logs}",
                }

            image_tag, logs, ok = self.build_docker_image()
            if not ok:
                self.logger.error(f"Failed to build docker image: {logs}")
                return {
                    "ok": False,
                    "log": f"Failed to build docker image\n{logs}",
                }

            job_id, logs, ok = self.deploy_to_nomad(image_tag)
            if not ok:
                self.logger.error(
                    "INTERNAL ERROR: Failed to deploy app to Nomad"
                )
                return {
                    "ok": False,
                    "log": f"Failed to deploy to Nomad\n{logs}",
                }

            _, logs, ok = self.check_health(job_id)
            if not ok:
                self.logger.error("App health check failed")
                return {
                    "ok": False,
                    "log": f"App health check failed\n{logs}",
                }

        return {"ok": True, "log": None}

    def run_command(self, *args, **kwargs) -> tuple[str, bool]:
        self.logger.info("")
        self.logger.info("$ %s", ' '.join(args))
        p = subprocess.Popen(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=self.cwd, **kwargs)
        status = p.wait()
        logs = p.stdout.read()  # type: ignore
        self.logger.info(logs)
        if status != 0:
            self.logger.error("Command failed with exit status: %s", status)
            return logs, False
        else:
            self.logger.info("Command finished successfully.")
            return logs, True

    def chdir(self, directory):
        self.logger.info("")
        self.logger.info("$ cd %s", directory)
        self.cwd = os.path.join(self.cwd or "", directory)

    def clone_repo(self, to: Path) -> tuple[str|None, str|None, bool]:
        self.logger.info("Cloning the git repository")
        logs_1, ok = self.run_command("git", "clone", self.git_url, str(to))
        cumulative_logs = "\n\n$ git clone {self.git_url} {to}\n" + logs_1
        if not ok:
            return None, logs_1, False

        logs_2, ok = self.run_command("git", "rev-parse", "HEAD")
        cumulative_logs += "\n\n$ git rev-parse HEAD\n" + logs_2
        if not ok:
            return None, cumulative_logs, False

        return logs_2.strip(), cumulative_logs, True

    def get_docker_image_tag(self) -> str:
        random_suffix = uuid.uuid4().hex[:10]
        return f"{config.docker_registry}/capstone-{self.site}-{self.name}:{random_suffix}"

    def build_docker_image(self) -> tuple[str|None, str|None, bool]:
        docker_image = self.get_docker_image_tag()
        self.logger.info("Building the docker image")
        logs_1, ok = self.run_command("cat", "Dockerfile")
        cumulative_logs = "\n\n$ cat Dockerfile\n" + logs_1
        if not ok:
            return None, cumulative_logs, False

        logs_2, ok = self.run_command("docker", "build", "-t", docker_image, ".")
        cumulative_logs += "\n\n$ docker build -t {docker_image} .\n" + logs_2
        if not ok:
            return None, cumulative_logs, False

        logs_3, ok = self.run_command("docker", "push", docker_image)
        cumulative_logs += "\n\n$ docker push {docker_image}\n" + logs_3
        if not ok:
            return None, cumulative_logs, False

        return docker_image, cumulative_logs, True

    def deploy_to_nomad(self, image: str) -> tuple[str|None, str|None, bool]:
        self.logger.info(f"Deploying the job to nomad {image}")
        try:
            job_id = NomadDeployer().deploy(self.name, self.hostname, image)
        except nomad.api.exceptions.BaseNomadException as e:
            self.logger.exception(f"Failed to deploy to Nomad: {e}")
            return None, str(e), False

        return job_id, None, True

    def check_health(
        self, job_id: str, timeout: int = 60, sleep_interval: int = 5,
    ) -> tuple[None, str|None, bool]:
        self.logger.info(f"Checking health of job {job_id}")
        start = time.perf_counter()
        while True:
            try:
                depl = nomad.Nomad().job.get_deployment(job_id)
            except nomad.api.exceptions.BaseNomadException as e:
                self.logger.exception(f"Failed to get deployment from Nomad: {e}")
                return None, str(e), False

            status = depl["Status"]
            if status == "successful":
                return None, None, True

            # TODO: use this logs API to stream app logs
            # https://developer.hashicorp.com/nomad/api-docs/client#stream-logs
            now = time.perf_counter()
            if now - start >= timeout:
                return None, f"Timeout after {timeout} seconds. Job status: {status}", False

            self.logger.info(f"Waiting for job to start. Current status: {status}. "
                             f"Will check again in {sleep_interval} seconds.")
            time.sleep(sleep_interval)


class NomadDeployer:
    """Creates a deployer based on Nomad.

    Uses env vars like NOMAD_ADDR to connect to Nomad.

    See documentation of python-nomad for more details.
    """
    def __init__(self):
        self.nomad = nomad.Nomad()

    def deploy(self, name: str, hostname: str, docker_image: str) -> str:
        """Returns job ID
        """
        job_hcl = get_nomad_job_hcl(name, hostname, docker_image)
        job = self.nomad.jobs.parse(job_hcl)

        job_id = name
        response = self.nomad.job.register_job(job_id, {"job": job})
        print("response", response, file=sys.stderr)

        return job_id


class NomadDeployment(Deployment):
    TYPE = "nomad"

    @classmethod
    def run(cls, site: Site, user_project: UserProject) -> dict[str, Any]:
        """
        Returns a result dict:
        { 
            "ok": bool,
            "logs": str,
            "app_url": optional str  # only if ok is True
        }
        """
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
        result = task.run()
        result["app_url"] = app_url
        return result
