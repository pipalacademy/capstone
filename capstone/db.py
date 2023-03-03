from __future__ import annotations

import hashlib
import json
import os
import string
import random
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import subprocess
from typing import Any

import web

from . import config
from .utils.files import get_private_file_path

db = web.database(config.db_uri)


@dataclass(kw_only=True)
class Document:
    _tablename = ...

    id: int | None = None
    created: datetime | None = None
    last_modified: datetime | None = None

    def _to_json(self):
        """Private method to convert self to a JSON-serializable dict.

        This will get all fields that are directly on the model.
        If any fields need to be handled specially, this method
        should be overloaded.
        """
        d = asdict(self)
        d.pop("id")
        d["created"] = d["created"].isoformat()
        d["last_modified"] = d["last_modified"].isoformat()
        return d

    @classmethod
    def from_json(cls, json_dict):
        """Private method to convert self from a JSON dict.

        This will return an object with the correct class and
        attributes.
        """
        return cls(**json_dict)

    def _to_db(self):
        """Private method to convert self to a database-compatible dict

        Should complement `_from_db`.
        """
        d = asdict(self)
        d["created"] = d["created"].isoformat()
        d["last_modified"] = d["last_modified"].isoformat()
        return d

    @classmethod
    def _from_db(cls, created, last_modified, **kwargs):
        """Method to convert the data obtained from database to a
        format that should be used in the model.

        Should complement `_to_db`.
        """
        return cls(
            **kwargs,
            created=datetime.fromisoformat(created),
            last_modified=datetime.fromisoformat(last_modified)
        )

    @classmethod
    def find_all(cls, **kwargs):
        rows = db.where(cls._tablename, **kwargs)
        return [cls._from_db(**row) for row in rows]

    @classmethod
    def find(cls, **kwargs):
        docs = cls.find_all(**kwargs, limit=1)
        return docs and docs[0] or None

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def save(self):
        if self.id is None:
            self.created = self.last_modified = get_current_timestamp()
            d = self._to_db()
            d.pop("id")
            self.id = db.insert(self._tablename, **d)
        else:
            self.last_modified = get_current_timestamp()
            db.update(
                self._tablename, where="id=$id", vars={"id": self.id},
                **self._to_db(),
            )
        return self

    def delete(self):
        db.delete(self._tablename, where="id=$id", vars={"id": self.id})

    def get_json(self):
        """Method to convert self to detailed JSON.

        This method returns a detailed JSON, along with extra fields for
        table relationships if there are any.
        """
        return self._to_json()

    def get_teaser(self):
        """Method to convert self to a teaser JSON.

        This method returns a teaser JSON, which can omit some fields
        or relationships that are not considered as important.
        """
        return self._to_json()


@dataclass(kw_only=True)
class Project(Document):
    _tablename = "projects"

    name: str
    title: str
    url: str = field(init=False)
    html_url: str = field(init=False)
    short_description: str
    description: str
    is_active: bool = True
    tags: list[str]
    checks_url: str
    commit_hook_url: str

    def __post_init__(self):
        self.url = get_project_url(self.name)
        self.html_url = get_project_html_url(self.name)

    def _to_json(self):
        d = super()._to_json()
        # TODO: maybe keep html_url in the response
        d.pop("html_url")
        return d

    def _to_db(self):
        d = super()._to_db()
        d["tags"] = json.dumps(d["tags"])
        d["is_active"] = 1 if d["is_active"] else 0
        d.pop("url")
        d.pop("html_url")
        return d

    @classmethod
    def _from_db(cls, name, tags, is_active, **kwargs):
        return super()._from_db(
            **kwargs,
            name=name,
            tags=json.loads(tags),
            is_active=True if is_active else False,
        )

    def get_json(self):
        project = self._to_json()
        tasks = self.get_tasks()
        project["tasks"] = [task.get_json() for task in tasks]
        return project

    def get_teaser(self):
        d = self._to_json()
        d.pop("description")
        return d

    def update_tasks(self, tasks):
        """Takes a list of dicts.

        Each task dict must have name, title, description, and checks.
        """
        if not self.id:
            self.save()

        old_tasks = self.get_tasks()
        new_tasks = [Task.from_json(get_zeroth_task_dict(project_id=self.id))]
        for idx, t_kwds in enumerate(tasks, start=1):
            task = Task.from_json({**t_kwds, "position": idx, "project_id": self.id})
            new_tasks.append(task)

        old_task_names = [t.name for t in old_tasks]
        new_task_names = [t.name for t in new_tasks]

        to_remove = list(
            filter(lambda x: x.name not in new_task_names, old_tasks))
        to_add = list(
            filter(lambda x: x.name not in old_task_names, new_tasks))

        for task in to_remove:
            task.delete()
        for task in to_add:
            task.save()

        for db_task, new_task in zip(self.get_tasks(), new_tasks):
            # NOTE: maybe check before updating?
            db_task.update(
                title=new_task.title,
                description=new_task.description,
                position=new_task.position,
                checks=new_task.checks,
            )
            db_task.save()

    def get_tasks(self):
        return self.id and Task.find_all(project_id=self.id, order="position") or []


