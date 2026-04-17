# AzureAD — Microsoft Entra ID Scripts for Windmill

Scripts for interacting with Microsoft Entra ID (Azure AD) via the Microsoft
Graph API, using the OAuth 2.0 client credentials flow.

## Scripts

| Script | Path in Windmill | Description |
|---|---|---|
| `auth.py` | `f/AzureAD/auth` | Authenticate & cache Graph API token |
| `get_user.py` | `f/AzureAD/get_user` | Fetch a single user by ID or UPN |
| `get_users.py` | `f/AzureAD/get_users` | List users with filter, search & pagination |
| `get_group_members.py` | `f/AzureAD/get_group_members` | Get members of a group by ID or name |

## Resource Type

Import `resource_type_ms_entra_id.json` into your Windmill workspace before
creating credentials.

| Field | Description |
|---|---|
| `tenant_id` | Azure AD tenant ID (GUID or domain) |
| `client_id` | App registration client ID |
| `client_secret` | App registration client secret (**sensitive**) |

## Setup

### 1. Register an App in Azure

1. **Azure Portal → Entra ID → App registrations → New registration**
2. Name it (e.g. `windmill-graph-reader`), click **Register**
3. Note the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Certificates & secrets → New client secret** — copy the value immediately
5. Go to **API permissions → Add → Microsoft Graph → Application permissions**, add:
   - `User.Read.All`
   - `GroupMember.Read.All`
6. Click **Grant admin consent**

### 2. Create the Resource in Windmill

1. **Resources → Add resource type** → import `resource_type_ms_entra_id.json`
2. **Resources → Add resource** → choose `ms_entra_id` → fill in your credentials
3. Ensure `client_secret` is marked **sensitive**

### 3. Deploy Scripts

Deploy in this order — `auth` must exist before the others:

```
auth.py               → f/AzureAD/auth
get_user.py           → f/AzureAD/get_user
get_users.py          → f/AzureAD/get_users
get_group_members.py  → f/AzureAD/get_group_members
```

> Scripts import from `f.AzureAD.auth` — deploy paths must match exactly.

## Usage Examples

**Get a single user:**
```
user_id: john.doe@contoso.com
```

**List users in a department:**
```
filter: "department eq 'Engineering'"
```

**Search by name:**
```
search: "displayName:John"
```

**Get group members by name:**
```
group_id: "IT Admins"
users_only: true
```

## Security Notes

- Token is cached in Windmill state (`f/AzureAD/entra_token_cache`) — not in logs or memory
- Only the token prefix is printed during auth verification
- Grant only the Graph API permissions your use case requires
