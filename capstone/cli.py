import click
import sys
import yaml

from capstone import db, deployment


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
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    else:
        site_dict = db_site.get_dict()
        print(prettify(site_dict))

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
    print(prettify([project.get_teaser() for project in projects]))


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
    print(prettify([user.get_teaser() for user in users]))

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
    print(prettify(user_dict))

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

## USER PROJECTS

@cli.group()
def user_projects():
    """manage user projects"""
    pass

@user_projects.command("list")
@site_option()
@click.option("-u", "--user", default=None)
@click.option("-p", "--project", default=None)
def user_projects_list(site, user, project):
    print("List user projects", site, f"user={user or 'any'}", f"project={project or 'any'}")
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user = db.User.find(username=user) if user else None
    if user:
        if db_user is None:
            print("User not found")
            sys.exit(1)
        elif db_user.site_id != db_site.id:
            print("User not found in site")
            sys.exit(1)
    db_project = db.Project.find(name=project) if project else None
    if project:
        if db_project is None:
            print("Project not found")
            sys.exit(1)
        elif db_project.site_id != db_site.id:
            print("Project not found in site")
            sys.exit(1)
    filters = {}
    if db_user:
        filters["user_id"] = db_user.id
    if db_project:
        filters["project_id"] = db_project.id
    if filters:
        user_projects = db.UserProject.find_all(**filters)
    else:
        user_projects = sum([p.get_user_projects() for p in db.Project.find_all(site_id=db_site.id)], [])
    table_data = []
    for user_project in user_projects:
        table_data.append({
            "id": user_project.id,
            "project": db.Project.find(id=user_project.project_id).name,
            "email": db.User.find(id=user_project.user_id).email,
            "git_url": user_project.git_url,
            # "progress": user_project.get_progress(),  # TODO: add progress here
        })
    if not table_data:
        print("No matching rows found")
        sys.exit(0)
    print(prettify(table_data))

@user_projects.command("show")
@site_option()
@click.argument("user_project_id")
def user_projects_show(site, user_project_id):
    """Show a user project in a site."""
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user_project = db.UserProject.find(id=user_project_id)
    if db_user_project is None:
        print("User project not found")
        sys.exit(1)
    user_project_dict = db_user_project.get_dict()
    project_name = db_user_project.get_project().name
    user_email = db_user_project.get_user().email
    print(prettify(dict(user_project_dict, project=project_name, email=user_email)))

@user_projects.command("delete")
@site_option()
@click.argument("user_project_id")
def user_projects_delete(site, user_project_id):
    """Delete a user project in a site."""
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user_project = db.UserProject.find(id=user_project_id)
    if db_user_project is None:
        print("User project not found")
        sys.exit(1)
    if db_user_project.get_project().site_id != db_site.id:
        print("User project does not belong to site")
        sys.exit(1)

    db_user_project.delete()

## DEPLOYMENTS

@cli.group()
def deploys():
    """manage deployments"""
    pass

@deploys.command("list")
@site_option()
@click.option("-u", "--user", default=None)
@click.option("-p", "--project", default=None)
def deploys_list(site, user, project):
    """List deployments in a site."""
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user = db_site.get_user(username=user) if user else None
    if user:
        if db_user is None:
            print("User not found")
            sys.exit(1)
        elif db_user.site_id != db_site.id:
            print("User not found in site")
            sys.exit(1)
    db_project = db_site.get_project(name=project) if project else None
    if project:
        if db_project is None:
            print("Project not found")
            sys.exit(1)
        elif db_project.site_id != db_site.id:
            print("Project not found in site")
            sys.exit(1)
    filters = {}
    if db_user:
        filters["user_id"] = db_user.id
    if db_project:
        filters["project_id"] = db_project.id
    deployments = deployment.get_deployments(site=db_site, **filters)
    if not deployments:
        print("No matching rows found")
        sys.exit(0)
    print(prettify(deployments))

@deploys.command("new")
@site_option()
@click.option("-u", "--user")
@click.option("-p", "--project")
def deploys_new(site, user, project):
    """List deployments in a site."""
    db_site = db.Site.find(name=site)
    if db_site is None:
        print("Site not found")
        sys.exit(1)
    db_user = db_site.get_user(username=user)
    if db_user is None:
        print("User not found")
        sys.exit(1)
    if db_user.site_id != db_site.id:
        print("User not found in site")
        sys.exit(1)
    db_project = db_site.get_project(name=project)
    if db_project is None:
        print("Project not found")
        sys.exit(1)
    if db_project.site_id != db_site.id:
        print("Project not found in site")
        sys.exit(1)
    user_project = db.UserProject.find(user_id=db_user.id, project_id=db_project.id)
    if user_project is None:
        print("User hasn't started project")
        sys.exit(1)
    deployment.new_deployment(user_project=user_project)
    print("Deployment created")

if __name__ == "__main__":
    cli()
