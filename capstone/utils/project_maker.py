import tempfile
from pathlib import Path

from cookiecutter.main import cookiecutter

from . import git, gitto
from capstone import db


project_template_dir = str(
    Path(__file__).parent.parent.parent / "cookiecutter-capstone-project"
)


def create_project(site: db.Site, name: str, title: str) -> db.Project:
    """Creates a project, its repository on gitto, and initialises it.

    1. Create repo on gitto
    2. Create project in DB (delete gitto repo if this fails)
    3. Set webhook on gitto
    4. Call init_project() to do the rest
    """
    assert site.id is not None

    repo_name = f"capstone-{name}"
    repo_id = gitto.create_repo(name=repo_name)
    repo_info = gitto.get_repo(id=repo_id)

    # the values here except site_id and name don't matter because they will
    # be overwritten after init_project is called and it makes a git push.
    project = db.Project(
        site_id=site.id, name=name, title=title,
        short_description="placeholder", description="placeholder",
        is_published=False, tags=[],
        git_url=repo_info["git_url"], repo_id=repo_id,
        project_type="web",
        deployment_type="nomad",
    )

    with db.db.transaction():
        # TODO: maybe also use a context manager for the gitto repo?
        # Like the transaction, it should also be deleted if any of
        # the next steps fail
        try:
            project.save()
        except Exception:
            gitto.delete_repo(id=repo_id)
            raise

        webhook_endpoint = f"/api/projects/{project.name}/hook/{project.repo_id}"
        gitto.set_webhook(
            id=repo_id,
            webhook_url=site.get_url() + webhook_endpoint
        )

    # init_project outside of transaction because the webhook call
    # after first push needs the project to be committed to db.
    try:
        init_project(project)
    except Exception:
        # note that project.delete() should also delete the gitto repo
        project.delete()
        raise

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
        git.clone(project.git_url, git_dir)
        cookiecutter(
            template=project_template_dir,
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
