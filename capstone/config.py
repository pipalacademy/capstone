import os

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL", "postgres:///capstone")

hostname = "127.0.0.1:5000"  # TODO: remove this
capstone_url = f"http://{hostname}"
git_post_receive_script = os.getenv("CAPSTONE_GIT_POST_RECEIVE_SCRIPT")
git_user = os.getenv("CAPSTONE_GIT_USER")
git_dir = os.getenv("CAPSTONE_GIT_DIR")
git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")

tasks_dir = os.getenv("CAPSTONE_TASKS_DIR") or "tasks"

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
