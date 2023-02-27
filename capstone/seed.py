from .db import Activity, CheckStatus, Project, Task, TaskActivity, User


if not User.find(username="test"):
    user = User(
        username="test",
        email_address="test@example.com",
        full_name="Test Alpha",
        password=None)
    user.set_password("testpass")
    user.save()
user = User.find(username="test")


if not Project.find(name="build-your-own-shell"):
    Project(
        name="build-your-own-shell",
        title="Build your own Shell",
        short_description="Learn about Unix by building your own shell",
        description="Learn the basics of Unix by building your own shell.\n\n### You will learn about Python and Unix",
        is_active=True,
        tags=["Unix", "Python"],
        checks_url="http://shell.capstone.pipal.in/checks",
    ).save()

project = Project.find(name="build-your-own-shell")
if not Task.find(name="write-parser", project_id=project.id):
    Task(name="write-parser",
         title="Write a parser",
         description="## Write a parser",
         checks=[],
         position=1,
         project_id=project.id).save()

if not Task.find(name="echo", project_id=project.id):
    Task(name="echo",
         title="Build echo",
         description="Echo command",
         checks=[],
         position=2,
         project_id=project.id).save()

if not Project.find(name="pippet"):
    Project(
        name="pippet",
        title="Pippet",
        short_description="Build your own web framework in Python",
        description="Learn about web and Python by building your own Web Framework.\n\n*web framework*, **bold**, `code`",
        is_active=True,
        tags=["Python", "Framework"],
        checks_url="http://pippet.capstone.pipal.in/checks",
    ).save()

if not Activity.find(user_id=user.id, project_id=project.id):
    Activity(user_id=user.id, project_id=project.id).save()

activity = Activity.find(username="test", project_name=project.name)
task_1, task_2 = project.get_tasks()

if not TaskActivity.find(activity_id=activity.id, task_id=task_1.id):
    TaskActivity(
        activity_id=activity.id,
        task_id=task_1.id,
        status="Completed",
        checks=[]).save()

if not TaskActivity.find(activity_id=activity.id, task_id=task_2.id):
    TaskActivity(
        activity_id=activity.id,
        task_id=task_2.id,
        status="In Progress",
        checks=[
            CheckStatus(name=c.name, status="pending", message="")
            for c in task_2.checks
        ]).save()
