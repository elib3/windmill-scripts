# ServiceNow — Scripts for Windmill

Scripts for interacting with ServiceNow via the Table API, using OAuth2
Resource Owner Password Credentials (ROPC) flow with automatic token caching.

## Scripts

| Script | Path in Windmill | Description |
|---|---|---|
| `auth.py` | `f/ServiceNow/auth` | Authenticate & cache OAuth2 access token |
| `get_record.py` | `f/ServiceNow/get_record` | Fetch a single record from any table by sys_id |

## Resource Type

Create a Windmill resource with the following fields:

| Field | Description |
|---|---|
| `instance_url` | Your ServiceNow instance URL (e.g. `https://yourinstance.service-now.com`) |
| `client_id` | OAuth2 application client ID |
| `client_secret` | OAuth2 application client secret (**sensitive**) |
| `username` | ServiceNow user account username |
| `password` | ServiceNow user account password (**sensitive**) |

## Setup

### 1. Create an OAuth2 Application in ServiceNow

1. Navigate to **System OAuth → Application Registry → New**
2. Select **Create an OAuth API endpoint for external clients**
3. Fill in a name, note the **Client ID** and set a **Client Secret**
4. Save the record

### 2. Create the Resource in Windmill

1. **Resources → Add resource** → create a new resource type (or use `object`)
2. Fill in all five fields above
3. Mark `client_secret` and `password` as **sensitive**

### 3. Deploy Scripts

Deploy in this order — `auth` must exist before `get_record`:

```
auth.py        → f/ServiceNow/auth
get_record.py  → f/ServiceNow/get_record
```

> Scripts import from `f.ServiceNow.auth` — deploy paths must match exactly.

## Usage Examples

**Fetch an incident by sys_id:**
```
table:  incident
sys_id: abc123def456abc123def456abc123de
fields: number,short_description,state,priority
```

**Fetch a full CMDB CI record:**
```
table:  cmdb_ci
sys_id: abc123def456abc123def456abc123de
fields: (leave empty for all fields)
```

## Security Notes

- Token is cached in Windmill state (`f/ServiceNow/snow_token_cache`) — not in logs or memory
- Only the token prefix is printed during auth verification
- Tokens are reused until within 60 seconds of expiry (default lifetime: 30 minutes)
- Never store credentials in scripts — always use a Windmill resource
