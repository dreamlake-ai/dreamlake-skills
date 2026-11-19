<!-- generated from https://cli.dreamlake.ai/runnable-api.md at 0.133.1 82925b5; do not edit -->

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

Agent prompts, README templates (`metadata.readme`), and runtime configuration
are editable draft fields. PATCH accepts `expectedUpdatedAt` and rejects stale
updates. Publishing captures the complete definition separately from executable
source versions. Context references never grant access.

## Whole-agent versions

Available in CLI and TypeScript SDK 0.130.0+ with the definition-version backend.

```bash cli-help="runnable definition publish"
dl runnable show Reviewer --namespace team --json
# Use updatedAt from the draft you reviewed:
dl runnable definition publish Reviewer --namespace team --expected-updated-at 2026-11-16T12:00:00.000Z --label v1
```

```bash cli-help="runnable definition list"
dl runnable definition list Reviewer --namespace team --page 1 --page-size 20
```

```bash cli-help="runnable definition show"
dl runnable definition show Reviewer DEFINITION_SHA256 --namespace team
```

```bash cli-help="runnable definition activate"
dl runnable definition activate Reviewer DEFINITION_SHA256 --namespace team --expected-updated-at 2026-11-16T12:00:00.000Z
```

Replace the example timestamp and hash with current returned values. Every command
emits JSON. Publish captures and activates the saved draft. Activate selects a
previous immutable release and preserves the draft. Stale writes return 409;
read current state before retrying. Optional labels are display names; hashes
identify content. Identical definitions reuse the original release and label.

```typescript
const agents = client.runnables('team');
const draft = await agents.get('Reviewer');
const release = await agents.publishDefinition(draft.id, {
  expectedUpdatedAt: draft.updatedAt, label: 'v1',
});
const history = await agents.definitionVersions(draft.id, {page: 1, pageSize: 20});
const frozen = await agents.definitionVersion(draft.id, release.version);
const current = await agents.get(draft.id);
await agents.activateDefinition(draft.id, release.version, {expectedUpdatedAt: current.updatedAt});
```

These wrap `/runnables/{id}/definition-versions` (GET history, POST publish),
`/definition-versions/{hash}` (GET detail), and
`/definition-versions/{hash}/activate` (POST). `publishedDefinitionVersion` points
to the active release. Existing `/versions` and `latestVersion` still refer to
executable source. Release bodies include frozen prompts and source revisions;
current source permissions are checked on every detail read and execution.

For built-in execution, `client.agent.definitions(namespace, {view: 'draft'})`
selects drafts explicitly; omission prefers published releases and supports
unpublished legacy agents. Pass a catalog selection's `id`, `revision`, and
`version` as `agentDefinition` to `client.agent.chat`. See
[agent authoring](https://docs.dreamlake.ai/agents/authoring) for snapshot scope,
limits and access behavior.

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
| `dl launch` | Queue invocation ID; placement requests a queue. |
| `dl run --target` | Managed host-run receipt; selects a host and exact enrollment when required. |
| `dl jobs register/report` | External job observation; not proof that DreamLake launched or verified the process. |
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
