from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields as get_fields
from datetime import datetime
from typing import Any, ClassVar, Type, TypeVar

from web import database
from web.db import SQLLiteral

from . import config


db = database(config.db_uri)


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

    def get_site(self) -> Site | None:
        return Site.find(id=self.site_id)


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
