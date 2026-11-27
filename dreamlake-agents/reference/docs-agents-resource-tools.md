<!-- generated from https://docs.dreamlake.ai/agents/resource-tools.md at 0.1.242 ff603b446; do not edit -->

# Resource APIs in the built-in agent

The built-in agent's resource API catalog is collected from the
server's registered routes, including routes enabled by deployment flags. It
is not a separately maintained copy of the HTTP API.

The built-in agent can create **agent definitions**, which are first-class
runnables rather than sessions. Ask, for example:

> Create a Reviewer agent in my project, using this memo as its instructions
> and the Review skills folder as its optional skills.

`dreamlake_agents_create` accepts `name`, optional `namespace`, `description`,
`projects` and `tools`. Instructions are either `markdown`, or
`instructionNoteId` plus optional `skills` entries with `kind` (`note` or
`folder`) and `id`. The canonical runnable route checks the caller's resource
permissions and performs project filing. The result contains the runnable ID
and its Agents editor link; creation does not launch a session.

```json
{
  "name": "Reviewer",
  "markdown": "Review the requested change. Cite the files you inspected.",
  "projects": ["example-project"],
  "tools": ["dreamlake_notes_read", "dreamlake_resource_api_discover", "dreamlake_resource_api_read"]
}
```

## Accounts and namespaces

An account is the authenticated identity. A namespace selects the default resource
scope within that account's existing access. Switching namespace never signs in
as another user, moves a saved session, or creates a Project delegation.

| Operation | Built-in agent | Browser command | External agent with local CLI |
| --- | --- | --- | --- |
| Inspect identity | `dreamlake_auth_status` | `/auth status` | `dl auth status` |
| List saved logins | Reports one browser identity; local profiles are unavailable | `/auth profiles` explains the browser boundary | `dl auth profiles` |
| Switch account | `dreamlake_auth_switch` returns a sign-in link | `/auth switch` opens the authenticated sign-out/sign-in flow | `dl auth switch <profile>` |
| List namespaces | `dreamlake_namespace_list` | `/namespace list` | `dl namespace list` |
| Inspect namespace | `dreamlake_namespace_status` | `/namespace status` | `dl namespace status` |
| Select namespace | `dreamlake_namespace_use` with `namespace` | `/namespace use <namespace>` or `/su <namespace>` | `dl namespace use <namespace>` or `dl su <namespace>` |

The browser has one active login. Its account switch clears that login through
the existing identity-provider flow and asks you to sign in again. Saved server
conversations retain their original owner; return to that account to reopen
them. A handoff result has `status: "sign_in_required"` and
`accountChanged: false`; it is not proof that another account was activated.
Credentials and local CLI profile files never enter the server tool context.
CLI profile selection changes the local CLI configuration, not the browser login.

The namespace-use tool requires the turn's write capability. It checks current
membership and the exact conversation owner and active turn before saving the
selection. The current turn keeps its admitted identity and namespace; subsequent
turns use the selected namespace and recheck access. Namespace status reports
both `namespace` (this turn) and `nextTurnNamespace` (the saved selection).
After an uncertain switch response, read status before retrying. An Agent
definition remains bound to its own namespace; reselect the definition before
changing that scope. Scoped durable/delegated credentials cannot change identity
or scope through these controls.

The corresponding authenticated API surfaces are:

- `GET /agent/identity`: credential-free caller ID, personal namespace,
  memberships, and browser sign-in handoff metadata. It never provisions an
  agent or lists local CLI profiles.
- `POST /agent/sessions/:id/namespace` with `{ "namespace": "fortyfive",
  "turnId": "the-active-turn-id" }`: saves the next-turn selection, returning
  `apiVersion: 1`, `namespace`, `appliesTo: "next_turn"`, `sessionId`, and `turnId`.
  A stale turn or foreign conversation cannot redirect ongoing work.
- `GET /agent/sessions/:id`: reads the owner's saved `actingNamespace`; callers
  starting an external agent turn may also supply `actingNamespace` directly
  to the existing chat API. Every admission independently checks membership.

These endpoints retain the deployment's built-in-agent access policy. Direct
resource APIs retain their own authorization; an identity response grants no
additional access.

## Choose tool permissions

