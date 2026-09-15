# Organizations

An **organization** owns projects and groups people. Members have a role —
`OWNER` or `MEMBER`. Creating an org makes you its first OWNER and creates a
matching namespace.

## Manage organizations

```bash file="terminal"
dreamlake org list
dreamlake org show my-org
dreamlake org create my-org --name "My Org" --description "..."
dreamlake org update my-org --description "..."
dreamlake org delete my-org          # must have no remaining projects
dreamlake org leave my-org           # owners must transfer ownership first
```

## Members

Users are referenced by **email or name** — the CLI resolves them to a user
id (an exact email is unambiguous).

```bash file="terminal"
dreamlake org member list   my-org
dreamlake org member add    my-org alice@example.com --role member
dreamlake org member role   my-org alice@example.com --role owner
dreamlake org member remove my-org alice@example.com
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
