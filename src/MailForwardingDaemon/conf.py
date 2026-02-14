from config.constants import DATA_NAME, APP_NAME
import json
import os
from platformdirs import PlatformDirs

def load_config():
    dirs = PlatformDirs("MailForwardingDaemon")
    config_dir = dirs.user_config_path
    config_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = dirs.user_cache_path
    cache_dir.mkdir(parents=True, exist_ok=True)


    dir = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
    os.makedirs(dir, exist_ok=True)
    try:
        with open(os.path.join(dir, DATA_NAME), "r") as f:
            app_data = json.load(f)
        