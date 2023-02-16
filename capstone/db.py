from __future__ import annotations

import hashlib
import json
import string
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import web

from . import config

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
        return d

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
        # TODO: implement this
        ...

    def get_tasks(self):
        return self.id and Task.find_all(project_id=self.id) or []


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
        started_activity = Activity.find_all(username=self.username)
        started_projects = [
            activity.project_name for activity in started_activity
        ]
        return project_name in started_projects


@dataclass(kw_only=True)
class Task(Document):
    _tablename = "tasks"

    name: str
    title: str
    description: str
    position: int
    checks: list[Check]

    project_id: int

    def _to_json(self):
        d = super()._to_json()
        d.pop("project_id")
        d.pop("checks")
        return d

    @classmethod
    def _from_db(cls, checks, **kwargs):
        return super()._from_db(
            **kwargs,
            checks=[Check(**kw) for kw in json.loads(checks)],
        )

    def _to_db(self):
        d = super()._to_db()
        d["checks"] = json.dumps([c.get_json() for c in d["checks"]])
        return d

    def get_teaser(self):
        return {
            "name": self.name,
        }


@dataclass
class Check:
    name: str
    args: dict[str, Any]  # json

    def get_json(self):
        return asdict(self)


@dataclass(kw_only=True)
class Activity(Document):
    _tablename = "activity"

    username: str
    project_name: str

    def get_user(self):
        return User.find(username=self.username)

    def get_project(self):
        return Project.find(name=self.project_name)

    def get_tasks(self):
        return TaskActivity.find_all(activity_id=self.id)

    def update_tasks(self, tasks):
        # TODO: implement this
        ...

    def get_json(self):
        user = self.get_user()
        project = self.get_project()
        return {
            "user": user.get_teaser(),
            "project": project.get_teaser(),
            # TODO: add progress and tasks keys
        }

    def get_teaser(self):
        user = self.get_user()
        project = self.get_project()
        return {
            "user": user.get_teaser(),
            "project": project.get_teaser(),
            # TODO: add progress key
        }


@dataclass(kw_only=True)
class TaskActivity(Document):
    _tablename = "task_activity"

    activity_id: int
    task_id: int
    status: str
    checks: list[CheckStatus]

    @classmethod
    def _from_db(self, checks, **kwargs):
        return super()._from_db(
            **kwargs,
            checks=[CheckStatus(**kw) for kw in json.loads(checks)],
        )

    def _to_db(self):
        d = super()._to_db()
        d["checks"] = json.dumps(d["checks"])
        return d


@dataclass
class CheckStatus:
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    ERROR = "error"

    name: str
    title: str
    status: str
    message: str

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
    return f"http://{config.hostname}/api/projects/{name}"

def get_project_html_url(name):
    return f"http://{config.hostname}/projects/{name}"

def get_current_timestamp():
    return datetime.now(tz=timezone.utc)
