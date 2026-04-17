
import re
import requests
from typing import Optional
from f.AzureAD.auth import ms_entra_id, get_token

_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _resolve_group_id(group_id_or_name: str, token: str) -> str:
    """If input is not a GUID, look up the group by displayName."""
    if _GUID_RE.match(group_id_or_name):
        return group_id_or_name
    resp = requests.get(
        "https://graph.microsoft.com/v1.0/groups",
        headers={"Authorization": f"Bearer {token}"},
        params={"$filter": f"displayName eq '{group_id_or_name}'", "$select": "id,displayName"},
        timeout=15,
    )
    resp.raise_for_status()
    groups = resp.json().get("value", [])
    if not groups:
        raise ValueError(f"Group '{group_id_or_name}' not found.")
    if len(groups) > 1:
        matches = [f"{g['displayName']} ({g['id']})" for g in groups]
        raise ValueError(f"Multiple groups match '{group_id_or_name}': {matches}. Use the object ID instead.")
    return groups[0]["id"]


def main(
    entra: ms_entra_id,
    group_id: str,
    users_only: bool = True,
    select_fields: str = "id,displayName,userPrincipalName,mail,jobTitle,department",
    max_results: int = 999,
):
    """
    Get members of an Entra ID group.

    Args:
        group_id: Group object ID (GUID) or exact displayName
        users_only: If True, exclude service principals and devices
        max_results: Maximum number of members to return (auto-paginates)
    """
    token = get_token(entra)
    resolved_id = _resolve_group_id(group_id, token)

    url: Optional[str] = (
        f"https://graph.microsoft.com/v1.0/groups/{resolved_id}/members/microsoft.graph.user"
        if users_only
        else f"https://graph.microsoft.com/v1.0/groups/{resolved_id}/members"
    )

    headers = {"Authorization": f"Bearer {token}"}
    params: dict = {"$select": select_fields, "$top": min(max_results, 999)}
    members = []

    while url and len(members) < max_results:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 404:
            raise ValueError(f"Group ID '{resolved_id}' not found.")
        resp.raise_for_status()
        data = resp.json()
        members.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = {}

    return {"group_id": resolved_id, "count": len(members), "members": members[:max_results]}
