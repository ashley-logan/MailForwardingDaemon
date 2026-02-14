# src/MailForwadingDaemon/startup.py

from platformdirs import PlatformDirs
from .constants import APP_NAME


dirs = PlatformDirs(APP_NAME)


def create_dirs():
    dirs.user_cache_path.mkdir(parents=True, exist_ok=True)
    dirs.user_config_path.mkdir(parents=True, exist_ok=True)
