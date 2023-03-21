import os

from capstone import config


PRIVATE_FILES_DIR = config.private_files_dir


def ensure_private_files_dir():
    os.makedirs(PRIVATE_FILES_DIR, exist_ok=True)


def save_private_file(key, stream):
    ensure_private_files_dir()
    path = f"{PRIVATE_FILES_DIR}/{key}"

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # TODO: maybe safer handling of key?
    with open(path, "wb") as f:
        for data in stream:
            f.write(data)

    return path


def get_private_file(key):
    # TODO: keep only one, maybe the below one with the path
    path = get_private_file_path(key)
    return open(path, "rb")


def get_private_file_path(key):
    return f"{PRIVATE_FILES_DIR}/{key}"
