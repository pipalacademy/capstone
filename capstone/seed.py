from db import Activity, Project, User


if not User.find(username="test"):
    user = User(
        username="test",
        email_address="test@example.com",
        full_name="Test Alpha",
        password=None)
    user.set_password("testpass")
    user.save()


if not Project.find(name="build-your-own-shell"):
    Project(
        name="build-your-own-shell",
        title="Build your own Shell",
        short_description="Learn about Unix by building your own shell",
        description="Learn the basics of Unix by building your own shell.\n\n### You will learn about Python and Unix",
        is_active=True,
        tags=["Unix", "Python"],
    ).save()


if not Project.find(name="pippet"):
    Project(
        name="pippet",
        title="Pippet",
        short_description="Build your own web framework in Python",
        description="Learn about web and Python by building your own Web Framework.\n\n*web framework*, **bold**, `code`",
        is_active=True,
        tags=["Python", "Framework"],
    ).save()

if not Activity.find(username="test", project_name="build-your-own-shell"):
    Activity(username="test", project_name="build-your-own-shell").save()
