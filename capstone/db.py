from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields as get_fields
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, IO, Type, TypeVar

from web import database
from web.db import SQLLiteral
from psycopg2.extensions import register_adapter
from psycopg2.extras import Json

from . import config
from .utils import files
from .utils import course as course_utils


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

    @classmethod
    def find_or_fail(cls: Type[DocumentT], **filters: Any) -> DocumentT:
        obj = cls.find(**filters)
        if obj is None:
            raise Exception(f"{cls.__name__} not found")
        return obj

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

    def get_projects(
            self,
            id: int | None = None,
            name: str | None = None,
            title: str | None = None,
            is_published: bool | None = None) -> list[Project]:
        filters = remove_none_values(
            {
                "id": id,
                "name": name,
                "title": title,
                "is_published": is_published,
            }
        )
        return Project.find_all(site_id=self.id, **filters)

    def get_project(self, name: str) -> Project | None:
        return Project.find(site_id=self.id, name=name)

    def get_project_or_fail(self, name: str) -> Project:
        project = self.get_project(name=name)
        if project is None:
            raise Exception(f"Project not found: '{name}'")
        return project

    def get_project_by_id(self, id: int) -> Project | None:
        return Project.find(site_id=self.id, id=id)

    def get_project_by_id_or_fail(self, id: int) -> Project:
        project = self.get_project_by_id(id=id)
        if project is None:
            raise Exception(f"Project not found: id={id}")
        return project

    def get_users(
        self,
        id: int | None = None,
        name: str | None = None,
        username: str | None = None,
        email: str | None = None
    ) -> list[User]:
        filters = remove_none_values(
            {
                "id": id,
                "name": name,
                "username": username,
                "email": email,
            }
        )
        return User.find_all(site_id=self.id, **filters)

    def get_user(self, username: str) -> User | None:
        return User.find(site_id=self.id, username=username)

    def get_user_or_fail(self, username: str) -> User:
        user = self.get_user(username=username)
        if user is None:
            raise Exception(f"User not found: '{username}'")
        return user

    def get_user_by_id(self, id: int) -> User | None:
        return User.find(site_id=self.id, id=id)

    def get_user_by_id_or_fail(self, id: int) -> User:
        user = self.get_user_by_id(id=id)
        if user is None:
            raise Exception(f"User not found: id={id}")
        return user

    def get_user_projects(self) -> list[UserProject]:
        user_projects = []
        for user in self.get_users():
            user_projects.extend(user.get_user_projects())
        return user_projects

    def get_user_project_by_id(self, id: int) -> UserProject | None:
        user_project = UserProject.find(id=id)
        if user_project and user_project.get_site().id == self.id:
            return user_project
        else:
            return None

    def get_user_project_by_id_or_fail(self, id: int) -> UserProject:
        user_project = self.get_user_project_by_id(id=id)
        if user_project is None:
            raise Exception(f"UserProject not found: id={id}")
        return user_project

    def get_changelogs(
        self,
        project_id: int | None = None,
        user_id: int | None = None,
        action: str | None = None,
        order: str = "timestamp desc",
    ) -> list[Changelog]:
        assert self.id is not None
        filters = remove_none_values(
            {
                "project_id": project_id,
                "user_id": user_id,
                "action": action,
                "order": order,
            }
        )
        return Changelog.find_all(
            site_id=self.id,
            **filters
        )

    def get_changelog_or_fail(self, id: int) -> Changelog:
        return Changelog.find_or_fail(site_id=self.id, id=id)

    def get_courses(
        self,
        id: int | None = None,
        name: str | None = None,
        title: str | None = None,
    ) -> list[Course]:
        filters = remove_none_values(
            {
                "id": id,
                "name": name,
                "title": title,
            }
        )
        return Course.find_all(site_id=self.id, **filters)

    def get_course(self, name: str) -> Course | None:
        return Course.find(site_id=self.id, name=name)

    def get_course_or_fail(self, name: str) -> Course:
        course = self.get_course(name=name)
        if course is None:
            raise Exception(f"Course not found: '{name}'")
        return course

    def get_url(self) -> str:
        if self.domain == "localhost":
            return f"http://{self.domain}:5000"
        else:
            return f"https://{self.domain}"

    def save_private_file(self, key: str, stream: IO[bytes]) -> None:
        """
        Possible errors:
        - capstone.utils.files.InvalidKey
        - capstone.utils.files.FileNotFound
        """
        assert self.id is not None
        files.save_private_file(key=f"{self.id}/{key}", stream=stream)

    def get_private_file(self, key: str) -> IO[bytes]:
        """
        Possible errors:
        - capstone.utils.files.InvalidKey
        - capstone.utils.files.FileNotFound
        """
        assert self.id is not None
        return files.get_private_file(key=f"{self.id}/{key}")

    def get_private_file_path(self, key: str) -> Path:
        """
        This file should not be edited or deleted.
        Possible errors:
        - capstone.utils.files.InvalidKey
        """
        assert self.id is not None
        return files.get_private_file_path(key=f"{self.id}/{key}")


