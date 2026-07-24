# WorkflowSpec v1 — field reference

Condensed from the adopted I/O & configuration specification. The JSON Schema
(`workflow-spec.schema.json`) is the machine contract; this page is the
human-readable companion with the semantic rules the schema cannot express.

## Envelope

| Field | Constraints |
|---|---|
| `version` | literal `1` |
| `name` | `^[a-z0-9][a-z0-9._-]{0,63}$` |
| `description` | ≤2000 |
| `stages` | 1–32, ordered — **array order is the spine** |
| `nodes` | ≤200 |
| `edges` | ≤400, acyclic |
| `defaults` | `{model?, provider?, queue?}` fallbacks for uda/compute |

## Data types (closed lattice)

`artifact` (root = any; accepts every subtype) · `file` · `directory` (blob,
single vs multipart; format is metadata) · `table` (schema-carrying *shape*) ·
`dataset` (versioned *product*) · `model` · `metrics` · `samples`
(media/episode collections). **Collection-like** (samplable): `samples`,
`table`, `directory`.

Edge validity: `type(fromPort) === type(toPort)` or `toPort.type === 'artifact'`.
An `artifact` output into a typed input is a warning (unproven cast).

## Ports & fan-in

- Port: `{name (^[a-z0-9][a-z0-9_-]{0,31}$), type, collect?}`. Defaults when
  omitted: `in: artifact` / `out: artifact`.
- **Output ports broadcast** (any number of outgoing edges).
- **Input ports take exactly ONE edge**, unless:
  1. `collect: true` — ≥1 edges from same-type producers, delivered as an
     ordered collection (edge declaration order), or
  2. **XOR-merge** — sources are mutually exclusive branches (ports of one
     condition/switch, or transitively: sources dominated by disjoint branches
     of a common exclusive gateway).
- Small inline values are node config (`params`), never ports.

## `stage`

`{id, title ≤120, detail? ≤2000}`. No data ports. Empty stages legal.

## `compute`

Ports user-declared (the UDF's typed interface); `collect` allowed.

| Field | Notes |
|---|---|
| `compute.udf` | `^[a-z0-9_]+(\.[a-z0-9_]+)+$` |
| `compute.params` | static UDF args, ≤64 keys, values string/number/boolean/JSON |
| `compute.provider` | ProviderRef (below) |
| `compute.dispatch` | `direct` \| `daemon` (defaults per launcher) |
| `execution` | retry/timeout/cache (below) |

## `uda`

Ports user-declared. Output validated against out-port type; `output_schema`
additionally validates the structured result.

| Field | Notes |
|---|---|
| `uda.instructions` | 1–8000; SYSTEM prompt — behavior, not per-run task data |
| `uda.description` | ≤500; when-to-delegate routing metadata |
| `uda.model` | falls back to `defaults.model` |
| `uda.tools` | ≤32 tool names — capability grants, own field |
| `uda.permissions` | grant strings (registry below); may be `[]` |
| `uda.max_turns` | 1–1000 |
| `uda.output_schema` | JSON Schema (2020-12) |
| `uda.provider` XOR `uda.queue` | exactly one |
| `execution` | retry + timeout only — **cache forbidden** (non-deterministic) |

### Permission registry

`dreamlake.datasets.{read,create,update,delete,release}` ·
`dreamlake.nodes.{read,create,update,delete}` ·
`dreamlake.artifacts.{read,create,update,delete}` ·
`dreamlake.providers.{read,create,update,delete}` ·
`dreamlake.workflows.{read,create,update,delete,run}` ·
`lakeshore.queues.{submit,consume}:<queue>` (scope required).
Optional `:scope` narrows any grant. Unknown domain/resource/verb = error.
`edit`/`remove` don't exist; `ToolUse.*` belongs in `tools`.

## `sampler`

Fixed signature: ONE input, type ∈ {samples, table, directory}; output derived
(same type — type-preserving). Never declare `outputs`. Determinism: same
input + same `seed` ⇒ same sample; no seed ⇒ non-reproducible (run records
the effective seed).

| Strategy | Required | Optional |
|---|---|---|
| `bernoulli` | `fraction` (0,1] | `min_size` ≥1 (floor extension — wins over quota), `seed` |
| `random_n` | `size` ≥1 | `with_replacement` (default false), `seed` |
| `stratified` | `stratify_by`, `fraction` XOR `fractions` (per-stratum map ≤256) | `min_size` (per-stratum), `seed` |
| `first_n` | `size` ≥1 | — (`seed` is an ERROR — head/LIMIT, not sampling) |

## `control`

Fixed signature: ONE typed input `in: T`; derived, type-preserving out ports.
Never declare `outputs`.

| Type | Out ports | Config |
|---|---|---|
| `condition` | `true: T`, `false: T` | `expression` ≤2000 (engine-defined, opaque v1) |
| `switch` | one per case + `default: T` | `cases` 1–16 `{name ≠ default/in, expression}`; first match wins |
| `loop` (while) | `out: T` | `until` (required), `max_iterations` 1–1000 (required) |
| `loop` (foreach) | `out: T` | `over` (required), `max_concurrency` 1–256 (default 8); input must be collection-like |
| `approval` | `out: T` | `approvers?` ≤32, `message?` ≤2000, `timeout_s?` ≥60 — timeout ⇒ `error`, never auto-approve |

## `ProviderRef`

`provider` (named, server-stored) XOR `launcher` (`SSH|SLURM|EC2|GCE|Kube`) +
`kwargs`. Per-machine: `instance_type`, `image_id`, `image`, `partition`,
`time_limit`, `resources {cpu, gpu, mem}`, `runner (process|docker)`,
`dispatch (direct|daemon)`. **Secret guard**: kwargs keys matching
`/pem|key|secret|token|password/i` must be `{"$secret": "<name>"}`.

## `execution` (compute & uda)

```json
{
  "retry": { "max_attempts": 3, "retry_on": "transient",
             "backoff": { "initial": "10s", "factor": 2.0, "max": "5m" } },
  "timeout": "1h",
  "cache": { "enabled": true, "version": "1" }
}
```

`max_attempts` = TOTAL attempts (1 = no retry). `timeout` per attempt.
Durations `^[0-9]+(ms|s|m|h)$`. Cache is content-based (inputs + config) with
a user-bumpable `version`; **compute only**.

## `outputBinding` (any member node)

`{kind: dataset|artifact|node|bindr, project (required unless artifact),
pathTemplate}` — template vars: `{workflow} {runId} {nodeId} {stageId} {date}`.
