import msal
from config.constants import CACHE_NAME


def update_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        with open(CACHE, "w+") as f:
            f.write(cache.serialize())