@dataclass(kw_only=True)
class Project(Document):
    _tablename: ClassVar[str] = "project"
    _teaser_fields = [
        "name", "title", "url", "short_description", "tags", "is_published", "project_type",
    ]
    _detail_fields = [
        "name", "title", "url", "short_description", "description",
        "tags", "is_published", "project_type", "created", "last_modified",
        # "tasks"
        "repo_id", "git_url"
    ]
    _db_fields = [
        "id", "site_id", "name", "title", "short_description", "description",
        "tags", "is_published", "project_type", "created", "last_modified",
        # private:
        "repo_id", "git_url"
    ]

    site_id: int
    name: str
    title: str
    short_description: str
    description: str
    tags: list[str]
    project_type: str  # can be 'web', 'cli'

    is_published: bool | None = None

    repo_id: str | None = None
    git_url: str | None = None

    created: datetime | None = None
    last_modified: datetime | None = None

    url: str | None = field(init=False, default=None)
    html_url: str | None = field(init=False, default=None)

    def __post_init__(self):
        site = self.get_site()
        if site is not None:
            self.url = f"http://{site.domain}/api/projects/{self.name}"
            self.html_url = f"http://{site.domain}/projects/{self.name}"

    def get_url(self) -> str:
        return f"/projects/{self.name}"

    def delete(self) -> int:
        with db.transaction():
            self.delete_tasks()
            return super().delete()

    def get_detail(self) -> dict[str, Any]:
        d = super().get_detail()
        d["tasks"] = [t.get_detail() for t in self.get_tasks()]
        return d

    def get_site(self) -> Site:
        return Site.find_or_fail(id=self.site_id)

    def get_tasks(self) -> list[Task]:
        return Task.find_all(project_id=self.id, order="position")

    def create_task(
            self,
            name: str, title: str, description: str, position: int,
            checks: list[dict[str, Any]] = []) -> Task:
        assert self.id is not None, "can't create task without saving project"
        with db.transaction():
            task = Task(
                name=name, title=title, description=description,
                position=position, project_id=self.id,
            ).save()
            task.update_checks(checks)
        return task

    def update_tasks(self, task_inputs: list[dict[str, Any]]) -> list[Task]:
        assert self.id is not None

        # each element of tasks list has four keys: name, title, description, and checks
        required_fields = ["name", "title", "description", "checks"]
        for task in task_inputs:
            assert all(k in task for k in required_fields), \
                f"task {task} is missing required fields"

        with db.transaction():
            new_tasks = {t["name"]: t for t in task_inputs}
            old_tasks = {t.name: t for t in self.get_tasks()}

            to_delete = [t for t in old_tasks if t not in new_tasks]
            to_create = [t for t in new_tasks if t not in old_tasks]

            for name in to_delete:
                old_tasks[name].delete()

            for i, name in enumerate(new_tasks):
                if name in to_create:
                    self.create_task(
                        position=i,
                        name=name,
                        title=new_tasks[name]["title"],
                        description=new_tasks[name]["description"],
                        checks=new_tasks[name]["checks"],
                    )
                else:
                    old_tasks[name].update(
                        position=i,
                        title=new_tasks[name]["title"],
                        description=new_tasks[name]["description"],
                    ).save().update_checks(new_tasks[name]["checks"])

        return self.get_tasks()

    def delete_tasks(self) -> int:
        count = 0
        for task in self.get_tasks():
            count += task.delete()

        return count

    def get_user_projects(self) -> list[UserProject]:
        return UserProject.find_all(project_id=self.id)

    def get_user_project(self, user_id: int) -> UserProject | None:
        return UserProject.find(user_id=user_id, project_id=self.id)

    def get_user_project_or_fail(self, user_id: int) -> UserProject:
        user_project = self.get_user_project(user_id)
        if user_project is None:
            raise Exception("UserProject not found")
        return user_project

    def get_private_file_key_for_zipball(self) -> str:
        """`utils.files` module should be used with this key.
        """
        return f"projects/{self.name}/repo.zip"

    def get_history(self) -> list[dict[str, Any]]:
        """Return a list of updates for this project.
        """
        updates = self.get_site().get_changelogs(
            project_id=self.id, action="update_project",
        )
        return [
            {
                "timestamp": update.timestamp,
                "status": update.details["status"],
                "log": update.details.get("log", ""),
            }
            for update in updates
        ]

    def publish(self):
        self.is_published = True
        self.save()

    def unpublish(self):
        self.is_published = False
        self.save()

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

    def get_project(self) -> Project:
        return Project.find_or_fail(id=self.project_id)

    def get_site(self) -> Site:
        return self.get_project().get_site()

    def get_url(self) -> str:
        return f"/projects/{self.get_project().name}/tasks/{self.name}"

    def get_detail(self) -> dict[str, Any]:
        d = super().get_detail()
        d["checks"] = [c.get_detail() for c in self.get_checks()]
        return d

    def delete(self) -> int:
        with db.transaction():
            self.delete_checks()
            for task_status in self.get_user_task_statuses():
                task_status.delete()
            return super().delete()

    def get_user_task_statuses(self) -> list[UserTaskStatus]:
        return UserTaskStatus.find_all(task_id=self.id)

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
            new_checks = {HashableCheck(name=t["name"], title=t["title"], args=t["args"]): t for t in check_inputs}
            old_checks = {HashableCheck(name=t.name, title=t.title, args=t.args): t for t in self.get_checks()}

            to_delete = [t for t in old_checks if t not in new_checks]
            to_create = [t for t in new_checks if t not in old_checks]

            for check_hash in to_delete:
                old_checks[check_hash].delete()

            for i, check_hash in enumerate(new_checks):
                check_dict = new_checks[check_hash]
                if check_hash in to_create:
                    check = TaskCheck(
                        name=check_dict["name"],
                        title=check_dict["title"],
                        args=check_dict["args"],
                        task_id=self.id,
                        position=i).save()
                else:
                    check = old_checks[check_hash]
                    check.update(title=check_dict["title"], position=i).save()

        return self.get_checks()

    def render_description(self, vars: dict[str, Any] | None = None) -> str:
        # TODO: maybe use %(...)s instead of formatting? so it doesn't break when keys are not present
        return self.description.format(**vars) if vars is not None else self.description


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

    def delete(self):
        with db.transaction():
            for user_check_status in self.get_user_check_statuses():
                user_check_status.delete()
            return super().delete()

    def get_task(self) -> Task:
        return Task.find_or_fail(id=self.task_id)

    def get_user_check_statuses(self) -> list[UserCheckStatus]:
        return UserCheckStatus.find_all(task_check_id=self.id)


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

    def get_site(self) -> Site:
        return Site.find_or_fail(id=self.site_id)

    def get_user_projects(self) -> list[UserProject]:
        return UserProject.find_all(user_id=self.id)


