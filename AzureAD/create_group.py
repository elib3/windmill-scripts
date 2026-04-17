import re
import requests
from typing import Optional
from f.AzureAD.auth import ms_entra_id, get_token


def _resolve_user_id(email: str, token: str) -> str:
    """Resolve a user email/UPN to their object ID."""
    resp = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{email}",
        headers={"Authorization": f"Bearer {token}"},
        params={"$select": "id,displayName"},
        timeout=15,
    )
    if resp.status_code == 404:
        raise ValueError(f"Owner '{email}' not found in Entra ID.")
    resp.raise_for_status()
    data = resp.json()
    print(f"Owner resolved: {data['displayName']} ({data['id']})")
    return data["id"]


def _mail_nickname(display_name: str) -> str:
    """Derive a valid mail nickname from the group display name."""
    slug = re.sub(r"[^a-zA-Z0-9]", "", display_name)
    return slug[:64] or "group"


def main(
    entra: ms_entra_id,
    display_name: str,
    description: str,
    owner_email: Optional[str] = None,
) -> dict:
    """
    Create a security group in Entra ID.

    Args:
        display_name: Name of the group (must be unique in the tenant)
        description: Purpose or description of the group
        owner_email: UPN/email of the user to set as group owner (optional)

    Returns:
        {"created": True, "group_id": "...", "display_name": "...", ...}

    Required Graph API permissions:
        Group.Create (or Group.ReadWrite.All), User.Read.All (if owner_email is used)
    """
    token = get_token(entra)

    payload: dict = {
        "displayName": display_name,
        "description": description,
        "mailEnabled": False,
        "mailNickname": _mail_nickname(display_name),
        "securityEnabled": True,
    }

    if owner_email:
        owner_id = _resolve_user_id(owner_email, token)
        # owners@odata.bind sets the owner atomically at creation time
        payload["owners@odata.bind"] = [
            f"https://graph.microsoft.com/v1.0/directoryObjects/{owner_id}"
        ]

    resp = requests.post(
        "https://graph.microsoft.com/v1.0/groups",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    group = resp.json()

    print(f"Group created: {group['displayName']} ({group['id']})")
    if owner_email:
        print(f"Owner set: {owner_email}")

    return {
        "created": True,
        "group_id": group["id"],
        "display_name": group["displayName"],
        "description": group.get("description"),
        "owner_email": owner_email,
    }
