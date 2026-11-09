<!-- generated from https://cli.dreamlake.ai/organizations.md at 0.112.1 2a2fef0; do not edit -->

# Organizations

An **organization** owns projects and groups people. Members have a role —
`OWNER` or `MEMBER`. Creating an org makes you its first OWNER and creates a
matching namespace.

## Manage organizations

```bash file="terminal"
dl org list
dl org show my-org
dl org create my-org --name "My Org" --description "..."
dl org update my-org --description "..."
dl org delete my-org          # must have no remaining projects
dl org leave my-org           # owners must transfer ownership first
```

## Members

Users are referenced by **email or name** — the CLI resolves them to a user
id (an exact email is unambiguous).

```bash file="terminal"
dl org member list   my-org
dl org member add    my-org alice@example.com --role member
dl org member role   my-org alice@example.com --role owner
dl org member remove my-org alice@example.com
```

## Permissions

Permissions are **enforced by the server**, not the CLI — it sends the
request with your token and surfaces the result.

| Action | OWNER | MEMBER |
| --- | --- | --- |
| Create / edit project | ✓ | ✓ |
| **Delete project** | ✓ | ✗ |
| Create / delete files & episodes | ✓ | ✓ |
| Manage org members | ✓ | ✗ |

> **Note:** Organization and team commands talk to the server's GraphQL endpoint
> (`POST /graphql`) using the same token as every other command.
