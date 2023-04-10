import os

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL", "postgres:///capstone")
redis_url = os.getenv("CAPSTONE_REDIS_URL", "redis://localhost:6379/0")

capstone_api_token = os.getenv("CAPSTONE_API_TOKEN", "test123")

git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")
gitto_base_url = os.getenv("CAPSTONE_GITTO_BASE_URL", "http://localhost:8080")
gitto_api_token = os.getenv("CAPSTONE_GITTO_API_TOKEN", "")

data_dir = os.getenv("CAPSTONE_DATA_DIR", "data")

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

capstone_dev = os.getenv("CAPSTONE_DEV", "0") == "1"

runner_docker_image = os.getenv("CAPSTONE_RUNNER_DOCKER_IMAGE", "capstone-runner")
runner_capstone_token = os.getenv("CAPSTONE_RUNNER_CAPSTONE_TOKEN", "test123")
runner_devmode_python_executable = os.getenv("CAPSTONE_RUNNER_DEVMODE_PYTHON_EXECUTABLE", "python3")
