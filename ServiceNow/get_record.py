
import requests
from typing import TypedDict

import wmill
from f.ServiceNow.auth import servicenow, get_token


def main(
    snow: servicenow,
    table: str,
    sys_id: str,
    fields: str = "",
) -> dict:
    """
    Fetch a single ServiceNow record by sys_id.

    Args:
        snow:   ServiceNow connection resource (instance_url, credentials).
        table:  Table name, e.g. 'incident', 'change_request', 'cmdb_ci'.
        sys_id: The 32-character sys_id of the record.
        fields: Comma-separated list of fields to return (empty = all fields).
    """
    token = get_token(snow)

    params = {"sysparm_display_value": "false"}
    if fields.strip():
        params["sysparm_fields"] = fields.strip()

    url = f"{snow['instance_url'].rstrip('/')}/api/now/table/{table}/{sys_id}"
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        params=params,
        timeout=30,
    )

    if resp.status_code == 404:
        raise ValueError(f"Record not found: table={table}, sys_id={sys_id}")

    resp.raise_for_status()
    record = resp.json().get("result", {})
    print(f"Retrieved record from {table}: {sys_id}")
    return record
