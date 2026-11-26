# Manage Project access and attach resources

For interactive permission management, first check installed help, then open the
exact Project in its owning namespace:

```bash
dl project permissions --help
dl project permissions "$PROJECT_ID" --namespace acme
```

Inspect the audience and its contributing access paths before choosing a change.
Follow the requested recipients and roles; review the exact Project identity,
policy change and surviving access in the terminal preview before confirming.
Cancel to leave a preview without writing. After an uncertain response, inspect
current access before deciding whether another mutation is needed. Installed
version and compatible-backend requirements are in
[Interactive permissions](../reference/cli-projects.md#interactive-permissions).
An unsupported capability is a stop, never a reason to weaken the requested
restriction or create first and restrict afterward.
For an SDK, GraphQL or MCP request, check the
[interface coverage](../reference/docs-workspaces-project-access.md#interface-coverage)
before choosing a supported call. Do not infer API or tool availability from the
existence of a CLI command, and never use a model invocation to bypass a refusal.

Project attachment commands require CLI 0.62.0 and the companion Project-sharing
backend release; `project inspect`, `grants`, `grant` and `revoke` require CLI
0.45.1. Python Project support requires SDK 0.29.0+. Check the installed version,
`dl project --help` and [Projects](../reference/cli-projects.md#project-attachment-access-cli-0620)
before relying on them; verify installed versions separately from server support.

```bash
dl project inspect research --namespace acme      # effective role, manageGrants
dl project grants research --namespace acme
dl project grant research --namespace acme --user teammate --role WRITE
dl project revoke research GRANT_ID --namespace acme
dl project attach research --namespace acme --type note --resource "$NOTE_ID"
dl project detach research --namespace acme --type note --resource "$NOTE_ID"
```

Grants target an existing active organization member or team and need the
server's current grant-management authority; a 401/403/404 is a failure, not an
empty list, and the commands never retry in another namespace. Grant rows alone
do not describe effective access: inspect the current policy and full audience,
including membership, owner recovery and public access paths. For selecting a
subset, follow [Workspace or Restricted](../reference/cli-projects.md#workspace-or-restricted-project-access)
and verify the policy after saving; do not infer it from private visibility or an
empty grant list. Attach by database ID (an Artifact uses its database ID,
not its `artifactId`); supported types are `note`, `artifact`, `annotation`,
`workflow`, `env` and `source`, plus `host` where the installed client lists it
([File a host in a Project](#file-a-host-in-a-project)). Attachment requires the Project's content-create
permission plus the resource's own sharing-management permission; ordinary
organization-member READ or public Project visibility is insufficient. Grouping
an already-attached resource into a Bindr of the same Project needs Project write
authority and resource readability, without sharing it again; use the server's
current `canBind` result, not a role guessed from membership.

## Share a Project with another namespace

Sharing a whole Project with another personal or organization namespace is
unreleased: use it only when the installed `dl project --help` lists `share`
and `shared`, and the server accepts the request. If either is missing, stop
and say so; do not substitute per-user grants, a public Project or raw HTTP.
Read each command's `--help` for its flags, roles and output.

```bash
dl project --help                                  # share, shares, unshare, shared, accept-share, leave-share
dl project share --help
dl project shares "$PROJECT_ID" --namespace acme   # sending side: pending and active
dl project shared --namespace partner-lab          # receiving side
```

- Sending: name the exact Project, recipient namespace and role the user asked
  for, then list the shares and report whether it is waiting for the recipient
  or in effect. An upgrade waits; do not describe it as granted.
- Receiving: list first, show the user the Project, sender, role and revision,
  and accept only that revision. If it is refused as stale, list again and ask
  again; never accept a revision the user has not seen.
- Before leaving or revoking, state that it ends the whole share, including a
  role already in effect, and that user and team grants are unaffected.
- After a failed or uncertain change, list the shares before any second
  attempt.

## File a host in a Project

Filing a host (type `host`, by its Host ID) is newer than the other types: use
it only when `dl project attach --help` lists it. It records placement only.

1. Establish the exact host, Project and optional Bindr. A request that
   names them explicitly is the authorization; ask only for what is missing
   or ambiguous. Who may file, and where, is in
   [Project attachment access](../reference/cli-projects.md#project-attachment-access-cli-0620);
   a refusal is reported, not worked around.
2. When you file, state once in the same reply that the Project's
   organization members, now and later, see the host's name and owner, and
   that nobody gains connection access through it.
3. File, with the Bindr in the same command when one was asked for:

   ```bash
   dl project attach research --namespace acme --type host --resource "$HOST_ID" --bindr "Lab machines" --json
   ```

   Output, exit codes and version floors are in
   [Hosts in Projects](../reference/cli-projects.md#hosts-in-projects).
   A partial result means the host is filed but not tagged: run the same
   command again, which re-files the same node and tags it. Never file a
   second copy, and report a tag that still did not succeed instead of
   dropping it. If the installed `dl project attach --help` does not list
   `--bindr` (or `host`), stop and update the CLI; do not tag through
   another command or raw HTTP. For an explicit SDK request, use only the
   documented SDK Project and Bindr methods.
4. If the user wants Project members to connect, that is a separate explicit
   grant: the `host-access` action of `dreamlake-lakeshore`. Do not file a host
   to share it, and do not grant connection access because it is filed.

Unfiling (detach) removes the placement and its Bindr tags and leaves the host
and its connection grants unchanged. A whole-Project move is refused while a
host is filed in the Project: unfile it first, with the user's authorization,
then preview the move again (the `projects` action).

## What Project grants give and withhold

- Explicit Project user/team READ grants read all current and future attached
  Memos, Artifacts, Scenes/Envs, Workflow specs and Sources; WRITE/ADMIN add
  supported content updates. For a Source, READ gives USE and WRITE/ADMIN give
  content EDIT, never Source ADMIN, Connection/Vault credentials or sharing
  management. Explicit grants cover future attachments without copied links.
- Grants never give resource sharing management, deletion, ownership transfer,
  execution, host/secret access (also for a host filed in the Project), catalog
  management or infrastructure credentials. Permission to publish a Workflow version is not permission to Run.
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

Deleting a Project removes its filing relationships; independently owned Memos
and Sources keep their namespace ownership. See
[inspect access](../reference/cli-projects.md#inspect-access-cli-0451) and the
owning contract at https://docs.dreamlake.ai/dev/notes/project-resource-sharing/.
