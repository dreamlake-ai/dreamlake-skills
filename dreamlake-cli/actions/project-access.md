# Grant Project access and attach resources

Project attachment commands require CLI 0.62.0 and the companion Project-sharing
backend release; `project inspect`, `grants`, `grant` and `revoke` require CLI
0.45.1. Python Project support requires SDK 0.29.0+. Check the installed version,
`dreamlake project --help` and [Projects](../reference/cli-projects.md#project-attachment-access-cli-0620)
before relying on them; verify installed versions separately from server support.

```bash
dreamlake project inspect research --namespace acme      # effective role, manageGrants
dreamlake project grants research --namespace acme
dreamlake project grant research --namespace acme --user teammate --role WRITE
dreamlake project revoke research GRANT_ID --namespace acme
dreamlake project attach research --namespace acme --type note --resource "$NOTE_ID"
dreamlake project detach research --namespace acme --type note --resource "$NOTE_ID"
```

Grants target an existing active organization member or team and need the
server's current grant-management authority; a 401/403/404 is a failure, not an
empty list, and the commands never retry in another namespace. Grant rows alone
do not describe effective access: organization members keep baseline Read on
organization projects. Attach by database ID (an Artifact uses its database ID,
not its `artifactId`); supported types are `note`, `artifact`, `annotation`,
`workflow`, `env` and `source`. Attachment requires the Project's content-create
permission plus the resource's own sharing-management permission; ordinary
organization-member READ or public Project visibility is insufficient. Grouping
an already-attached resource into a Bindr of the same Project needs Project write
authority and resource readability, without sharing it again; use the server's
current `canBind` result, not a role guessed from membership.

## What Project grants give and withhold

- Explicit Project user/team READ grants read all current and future attached
  Notes, Artifacts, Scenes/Envs, Workflow specs and Sources; WRITE/ADMIN add
  supported content updates. For a Source, READ gives USE and WRITE/ADMIN give
  content EDIT, never Source ADMIN, Connection/Vault credentials or sharing
  management. Explicit grants cover future attachments without copied links.
- Grants never give resource sharing management, deletion, ownership transfer,
  execution, host/secret access, catalog management or infrastructure
  credentials. Permission to publish a Workflow version is not permission to Run.
  Project ADMIN is not transfer authority.
- Public Project visibility alone never opens a private resource. Independent
  resource links, acceptance records and namespace membership remain valid; Project
  sharing creates, copies or revokes none of them.
- Detaching a resource, revoking a grant or leaving a granted team removes only
  that source of access; a resource attached to several Projects keeps the others.
- Project-only uploads need resource-scoped temporary credentials;
  `DELEGATED_UPLOAD_UNSUPPORTED` (403) is a safe broker refusal, not a reason to
  request static server credentials.
- A Project reader may lack namespace-list authority: use the exact Source name
  and canonical address; a denied list is not an empty catalog.
- Read with the reader's own credentials at the canonical address; do not mint a
  share link to simulate Project access.

Deleting a Project removes its filing relationships; independently owned Notes
and Sources keep their namespace ownership. See
[inspect access](../reference/cli-projects.md#inspect-access-cli-0451) and the
owning contract at https://docs.dreamlake.ai/dev/notes/project-resource-sharing/.