@dataclass(kw_only=True)
class UserProject(Document):
    _tablename = "user_project"
    _db_fields = ["id", "project_id", "user_id", "git_url", "repo_id", "app_settings", "created", "last_modified"]
    _detail_fields = [
        "git_url", "repo_id", "app_settings", "created", "last_modified",
        # added by hand: "project_name", "username", "app_url"
    ]
    _teaser_fields = [
        "git_url",
        # added by hand: "project_name", "username", "app_url"
    ]

    project_id: int
    user_id: int
    git_url: str
    repo_id: str

    app_settings: dict[str, Any] = field(default_factory=dict)

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_detail(self) -> dict[str, Any]:
        d = super().get_detail()
        d["project_name"] = self.get_project().name
        d["username"] = self.get_user().username
        d["app_url"] = self.get_app_url()
        return d

    def get_teaser(self) -> dict[str, Any]:
        d = super().get_teaser()
        d["project_name"] = self.get_project().name
        d["username"] = self.get_user().username
        d["app_url"] = self.get_app_url()
        return d

    def get_project(self) -> Project:
        return Project.find_or_fail(id=self.project_id)

    def get_user(self) -> User:
        return User.find_or_fail(id=self.user_id)

    def get_site(self) -> Site:
        return self.get_user().get_site()

    def get_context_vars(self) -> dict[str, Any]:
        # TODO: must ensure that the app is deployed before sending app_url
        return {
            "git_url": self.git_url,
            "app_url": self.get_app_url()
            # add app_settings too?
        }

    def get_app_url(self) -> str | None:
        return self.app_settings.get("app_url")

    def set_app_url(self, value: str) -> None:
        self.app_settings["app_url"] = value
        self.save()

    def get_task_statuses(self) -> list[UserTaskStatus]:
        return UserTaskStatus.find_all(user_project_id=self.id)

    def get_task_status(self, task: Task) -> UserTaskStatus | None:
        return UserTaskStatus.find(
            user_project_id=self.id, task_id=task.id)

    def get_in_progress_task_status(self) -> UserTaskStatus | None:
        return UserTaskStatus.find(
            user_project_id=self.id, status="In Progress")

    def update_task_status(self, task: Task, status: str) -> UserTaskStatus:
        assert task.project_id == self.project_id
        assert self.id is not None
        assert task.id is not None
        assert status in ["Pending", "In Progress", "Completed", "Failing"]

        user_task_status = self.get_task_status(task=task)
        if user_task_status is None:
            user_task_status = UserTaskStatus(
                user_project_id=self.id, task_id=task.id, status=status).save()
        else:
            user_task_status.status = status
            user_task_status.save()
        return user_task_status

    def set_in_progress_task(self):
        task_statuses = self.get_task_statuses()
        with db.transaction():
            for task_status, next_status in zip(task_statuses, task_statuses[1:]+[None]):
                if task_status.status == "In Progress":
                    task_status.status = "Pending"
                    task_status.save()

                if (task_status.status in {"Pending", "Failing"} and
                        (not next_status or next_status.status == "Pending")):
                    task_status.status = "In Progress"
                    task_status.save()
                    return

    def get_webhook_url(self) -> str:
        site = self.get_site()
        assert site is not None, "site not found"
        user = self.get_user()
        assert user is not None, "user not found"
        project = self.get_project()
        assert project is not None, "project not found"

        site_url = site.get_url()
        return f"{site_url}/api/users/{user.username}/projects/{project.name}/hook/{self.repo_id}"

    def get_history(self) -> list[dict[str, Any]]:
        """Return a list of updates for this user project.
        """
        updates = self.get_site().get_changelogs(
            project_id=self.project_id,
            user_id=self.user_id,
            action="update_user_project",
        )
        return [
            {
                "timestamp": update.timestamp,
                "status": update.details["status"],
                "log": update.details.get("log", ""),
            }
            for update in updates
        ]


