from db import Activity, Project, Task, TaskActivity, User


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
    ).save()

if not Activity.find(user_id=user.id, project_id=project.id):
    Activity(user_id=user.id, project_id=project.id).save()

activity = Activity.find(username="test", project_name=project.name)
task = project.get_tasks()[0]

if not TaskActivity.find(activity_id=activity.id, task_id=task.id):
    TaskActivity(
        activity_id=activity.id,
        task_id=task.id,
        status="Completed",
        checks=[]).save()
