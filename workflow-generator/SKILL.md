---
name: workflow-generator
description: >
  Generate a DreamLake Workflow v2 spec — a JSON file of stages, typed member
  nodes (compute/UDF, uda agents, samplers, control flow) and typed data
  edges — from a user's natural-language description of a data-production,
  labeling, or training goal. Use when the user asks to "create/generate/design
  a workflow", "turn this description into a workflow", or "scaffold stages and
  nodes" for data curation, annotation, or RL data production. Output must
  validate against reference/workflow-spec.schema.json.
---

# DreamLake Workflow generator

You produce **one JSON file**: a complete `WorkflowSpec` (version 1). It has two
consumers, both essential:

1. **The canvas** renders it — stages as hub nodes on a spine, members fanning
   out from their stage, typed edges between members.
2. **The validator/engine** executes it — every rule below is (or will be)
   machine-enforced. A spec that renders but violates a rule is not done.

Full field tables: `reference/schema.md`. Machine schema:
`reference/workflow-spec.schema.json` (validate your output against it —
mentally at minimum, with a JSON Schema validator when available). Worked
examples: `reference/examples.md`.

## Mental model

A workflow is a **spine of ordered stages** (phases of the work — 2–5 for most
goals). Each stage owns **member nodes** that do the work. **Data edges**
connect member outputs to member inputs — never stages — and may cross stage
boundaries. Stage order = array order. Stages group; they are NOT barriers.

Four member families — pick the right one:

| Family | Use for | Never for |
|---|---|---|
| `compute` | deterministic work: filter, transcode, extract, merge, train, publish — anything that is a UDF | judgment calls |
| `uda` | agent judgment: labeling, captioning, quality review, curation decisions | deterministic transforms |
| `sampler` | statistical subset selection | anything that isn't sampling |
| `control` | routing (condition/switch), iteration (loop), human gates (approval) | data transformation |

## Authoring procedure

1. **Parse the goal** → name the workflow (`^[a-z0-9][a-z0-9._-]{0,63}$`),
   write 1-line `description`.
2. **Stages**: decompose into 2–5 phases (e.g. Collect → Annotate → Publish).
   ids/titles short; `detail` optional one-liner.
3. **Members per stage**: 1–4 typical. Every workflow that labels or judges
   data should have at least one `uda`; every one that trains or publishes
   should gate publication behind an `approval` control node.
4. **Type the ports**: choose from the closed lattice —
   `artifact` (root/any) · `file` · `directory` · `table` · `dataset` ·
   `model` · `metrics` · `samples` (media/episode collections — the workhorse
   for robot data). Small inline values (thresholds, flags) are **`params`
   config, never ports**.
5. **Wire edges**: member → member, forward through the flow. Edge types must
   match end-to-end (equal, or into an `artifact` input).
6. **Self-check** against the rules below; fix before delivering.

## Rules that generators get wrong (each is validated)

- **One inbound edge per input port.** Fan-in requires either
  `"collect": true` on the port (N same-type producers → ordered collection)
  or mutually **exclusive** sources (branches of condition/switch — at most
  one fires).