@dataclass(kw_only=True)
class UserTaskStatus(Document):
    _tablename = "user_task_status"
    _db_fields = ["id", "user_project_id", "task_id", "status", "created", "last_modified"]

    user_project_id: int
    task_id: int
    status: str = "Pending"

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_task(self) -> Task | None:
        return Task.find(id=self.task_id)

    def get_user_project(self) -> UserProject:
        return UserProject.find_or_fail(id=self.user_project_id)

    def get_check_statuses(self) -> list[UserCheckStatus]:
        return UserCheckStatus.find_all(user_task_status_id=self.id)

    def get_check_status(self, check: TaskCheck) -> UserCheckStatus | None:
        return UserCheckStatus.find(
            user_task_status_id=self.id, task_check_id=check.id)

    def update_check_status(
        self,
        check: TaskCheck,
        status: str,
        message: str | None = None,
    ) -> UserCheckStatus:
        assert check.task_id == self.task_id
        assert self.id is not None
        assert check.id is not None
        assert status in ["pending", "pass", "fail", "error"]

        user_check_status = self.get_check_status(check=check)
        if user_check_status is None:
            user_check_status = UserCheckStatus(
                user_task_status_id=self.id,
                task_check_id=check.id,
                status=status,
                message=message,
            ).save()
        else:
            user_check_status.update(status=status, message=message)
            user_check_status.save()

        return user_check_status

    def compute_status(self) -> str:
        """Returns one of 'Completed', 'Failing', 'Pending'
        """
        task = self.get_task()
        assert task is not None

        check_statuses = self.get_check_statuses()
        assert len(task.get_checks()) == len(check_statuses), "check statuses are missing"

        if all(cs.status == "pass" for cs in check_statuses):
            return "Completed"
        elif any(cs.status == "fail" or cs.status == "error" for cs in check_statuses):
            return "Failing"
        else:
            return "Pending"


