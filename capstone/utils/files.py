"""Files module.

Thin abstraction over the filesystem to store private files.

Primary function of this module is to provide basic security such as
not allowing relative paths in keys and making sure files are only
written within the designated private directory.
"""
import re
from pathlib import Path
from typing import IO

from capstone import config


PRIVATE_FILES_DIR = Path(config.data_dir) / "private"

# only allow ascii letters, numbers, spaces, and these chars: -_./
key_pattern = re.compile(r"^[a-zA-Z0-9\-\_\.\/ ]+$")


class FilesException(Exception):
    pass


class FileNotFound(FilesException):
    pass


class InvalidKey(FilesException):
    pass


def ensure_private_files_dir():
    PRIVATE_FILES_DIR.mkdir(parents=True, exist_ok=True)


def save_private_file(key: str, stream: IO[bytes]) -> Path:
    ensure_private_files_dir()
    validate_key(key)

    path = get_private_file_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        for data in stream:
            f.write(data)

    return path


def get_private_file(key: str) -> IO[bytes]:
    # TODO: keep only one? maybe the below one with the path
    path = get_private_file_path(key)

    if not path.exists():
        raise FileNotFound(f"Private file not found: {key}")
    return open(path, "rb")


def get_private_file_path(key: str) -> Path:
    validate_key(key)
    return PRIVATE_FILES_DIR / key


def validate_key(key: str) -> None:
    if not key:
        raise InvalidKey("Key is empty")

    if ".." in Path(key).parts:
        raise InvalidKey("Key cannot contain relative paths")

    if key.startswith("/"):
        raise InvalidKey("Key cannot start with /")

    if key.startswith("."):
        raise InvalidKey("Key cannot start with .")

    if not key_pattern.match(key):
        raise InvalidKey("Key contains invalid characters")
