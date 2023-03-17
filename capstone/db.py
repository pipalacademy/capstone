from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields as get_fields
from datetime import datetime
from typing import Any, ClassVar, Type, TypeVar

from web import database
from web.db import SQLLiteral
from psycopg2.extensions import register_adapter
from psycopg2.extras import Json

from . import config


db = database(config.db_uri)
register_adapter(dict, Json)


DocumentT = TypeVar("DocumentT", bound="Document")

CURRENT_TIMESTAMP = SQLLiteral("CURRENT_TIMESTAMP at time zone 'utc'")


@dataclass(kw_only=True)
class Document:
    _tablename: ClassVar[str] = ""
    _teaser_fields: ClassVar[list[str]] = []
    _detail_fields: ClassVar[list[str]] = []
    _db_fields: ClassVar[list[str]] = []

    id: int | None = None

    @classmethod
    def find_all(cls: Type[DocumentT], **filters: Any) -> list[DocumentT]:
        rows = find_all(cls._tablename, **filters)
        return [cls.from_db(row) for row in rows]

    @classmethod
    def find(cls: Type[DocumentT], **filters: Any) -> DocumentT | None:
        row = find(cls._tablename, **filters)
        return row and cls.from_db(row) or None

    def update(self: DocumentT, **fields: Any) -> DocumentT:
        self.__dict__.update(**fields)
        return self

    def save(self: DocumentT) -> DocumentT:
        field_names = get_fields(self)
        fields = self.to_db()
        if "last_modified" in field_names:
            fields.update({"last_modified": CURRENT_TIMESTAMP})
        id = int(save(self._tablename, **fields))
        self.refresh(id=id)
        return self

    def refresh(self: DocumentT, id: int | None = None) -> DocumentT:
        id = id if id is not None else self.id
        fresh = self.__class__.find(id=id)
        assert fresh is not None
        return self.update(**fresh.get_dict())

    def delete(self: DocumentT) -> int:
        return delete(self._tablename, id=self.id)

    # generic get_dict

    def get_dict(self: DocumentT) -> dict[str, Any]:
        return asdict(self)

    # db<->model serialization

    @classmethod
    def from_db(cls: Type[DocumentT], db_repr: dict[str, Any]) -> DocumentT:
        return cls(**db_repr)

    def to_db(self: DocumentT) -> dict[str, Any]:
        d = self.get_dict()
        return remove_none_values({
            k: d[k] for k in self._db_fields
        })

    # model<->json-api serialization

    def _serialize(self: DocumentT, fields: list[str]) -> dict[str, Any]:
        d = self.get_dict()
        return {k: sanitize_value(d[k]) for k in fields}

    def get_teaser(self: DocumentT) -> dict[str, Any]:
        return self._serialize(fields=self._teaser_fields)

    def get_detail(self: DocumentT) -> dict[str, Any]:
        return self._serialize(fields=self._detail_fields)


@dataclass(kw_only=True)
class Site(Document):
    _tablename: ClassVar[str] = "site"
    _db_fields = ["name", "title", "domain"]

    name: str
    title: str
    domain: str

    created: datetime | None = None
    last_modified: datetime | None = None


@dataclass(kw_only=True)
class Project(Document):
    _tablename: ClassVar[str] = "project"
    _teaser_fields = [
        "name", "title", "url", "short_description", "tags", "is_published"
    ]
    _detail_fields = [
        "name", "title", "url", "short_description", "description",
        "tags", "is_published", "created", "last_modified",
        # "tasks"
    ]
    _db_fields = [
        "id", "site_id", "name", "title", "short_description", "description",
        "tags", "is_published", "created", "last_modified",
    ]

    site_id: int
    name: str
    title: str
    short_description: str
    description: str
    tags: list[str]

    is_published: bool | None = None

    created: datetime | None = None
    last_modified: datetime | None = None

    url: str | None = field(init=False, default=None)
    html_url: str | None = field(init=False, default=None)

    def __post_init__(self):
        site = self.get_site()
        if site is not None:
            self.url = f"http://{site.domain}/api/projects/{self.name}"
            self.html_url = f"http://{site.domain}/projects/{self.name}"

    def delete(self) -> int:
        with db.transaction():
            self.delete_tasks()
            return super().delete()

    def get_detail(self) -> dict[str, Any]:
        d = super().get_detail()
        d["tasks"] = [t.get_detail() for t in self.get_tasks()]
        return d

    def get_site(self) -> Site | None:
        return Site.find(id=self.site_id)

    def get_tasks(self) -> list[Task]:
        return Task.find_all(project_id=self.id, order="position")

    def update_tasks(self, task_inputs: list[dict[str, Any]]) -> list[Task]:
        assert self.id is not None

        # each element of tasks list has three keys: name, title, description
        required_fields = ["name", "title", "description", "checks"]

        with db.transaction():
            # remove previous tasks, then add new tasks
            for old_task in self.get_tasks():
                old_task.delete()

            tasks = []
            for (i, task_dict) in enumerate(task_inputs, start=0):
                for field_name in required_fields:
                    assert field_name in task_dict, f"task: '{field_name}' is required"
                task = Task(
                    name=task_dict["name"],
                    title=task_dict["title"],
                    description=task_dict["description"],
                    project_id=self.id,
                    position=i).save()
                task.update_checks(task_dict["checks"])
                tasks.append(task)

        return tasks

    def delete_tasks(self) -> int:
        count = 0
        for task in self.get_tasks():
            count += task.delete()

        return count

    def get_user_project(self, user_id: int) -> UserProject | None:
        return UserProject.find(user_id=user_id, project_id=self.id)