- **Sampler**: exactly one input, type ∈ {`samples`,`table`,`directory`};
  do NOT declare outputs (derived, same type). Strategies:
  `bernoulli {fraction (0,1], min_size?, seed?}` ·
  `random_n {size, with_replacement?, seed?}` ·
  `stratified {stratify_by, fraction XOR fractions, min_size?, seed?}` ·
  `first_n {size}` — first_n takes NO seed (it's LIMIT, not sampling).
- **Control nodes are type-preserving pass-throughs**: single typed input; do
  NOT declare outputs. `condition` → ports `true`/`false`; `switch` → one port
  per case **plus `default`** (route every case's edge AND a default edge);
  `loop` is strict: `{mode:"while", until, max_iterations}` (both required) or
  `{mode:"foreach", over, max_concurrency?}`; `approval` pauses until a human
  decides — timeout means error, never auto-approve.
- **uda**: `instructions` is the SYSTEM prompt (behavior, not the task data);
  `tools` is its own list (NEVER `ToolUse.*` permission strings);
  `permissions` use `domain.resource.verb` grants from the registry
  (`dreamlake.datasets.read|create|update|delete|release`,
  `dreamlake.nodes.*`, `dreamlake.artifacts.*`, `dreamlake.providers.*`,
  `dreamlake.workflows.*|run`, `lakeshore.queues.submit|consume:<queue>`) —
  verbs `read/create/update/delete` + registered custom verbs; NEVER
  `edit`/`remove`. Exactly ONE of `queue` | `provider`. `execution.cache` is
  FORBIDDEN on uda (agents are non-deterministic).
- **compute**: `udf` is `module.path.func`; static arguments go in
  `compute.params`; provider secrets must be `{"$secret":"name"}` markers —
  plaintext credentials are an error. `execution` (optional):
  `retry {max_attempts 1–10 (1 = no retry), backoff {initial, factor, max}}`,
  per-attempt `timeout` ("30m"), `cache {enabled, version}`.
- **Graph**: acyclic (loops live in loop-node config, not back-edges);
  ids `^[a-z0-9][a-z0-9_-]{0,63}$` unique across stages+nodes; ≤32 stages,
  ≤200 nodes, ≤400 edges.

## Minimal example

> "Filter bimanual clips, label them with a VLM, publish after review."

```json
{
  "version": 1,
  "name": "bimanual-label-set",
  "stages": [
    { "id": "collect", "title": "Collect" },
    { "id": "annotate", "title": "Annotate" },
    { "id": "publish", "title": "Publish" }
  ],
  "nodes": [
    { "id": "filter", "kind": "compute", "stageId": "collect", "title": "bimanual_filter",
      "compute": { "udf": "pipelines.bimanual_filter", "params": { "hand_visibility": "both" } },
      "outputs": [{ "name": "out", "type": "samples" }] },
    { "id": "labeler", "kind": "uda", "stageId": "annotate", "title": "vlm_labeler",
      "uda": { "instructions": "Label task and active hand for each clip",
               "model": "qwen-vl-72b", "tools": ["Read"],
               "permissions": ["dreamlake.datasets.read", "dreamlake.datasets.create"],
               "queue": "gpu-a10g" },
      "inputs": [{ "name": "in", "type": "samples" }],
      "outputs": [{ "name": "out", "type": "dataset" }] },
    { "id": "gate", "kind": "control", "stageId": "publish", "title": "review_gate",
      "control": { "type": "approval", "message": "Review before publish" },
      "inputs": [{ "name": "in", "type": "dataset" }] },
    { "id": "pub", "kind": "compute", "stageId": "publish", "title": "dataset_publish",
      "compute": { "udf": "datasets.publish_version" },
      "inputs": [{ "name": "in", "type": "dataset" }],
      "outputs": [{ "name": "out", "type": "dataset" }] }
  ],
  "edges": [
    { "id": "e1", "from": "filter", "to": "labeler" },
    { "id": "e2", "from": "labeler", "to": "gate" },
    { "id": "e3", "from": "gate", "to": "pub" }
  ]
}
```

## Deliverable

1. Write the spec to `<name>.workflow.json` (pretty-printed, 2-space indent).
2. **Push it**: `dreamlake workflow push <name>` (the `.workflow.json` suffix
   is resolved automatically) — the CLI
   validates the bundled JSON Schema AND the graph rules above (edge types,
   fan-in legality incl. transitive exclusivity, switch coverage, acyclicity,
   sampler input types, uda queue-XOR-provider/no-cache — fails before any
   upload), stores the
   version in the workflow's DreamDB dataset, registers the catalog, and
   prints the dashboard link. The open workflow page hot-reloads within
   ~2.5s of every push. (`dreamlake workflow list` shows versions.)
   Not pushed = not finished. If the CLI is unavailable (`pip install
   'dreamlake>=0.5.0'`), fall back to validating against
   `reference/workflow-spec.schema.json` and hand the user the file with
   the push command to run.
3. Summarize the design in 3–5 bullets: stages, node choices (and WHY each
   family), the human gates, and any assumption you made about available UDFs
   or queues (mark them clearly — the user must confirm names).