@dataclass(kw_only=True)
class UserCheckStatus(Document):
    _tablename = "user_check_status"
    _db_fields = ["id", "user_task_status_id", "task_check_id", "status", "message", "created", "last_modified"]

    user_task_status_id: int
    task_check_id: int
    status: str = "pending"
    message: str | None = None

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_task_check(self) -> TaskCheck:
        return TaskCheck.find_or_fail(id=self.task_check_id)

    def get_user_task_status(self) -> UserTaskStatus:
        return UserTaskStatus.find_or_fail(id=self.user_task_status_id)


@dataclass(kw_only=True)
class Changelog(Document):
    _tablename = "changelog"
    _db_fields = [
        "id", "site_id", "project_id", "user_id", "action", "timestamp",
        "details"
    ]

    site_id: int
    project_id: int | None = None
    user_id: int | None = None
    action: str
    timestamp: datetime | None = None  # defaults to utcnow in db
    details: dict[str, Any] = field(default_factory=dict)

    def get_site(self) -> Site:
        return Site.find_or_fail(id=self.site_id)

    def get_project(self) -> Project | None:
        if self.project_id is not None:
            return Project.find_or_fail(id=self.project_id)
        else:
            return None

    def get_user(self) -> User | None:
        if self.user_id is not None:
            return User.find_or_fail(id=self.user_id)
        else:
            return None


@dataclass(kw_only=True)
class Course(Document):
    _tablename = "course"
    _teaser_fields = ["name", "title", "description"]
    _detail_fields = ["id", "name", "title", "description", "created", "last_modified"]  # + ["modules"]
    _db_fields = ["id", "site_id", "name", "title", "description", "created", "last_modified"]

    site_id: int
    name: str
    title: str
    description: str | None = None

    created: datetime | None = None
    last_modified: datetime | None = None

    def delete(self):
        with db.transaction():
            for module in self.get_modules():
                module.delete()
            return super().delete()

    def get_detail(self):
        d = super().get_detail()
        d["modules"] = [m.get_detail() for m in self.get_modules()]
        return d

    def get_media_dir(self) -> Path:
        return course_utils.get_media_dir(self)

    def get_lessons_dir(self) -> Path:
        return course_utils.get_lessons_dir(self)

    def get_url(self) -> str:
        return f"/courses/{self.name}"

    def get_site(self) -> Site:
        return Site.find_or_fail(id=self.site_id)

    def get_module(self, name: str) -> Module | None:
        return Module.find(course_id=self.id, name=name)

    def get_module_by_position(self, position: int) -> Module | None:
        return Module.find(course_id=self.id, position=position)

    def get_modules(self) -> list[Module]:
        return Module.find_all(course_id=self.id)

    def update_modules(self, module_inputs: list[dict[str, Any]]) -> list[Module]:
        assert self.id is not None

        required_fields = ["name", "title", "lessons"]
        for module in module_inputs:
            assert all(k in module for k in required_fields), \
                f"module {module} is missing required fields"

        with db.transaction():
            new_modules = {t["name"]: t for t in module_inputs}
            old_modules = {t.name: t for t in self.get_modules()}

            to_delete = [t for t in old_modules if t not in new_modules]
            to_create = [t for t in new_modules if t not in old_modules]

            for name in to_delete:
                old_modules[name].delete()

            for i, name in enumerate(new_modules):
                if name in to_create:
                    self.create_module(
                        position=i,
                        name=name,
                        title=new_modules[name]["title"],
                        lessons=new_modules[name]["lessons"],
                    )
                else:
                    old_modules[name].update(
                        position=i,
                        title=new_modules[name]["title"],
                    ).save().update_lessons(new_modules[name]["lessons"])

        return self.get_modules()

    def create_module(
        self, position: int, name: str, title: str, lessons: list[dict[str, Any]],
    ) -> Module:
        assert self.id is not None, "course must be saved before creating modules"
        with db.transaction():
            module = Module(course_id=self.id, name=name, title=title, position=position)
            module.save().update_lessons(lessons)
        return module


