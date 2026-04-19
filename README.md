# Windmill Script Library

A growing collection of reusable [Windmill](https://windmill.dev) scripts and
resource types, organized by integration. Each subfolder is a self-contained
package you can deploy independently into any Windmill workspace.

## Packages

| Package | Description |
|---|---|
| [`AzureAD/`](./AzureAD/) | Microsoft Entra ID (Azure AD) via Microsoft Graph API |
| [`ServiceNow/`](./ServiceNow/) | ServiceNow Table API via OAuth2 ROPC flow |

> More packages coming soon.

## Repository Structure

```
windmill-scripts/
├── AzureAD/
│   ├── auth.py
│   ├── get_user.py
│   ├── get_users.py
│   ├── get_group_members.py
│   └── resource_type_ms_entra_id.json
└── <NextPackage>/
    └── ...
```

Each package folder contains:
- **Scripts** — ready to deploy to Windmill
- **Resource type JSON** (where applicable) — import into your workspace for
  typed credentials and UI integration

## How to Use

1. Browse to the package folder you need
2. Import the resource type JSON into your Windmill workspace (if provided)
3. Deploy the scripts in the order listed in that package's README
4. Create a resource with your credentials — never hardcode them in scripts

## Security Philosophy

- Credentials are always passed via Windmill resource types — never hardcoded
- Secrets are marked sensitive in resource schemas
- Scripts follow the principle of least privilege

## Requirements

- [Windmill](https://windmill.dev) (self-hosted or cloud)
- Python 3.11+

## License

MIT
