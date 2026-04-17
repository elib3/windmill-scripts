
import time
import requests
from typing import TypedDict

try:
    import wmill
    _WMILL_AVAILABLE = True
except ImportError:
    _WMILL_AVAILABLE = False

TOKEN_CACHE_PATH = "f/AzureAD/entra_token_cache"
TOKEN_EXPIRY_BUFFER_SECS = 60


class ms_entra_id(TypedDict):
    tenant_id: str
    client_id: str
    client_secret: str


def get_token(entra: ms_entra_id) -> str:
    """
    Returns a valid Microsoft Graph API access token.
    Caches the token in f/AzureAD/entra_token_cache and reuses it across
    scripts/flow steps until it is within 60s of expiry (~1 hour lifetime).
    """
    if _WMILL_AVAILABLE:
        try:
            cached = wmill.get_resource(TOKEN_CACHE_PATH)
            if (
                isinstance(cached, dict)
                and cached.get("expires_at", 0) > time.time() + TOKEN_EXPIRY_BUFFER_SECS
            ):
                return cached["token"]
        except Exception:
            pass

    resp = requests.post(
        f"https://login.microsoftonline.com/{entra['tenant_id']}/oauth2/v2.0/token",
        data={
            "grant_type": "client_credentials",
            "client_id": entra["client_id"],
            "client_secret": entra["client_secret"],
            "scope": "https://graph.microsoft.com/.default",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    expires_in = data.get("expires_in", 3600)

    if _WMILL_AVAILABLE:
        try:
            wmill.set_resource(
                path=TOKEN_CACHE_PATH,
                value={"token": token, "expires_at": time.time() + expires_in},
                resource_type="state",
            )
        except Exception:
            pass

    return token


def main(entra: ms_entra_id) -> str:
    """Verify credentials and warm the token cache. Safe to run standalone."""
    token = get_token(entra)
    print(f"Token obtained successfully (prefix: {token[:10]}...)")
    print(f"Cached at: {TOKEN_CACHE_PATH}")
    return "OK"
