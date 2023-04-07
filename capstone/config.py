import os
from pathlib import Path

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL", "postgres:///capstone")

capstone_api_token = os.getenv("CAPSTONE_API_TOKEN", "test123")

git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")
git_post_receive_token = os.getenv("CAPSTONE_GIT_POST_RECEIVE_TOKEN")
gito_base_url = os.getenv("CAPSTONE_GITO_BASE_URL", "http://localhost:8080")
gito_api_token = os.getenv("CAPSTONE_GITO_API_TOKEN", "")

private_files_dir = os.getenv("CAPSTONE_PRIVATE_FILES_DIR", "private")

tasks_dir = os.getenv("CAPSTONE_TASKS_DIR") or "tasks"

deployment_root = os.getenv("CAPSTONE_DEPLOYMENT_ROOT", "deployment")

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

project_template_dir = str(
    Path(__file__).parent.parent / "cookiecutter-capstone-project"
)

runner_docker_image = os.getenv("CAPSTONE_RUNNER_DOCKER_IMAGE", "capstone-runner")
runner_capstone_token = os.getenv("CAPSTONE_RUNNER_CAPSTONE_TOKEN", "test123")
