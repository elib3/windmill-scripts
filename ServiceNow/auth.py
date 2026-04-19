
import time
import requests
from typing import TypedDict

try:
    import wmill
    _WMILL_AVAILABLE = True
except ImportError:
    _WMILL_AVAILABLE = False

TOKEN_CACHE_PATH = "f/ServiceNow/snow_token_cache"
TOKEN_EXPIRY_BUFFER_SECS = 60


class servicenow(TypedDict):
    instance_url: str
    client_id: str
    client_secret: str
    username: str
    password: str


def get_token(snow: servicenow) -> str:
    """
    Returns a valid ServiceNow access token.
    Caches the token in f/ServiceNow/snow_token_cache and reuses it until
    it is within 60s of expiry (default lifetime is 30 minutes).
    Uses OAuth2 Resource Owner Password Credentials grant.
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
        f"{snow['instance_url'].rstrip('/')}/oauth_token.do",
        data={
            "grant_type": "password",
            "client_id": snow["client_id"],
            "client_secret": snow["client_secret"],
            "username": snow["username"],
            "password": snow["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"ServiceNow OAuth error: {data['error']} — {data.get('error_description', '')}")

    token = data["access_token"]
    expires_in = data.get("expires_in", 1800)

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


def main(snow: servicenow) -> str:
    """Verify credentials and warm the token cache. Safe to run standalone."""
    token = get_token(snow)
    print(f"Token obtained successfully (prefix: {token[:10]}...)")
    print(f"Cached at: {TOKEN_CACHE_PATH}")
    return "OK"
