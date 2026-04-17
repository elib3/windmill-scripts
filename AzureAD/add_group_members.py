from f.AzureAD.auth import ms_entra_id, get_token
from f.AzureAD.add_group_member import _resolve_group_id, _resolve_user_id
import requests


def main(
    entra: ms_entra_id,
    group: str,
    users: list[str],
) -> dict:
    """
    Add multiple users to an Entra ID group.

    Resolves each user independently and reports per-user results.
    Skips users who are already members without failing the whole run.

    Args:
        group: Group object ID (GUID) or exact displayName
        users: List of user object IDs, UPNs, or email addresses

    Returns:
        {
            "group_id": "...",
            "total": N,
            "added": N,
            "already_member": N,
            "failed": N,
            "results": [{"user": "...", "status": "added|already_member|failed", ...}]
        }

    Required Graph API permissions:
        GroupMember.ReadWrite.All
    """
    token = get_token(entra)
    group_id = _resolve_group_id(group, token)

    results = []
    added = 0
    already_member = 0
    failed = 0

    for user in users:
        try:
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
                print(f"[+] Added '{user}'")
                results.append({"user": user, "user_id": user_id, "status": "added"})
                added += 1

            elif resp.status_code == 400:
                message = resp.json().get("error", {}).get("message", "")
                if "already exist" in message.lower():
                    print(f"[=] '{user}' already a member — skipping")
                    results.append({"user": user, "user_id": user_id, "status": "already_member"})
                    already_member += 1
                else:
                    resp.raise_for_status()

            else:
                resp.raise_for_status()

        except Exception as e:
            print(f"[!] Failed to add '{user}': {e}")
            results.append({"user": user, "status": "failed", "error": str(e)})
            failed += 1

    print(f"\nDone — added: {added}, already_member: {already_member}, failed: {failed}")

    return {
        "group_id": group_id,
        "total": len(users),
        "added": added,
        "already_member": already_member,
        "failed": failed,
        "results": results,
    }
