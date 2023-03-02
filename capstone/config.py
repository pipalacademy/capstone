import os

db_uri = "sqlite:///capstone.db"
hostname = "127.0.0.1:5000"  # TODO: remove this
capstone_url = f"http://{hostname}"
git_post_receive_script = os.getenv("CAPSTONE_GIT_POST_RECEIVE_SCRIPT")
git_user = os.getenv("CAPSTONE_GIT_USER")
git_dir = os.getenv("CAPSTONE_GIT_DIR")
git_base_url = os.getenv("CAPSTONE_GIT_BASE_URL")
