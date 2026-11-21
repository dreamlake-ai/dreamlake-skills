<!-- generated from https://cli.dreamlake.ai/organizations.md at 0.140.0 14b9b01; do not edit -->

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

### Remove a member

Only an org OWNER can remove a member; a team MAINTAINER manages team
membership, not organization membership. The server refuses to remove the last
OWNER. Removal ends the person's organization membership: org-wide
(workspace-member) access, any OWNER authority over the organization's
namespace, and their memberships in its teams, so Project access shared with
those teams ends too. Project grants they issued on Projects owned by the
organization are deleted.

By default their **direct personal grants** on Projects owned by the
organization are kept, as before. Add `--revoke-direct-project-grants` to delete
those grants in the same removal. Independent resource shares and public
access are not changed either way. The confirmation states which applies;
`--yes` skips it.

```bash cli-help="org member remove"
# Remove a member; their direct Project grants are kept.
dl org member remove my-org alice@example.com
# Also delete their direct personal grants on Projects owned by my-org.
dl org member remove my-org alice@example.com --revoke-direct-project-grants
```

`--revoke-direct-project-grants` needs a server that supports it. An older
server rejects the request and nobody is removed; the CLI reports this and
never retries without the option. Without the option, the CLI sends the same
request as earlier versions.

In TypeScript, the same opt-in is an optional third argument:

```typescript
await client.organizations.removeMember(orgId, userId, { revokeDirectProjectGrants: true })
```

An older server makes this throw `OrganizationMemberRemoveRevokeUnsupportedError`.

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
