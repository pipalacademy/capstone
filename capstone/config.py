import os


_app_root = os.environ.get("APP_ROOT")

db_path = f"{_app_root}/private/capstone.db" if _app_root else "capstone.db"
db_uri = f"sqlite:///{db_path}"

github_client_id = os.environ.get("GITHUB_CLIENT_ID", "")
github_client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "")

secret_key = "development"
