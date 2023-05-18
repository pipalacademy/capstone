import os
from pathlib import Path

# TODO: rename to database_url or DATABASE_URL
db_uri = os.getenv("DATABASE_URL", "postgres:///capstone")
redis_url = os.getenv("CAPSTONE_REDIS_URL", "redis://localhost:6379/0")

capstone_api_token = os.getenv("CAPSTONE_API_TOKEN", "test123")

gitto_base_url = os.getenv("CAPSTONE_GITTO_BASE_URL", "http://localhost:7878")
gitto_api_token = os.getenv("CAPSTONE_GITTO_API_TOKEN", "gitto")

data_dir = os.getenv("CAPSTONE_DATA_DIR", "data")

docker_registry = os.getenv("CAPSTONE_DOCKER_REGISTRY", "localhost:7979")

# Set this to disable multi-tenancy and always use this site
default_site = os.getenv("CAPSTONE_DEFAULT_SITE", "")


# Default Google OAuth Credentials, works only for internal users of Pipal Academy
DEFAULT_GOOGLE_OAUTH_CLIENT_ID = "184068666662-6f05u07212f7s86vueaba15uihkprmui.apps.googleusercontent.com"
DEFAULT_GOOGLE_OAUTH_CLIENT_SECRET = "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"

google_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID") or DEFAULT_GOOGLE_OAUTH_CLIENT_ID
google_client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") or DEFAULT_GOOGLE_OAUTH_CLIENT_SECRET

capstone_dev = os.getenv("CAPSTONE_DEV", "0") == "1"
capstone_test = os.getenv("CAPSTONE_TEST", "0") == "1"

runner_docker_image = os.getenv("CAPSTONE_RUNNER_DOCKER_IMAGE", "capstone-runner")
runner_capstone_token = os.getenv("CAPSTONE_RUNNER_CAPSTONE_TOKEN", "test123")
runner_devmode_python_executable = os.getenv(
    "CAPSTONE_RUNNER_DEVMODE_PYTHON_EXECUTABLE",
    str(Path(__file__).parent.parent / "venv" / "bin" / "python3")
)

app_url_hostname_template = os.getenv(
    "CAPSTONE_APP_URL_HOSTNAME_TEMPLATE",
    "{username}-{project_name}.local.pipal.in"
)
app_url_scheme = os.getenv("CAPSTONE_APP_URL_SCHEME", "http")

copyright_owner = os.getenv("CAPSTONE_COPYRIGHT_OWNER", "Pipal Academy LLP")
github_repository = os.getenv(
    "CAPSTONE_GITHUB_REPOSITORY", "https://github.com/pipalacademy/capstone")