@dataclass(kw_only=True)
class Module(Document):
    _tablename = "module"
    _db_fields = ["id", "course_id", "name", "title", "position", "created", "last_modified"]

    course_id: int
    name: str
    title: str
    position: int

    created: datetime | None = None
    last_modified: datetime | None = None

    def delete(self):
        with db.transaction():
            for lesson in self.get_lessons():
                lesson.delete()
            return super().delete()

    def get_detail(self):
        d = super().get_detail()
        d["lessons"] = [l.get_detail() for l in self.get_lessons()]
        return d

    def get_course(self) -> Course:
        return Course.find_or_fail(id=self.course_id)

    def get_lesson(self, name: str) -> Lesson | None:
        return Lesson.find(module_id=self.id, name=name)

    def get_lesson_by_position(self, position: int) -> Lesson | None:
        return Lesson.find(module_id=self.id, position=position)

    def get_last_lesson(self) -> Lesson | None:
        lessons = self.get_lessons(order="position DESC", limit=1)
        return lessons[0] if lessons else None

    def create_lesson(self, position: int, name: str, title: str, path: str) -> Lesson:
        assert self.id is not None
        return Lesson(module_id=self.id, position=position, name=name, title=title, path=path).save()

    def get_lessons(self, **kwargs) -> list[Lesson]:
        return Lesson.find_all(module_id=self.id, **kwargs)

    def update_lessons(self, lesson_inputs: list[dict[str, Any]]) -> list[Lesson]:
        assert self.id is not None

        required_fields = ["name", "title", "path"]
        for lesson in lesson_inputs:
            assert all(k in lesson for k in required_fields), \
                f"lesson {lesson} is missing required fields"

        with db.transaction():
            new_lessons = {t["name"]: t for t in lesson_inputs}
            old_lessons = {t.name: t for t in self.get_lessons()}

            to_delete = [t for t in old_lessons if t not in new_lessons]
            to_create = [t for t in new_lessons if t not in old_lessons]

            for name in to_delete:
                old_lessons[name].delete()

            for i, name in enumerate(new_lessons):
                if name in to_create:
                    self.create_lesson(
                        position=i,
                        name=name,
                        title=new_lessons[name]["title"],
                        path=new_lessons[name]["path"],
                    )
                else:
                    old_lessons[name].update(
                        position=i,
                        title=new_lessons[name]["title"],
                        path=new_lessons[name]["path"],
                    ).save()

        return self.get_lessons()


@dataclass(kw_only=True)
class Lesson(Document):
    _tablename = "lesson"
    _db_fields = [
        "id", "module_id", "name", "title", "path", "position",
        "created", "last_modified"
    ]

    module_id: int
    name: str
    title: str
    path: str
    position: int

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_module(self) -> Module:
        return Module.find_or_fail(id=self.module_id)

    def get_course(self) -> Course:
        return self.get_module().get_course()

    def get_url(self) -> str:
        course, module = self.get_course(), self.get_module()
        return f"/courses/{course.name}/lessons/{module.name}/{self.name}"

    def get_next(self) -> Lesson | None:
        module = self.get_module()
        if (next_lesson := module.get_lesson_by_position(self.position+1)):
            return next_lesson
        elif (next_module := self.get_course().get_module_by_position(module.position+1)):
            return next_module.get_lesson_by_position(0) or None
        else:
            return None

    def get_prev(self) -> Lesson | None:
        module = self.get_module()
        if (prev_lesson := module.get_lesson_by_position(self.position-1)):
            return prev_lesson
        elif (prev_module := self.get_course().get_module_by_position(module.position-1)):
            return prev_module.get_last_lesson() or None
        else:
            return None

    def get_html(self) -> str:
        return (self.get_course().get_lessons_dir() / self.path).read_text()


@dataclass(kw_only=True)
class UserCourse(Document):
    _tablename = "user_course"
    _db_fields = ["id", "user_id", "course_id", "created", "last_modified"]

    user_id: int
    course_id: int

    created: datetime | None = None
    last_modified: datetime | None = None

    def get_user(self) -> User:
        return User.find_or_fail(id=self.user_id)

    def get_course(self) -> Course:
        return Course.find_or_fail(id=self.course_id)


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


class HashableCheck:
    def __init__(self, name, title, args):
        self.name = name
        self.title = title
        self.args = args

    def __hash__(self):
        return hash(f"{self.name}/{self.args}")

    def __eq__(self, other):
        return hash(self) == hash(other)
