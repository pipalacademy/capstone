import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL")

capstone_api_token = os.getenv("CAPSTONE_API_TOKEN")

git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")
git_post_receive_token = os.getenv("CAPSTONE_GIT_POST_RECEIVE_TOKEN")
gito_base_url = os.getenv("CAPSTONE_GITO_BASE_URL", "")
gito_api_token = os.getenv("CAPSTONE_GITO_API_TOKEN", "")

private_files_dir = os.getenv("CAPSTONE_PRIVATE_FILES_DIR")

tasks_dir = os.getenv("CAPSTONE_TASKS_DIR")

deployment_root = os.getenv("CAPSTONE_DEPLOYMENT_ROOT")

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

project_template_dir = str(
    Path(__file__).parent.parent / "cookiecutter-capstone-project"
)