Open the **Permissions** popover in agent chat, or the matching control in
**Built-in agent** settings. **Read only** lets the agent inspect accessible DreamLake resources and connected accounts. It can draft text in the conversation. **Full access** enables changes and administrative tools within your existing permissions, including commands on authorized enrolled hosts and authorized actions in connected apps. The selected level applies to your next message. Your browser remembers the choice for your signed-in account across chat and settings.

Arrow keys move focus in the popover. Enter, Space or a click selects the level. Each call still requires the relevant Project grant, host permission or provider authorization. App tool policies can require approval or block an action. See [Connected agent apps](https://docs.dreamlake.ai/agents/apps).

## Diagnose Project access

Human Project ADMIN, the built-in agent's persistent Project delegation, and the
turn's enabled tools are separate permissions. A folder write can be denied even
when the human is an administrator. Use `dreamlake_agent_project_access` with the
verified `namespace` and full `projectId` to inspect these layers. The read-only
diagnostic requires human read access, works without an agent Project grant, and
reports only the caller's own agent. It cannot change access.

A human administrator can explicitly save READ or WRITE delegation for one Project
through the [personal-agent delegation API](https://docs.dreamlake.ai/dev/builtin-agent-harness#explicit-personal-agent-project-delegation).
The model cannot invoke that API's mutations. Enabling write tools alone does not
save a delegation. Organization-scoped turns can use exact delegated Projects in
that organization, subject to current human access; personal or other-organization
grants are not inherited. A diagnostic is a snapshot: execution checks access again.

Memo filing has a separate caller-permission path. Inspect the Memo's current
filing permissions before concluding that a Project tree denial blocks filing.
Keep the requested namespace and verified IDs; never silently create or search in
a personal workspace as a workaround for denied organization access.

The diagnostic accepts `operation: "readProject"` or `"createFolder"` (the
default). Its `accessAction` is null when that operation is available, or one
scoped action identifying the Project and required capability or delegation.
For example, a human administrator with an agent READ grant receives a WRITE
delegation action for folder creation. A caller who also lacks human write
access receives an administrator action instead. The diagnostic never grants
access, and a successful read of it does not imply the requested write is allowed.

## Moving Memos and artifacts

`dreamlake_move_preflight` checks explicit source and destination endpoints.
Each endpoint contains a `namespace` and optional verified `projectId`;
`kinds` contains `note`, `artifact`, or both. Set `createDestinationFolder` when
the requested placement needs a new folder or Bindr. The tool is read-only and
checks the caller's own agent delegation, without enumerating other agents.
Its result is advisory: each mutation still checks current authorization.

Project-only moves do not require namespace ownership authority. Filing a
Memo in another Project retains its owner and existing filings. A missing
folder grant does not establish that caller-authorized Memo filing is denied.
Individual Memo filing/location previews use `dreamlake_notes_move` with
`dryRun: true`; artifact filing uses its discovered canonical API.

For cross-namespace ownership changes, preflight reads both namespaces'
advertised capabilities. Disabled artifact transfer is reported as unsupported,
with `accessGrantWillFix: false`. Memo metadata transfer and preserving transfer
are separate capabilities: the exact per-Memo `dreamlake_notes_transfer_preview`
determines whether its access and filings can be preserved. Preflight never
authorizes a transfer or relaxes that policy. Unknown or inaccessible capability
responses are inspection failures, not proof that a feature is disabled.

Transfer previews carry the ownership and sharing consequences for review.
Submission retains that exact review and idempotency key. Recipient acceptance
remains separate; a pending request is not a completed move. Blocked previews
and pending transfers have distinct tool outcomes even when the HTTP request
succeeds. Readback verifies stable resource IDs, owner, filing/location and
transfer completion; partial results retain their completed steps.

Within a turn, an unchanged request that already received a deterministic
access or unsupported-transfer denial is suppressed before another execution.
A changed request still undergoes normal checks. A relevant successful Project access or transfer capability observation permits
one new attempt when no earlier observation exists. If execution still fails,
rereading the same snapshot does not permit another attempt: relevant access or
capability values must change. Unrelated diagnostics do not reset suppression.
Every permitted attempt still checks authorization at execution. No grant, content or session is changed
by preflight or retry suppression.

## Sending and steering

The built-in composer moves submitted text into the conversation immediately,
before server acknowledgement. A rejected send restores the original input if
it has not been edited; otherwise the unsent message stays visible alongside
the newer draft. Consecutive assistant segments share one text block and one
copy button below it. Message boundaries do not create line breaks; explicit
newlines in the answer do.

While a turn is running, Enter sends a steering message. It keeps the same
conversation, active turn, namespace and capability grants. Messages entered
before the first acknowledgement wait for that turn's identity. The server
stores steering durably and consumes it at model/tool boundaries, before
proposed tools are dispatched or the final answer completes. An already
executing tool finishes before the next model request receives the steering.
A closed turn rejects late steering so the composer can recover the input.

`POST /agent/sessions/:id/steer` accepts `turnId`, `messageId` and `message`
(up to 8,000 characters). The authenticated conversation owner and active lease
are checked transactionally. `messageId` deduplicates retries within the turn;
there are at most 32 steering messages per turn. The chat SSE stream emits
`{type:"steering", messageIds:[...]}` when the messages enter model context.
Admission and the final queue check share a transaction, including across
server replicas. Capability and namespace changes require a new turn.

Memo tool writes commit after their complete arguments arrive; the built-in
agent does not stream partially generated text into the Memo. Read activity
publishes source-hash-bound ranges. `dreamlake_notes_visit` can publish intent
and an address/cursor together, pinned to the read's `baseRevision`; stale
locations are refused. `dreamlake_notes_presence` also reads source-bound human
selections and reports roster, selection and activity availability separately.
Empty activity arrays are not historical inactivity: the markers expire in
seconds. Use `dreamlake_notes_diff` from a retained revision for recent source
changes, without inferring human authorship. Selected editor text carried into
the composer is retained as bounded, untrusted `page.quote` context; its UTF-16
offsets must not be reused as API code-point ranges. See
[agent presence](https://docs.dreamlake.ai/notes/agent-presence).
The chat shows a thinking indicator and tool receipts, not provider reasoning
text.

For other resource operations the model uses this sequence:

1. Call `dreamlake_resource_api_discover` with `family`, `search` or `method`.
   Search matches every whitespace-separated keyword against the family,
   method, route and description; for example, `artifacts POST`. Results
   include operation IDs, methods, route templates, required scopes,
   availability and pagination (`offset`, `limit`, `nextOffset`). An unfiltered
   call also returns all registered resource families.
2. Call discovery again with one `operation` ID to obtain its exact path
   parameters, query, body and declared header schemas, plus `referencedSchemas`
   for any schema references. `executionTool` names the correct gateway, or is
   null for an excluded operation. `granted` describes turn scopes only; it
   does not promise resource access or override an unavailable operation.
3. For project tree operations, use the discovered `dreamlake_resource_project_api_read`, `dreamlake_resource_project_api_write` or `dreamlake_resource_project_api_control` tool and supply `projectId`. The server resolves the actual target and parent through the caller API, rejects a different project, checks the grant before dispatch and again before releasing read results. Project-root and access-management mutations additionally require an ADMIN grant. Project control requires both `resources:control` and `projects:write` scopes. For other operations, call `dreamlake_resource_api_read`, `dreamlake_resource_api_write` or
   `dreamlake_resource_api_control` with that ID, `parameters`, optional
   `query`, `body` and conditional/idempotency `headers`.
4. Inspect the result. After an uncertain mutation, read the affected resource
   or its operation receipt before retrying. A pending command is not complete.

Read scope is available by default. Write and control scopes require the
client's explicit `toolsWrite` capability. Creation, archival, deletion,
sharing, grants and ownership transfer use the canonical resource route's
permissions and preconditions; enabling tools never supplies those permissions.
Destructive actions and outward access changes require the user's stated
intent. Resource discovery alone does not authorize an action.

### Coverage and transport limits

Discovery enumerates each registered supported-method route under a recognized
resource family. Every namespace resource family is discoverable; newly added
families without an execution policy are returned as unavailable, instead of
silently being enabled. Methods are GET, POST, PUT, PATCH and DELETE. The
catalog is therefore the exact operation inventory for that running deployment;
feature-disabled routes are absent rather than promised.

| Resource surface | Built-in interface |
| --- | --- |
| Agents/runnables, versions and execution bindings | Dedicated agent creation and discovered canonical operations |
| Projects, resource filings/bindrs, external mount grants and ownership operations | Discovered canonical operations; existing role checks and transfer review/acceptance still apply |
| Artifact, workflow, pipeline, environment, annotation, library and dataset metadata/lifecycle | Discovered canonical operations |
| Sources, connections, repositories and deletion-operation status | Discovered canonical JSON operations |
| Hosts, machines, jobs, runs, clusters, providers and infrastructure | Discovered read/control operations; the existing user-configured launch-server boundary remains authoritative |
| Memo metadata, creation, archive/delete and sharing | Discovered canonical operations or the existing Memo adapters |
| Memo ownership transfer | Dedicated preview, execute, recipient acceptance and status tools; legacy move remains separate |
| Memo body/sections/diff, duplicate and attached-file operations | Dedicated `dreamlake_notes_*` adapters preserve revisions, read coverage and recovery; discovery returns the adapter guidance |
| Project files/folders/tree nodes | `dreamlake_resource_project_api_read` / `dreamlake_resource_project_api_write` / `dreamlake_resource_project_api_control` support JSON tree operations with an explicit project grant and caller ACL; binary content uses the existing transport |
| Sessions and commands | Existing `dreamlake_session_*` / `dreamlake_sessions_*` adapters preserve durable command identity and bounded transcript reads |
| Memory | Dedicated memory adapters retain per-operation explicit-intent gates |
| Task creation, updates, moves, deletion/restoration, progress events and Memo links | Project-granted resource gateway with canonical body schemas and revision checks; task progress events are bounded JSON |
| Skills, activity, search, social, billing and namespace metadata | Discovered canonical operations where the registered route has a JSON contract |
| Binary upload/download, streaming watch/events, interactive terminals, wildcard proxy routes | Discoverable with CLI/SDK workflow guidance; no raw binary or live-stream transport in model tools |
| Authentication, credentials, OAuth callbacks, Vault, service-account identity, daemon/internal APIs and recursive agent turns | Not executable through the resource gateway |

The raw gateway accepts no caller-selected URL, host, bearer, attribution or
arbitrary request header. Path parameters cannot contain separators or encoded
traversal. Array query parameters are sent as repeated keys. Bodies are limited to 64 KiB and validated against registered route
schemas before dispatch. Routes without a body or query schema cannot accept
that payload through this gateway. Only `if-match`, `if-none-match`,
`idempotency-key` and `x-idempotency-key` headers can be supplied. Responses are
bounded by the existing harness; credential-shaped fields (including snake_case tokens and password hashes) and credential-bearing URLs are redacted. A
truncated response is not a complete resource export.

The API is invoked in process with the signed-in caller's bearer. Each tool
call retains its normal receipt, lease fence and timeout. Mutation receipts
store an input digest rather than the full body. No generic resource operation
can increase the selected agent's tool allowlist.

## Note ownership transfers

These adapters require a server version that includes them and an enabled
Note metadata-transfer backend. Check `GET /agent/tools` for registration;
the preview also checks the server's current transfer capabilities. A tool
appearing in source code does not establish deployment readiness.

Use this workflow when a Note changes owning namespace. Filing a Note in
another project or adding a Bindr is a different operation. The legacy
`dreamlake_notes_move` can still return `NOTE_TRANSFER_UNAVAILABLE`; repeating
that call does not activate the transfer backend.

| Tool | Inputs | Result and authority |
| --- | --- | --- |
| `dreamlake_notes_transfer_preview` | `note`, `source`, `destination` | Read capability. Fetches the canonical plan and preview; returns `ready`, `plan`, `preview` and the exact `review`. Creates no transfer. |
| `dreamlake_notes_transfer_execute` | `review`, `confirm: true` | Note write capability and source authority. Submits the reviewed request once. A pending operation still needs recipient acceptance. |
| `dreamlake_notes_transfer_accept` | `review`, `operationId`, `confirm: true` | Note write capability and current destination acceptance authority. Accepts a matching pending operation; returns an already completed operation without another write. |
| `dreamlake_notes_transfer_status` | `note`, `namespace`, `operationId` | Read capability in the source or destination namespace. Reads one operation without polling or changing it. |

For example, preview with:

```json
{
  "note": "<note-id-from-a-successful-read>",
  "source": "my-workspace",
  "destination": "team-workspace"
}
```

Copy the returned `review` unchanged into execute. It includes the source and
destination slugs, resource ID, expected owner/version, destination namespace
ID, singleton manifest, preview hash and stable idempotency key. Do not build
this object from guessed IDs or generate a replacement key after a failure.

The supported policy is explicit: private visibility, preserved existing
access and preserved external filings, with no hand-selected retained grants.
Inspect the preview's blockers and filing counts. `ready` requires an executable
plan, no blockers and no detached filings. Other access-policy choices require
the ownership interface; the agent does not discard grants to make a move work.

Execute and acceptance are separate actions under the user's intent. `confirm`
is a tool argument acknowledging the reviewed request, not an authorization
grant. Only `moved: true` with a completed operation and `ownerCommitted: true`
establishes completion. Pending, rejected, expired, cancelled or recovery states
must be reported as such.

If submission or acceptance loses its response, preserve the review and read
status with the known operation ID. If the ID is unknown, inspect outgoing
ownership transfers through discovery to locate the request before considering
an identical idempotent resend. Never automatically retry a POST, copy Note
content as a fallback, or obtain a fresh plan/key to conceal uncertainty.
Status remains available when the metadata adapter is disabled; execution and
acceptance refuse that disabled capability.

## Folders and tasks

Folder creation already uses the project gateway. Discover `family: "nodes"`
with `method: "POST"`, inspect the selected `/nodes` schema, then call
`dreamlake_resource_project_api_write` with the granted `projectId` and:

```json
{
  "operation": "<discovered-POST-nodes-operation>",
  "projectId": "<granted-project-id>",
  "body": {
    "namespace": "my-workspace",
    "project": "research",
    "kind": "folder",
    "name": "/Research/Reviews"
  }
}
```

Omit `parentId` for the project root. If supplied, it must identify an existing
folder or episode in the same granted project. The project node ID is not a
folder parent. Both caller permission and the service-account project grant
are required; destination and grant checks also protect rename/delete operations.

Find Task operations with `search: "tasks"`, because their routes are nested
under the `projects` family. Creation, update, move, delete, restore, progress
events and Memo links expose their canonical JSON body schemas. Use the
operation's project gateway and exact schema, including required revisions.
Read the current Task before an update; a stale revision requires a new read.
Task events are paginated JSON records. Note SSE events and other live streams
remain excluded from the generic gateway.

## Other recent resource capabilities

These features already use canonical registered operations; they do not need
duplicate dedicated tools. Inspect the schema in the running deployment first.

| Request | Discover and use |
| --- | --- |
| Create or revise artifact content | The discovered Artifact `POST /namespaces/:slug/artifacts/:artifactId/apply` operation takes `contentBase64` and appends a version under the resource write grant. Its response includes the resulting version. |
| Share only an artifact's most recent version | Find the artifact catalog POST operation and set `shareLatestOnly: true`. Add `share: true` only when the user also requested issuing a share link. This does not upload a new artifact version. |
| Rename an annotation | Find the annotation PATCH operation and set `title`; unchanged visibility should be omitted. Annotation share operations remain separate. |
| Add a resource to a Bindr in another project | Discover Bindr membership operations and use the exact resource and Bindr identifiers. An association does not transfer resource ownership or imply formal project filing. Canonical namespace and access checks still apply. |
| Create an agent with an instruction Note and skill folders | Use `dreamlake_agents_create` as documented above. A definition is not a running session. |

## Host inventory and partial search

`dreamlake_providers_list` reads the acting namespace’s compute provider catalog
with the caller’s provider-read permission. It returns provider IDs, names and
kinds, the total count and the next page. Check this catalog separately from
registered Hosts when assessing machine launch prerequisites. Launch-server
identity and readiness require their own verification.

`dreamlake_hosts_list` accepts `prefix`, `search`, `page`, `pageSize`,
`offsetWithinPage` (default 0) and `archived`. `prefix` filters the canonical catalog. `search` performs a literal,
case-insensitive match within **one returned page**, over names, IDs, verified
hostnames and observed IP addresses. Continue with `page: nextPage` and
`offsetWithinPage: nextOffset`, preserving all other inputs, even after zero
matches. A byte-limited result can continue within the same catalog page;
`nextOffset` returns to 0 for the next page. Both fields are null when exhausted.
`total` is the catalog count, not the number of search matches.

Both list and `dreamlake_host_get` return allowlisted catalog and enrollment
metadata, including verified hostname, network observations and system details.
Each host returns at most 20 enrollments, bounded further to 24 KiB, with at
most eight addresses per enrollment. `enrollmentsTruncated` and
`network.addressesTruncated` identify omissions; `inventoryOmitted` summarizes
them for the scanned rows. `searchIncomplete` signals a continuation or omitted inventory.
This is a bounded lookup, not an exhaustive network search.

Unknown/unverified inventory remains null. Network observations carry
`observedAt` and freshness (`fresh` for at most 60 seconds, otherwise `stale`).
IPs are validated observed addresses, not inferred from hostname spelling.
Online or fresh inventory does not prove SSH or workload readiness.

## Host connection grants

`dreamlake_host_access_grants`, `dreamlake_host_access_grant` and
`dreamlake_host_access_revoke` manage who may connect to a host you
own and read its [machine readings](https://docs.dreamlake.ai/lakeshore/hosts/metrics#shared-hosts), using [the same owner-only grant](https://docs.dreamlake.ai/lakeshore/hosts/browser-terminal#share-a-machine-with-a-teammate)
as Compute. Listing needs only the default host read scope and returns
`grants` (people) and `teamGrants` (organization teams). Granting and
revoking need **Full access** for the message, and run only when you name the
person or team and the machine. `dreamlake_host_access_grant` takes exactly one
of `grantee` (a username) or `team` (a team slug). A grant takes an exact `hostId` and `enrollmentId`, so
the agent asks which Unix account when a host has several, and says that the
member will act as that account; for a team, that this applies to every
current direct member and to anyone added later (parent teams are not
included). The generic resource API tools refuse the
`access-grants` routes and point to these tools. Background (durable) turns
cannot use them.

An unconfirmed grant or revoke is reported as uncertain, and the agent lists
grants before doing anything else rather than repeating the call. A revoke
reports `closedConnections`, `stillAuthorizedConnections` (kept because the
same person holds another current grant to that enrollment) and
`unconfirmedConnections`; while
`closeConfirmed` is false, the agent reports the connections as possibly open
until `unconfirmedUntil`, not as closed.

The agent files a host you own in a Project of the same namespace with
`dreamlake_resource_project_api_write` (`resourceType: "host"`), which needs an
explicit service-account grant on that Project. Filing is placement only and
gives Project members no host access; see
[Hosts in Projects](https://docs.dreamlake.ai/lakeshore/hosts/browser-terminal#hosts-in-projects).
`dreamlake_host_move_preview` reports `projectPlacements` when the host is
filed; applying the move unfiles it from that many Projects without deleting
the host, and the agent says so before applying.

## Connections and credential entry

Use the credential-entry tools below when the deployed assistant offers them.
If they are not offered, create or reconnect through the signed-in Connections
page instead; this reference does not establish their availability in every deployment.

Connection reads — `GET /namespaces/:ns/connection-connectors`, the list,
detail, Check and affected Sources — and credential-free create (an auth kind
whose mode is `none`) are discovered canonical operations, available to the
namespace's credential managers. The gateway refuses any tool call that carries
a credential, so a Connection that needs a secret is created or reconnected by
**browser credential entry**:

- `dreamlake_connection_entry_begin` (`resources:write`) starts an entry in the
  turn's namespace for one connector and `fields` auth kind (create), or for one
  Connection at its current settings revision (reconnect). It returns an
  operation id and a link to the Connections page; the label is only a
  suggestion the user may edit.
- The user opens the link, signed in, and enters the secret in the existing
  form. The entry is bound to that user and namespace, single use, and expires
  after 30 minutes; the connector, auth kind, target and revision cannot be
  changed there.
- `dreamlake_connection_entry_status` (`resources:read`) returns `pending`,
  `succeeded` (with the Connection id and masked metadata), `cancelled` or
  `expired`. It works after a reload or a later turn.
- `dreamlake_connection_entry_cancel` (`resources:write`) closes a pending
  entry.

Neither the arguments, the results nor the receipts of these tools contain a
credential. The entry routes are not reachable through the generic gateway.
Background and delegated runs, and service accounts, cannot manage Connections,
and Connections cannot be granted to an agent service account.

## Recovering from tool errors

Canonical schema failures now return a bounded `validation` object to the
model: operation ID, input part, schema path, keyword and, where applicable,
the missing schema property or numeric limit. Values, unknown property names,
raw API errors and document bodies are omitted. These details are not added
to browser tool-event telemetry.

| Error | Meaning and next step |
| --- | --- |
| `agent_resource_body_invalid`, `agent_resource_query_invalid` | No API request dispatched. Rediscover the exact operation, resolve `referencedSchemas` and correct the indicated constraint. Do not repeat identical arguments. |
| `agent_resource_tool_mismatch` | The operation uses another gateway, such as write instead of read or a project-granted gateway. Inspect `executionTool`; use it only if offered this turn. |
| `agent_resource_schema_missing` | A supplied body/query has no declared canonical schema. Use the documented dedicated adapter or report the specific capability gap. |
| `agent_resource_operation_unavailable` | Follow `dedicatedTools` and `guidance`; do not bypass an excluded transport or authorization boundary. |
| `agent_tool_scope_not_granted` | The current turn lacks the capability. This does not establish whether the underlying API exists. |
| `NOTE_TRANSFER_UNAVAILABLE` | Use the reviewed transfer workflow when available; do not repeatedly call legacy move or remove access grants. |
| `note_transfer_outcome_unknown` | The transfer may have changed state. Preserve the original review/key and inspect status before any further mutation. |

When reporting an error, retain its exact code, tool, time and available
receipt/request IDs. A 404 alone does not distinguish an incorrect identifier,
wrong namespace, unavailable route or denied visibility. Inspect authorized
resource discovery before attributing it to a missing tool.

## Reading public posts

For a public X status URL, `dreamlake_web_read` retrieves the single post
from X’s official oEmbed endpoint and returns its canonical permalink and
author. Reading a public Thread Reader index exposes up to eight candidate
post links in order. Each post can then be checked at X. The author’s numbered
parts can establish the extent of a numbered series. A WeChat verification
redirect ends the read with `agent_web_read_challenge`.

A YouTube watch-page read can return the title, public description and links
from the description for the requested video. The publisher may link its
download page there. Video playback restrictions still apply.

## Files in the current Source

Resolve the Source shown in the active panel or page to its namespace and ID.
A managed Source can receive a direct public HTTPS file with
`dreamlake_files_download_url`. The tool creates a new path, verifies the
stored bytes and returns the size, revision and SHA-256 digest. The limit is
8 MiB. Redirects and authenticated downloads are unsupported. A social video
page requires a separate media URL, and playback needs a player check.

When a publisher offers a downloadable copy of a YouTube or X video, pass
its publisher page as `url` to `dreamlake_web_read` and the platform permalink
as `mediaFor`. Verify the publisher identity when selecting the page. The matching section, article or figure must contain one video,
the platform link, and same-origin file links that are also sources on that
player. The returned links retain the publisher’s rendition labels. Choose a
matching format and language within the Source size limit. Ambiguous blocks
return `agent_web_read_media_unmatched`.

Use `dreamlake_files_mcap_summary` on a managed uncompressed MCAP up to
8 MiB to count messages, list topics and read the log-time span in nanoseconds.
A malformed or incomplete recording produces an error. Empty recordings have
a zero count and null timestamps.

## Thread links in the local MCP adapter

The local MCP adapter exposes `thread_open_url`. Pass a `namespace` to
open its Threads list. To open a known Thread, pass its `id` with an optional
`session` selector. The tool returns a browser URL and the
storage type `browser-local`. It does not inspect or change saved layouts.

## Remote shell execution

The built-in agent offers `dreamlake_exec` (equivalent to `dl exec`) and
`dreamlake_ssh` (an interactive login shell, equivalent to `dl ssh`). Both use
an exact `hostId` and `enrollmentId`, the enrolled host key, and the caller's
existing SSH connection permissions. Execution happens on that host, never in
the API server's local shell. The target needs POSIX and Python 3.

Full access enables the `hosts:execute` turn scope. API clients may instead
supply `capabilities: { "hostExecution": 1 }`. Read-only, session-control and
host-inventory access alone do not enable it. Each start, read, write, resize
and cancel resolves current caller access again and obtains a fresh bounded
SSH delegation. Revocation prevents subsequent access; it does not prove that
a previously detached remote process has stopped. An agent definition must
also include the tools in its allowed tool list. These are foreground agent
tools; asynchronous remote processes are separate from durable agent jobs.

For `dreamlake_exec`, choose exactly one of `command` or `argv`:

```json
{
  "hostId": "HOST_ID",
  "enrollmentId": "ENROLLMENT_ID",
  "requestId": "build-1",
  "command": "printf '%s\\n' \"$PROJECT\" | head -1",
  "cwd": "/workspace/project",
  "env": { "PROJECT": "example" },
  "mode": "streaming",
  "yieldTimeMs": 1000
}
```

`command` runs `/bin/bash -lc`, preserving pipes, redirects and expansion.
`argv` passes literal arguments without expansion. `cwd` is absolute and `env`
overrides the remote environment. `pty: true` requests a terminal; stdout and
stderr then share the PTY stream. `dreamlake_ssh` always uses a PTY and the
remote login shell. `cols` and `rows` set its initial size.

Both modes return `executionId`, `state`, `exitCode`, `signal`, ordered `output`
records, `nextCursor`, `hasMore` and `truncated`. Output records contain a
`stream` and base64 `data`; these preserve exact bytes across arbitrary UTF-8
and binary chunk boundaries. `stdout` and `stderr` are bounded convenience
previews, with `previewTruncated` when shortened. Streaming emits live
`execution_output` SSE events for the returned batch and yields after the
requested wait (0–10000 ms; default 1000); async uses zero wait. SSH connection
setup still occurs before either result. Continue with the same lifecycle:

| Tool | Inputs beyond the exact host/enrollment |
| --- | --- |
| `dreamlake_execution_read` | `executionId`, `cursor` (default 0), optional `mode` and `yieldTimeMs` |
| `dreamlake_execution_write` | `executionId`, stable `operationId`, `chars` and/or `eof` |
| `dreamlake_execution_resize` | `executionId`, stable `operationId`, `cols`, `rows` |
| `dreamlake_execution_cancel` | `executionId`, stable `operationId` |

Use `nextCursor` for the next read; `hasMore` means another retained page
exists. Input acceptance queues bytes to remote stdin; it does not prove the
program consumed them. EOF closes pipe stdin or sends Ctrl-D to a PTY.
Cancellation requests SIGTERM followed by SIGKILL after two seconds. Read until
a terminal state is observed; closing a transport is not process termination.
Detached descendants can remain after the observed shell exits.

`timeout` limits the remote process lifetime, independently of the tool wait:
1–1800 seconds, default 1800. Handles survive agent-turn completion and API
restarts while their private host-side state under `/tmp` remains. Host reboot,
temporary-file cleanup, or supervisor loss can make a handle unavailable or
unknown; do not infer completion or restart the command. Retained output is
bounded to 8 MiB of encoded records per execution and reads are paged. Each
caller/namespace/host/enrollment binding retains at most 256 execution records;
at most eight may be active (`execution_concurrency_limit`). History
exhaustion reports `execution_history_limit` without launching another command.
State is owned by the enrolled Unix account, whose existing access boundary
also applies to these files.

A durable server reservation permits only the first admission to create a
remote process. It has no automatic expiry and stores only identity and a
request digest. A lost admission acknowledgement or missing host state fails
closed instead of dispatching again.

Choose a stable `requestId` before starting. After an uncertain response, reuse
that ID and identical inputs, or read the checkpointed `executionId`; changed
inputs conflict instead of launching a second command. Reuse `operationId`
after an uncertain stdin/control call, never a fresh ID as an automatic retry.
Missing state is uncertainty, not permission to relaunch. Tool receipts retain
identifiers and status, not commands, environment values, stdin or raw output.
Output is not automatically indexed. The browser's output preview is transient;
use the handle and cursor to read it again.
