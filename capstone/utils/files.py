import os


PRIVATE_FILES_DIR = "private"


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
    path = f"{PRIVATE_FILES_DIR}/{key}"
    return open(path, "rb")