@dataclass(kw_only=True)
class User(Document):
    _tablename = "users"

    username: str
    full_name: str
    email_address: str
    password: str

    def _to_json(self):
        d = super()._to_json()
        d.pop("password")
        return d

    def get_teaser(self):
        return {
            "username": self.username,
        }

    def set_password(self, new):
        salt = generate_salt()
        hashed = hash_with_salt(new, salt=salt)
        self.update(password=hashed)
        return self

    def has_started_project(self, project_name):
        return bool(self.get_activity(project_name))

    def get_activity(self, project_name):
        return Activity.find(user_id=self.id, project_name=project_name)

    def start_project(self, project_name):
        project = Project.find(name=project_name)
        repo_path = make_new_project_dir(
            git_dir=config.git_dir, git_user=config.git_user,
            username=self.username, project_name=project.name)
        activity = Activity(
            user_id=self.id, project_id=project.id,
            git_url=f"{config.git_base_url}/{repo_path}").save()
        for i, task in enumerate(project.get_tasks()):
            task.get_default_task_activity(activity_id=self.id).save()

        return activity


@dataclass(kw_only=True)
class Task(Document):
    _tablename = "tasks"

    name: str
    title: str
    description: str
    position: int
    checks: list[Check]

    project_id: int

    def delete(self):
        # overloading the delete method to also delete
        # references in task activity
        related_activities = TaskActivity.find_all(task_id=self.id)
        for task_activity in related_activities:
            task_activity.delete()

        return super().delete()

    def save(self):
        is_new_task = not self.id
        super().save()

        if is_new_task:
            # create default task activity for all projects
            project = self.get_project()
            activities = Activity.find_all(project_id=project.id)
            for activity in activities:
                self.get_default_task_activity(activity_id=activity.id).save()

    def get_default_task_activity(self, activity_id):
        return TaskActivity(
            task_id=self.id,
            activity_id=activity_id,
            checks=[
                CheckStatus(
                    name=check.name, status=CheckStatus.PENDING, message=None)
                for check in self.checks
            ],
            status="In Progress" if self.position == 0 else "Pending",
        )

    def _to_json(self):
        d = super()._to_json()
        d.pop("project_id")
        d.pop("checks")
        d["checks"] = [c.get_json() for c in self.checks]
        return d

    @classmethod
    def from_json(cls, json_dict):
        checks = [
            Check(**check_kwargs) for check_kwargs in json_dict.pop("checks")]
        return cls(**json_dict, checks=checks)

    def _to_db(self):
        d = super()._to_db()
        d.pop("checks")
        d["checks"] = json.dumps([c.get_json() for c in self.checks])
        return d

    @classmethod
    def _from_db(cls, checks, **kwargs):
        return super()._from_db(
            **kwargs,
            checks=[Check(**kw) for kw in json.loads(checks)],
        )

    def get_project(self):
        return Project.find(id=self.project_id)

    def get_teaser(self):
        return {
            "name": self.name,
        }


@dataclass
class Check:
    name: str
    args: dict[str, Any]  # json
    title: str | None = None

    def get_json(self):
        return asdict(self)


@dataclass(kw_only=True)
class Activity(Document):
    _tablename = "activity"

    user_id: int
    project_id: int
    git_url: str

    username: str | None = None
    project_name: str | None = None

    def __post_init__(self):
        if not self.username:
            self.username = self.get_user().username
        if not self.project_name:
            self.project_name = self.get_project().name

    def _to_db(self):
        d = super()._to_db()
        d.pop("username")
        d.pop("project_name")
        return d

    def _to_json(self):
        d = super()._to_json()
        d.pop("user_id")
        d.pop("project_id")
        return d

    @classmethod
    def find_all(cls, **kwargs):
        rows = db.where("activity_view", **kwargs)
        return [cls._from_db(**row) for row in rows]

    def get_user(self):
        return User.find(id=self.user_id)

    def get_project(self):
        return Project.find(id=self.project_id)

    def get_task_activities(self):
        task_activities = []
        for task in self.get_project().get_tasks():
            task_activities.append(self.get_task_activity(task.id))

        return task_activities

    def get_task_activity(self, task_id):
        # TODO: task_id -> task?
        task_activity = TaskActivity.find(activity_id=self.id, task_id=task_id)
        if task_activity is None:
            task = Task.find(id=task_id)
            return task.get_default_task_activity(activity_id=self.id)
        else:
            return task_activity

    def get_progress(self):
        task_activities = self.get_task_activities()
        completed_task_activities = [
            t for t in task_activities if t.status == "Completed"
        ]
        total_tasks = len(task_activities)
        completed_tasks = len(completed_task_activities)
        percentage = round(completed_tasks * 100 / total_tasks, 2) if total_tasks > 0 else 0
        status = get_activity_status_from_task_statuses(
            task.status for task in task_activities)
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "percentage": percentage,
            "status": status,
        }

    def _compute_in_progress_task(self):
        task_activities = self.get_task_activities()

        for (this, next_) in zip(task_activities, task_activities[1:]+[None]):
            if this.status != "Completed" and (
                    next_ is None or next_.status == "Pending"):
                return this

    def update_tasks(self, task_activity_inputs):
        for input in task_activity_inputs:
            task = Task.find(name=input.name)
            task_activity = self.get_task_activity(task.id)
            task_activity.update_from_input(input).save()

        self.set_in_progress_task()

    def set_in_progress_task(self):
        in_progress_task = self._compute_in_progress_task()
        if in_progress_task:
            in_progress_task.status = "In Progress"
            in_progress_task.save()

    def get_json(self):
        user = self.get_user()
        project = self.get_project()
        return {
            "user": user.get_teaser(),
            "project": project.get_teaser(),
            "tasks": [t.get_teaser() for t in self.get_task_activities()],
            "progress": self.get_progress(),
        }

    def get_teaser(self):
        user = self.get_user()
        project = self.get_project()
        return {
            "user": user.get_teaser(),
            "project": project.get_teaser(),
            "progress": self.get_progress(),
        }


