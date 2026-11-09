<!-- generated from https://docs.dreamlake.ai/agents/resource-tools.md at 0.1.132 e997a2d0; do not edit -->

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
| Task creation, updates, moves, deletion/restoration, progress events and Note links | Project-granted resource gateway with canonical body schemas and revision checks; task progress events are bounded JSON |
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
events and Note links expose their canonical JSON body schemas. Use the
operation's project gateway and exact schema, including required revisions.
Read the current Task before an update; a stale revision requires a new read.
Task events are paginated JSON records. Note SSE events and other live streams
remain excluded from the generic gateway.

## Other recent resource capabilities

These features already use canonical registered operations; they do not need
duplicate dedicated tools. Inspect the schema in the running deployment first.

| Request | Discover and use |
| --- | --- |
| Share only an artifact's most recent version | Find the artifact catalog POST operation and set `shareLatestOnly: true`. Add `share: true` only when the user also requested issuing a share link. This does not upload a new artifact version. |
| Rename an annotation | Find the annotation PATCH operation and set `title`; unchanged visibility should be omitted. Annotation share operations remain separate. |
| Add a resource to a Bindr in another project | Discover Bindr membership operations and use the exact resource and Bindr identifiers. An association does not transfer resource ownership or imply formal project filing. Canonical namespace and access checks still apply. |
| Create an agent with an instruction Note and skill folders | Use `dreamlake_agents_create` as documented above. A definition is not a running session. |

## Host inventory and partial search

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
