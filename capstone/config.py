import os

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL", "postgres:///capstone")

git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")
git_root_directory = os.getenv("CAPSTONE_GIT_ROOT_DIRECTORY")
git_post_receive_token = os.getenv("CAPSTONE_GIT_POST_RECEIVE_TOKEN")

tasks_dir = os.getenv("CAPSTONE_TASKS_DIR") or "tasks"

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
