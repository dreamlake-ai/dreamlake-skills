<!-- generated from https://docs.dreamlake.ai/workspaces/project-access.md at 0.1.158 e3e61780; do not edit -->

# Project access

**Version requirements.** The Project access backend and Web controls must be
deployed. Terminal controls and the TypeScript API require CLI/package 0.117.0+;
Python access methods require SDK 0.46.1+. Clients check the server contract and
stop when support cannot be confirmed. Earlier clients can still manage direct
grants, but cannot remove organization-member READ.

A Project can use its normal workspace baseline or be restricted to explicitly
granted users and teams. This is a **Project access** feature, not a new permission
editor for every Memo, Artifact, host or attached resource.

## Open the Access page

Open the Project and choose **Access**, or navigate to
`/<namespace>/projects/<project>/access`. The page shows current effective access,
Workspace/Restricted mode, visibility, owner baseline and direct user/team grants.
Readers can inspect access where permitted; changing mode or grants requires
current Project ADMIN authority. The server rechecks authority on mutation.

Use the existing Teams UI at `/<namespace>/teams` to create/manage teams and open
a team to manage its membership. Project grants select an active team belonging
to the Project's organization. This feature does not introduce a new external
invite, guest identity or team administration system.

There is **no namespace-wide default Project access setting** in this feature.
Existing Projects with no stored mode retain Workspace behavior. New creation
defaults remain Workspace/private unless the caller explicitly chooses Restricted.
No existing Project is automatically made private, public or restricted.

## Workspace, Restricted and visibility

| Access mode | Visibility | Baseline access |
|---|---|---|
| Workspace | Private | Organization members retain their existing READ baseline; private personal Projects have no organization baseline |
| Workspace | Public | Public READ remains available |
| Restricted | Private | Active explicit user/team grants and namespace-owner authority only |
| Restricted | Public | Invalid; rejected without a partial policy change |

Private visibility alone does not mean "only selected coworkers." Restricted mode
is what removes the normal workspace-member baseline. Namespace owners retain
ADMIN recovery authority. Explicit user/team roles combine using the highest
applicable active role; removing one grant does not cancel another access path.

- **READ:** inspect the Project and its permitted content.
- **WRITE:** content editing in addition to reading.
- **ADMIN:** manage the Project and grants under existing policy.

Project ADMIN does not transfer resource ownership or grant cloud/host execution
credentials. It also does not grant independent sharing-management authority over
attached resources.

## Identity and shared API conventions

Use a stable Project ID whenever available. The REST/SDK/CLI Project reference may
be an ID or slug scoped to the source namespace. An ID from another namespace is
not accepted through the wrong namespace path. CLI `--namespace` / `--ns` is source
context for the new access command; it never means move destination.

