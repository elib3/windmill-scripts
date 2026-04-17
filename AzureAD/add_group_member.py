import re
import requests
from f.AzureAD.auth import ms_entra_id, get_token

_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _resolve_group_id(group: str, token: str) -> str:
    if _GUID_RE.match(group):
        return group
    resp = requests.get(
        "https://graph.microsoft.com/v1.0/groups",
        headers={"Authorization": f"Bearer {token}"},
        params={"$filter": f"displayName eq '{group}'", "$select": "id,displayName"},
        timeout=15,
    )
    resp.raise_for_status()
    groups = resp.json().get("value", [])
    if not groups:
        raise ValueError(f"Group '{group}' not found.")
    if len(groups) > 1:
        matches = [f"{g['displayName']} ({g['id']})" for g in groups]
        raise ValueError(f"Multiple groups match '{group}': {matches}. Use the object ID.")
    return groups[0]["id"]


def _resolve_user_id(user: str, token: str) -> str:
    """Resolve email, UPN, or object ID to a user object ID."""
    if _GUID_RE.match(user):
        return user
    # UPN and email both work directly on the users endpoint
    resp = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user}",
        headers={"Authorization": f"Bearer {token}"},
        params={"$select": "id,displayName,userPrincipalName"},
        timeout=15,
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"User resolved: {data['displayName']} ({data['id']})")
        return data["id"]
    # Fallback: filter by mail (handles cases where email != UPN)
    resp2 = requests.get(
        "https://graph.microsoft.com/v1.0/users",
        headers={"Authorization": f"Bearer {token}"},
        params={"$filter": f"mail eq '{user}'", "$select": "id,displayName"},
        timeout=15,
    )
    resp2.raise_for_status()
    users = resp2.json().get("value", [])
    if not users:
        raise ValueError(f"User '{user}' not found in Entra ID.")
    data = users[0]
    print(f"User resolved: {data['displayName']} ({data['id']})")
    return data["id"]


def main(
    entra: ms_entra_id,
    group: str,
    user: str,
) -> dict:
    """
    Add a single user to an Entra ID group.

    Args:
        group: Group object ID (GUID) or exact displayName
        user: User object ID, UPN, or email address

    Returns:
        {"added": True, "group_id": "...", "user_id": "..."}
        {"added": False, "already_member": True, ...} if already in group

    Required Graph API permissions:
        GroupMember.ReadWrite.All
    """
    token = get_token(entra)
    group_id = _resolve_group_id(group, token)
    user_id = _resolve_user_id(user, token)

    resp = requests.post(
        f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"},
        timeout=15,
    )

    if resp.status_code == 204:
        print(f"Added '{user}' to group '{group}'")
        return {"added": True, "group_id": group_id, "user_id": user_id}

    if resp.status_code == 400:
        message = resp.json().get("error", {}).get("message", "")
        if "already exist" in message.lower():
            print(f"'{user}' is already a member of '{group}' — skipping")
            return {"added": False, "already_member": True, "group_id": group_id, "user_id": user_id}

    resp.raise_for_status()
