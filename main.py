import json
import msal
import requests
import time
import os


def main():
    cache = msal.SerializableTokenCache()

    if os.path.exists(CACHE_PATH):
        cache.deserialize(open(CACHE_PATH, "r").read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/common",
        token_cache=cache,
    )

    account: str | None = app.get_accounts()[0] if app.get_accounts() else None

    delta_link: str = startup(app, account, cache)

    while True:
        forward_msgs(app, account, cache, delta_link)
        time.sleep(30)


def startup(
    app: msal.PublicClientApplication,
    account: str | None,
    cache: msal.SerializableTokenCache,
):
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = None

    if account and data:
        print("Cache exists, pulling from existing cache")
        r = app.acquire_token_silent(SCOPES, account=account)
        if not r:
            r = app.acquire_token_interactive(SCOPES)
        token = r["access_token"]
        delta_link = data["delta_link"]
    else:
        print("No cache exists, fetching new delta link")
        r = app.acquire_token_interactive(SCOPES)
        token = r["access_token"]
        delta_link = get_delta_link(token)
        time.sleep(30)

    with open(DATA_PATH, "w+") as f:
        print(f"writing link to {DATA_PATH}")
        json.dump({"delta_link": delta_link}, f)

    with open(CACHE_PATH, "w+") as f:
        print(f"writing data to cache at {CACHE_PATH}")
        f.write(cache.serialize())

    print("returning delta link")
    return delta_link


## for startup: interactive token, get initial link
def get_delta_link(token: str) -> str:
    headers = {"Authorization": f"Bearer {token}", "Prefer": "odata.maxpagesize=500"}
    params = {
        "changeType": "created",
        "orderby": "receivedDateTime desc",
        "select": ["id", "subject", "receivedDateTime"],
    }
    for pg in iter_pages(
        "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages/delta",
        headers,
        params,
    ):
        result = pg

    return result["@odata.deltaLink"]


def iter_pages(link: str, headers: dict, params: dict | None = None):
    while link:
        response = requests.get(link, headers=headers, params=params)
        response.raise_for_status()
        link = response.json().get("@odata.nextLink")
        print("yielding page")
        yield response.json()


def forward(msg: dict, session: requests.Session, headers: dict, recipient: str):
    session.post(
        f"https://graph.microsoft.com/v1.0/me/messages/{msg['id']}/forward",
        json={"toRecipients": [{"emailAddress": {"address": recipient}}]},
        headers=headers,
    ).raise_for_status()


def forward_msgs(
    app: msal.PublicClientApplication,
    account: str | None,
    cache: msal.SerializableTokenCache,
    delta_link: str,
):
    r = app.acquire_token_silent(SCOPES, account=account)
    if not r:
        r = app.acquire_token_interactive(SCOPES)
    headers = {
        "Authorization": f"Bearer {r['access_token']}",
        "Prefer": "odata.maxpagesize=50",
    }
    print("creating request session")
    with requests.Session() as s:
        for pg in iter_pages(delta_link, headers):
            for msg in pg["value"]:
                forward(
                    msg,
                    s,
                    headers={"Authorization": f"Bearer {r['access_token']}"},
                    recipient="logana2005@aol.com",
                )

    delta_link = pg["@odata.deltaLink"]

    with open(DATA_PATH, "w+") as f:
        json.dump({"delta_link": delta_link}, f)

    if cache.has_state_changed:
        with open(CACHE_PATH, "w+") as f:
            f.write(cache.serialize())


"""
Steps:
    Create app object
    Get token via interactive
    Call delta endpoint
"""


if __name__ == "__main__":
    main()
