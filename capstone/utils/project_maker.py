import tempfile
from pathlib import Path

from cookiecutter.main import cookiecutter

from . import git, gito
from capstone import config, db


def create_project(site: db.Site, name: str, title: str) -> db.Project:
    """Creates a project, its repository on gito, and initialises it.

    1. Create repo on gito
    2. Create project in DB (delete gito repo if this fails)
    3. Set webhook on gito
    4. Call init_project() to do the rest
    """
    assert site.id is not None

    repo_name = f"capstone-{name}"
    repo_id = gito.create_repo(name=repo_name)
    repo_info = gito.get_repo(id=repo_id)

    project = db.Project(
        site_id=site.id, name=name, title=title,
        short_description="placeholder", description="placeholder",
        is_published=False, tags=[],
        git_url=repo_info["git_url"], gito_repo_id=repo_id,
    )

    with db.db.transaction():
        # TODO: maybe also use a context manager for the gito repo?
        # Like the transaction, it should also be deleted if any of
        # the next steps fail
        try:
            project.save()
        except Exception:
            gito.delete_repo(id=repo_id)
            raise

        webhook_endpoint = f"/api/projects/{project.name}/hook/{project.gito_repo_id}"
        gito.set_webhook(
            id=repo_id,
            webhook_url=site.get_url() + webhook_endpoint
        )

        init_project(project)

    return project


def init_project(project: db.Project) -> db.Project:
    """Initializes a created project with the template files.
    """
    assert project.git_url is not None, "project must have git url"

    with tempfile.TemporaryDirectory() as tmp:
        # create directory inside tmp named project.name
        # clone into this directory. cookiecutter will write
        # into this directory when tmp is passed as output_dir
        Path(tmp) / project.name
        git_dir = str(Path(tmp) / project.name)
        git.clone(project.git_url, git_dir, workdir=git_dir)
        cookiecutter(
            template=config.project_template_dir,
            no_input=True,
            extra_context={
                "project_name": project.name, "project_title": project.title
            },
            output_dir=tmp,
            overwrite_if_exists=True,
        )
        git.add(".", workdir=git_dir)
        git.commit(message="Initial commit", workdir=git_dir)
        git.push(workdir=git_dir)

    return project
