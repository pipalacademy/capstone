import click
import sys
import yaml

from capstone import db, deployment
from capstone.utils.project_maker import create_project


@click.group()
def cli():
    pass

def site_option():
    return click.option("-s", "--site",
                        help="Site name",
                        envvar="CAPSTONE_SITE",
                        required=True)

def prettify(rows, **kwargs):
    # rows is a list of rows
    # each row is a dict with `"column_name": "value"` mapping
    return yaml.dump(rows, sort_keys=False)

def sanitize_rows(rows):
    """Convert None values to str(None).

    Rows could be list, dict, dict_keys, or dict_values.
    """
    if isinstance(rows, list):
        return [sanitize_rows(row) for row in rows]
    elif isinstance(rows, dict):
        return {k: sanitize_rows(v) for k, v in rows.items()}
    elif rows is None:
        return "None"
    else:
        return rows

def get_project(site_name, project_name):
    site = db.Site.find_or_fail(name=site_name)
    project = site.get_project_or_fail(name=project_name)

    return project

def get_projects(site_name):
    site = db.Site.find_or_fail(name=site_name)
    projects = site.get_projects()

    return projects

def get_user(site_name, username):
    site = db.Site.find_or_fail(name=site_name)
    user = site.get_user_or_fail(username=username)

    return user

def get_users(site_name):
    site = db.Site.find_or_fail(name=site_name)
    users = site.get_users()

    return users

def get_user_projects(site_name, username=None, project_name=None):
    site = db.Site.find_or_fail(name=site_name)
    user = username and get_user(site_name, username)
    project = project_name and get_project(site_name, project_name)

    if user and project:
        user_projects = [project.get_user_project(user_id=user.id)]
    elif user:
        user_projects = user.get_user_projects()
    elif project:
        user_projects = project.get_user_projects()
    else:
        user_projects = site.get_user_projects()

    return user_projects

def get_user_project(site_name, user_project_id):
    site = db.Site.find_or_fail(name=site_name)
    user_project = db.UserProject.find_or_fail(
        id=user_project_id,
    )
    assert user_project.get_site().id == site.id
    return user_project

## SITES

@cli.group()
def sites():
    """manage sites"""
    pass

@sites.command("list")
def sites_list():
    """Lists sites"""
    print("List sites")
    sites = db.Site.find_all()
    print(prettify([site.get_dict() for site in sites]))

@sites.command("show")
@click.argument("site")
def sites_show(site):
    """Show a site."""
    print("Show site", site)
    db_site = db.Site.find_or_fail(name=site)
    print(prettify(db_site.get_dict()))

@sites.command("new")
@click.option("-t", "--title", prompt=True, required=True, help="Site title")
@click.option("-n", "--name", prompt=True, required=True, help="Site name")
@click.option("-d", "--domain", prompt=True, required=True, help="Site domain")
def sites_new(title, name, domain):
    """Create a new site."""
    print("New site", title, name, domain)
    db_site = db.Site(title=title, name=name, domain=domain).save()
    print(prettify(db_site.get_dict()))

## PROJECTS

@cli.group()
def projects():
    """manage projects"""
    pass

@projects.command("list")
@site_option()
def projects_list(site):
    """Lists projects of a site."""
    print("List projects", site)
    projects = get_projects(site)
    print(prettify([project.get_teaser() for project in projects]))


@projects.command("show")
@site_option()
@click.argument("project_name")
def projects_show(site, project_name):
    """Show a project in a site."""
    print("Show project", site, project_name)
    project = get_project(site, project_name)
    tasks = project.get_tasks()
    project_dict = dict(project.get_dict(), num_tasks=len(tasks))
    print(prettify(project_dict))
    if tasks:
        # TODO: maybe figure out a better way to print checks?
        print("Tasks")
        print(prettify([
            {
                **t.get_dict(),
                "checks": [c.title for c in t.get_checks()],
            }
            for t in tasks
        ]))


@projects.command("delete")
@site_option()
@click.argument("project_name")
def projects_delete(site, project_name):
    """Delete a project in a site."""
    print("Delete project", site, project_name)
    get_project(site, project_name).delete()
    print(f"Deleted project {project_name}")


@projects.command("new")
@site_option()
@click.option("-t", "--title", help="Project title")
@click.option("-n", "--name", help="Project name")
def projects_new(site, title=None, name=None):
    """Create a new project in a site."""
    if title is None:
        title = click.prompt("Project title", default="Build your own Shell")
    if name is None:
        name = click.prompt(
            "Project name",
            default=title.lower().replace(" ", "-").replace("_", "-").replace(".", "-")
        )

    print("New project", site, title, name)
    db_site = db.Site.find_or_fail(name=site)
    project = create_project(site=db_site, name=name, title=title)
    preview = dict(project.get_teaser(), git_url=project.git_url)
    print(prettify(preview))


