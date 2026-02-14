import msal
import os
from pathlib import Path
from .constants import SCOPES


def initialize_app(client_id: str, cache_path: Path, config_path: Path):
    cache = msal.SerializableTokenCache()
    cache_file = cache_path / "cache.json"
    config_file = config_path / "config.yaml"
    if cache_file.exists():
        cache.deserialize(cache_file.read_text())
    if config_file.exists():
        # load config into variables

    app = msal.PublicClientApplication(
        client_id,
        authority="https://login.microsoftonline.com/common",
        token_cache=cache,
    )

    account: str | None = app.get_accounts()[0] if app.get_accounts() else None

    return app, account, cache


def get_access_token(
    app: msal.PublicClientApplication, account: str, cache: msal.SerializableTokenCache
):
    r = app.acquire_token_silent(SCOPES, account)
    if not r:
        r = app.acquire_token_interactive(SCOPES)

    return r["access_token"]
