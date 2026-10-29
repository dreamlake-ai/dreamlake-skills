<!-- generated from https://cli.dreamlake.ai/runnable-api.md at 0.94.0 cbe0f3f; do not edit -->

# Runnable registry API

All routes are authenticated and namespace-scoped under
`/namespaces/{namespace}`. Server permissions remain authoritative.

| Method / path | Purpose |
| --- | --- |
| `GET/POST /repos` | List/register a repository pointer. |
| `GET /repos/{repo}` | Read a repository by ID or name. |
| `GET/POST /repos/{repo}/snapshots` | List/register immutable archive pointers. |
| `GET/POST /runnables` | List/register a mutable definition head. |
| `GET/PATCH /runnables/{runnable}` | Read/save a definition. |
| `GET/POST /runnables/{runnable}/versions` | List/register immutable source versions. |
| `GET /runnables/{runnable}/versions/{sha256}` | Read exact source bytes and version metadata. |

Snapshot registration is idempotent by repository plus commit. Source registration
is idempotent by runnable plus SHA-256 of source. A 200 existing receipt is not
permission to overwrite it; compare requested fields. No source-version delete
endpoint exists. Registry heads have a soft-delete API; a permanent-release
retention policy must be reconciled before exposing deletion as a release action.

UDF example:

```json
{"module":"recipes","qualname":"add","kind":"udf",
 "metadata":{"repo_id":"REPO_ID","snapshot_id":"SNAPSHOT_ID",
 "source_file":"tasks/math.py","entrypoint":"tasks.math:add"}}
```

Agent example:

```json
{"module":"recipes","qualname":"triage","kind":"agent",
 "markdown":"Inspect {{ target }}.",
 "metadata":{"agent":{"projects":["research"],
 "arguments":[{"name":"target","type":"string","required":true}],
 "context":[{"kind":"repo","repo":"udf-recipes","snapshot":"SNAPSHOT_ID","mode":"ro"}]}}}
```

Agent prompts/parameters are mutable head metadata; a source version does not
atomically version that mutable head. PATCH currently has no atomic compare-and-swap
precondition. Editor readback detects observed concurrent changes but cannot
eliminate the race between its preflight read and PATCH. A save is neither a run
nor publication. Context references do not grant access; runtime authorization
and materialization remain separate from storing these declarations.

## Execution vocabulary

A repo names the code project; a snapshot pins a tree; a UDF/agent identifies
what to invoke; a run identifies one execution. The proposed bundle runnable
reuses repo/snapshot records and adds an execution entrypoint. Relaunch must
record the snapshot, resolved runtime, inputs, target, and resource versions.
Do not substitute declaration snapshot IDs for execution-control-plane snapshot
IDs; those APIs currently have separate records.

## Nymph, hosts, and Jobs

Keep these receipt types distinct:

| Execution path | Identity / evidence |
| --- | --- |
| `dreamlake launch` | Queue invocation ID; placement requests a queue. |
| `dreamlake run --target` | Managed host-run receipt; selects a host and exact enrollment when required. |
| `dreamlake jobs register/report` | External job observation; not proof that DreamLake launched or verified the process. |
| Provider worker provisioning | Durable provisioning request; acceptance is not workload readiness. |

A future unified execution receipt needs `execution_kind`, typed linked IDs,
requested placement and resolved worker/enrollment. Relaunch creates a new
execution with fresh authorization, capability/readiness checks and a new request
identity. Recovering the same uncertain submission must reuse its original
identity and exact payload. Retiring, archiving or revoking a host cannot delete
retained runnable code. Code retention after repository deletion remains an
explicit policy decision for receipts that outlive the repository.

## Workflow composition

A workflow version retains its orchestration program or graph and a dependency
lock of exact UDF versions. A workflow run is one execution of that version;
its receipt links each node/call to the resulting invocation or host-run ID.
Changing a UDF must not change an existing workflow version.

Existing interfaces are distinct:

| Representation | Command | Current behavior |
| --- | --- | --- |
| JavaScript program | `workflow create NAME --file workflow.js`; `workflow update NAME --file workflow.js` | Creates script-based workflow versions. |
| WorkflowSpec v1 graph | `workflow push workflow.json` | Validates schema/graph rules and uploads a new version through its separate storage path. |
| Execution trace | `workflow push-run NAME wf_run.json` | Records an observed run; does not execute the workflow. |

The common pinned-UDF composition contract remains planned. It must retain exact
orchestration bytes/digest, full UDF hashes and entrypoints, input/output wiring,
runtime requirements, and verified delivery bindings. Resolve aliases or `latest`
before retaining a version. Script and graph histories are not currently joined;
do not interchange their version IDs. A `.dreamrc` workflow declaration requires
an explicit schema before implementation. See [workflows](cli-workflows.md).
