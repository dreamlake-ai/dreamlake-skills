<!-- generated from https://docs.dreamlake.ai/agents/resource-tools.md at 0.1.118 967fe678; do not edit -->

# Resource APIs in the built-in agent

The built-in agent's resource API catalog is collected from the
server's registered routes, including routes enabled by deployment flags. It
is not a separately maintained copy of the HTTP API.

The built-in agent can create **agent definitions**, which are first-class
runnables rather than sessions. Ask, for example:

> Create a Reviewer agent in my project, using this note as its instructions
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

For other resource operations the model uses this sequence:

1. Call `dreamlake_resource_api_discover` with `family` or `search`. Results
   include operation IDs, methods, route templates, required scopes,
   availability and pagination (`offset`, `limit`, `nextOffset`). An unfiltered
   call also returns all registered resource families.
2. Call discovery again with one `operation` ID to obtain its exact path
   parameters, query, body and declared header schemas.
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
| Note metadata, creation, archive/delete and sharing | Discovered canonical operations or the existing Note adapters |
| Note body/sections/diff, duplicate and attached-file operations | Dedicated `dreamlake_notes_*` adapters preserve revisions, read coverage and recovery; discovery returns the adapter guidance |
| Project files/folders/tree nodes | `dreamlake_resource_project_api_read` / `dreamlake_resource_project_api_write` / `dreamlake_resource_project_api_control` support JSON tree operations with an explicit project grant and caller ACL; binary content uses the existing transport |
| Sessions and commands | Existing `dreamlake_session_*` / `dreamlake_sessions_*` adapters preserve durable command identity and bounded transcript reads |
| Memory | Dedicated memory adapters retain per-operation explicit-intent gates |
| Skills, activity, search, social, task, billing and namespace metadata | Discovered canonical operations where the registered route has a JSON contract |
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
