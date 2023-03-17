import click
import sys
from tabulate import tabulate

from capstone import db


@click.group()
def cli():
    pass

def site_option():
    return click.option("-s", "--site",
                        help="Site name",
                        envvar="CAPSTONE_SITE",
                        required=True)

def make_table(rows, **kwargs):
    # rows is a list of rows
    # each row is a dict with `"column_name": "value"` mapping
    options = dict(
        headers="keys",
        tablefmt="grid",
        maxcolwidths=12)
    options.update(kwargs)
    return tabulate(sanitize_rows(rows), **options)

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
    print(make_table([site.get_dict() for site in sites]))

@sites.command("show")
@click.argument("site")
def sites_show(site):
    """Show a site."""
    print("Show site", site)
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    else:
        site_dict = db_site.get_dict()
        print(make_table(
            {"key": list(site_dict.keys()), "value": list(site_dict.values())},
            maxcolwidths=50))

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
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    projects = db.Project.find_all(site_id=db_site.id)
    print(make_table([project.get_teaser() for project in projects]))


@projects.command("show")
@site_option()
@click.argument("project")
def projects_show(site, project):
    """Show a project in a site."""
    print("Show project", site, project)
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_project = db.Project.find(name=project)
    tasks = db_project.get_tasks()
    if db_project is None:
        print("Project not found")
        sys.exit(1)
    project_dict = db_project.get_dict()
    project_dict["num_tasks"] = len(tasks)
    print(make_table(
        {"key": list(project_dict.keys()), "value": list(project_dict.values())},
        maxcolwidths=60))
    if tasks:
        # TODO: maybe figure out a better way to print checks?
        print("Tasks")
        print(make_table([
            {
                **t.get_dict(),
                "checks": [c.title for c in t.get_checks()],
            }
            for t in tasks
        ]))


@projects.command("delete")
@site_option()
@click.argument("project")
def projects_delete(site, project):
    """Delete a project in a site."""
    print("Delete project", site, project)
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_project = db.Project.find(name=project)
    if db_project is None:
        print("Project not found")
        sys.exit(1)
    project_name = db_project.name
    db_project.delete()
    print(f"Deleted project {project_name}")

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
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    users = db.User.find_all(site_id=db_site.id)
    print(make_table([user.get_teaser() for user in users]))

@users.command("show")
@site_option()
@click.argument("username")
def users_show(site, username):
    """Show a user in a site."""
    print("Show user", site, username)
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user = db.User.find(username=username)
    if db_user is None:
        print("User not found")
        sys.exit(1)
    user_dict = db_user.get_dict()
    print(make_table(
        {"key": list(user_dict.keys()),
         "value": list(user_dict.values())},
        maxcolwidths=60))

@users.command("delete")
@site_option()
@click.argument("username")
def users_delete(site, username):
    """Delete a user in a site."""
    print("Delete user", site, username)
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user = db.User.find(username=username)
    if db_user is None:
        print("User not found")
        sys.exit(1)
    user_name = db_user.username
    db_user.delete()
    print(f"Deleted user {user_name}")

if __name__ == "__main__":
    cli()
