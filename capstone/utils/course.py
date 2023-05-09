from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from pydantic import BaseModel

from capstone import config, db


class LessonSpec(BaseModel):
    """Lesson specification.
    """
    name: str
    title: str
    path: str

class ModuleSpec(BaseModel):
    """Module specification.
    """
    name: str
    title: str
    lessons: list[LessonSpec]

class CourseFileSpec(BaseModel):
    """Course file specification.
    """
    name: str
    title: str
    description: str
    modules: list[ModuleSpec]

def validate_course_package(path: Path):
    metadata_file = path / "metadata.json"
    metadata = json.loads(metadata_file.read_text())

    if metadata.get("kind") != "course":
        raise ValueError("Not a course package")
    if metadata.get("version") > "0.1":
        raise ValueError("Unsupported course package version")
    if not (path / "contents").is_dir():
        raise ValueError("Missing contents directory")

def load_from_package(site: db.Site, path: os.PathLike, overwrite: bool = True) -> db.Course:
    """Loads course from package directory.
    """
    path = Path(os.fspath(path))
    validate_course_package(path)

    contents_path = path / "contents"
    course_file = contents_path / "course.json"

    course_def = CourseFileSpec.parse_file(course_file)

    with db.db.transaction():
        course = db.Course.find(name=course_def.name)
        if course is None:
            course = db.Course(
                site_id=site.id,
                name=course_def.name,
                title=course_def.title,
                description=course_def.description
            ).save()
        elif not overwrite:
            raise ValueError("Course already exists")
        else:
            course.update(title=course_def.title, description=course_def.description).save()

        course.update_modules([m.dict() for m in course_def.modules])

        course_dir = get_course_dir(course)
        update_course_dir(course_dir=course_dir, contents_dir=contents_path)

    return course


def update_course_dir(course_dir: Path, contents_dir: Path):
    # first copy to temporary directory
    # then, if it succeeds, rename temporary directory to course_dir
    # this makes sure we don't lose old data if something fails midway
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        if (contents_dir / "lessons").is_dir():
            shutil.copytree(contents_dir / "lessons", tmp_path / "lessons")
        else:
            (tmp_path / "lessons").mkdir()

        if (contents_dir / "media").is_dir():
            shutil.copytree(contents_dir / "media", tmp_path / "media")
        else:
            (tmp_path / "media").mkdir()

        if course_dir.is_dir():
            shutil.rmtree(course_dir)

        shutil.move(tmp_path, course_dir)


def get_media_dir(course: db.Course) -> Path:
    return get_course_dir(course) / "media"


def get_lessons_dir(course: db.Course) -> Path:
    return get_course_dir(course) / "lessons"


def get_course_dir(course: db.Course) -> Path:
    return get_site_courses_dir(course.get_site()) / course.name


def get_site_courses_dir(site: db.Site) -> Path:
    return Path(config.data_dir) / "courses" / site.name
