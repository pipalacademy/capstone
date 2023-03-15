import click
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

## SITES

@cli.group()
def sites():
    """manage sites"""
    pass

@sites.command("list")
def sites_list():
    """Lists sites"""
    print("List sites")

@sites.command("show")
@click.argument("site")
def sites_show(site):
    """Show a site."""
    print("Show site", site)

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
    projects = db.Project.find_all(site_id=db_site.id)
    print(tabulate(
        [project.get_teaser() for project in projects],
        headers="keys",
        maxcolwidths=[40] * 10))


@projects.command("show")
@site_option()
@click.argument("project")
def projects_show(site, project):
    """Show a project in a site."""
    print("Show project", site, project)

if __name__ == "__main__":
    cli()