@dataclass(kw_only=True)
class TaskActivity(Document):
    _tablename = "task_activity"

    activity_id: int
    task_id: int
    status: str
    checks: list[CheckStatus]

    position: int | None = None
    name: str | None = None
    title: str | None = None

    def __post_init__(self):
        if not self.position or not self.name or not self.title:
            task = self.get_task()
            self.position = task.position
            self.name = task.name
            self.title = task.title

    @classmethod
    def find_all(cls, **kwargs):
        rows = db.where("task_activity_view", **kwargs)
        return [cls._from_db(**row) for row in rows]

    @classmethod
    def _from_db(cls, checks, **kwargs):
        return super()._from_db(
            **kwargs,
            checks=[CheckStatus(**kw) for kw in json.loads(checks)],
        )

    def update_from_input(self, input):
        new_status = get_task_status_from_check_statuses([
            c.status for c in input.checks
        ])
        self.checks = input.checks
        self.status = new_status
        return self

    def _to_db(self):
        d = super()._to_db()
        d.pop("position")
        d.pop("name")
        d.pop("title")
        d["checks"] = json.dumps(d["checks"])
        return d

    def _to_json(self):
        d = super()._to_json()
        return {
            "name": d["name"],
            "title": d["title"],
            "status": d["status"],
            "checks": d["checks"],
        }

    def get_task(self):
        return Task.find(id=self.task_id)

    def get_activity(self):
        return Activity.find(id=self.activity_id)


@dataclass
class TaskActivityInput:
    name: str
    checks: list[CheckStatus]

    @classmethod
    def from_json(cls, name, checks):
        return cls(name=name, checks=[CheckStatus(**kwds) for kwds in checks])


@dataclass
class CheckStatus:
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    ERROR = "error"

    name: str
    status: str
    message: str | None = None

    def get_json(self):
        return asdict(self)


def hash_with_salt(text, salt):
    hash = hashlib.sha256((text + salt).encode()).hexdigest()
    return f"{salt}${hash}"

def check_password(text, hash):
    salt = hash.split("$", maxsplit=1)[0]
    return hash_with_salt(text, salt) == hash

def generate_salt(length=16):
    allowed = string.ascii_letters + string.digits
    return "".join(random.choice(allowed) for _ in range(length))

def get_project_url(name):
    # TODO: take hostname from request
    return f"http://{config.hostname}/api/projects/{name}"

def get_project_html_url(name):
    return f"http://{config.hostname}/projects/{name}"

def get_current_timestamp():
    return datetime.now(tz=timezone.utc)

def get_task_status_from_check_statuses(check_statuses):
    if all(status == CheckStatus.PASS for status in check_statuses):
        return "Completed"
    elif any(status == CheckStatus.FAIL for status in check_statuses):
        return "Failing"
    else:
        return "Pending"

def get_activity_status_from_task_statuses(task_statuses):
    if all(status == "Completed" for status in task_statuses):
        return "Completed"
    else:
        return "In Progress"

def get_zeroth_task_dict(project_id):
    description = """\
Clone this Git repository which contains the starter code.

You'll make progress as you push to this repository with each
task.

```shell
git clone {git_url}
```

To complete this task, make a dummy commit and push to the repo.

```
git commit --allow-empty -m "test"
git push
```
"""

    zeroth_task = {
       "name": "clone-repository",
       "title": "Clone the repository",
       "description": description,
       "position": 0,
       "checks": [],
       "project_id": project_id,
    }

    return zeroth_task

def make_new_project_dir(git_dir, git_user, username, project_name):
    # TODO: use git_user to create users
    random_hash = uuid.uuid4().hex
    repo_path = f"{random_hash}-{username}/{project_name}.git"
    zipfile_path = get_private_file_path(f"projects/{project_name}/repo-git.zip")
    extraction_dir = f"{git_dir}/{repo_path}"
    os.makedirs(extraction_dir, exist_ok=True)
    subprocess.check_call(["unzip", "-d", extraction_dir, os.path.abspath(zipfile_path)])
    return repo_path