@projects.command("publish")
@site_option()
@click.argument("project_name")
def projects_publish(site, project_name):
    """Publish a project in a site.
    """
    project = get_project(site, project_name)
    project.publish()


@projects.command("unpublish")
@site_option()
@click.argument("project_name")
def projects_unpublish(site, project_name):
    """Unpublish a project in a site.
    """
    project = get_project(site, project_name)
    project.unpublish()


## USERS

@cli.group()
def users():
    """manage projects"""
    pass


@users.command("list")
@site_option()
def users_list(site):
    """Lists users of a site."""
    print("List users", site)
    print(
        prettify([user.get_teaser() for user in get_users(site)])
    )


@users.command("show")
@site_option()
@click.argument("username")
def users_show(site, username):
    """Show a user in a site."""
    print("Show user", site, username)
    print(prettify(get_user(site, username).get_dict()))


@users.command("delete")
@site_option()
@click.argument("username")
def users_delete(site, username):
    """Delete a user in a site."""
    print("Delete user", site, username)
    get_user(site, username).delete()
    print(f"Deleted user {username}")


## USER PROJECTS

@cli.group()
def user_projects():
    """manage user projects"""
    pass


@user_projects.command("list")
@site_option()
@click.option("-u", "--user", "username", default=None)
@click.option("-p", "--project", "project_name", default=None)
def user_projects_list(site, username, project_name):
    # TODO: list username instead of email?
    print(
        "List user projects",
        site,
        f"user={username or 'any'}",
        f"project={project_name or 'any'}"
    )
    user_projects = get_user_projects(
        site, username=username, project_name=project_name
    )

    table_data = []
    for user_project in user_projects:
        table_data.append({
            "id": user_project.id,
            "project": user_project.get_project().name,
            "email": user_project.get_user().email,
            "git_url": user_project.git_url,
            # "progress": user_project.get_progress(),  # TODO: add progress here
        })
    if table_data:
        print(prettify(table_data))
    else:
        print("No matching rows found")


@user_projects.command("show")
@site_option()
@click.argument("user_project_id")
def user_projects_show(site, user_project_id):
    """Show a user project in a site."""
    # TODO: show username instead of email?
    print("Show user project", site, user_project_id)
    user_project = get_user_project(site, user_project_id)
    user_project_dict = user_project.get_dict()
    project_name = user_project.get_project().name
    user_email = user_project.get_user().email
    print(
        prettify(
            dict(user_project_dict, project=project_name, email=user_email)
        )
    )


@user_projects.command("delete")
@site_option()
@click.argument("user_project_id")
def user_projects_delete(site, user_project_id):
    """Delete a user project in a site."""
    print("Delete user project", site, user_project_id)
    get_user_project(site, user_project_id).delete()
    print(f"Deleted user project {user_project_id}")


## DEPLOYMENTS

@cli.group()
def deploys():
    """manage deployments"""
    pass


@deploys.command("list")
@site_option()
@click.option("-u", "--user", "username", default=None)
@click.option("-p", "--project", "project_name", default=None)
def deploys_list(site, username, project_name):
    """List deployments in a site."""
    print(
        "List deployments",
        site,
        f"user={username or 'any'}",
        f"project={project_name or 'any'}"
    )
    db_site = db.Site.find_or_fail(name=site)
    user = get_user(site, username) if username else None
    project = get_project(site, project_name) if project_name else None
    filters = {}
    if user:
        filters["user_id"] = user.id
    if project:
        filters["project_id"] = project.id
    deployments = deployment.get_deployments(site=db_site, **filters)
    if deployments:
        print(prettify(deployments))
    else:
        print("No matching rows found")


@deploys.command("new")
@site_option()
@click.option("-u", "--user", "username", required=True)
@click.option("-p", "--project", "project_name", required=True)
def deploys_new(site, username, project_name):
    """Create a new deployment in a site."""
    print(
        "Create deployment",
        site,
        f"user={username or 'any'}",
        f"project={project_name or 'any'}"
    )
    user = get_user(site, username)
    project = get_project(site, project_name)

    user_project = project.get_user_project(user_id=user.id)
    if user_project is None:
        print("User hasn't started project")
        sys.exit(1)

    deployment.new_deployment(user_project=user_project)
    print("Deployment created")


if __name__ == "__main__":
    cli()
