from pathlib import Path

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
        deployment_dir = Path(config.deployment_root) / app_domain
        deployment_dir.mkdir(exist_ok=True)

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