Examples use the same accessible `projectId` / `project_id` / `$PROJECT_ID`.
TypeScript uses `client.projects("acme")`; Python uses the existing
`client.projects` interface. New settings calls take named fields. Existing grant
methods retain compatibility, rather than migrating unrelated collection APIs.
Model tools receive explicit namespace and stable `projectId`; there is no hidden
current Project. See the [shared API conventions](https://docs.dreamlake.ai/notes/api).

## Inspect effective access

**CLI**

```bash
dl project access "$PROJECT_ID" --ns acme --json
```

**TypeScript**

```typescript
const policy = await client.projects("acme").access({ project: projectId })
```

**Python**

```python
policy = client.projects.access(namespace="acme", project=project_id)
```

**Tool call**

```javascript
dreamlake_project_access({ namespace: "acme", projectId })
```

The response is the same policy envelope through every interface:

```json
{
  "projectId": "507f1f77bcf86cd799439011",
  "namespace": "acme",
  "projectSlug": "research",
  "accessMode": "restricted",
  "visibility": "private",
  "baseline": { "orgMembers": null, "namespaceOwners": "ADMIN", "public": null },
  "viewerRole": "ADMIN",
  "manageGrants": true
}
```

`viewerRole` is current effective authority, not ownership inferred from a label.
`baseline` explains access that would remain without a direct grant. The grants
endpoint lists direct user/team grants; it is not an exhaustive audience. Use
the [effective audience](#effective-audience-and-terminal-management) to inspect
named people and every contributing access path. Both inventories require
grant-management authority. Unauthorized direct lookups return not found rather
than revealing a restricted Project's existence.

## Restrict an existing Project

Set Restricted/private explicitly in one request. This also handles a currently
public Project without a separate first mutation or an exposure window between
settings changes.

**CLI**

```bash
dl project access "$PROJECT_ID" --namespace acme --mode restricted --visibility private --json
```

**TypeScript**

```typescript
const policy = await client.projects("acme").setAccess({ project: projectId, accessMode: "restricted", visibility: "private" })
```

**Python**

```python
policy = client.projects.set_access(namespace="acme", project=project_id, access_mode="restricted", visibility="private")
```

**Tool call**

```javascript
dreamlake_project_access_set({ namespace: "acme", projectId, accessMode: "restricted", visibility: "private" })
```

Omitting visibility preserves its current value. A public Project therefore
cannot become Restricted unless `visibility: private` is explicitly included.
`PROJECT_ACCESS_VISIBILITY_CONFLICT` reports this conflict. The mode/visibility
change is serialized with grant changes, ownership and deletion, then returns the
acknowledged effective policy. Clients must not report success from a receipt
that identifies another resource or disagrees with the requested settings.

## Restore the workspace baseline

This action restores workspace-member baseline access without implicitly making
the Project public. Current visibility is preserved.

**CLI**

```bash
dl project access "$PROJECT_ID" --namespace acme --mode workspace --json
```

**TypeScript**

```typescript
const policy = await client.projects("acme").setAccess({ project: projectId, accessMode: "workspace" })
```

**Python**

```python
policy = client.projects.set_access(namespace="acme", project=project_id, access_mode="workspace")
```

**Tool call**

```javascript
dreamlake_project_access_set({ namespace: "acme", projectId, accessMode: "workspace" })
```

Restoring an organization baseline is refused with
`FOREIGN_NOTE_RESHARING_UNSUPPORTED` when the Project retains a foreign-owned Note
without an external mount grant authorizing its future audience. This preserves
the existing redistribution boundary; the policy remains unchanged. Grant-admitted
external mounts follow their existing owner consent. Making a Project public does
not publish independently private Notes attached to it.

## Create Restricted from the start

For a new confidential Project, choose Restricted before creating it. The
backend creates the Project, policy and creator grant in the same transaction.
Do not create Workspace and then PATCH it Restricted as a confidentiality shortcut.

**CLI**

```bash
dl create project "Research" --namespace acme --access-mode restricted --visibility private
```

**TypeScript**

```typescript
const project = await client.projects("acme").create({ name: "Research", accessMode: "restricted", visibility: "private" })
```

**Python**

```python
project = client.projects.create(namespace="acme", name="Research", access_mode="restricted", visibility="private")
```

**Tool call**

```javascript
// No built-in Project creation tool is registered by this feature.
// Use the UI, CLI or SDK; do not invent a tool name or broaden machine authority.
```

Before restricted creation, supported clients require an explicit catalog
capability, so an older server cannot silently ignore `accessMode` and create an
unrestricted Project:

```json
{ "accessPolicy": { "apiVersion": 1, "modes": ["workspace", "restricted"], "atomicCreate": true } }
```

Missing/unsupported capability produces `PROJECT_ACCESS_UNSUPPORTED` before POST.
There is no create-then-restrict fallback. A successful receipt must identify the
created Project and confirm restricted/private. If the response is unconfirmed,
retain any returned ID and inspect it; do not blindly create a duplicate or delete
an uncertain result. UI choices must be capability-gated too.

## List grants

**CLI**

```bash
dl project grants "$PROJECT_ID" --namespace acme --json
```

**TypeScript**

```typescript
const grants = await client.projects("acme").grants(projectId)
```

**Python**

```python
grants = client.projects.grants(namespace="acme", project=project_id)
```

**Tool call**

```javascript
dreamlake_project_grants({ namespace: "acme", projectId })
```

The grant response includes active direct-user/team entries, current effective
roles and baseline information. A grant's own READ role may coexist with effective
WRITE through a team. The UI must show both rather than imply that removing the
listed grant removes all access. Team grants apply through current active team
membership; stale, revoked or deactivated membership must not keep access alive.

## Grant a selected user

**CLI**

```bash
dl project grant "$PROJECT_ID" --namespace acme --user alice --role READ --json
```

**TypeScript**

```typescript
const grant = await client.projects("acme").grant(projectId, { granteeSlug: "alice", role: "READ" })
```

**Python**

```python
grant = client.projects.grant(namespace="acme", project=project_id, role="READ", user="alice")
```

**Tool call**

```javascript
dreamlake_project_grant({ namespace: "acme", projectId, granteeSlug: "alice", role: "READ" })
```

A direct user grant does not turn off Workspace baseline access. Select Restricted
when the intended audience is only named users/teams. Grant changes require current
ADMIN and preserve existing ownership/redistribution checks.

## Grant an existing team

**CLI**

```bash
dl project grant "$PROJECT_ID" --namespace acme --team "$TEAM_ID" --role WRITE --json
```

**TypeScript**

```typescript
const grant = await client.projects("acme").grant(projectId, { teamId, role: "WRITE" })
```

**Python**

```python
grant = client.projects.grant(namespace="acme", project=project_id, role="WRITE", team=team_id)
```

**Tool call**

```javascript
dreamlake_project_grant({ namespace: "acme", projectId, teamId, role: "WRITE" })
```

Choose exactly one user or team. Team identifiers are stable IDs, validated against
an active team in the owning organization. Team membership administration remains
in the existing Teams UI/API; this operation grants the team a Project role, not
organization-wide membership or unrelated resource access.

## Revoke one grant

**CLI**

```bash
dl project revoke "$PROJECT_ID" "$GRANT_ID" --namespace acme --json
```

**TypeScript**

```typescript
await client.projects("acme").revoke(projectId, grantId)
```

**Python**

```python
client.projects.revoke(namespace="acme", project=project_id, grant_id=grant_id)
```

**Tool call**

```javascript
dreamlake_project_revoke({ namespace: "acme", projectId, grantId })
```

Revocation removes exactly that grant. Reinspect effective access: the user may
still be an owner, have another direct/team grant, or receive Workspace/public
baseline access. Namespace-owner recovery remains available; deleting a grant
must not manufacture a new owner or bypass transaction fencing.

## Project boundary and independent resource access

The policy controls Project discovery, its structure and content access derived
through that Project. Project listings, counts, search, tree requests and known-ID
lookups must share the same server checks, including before pagination and before
external vector/search work. A restricted Project must not leak through a bindr,
resource-location picker, recent list or metadata summary.

Memos, Artifacts and other resources retain their **independent** ownership,
namespace membership, public visibility, share links and other Project grants.
Restricting a Project does not revoke those paths. In particular, a Memo owned by
an organization may still be readable by organization members through its own
resource contract even when its Project is restricted. The page must not promise
"only these people can see every resource inside."

Moving or restricting a Project does not automatically grant SSH, host execution,
provider credentials or cloud access. Those are separate resource contracts.

## Agent authority and revocation

The built-in tools use `projects:read` / `projects:write` turn scopes and explicit
service-account Project grants in addition to the current human authority carried
by the API call. Knowing a Project ID, having a model-visible tool or holding a
Memo write capability is not permission to manage Project access.

The existing built-in account is normally personal, and its Project grant manager
requires the account and target Project to share a namespace. Do not infer that
a human organization administrator can automatically call these tools for an
organization Project: that account/grant provisioning path remains a separate
limitation. Tools are registered for explicitly permitted Projects, not a
promise of unrestricted human-account parity.

A read preflight/reauthorization and current human mutation checks are not an atomic
machine-grant revocation fence across the downstream mutation. Concurrent machine
revocation needs its own explicit server guarantee; do not claim it from the
client preflight alone. Turn fencing does not replace resource authorization.

## Results, streams and recovery

These calls do not accept document stdin. CLI stdout contains the policy/grant
result, with structured JSON when requested or piped; stderr carries diagnostics.
Tool results include stable Project identity and resolved policy fields rather
than inferred permission. See [CLI outcomes](https://docs.dreamlake.ai/notes/api/cli).

Clients do not automatically retry policy or grant mutations. A transport timeout
may follow acceptance. Inspect current policy/grants before deciding whether to
submit again. Do not change a requested mode, privatize a Project silently, or
use a weaker legacy endpoint to make a refusal pass.

## Interface coverage

| Interface | Shipped support and boundary |
| --- | --- |
| REST | Policy read/change, atomic restricted creation, direct grants and complete bounded effective audience. |
| Web UI | Project Access controls for policy and user/team grants; the baseline/direct-grant display is not the complete human audience. |
| CLI and terminal | CLI 0.117.0+: noninteractive commands, JSON, `project audience` and keyboard `project permissions`. |
| TypeScript | Package 0.117.0+: `client.projects(namespace)` policy, grant and audience methods. |
| Python | SDK 0.46.1+: policy, atomic creation and user/team grant methods. No dedicated effective-audience helper; use REST or the CLI for that inventory. See the [SDK reference](https://github.com/fortyfive-labs/dreamlake/blob/main/docs/api/projects.md). |
| GraphQL | Existing Project catalog, known-ID and association reads apply the shared permission rules. No policy/audience fields or Project access mutations; use REST. See [Project queries](https://docs.dreamlake.ai/api/project-queries). |
| Built-in agent tools | `dreamlake_project_access`, `dreamlake_project_access_set`, `dreamlake_project_grants`, `dreamlake_project_grant` and `dreamlake_project_revoke` are registered with declared scopes, explicit machine grants and current human authority. No whole-audience tool; retain the namespace/provisioning limits above. |
| Local MCP adapter | Source-only adapter; no direct Project policy, grant or audience tools. `assistant_invoke` does not bypass the built-in assistant's restrictions and is not an organization-admin permission API. See [MCP](https://docs.dreamlake.ai/lakeshore/agents/mcp). |
| Skills API | Authenticated `/skills` and file reads serve the backend's separately pinned bundle. Check tag/commit headers and bytes; reading guidance grants no Project authority. |

The public skill is guidance, not an authority or a server API. Installed help,
package versions and deployed capability determine what can be called; a new
skill bundle cannot add an unsupported GraphQL field or MCP tool. See
[skill distribution and API](https://docs.dreamlake.ai/dev/skills#authenticated-skills-api) for generated
references and the separately accepted public, CLI-embedded and server pins.

## REST contract

- `GET /namespaces/:namespace/projects/:project/access` reads the effective policy.
- `PATCH` on the same path requires `accessMode` and optional explicit `visibility`;
  it requires current ADMIN and returns the effective policy.
- Existing `/grants` GET/POST and `/grants/:grantId` DELETE remain the grant API.
- `POST /namespaces/:namespace/projects` optionally accepts `accessMode`; omission
  preserves Workspace behavior. Restricted/private creation is atomic.
- Catalog responses advertise the versioned atomic-create capability above.

Unknown/malformed policy input fails validation. Denied access is not a valid empty
Project response. A body RTC revision is not a metadata permission/version token.
Review UI deployment, server capability, CLI binary and SDK package publication
separately before treating these source APIs as available everywhere.

Once any Project uses Restricted mode, backend rollback must preserve enforcement
of that mode. The first compatible production revision is
`d0efbb75d4b040d2574429702b5375cb8d477eec`. A rollback to an older backend that
ignores `accessMode` would restore the organization-member READ baseline. Keep a
compatible revision or carry the restriction checks into the rollback revision;
do not clear policy fields or convert existing Projects to make a rollback pass.

## Effective audience and terminal management

`GET /namespaces/:slug/projects/:project/audience` requires current human Project
ADMIN and returns a consistent read of the same authority rules used by the
Project. It includes the exact Project ID/namespace, current policy, named active
users (including organization members with no surviving Project role), effective
roles and every contributing direct grant, team grant, workspace, owner-recovery
or public source. Public access is also an open audience, never an exhaustive
list of named visitors. Independent resource shares are outside this inventory.
The response includes `apiVersion: 1`, `complete: true` and `people`.

The bounded inventory refuses more than 1,000 grant rows, organization membership
rows, granted-team membership rows or candidate users with
`PROJECT_AUDIENCE_TOO_LARGE` (413). It never silently returns a truncated audience.
The existing direct-grant endpoint remains available. This inventory is a read
snapshot, not a promise that memberships cannot change after review.

CLI 0.117.0 adds `dl project permissions [PROJECT] --namespace ORG` for
keyboard management, plus `dl project audience PROJECT --namespace ORG --json`.
These commands are unavailable in CLI 0.116.0 and earlier. The terminal flow selects a namespace and exact Project,
shows audience sources, previews and confirms grants/policy/revocation, and
reloads access before mutation. Unsupported audience/policy responses stop
mutations. Cancel before confirmation submits no writes. Unknown mutation
outcomes require readback instead of automatic retries.
