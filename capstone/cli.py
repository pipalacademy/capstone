import click

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


@projects.command("show")
@site_option()
@click.argument("project")
def projects_show(site, project):
    """Show a project in a site."""
    print("Show project", site, project)

if __name__ == "__main__":
    cli()