@dataclass(kw_only=True)
class Task(Document):
    _tablename = "task"
    _db_fields = [
            "id", "project_id", "position", "name", "title", "description"]
    _teaser_fields = ["name", "title", "description"]
    _detail_fields = ["name", "title", "description"]

    project_id: int
    position: int
    name: str
    title: str
    description: str

    def get_project(self) -> Project | None:
        return Project.find(id=self.project_id)

    def get_site(self) -> Site | None:
        return (project := self.get_project()) and project.get_site() or None

    def get_detail(self) -> dict[str, Any]:
        d = super().get_detail()
        d["checks"] = [c.get_detail() for c in self.get_checks()]
        return d

    def delete(self) -> int:
        with db.transaction():
            self.delete_checks()
            return super().delete()

    def delete_checks(self) -> int:
        count = 0
        for check in self.get_checks():
            count += check.delete()

        return count

    def get_checks(self) -> list[TaskCheck]:
        return TaskCheck.find_all(task_id=self.id)

    def update_checks(
            self, check_inputs: list[dict[str, Any]]) -> list[TaskCheck]:
        assert self.id is not None, "task must be saved before adding checks"

        # each element of checks list has three keys: name, title, args
        required_fields = ["name", "title", "args"]

        with db.transaction():
            # remove previous checks, then add new checks
            for old_check in self.get_checks():
                old_check.delete()

            checks = []
            for (i, check_dict) in enumerate(check_inputs, start=0):
                for field_name in required_fields:
                    assert field_name in check_dict
                check = TaskCheck(
                    name=check_dict["name"],
                    title=check_dict["title"],
                    args=check_dict["args"],
                    task_id=self.id,
                    position=i).save()
                checks.append(check)

        return checks

    def render_description(self, vars: dict[str, Any]) -> str:
        return self.description.format(**vars)


@dataclass(kw_only=True)
class TaskCheck(Document):
    _tablename = "task_check"
    _db_fields = ["id", "task_id", "position", "name", "title", "args"]
    _teaser_fields = ["name", "title", "args"]
    _detail_fields = ["name", "title", "args"]

    task_id: int
    position: int
    name: str
    title: str
    args: dict[str, Any]

    def get_task(self) -> Task | None:
        return Task.find(id=self.task_id)


@dataclass(kw_only=True)
class User(Document):
    _tablename = "user_account"
    _db_fields = [
        "id", "site_id", "username", "email", "full_name", "enc_password",
        "created", "last_modified"]
    _teaser_fields = ["username", "email", "full_name"]
    _detail_fields = [
        "username", "email", "full_name", "created", "last_modified"]

    site_id: int
    username: str
    email: str
    full_name: str
    enc_password: str | None = None

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_site(self) -> Site | None:
        return Site.find(id=self.site_id)


@dataclass(kw_only=True)
class UserProject(Document):
    _tablename = "user_project"

    project_id: int
    user_id: int
    git_url: str

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_project(self) -> Project | None:
        return Project.find(id=self.project_id)

    def get_user(self) -> User | None:
        return User.find(id=self.user_id)


# db queries

def find_all(table_name: str, **filters: Any) -> list[dict]:
    rows = db.where(table_name, **filters)
    return [dict(row) for row in rows]


def find(table_name: str, **filters: Any) -> dict | None:
    rows = find_all(table_name, **filters, limit=1)
    return rows and rows[0] or None


def save(table_name: str, _pk_field: str = "id", **fields: Any) -> Any:
    id = fields.pop(_pk_field, None)
    if id is not None:
        db.update(
            table_name, where=f"{_pk_field}=$id", vars={"id": id}, **fields)
    else:
        id = db.insert(table_name, **fields)

    return id


def delete(table_name: str, *, _pk_field="id", id: Any) -> int:
    return int(db.delete(table_name, where="id=$id", vars={"id": id}))

# NOTE: maybe add a method to delete_all with filters?


# utilities

def sanitize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    else:
        return value


def remove_none_values(d: dict) -> dict:
    return {
        k: v for k, v in d.items() if v is not None
    }
