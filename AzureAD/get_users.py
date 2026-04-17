
import requests
from typing import Optional
from f.AzureAD.auth import ms_entra_id, get_token


def main(
    entra: ms_entra_id,
    filter: Optional[str] = None,
    search: Optional[str] = None,
    select_fields: str = "id,displayName,userPrincipalName,mail,jobTitle,department,accountEnabled",
    max_results: int = 100,
):
    """
    List users from Entra ID (Azure AD).

    Args:
        filter: OData $filter expression (e.g. "department eq 'Engineering'")
        search: OData $search expression (e.g. '"displayName:John"')
        max_results: Maximum number of users to return (auto-paginates)
    """
    token = get_token(entra)
    headers = {"Authorization": f"Bearer {token}"}
    params: dict = {"$select": select_fields, "$top": min(max_results, 999)}

    if filter:
        params["$filter"] = filter
    if search:
        params["$search"] = search
        headers["ConsistencyLevel"] = "eventual"
        params["$count"] = "true"

    users = []
    url: Optional[str] = "https://graph.microsoft.com/v1.0/users"

    while url and len(users) < max_results:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        users.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = {}

    return {"count": len(users), "users": users[:max_results]}
