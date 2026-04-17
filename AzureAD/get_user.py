
import requests
from f.AzureAD.auth import ms_entra_id, get_token


def main(
    entra: ms_entra_id,
    user_id: str,
    select_fields: str = "id,displayName,userPrincipalName,mail,jobTitle,department,accountEnabled",
):
    """
    Fetch a single user from Entra ID (Azure AD).

    Returns:
        On success: {"found": True, "user": {...}}
        Not found:  {"found": False, "user_id": user_id}
    """
    token = get_token(entra)
    resp = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"$select": select_fields},
        timeout=15,
    )
    if resp.status_code == 404:
        return {"found": False, "user_id": user_id}
    resp.raise_for_status()
    return {"found": True, "user": resp.json()}
