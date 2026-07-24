# Worked examples — natural language → WorkflowSpec

Two full examples showing the reasoning, not just the JSON. Follow the same
decomposition discipline; mark every assumed UDF/queue name for the user to
confirm.

---

## Example 1 — sampling + agent labeling + gated publish

> **User**: "Take about 10% of our egocentric clips (at least 50), have a VLM
> label the task and hands, transcode everything to mp4, and publish a dataset
> — but I want to sign off before it goes out."

**Decomposition**: 3 stages. "About 10%, at least 50" = `bernoulli` with
`min_size` (probabilistic count + floor). VLM labeling = `uda` (judgment).
Transcode = `compute` (deterministic). Sign-off = `approval` control before a
publish `compute`. Transcode consumes ALL clips (not the sample) → cross-stage
edge from the filter output. Publish needs both the reviewed dataset and the
media → two typed input ports.

```json
{
  "version": 1,
  "name": "bimanual-pretrain-set",
  "description": "Sample egocentric clips, VLM-label, transcode, publish after review.",
  "stages": [
    { "id": "collect", "title": "Collect & filter" },
    { "id": "annotate", "title": "Annotate" },
    { "id": "publish", "title": "Publish" }
  ],
  "nodes": [
    {
      "id": "clip_source", "kind": "compute", "stageId": "collect", "title": "clip_source",
      "compute": { "udf": "catalog.list_clips" },
      "outputs": [{ "name": "out", "type": "samples" }]
    },
    {
      "id": "take_sample", "kind": "sampler", "stageId": "collect", "title": "take_sample",
      "sampler": { "strategy": "bernoulli", "fraction": 0.1, "min_size": 50, "seed": 42 },
      "inputs": [{ "name": "in", "type": "samples" }]
    },
    {
      "id": "vlm_labeler", "kind": "uda", "stageId": "annotate", "title": "vlm_labeler",
      "uda": {
        "instructions": "Label the task, sub-task and active hand for each clip.",
        "model": "qwen-vl-72b",
        "tools": ["Read"],
        "permissions": ["dreamlake.datasets.read", "dreamlake.datasets.create"],
        "queue": "gpu-a10g"
      },
      "inputs": [{ "name": "in", "type": "samples" }],
      "outputs": [{ "name": "out", "type": "dataset" }],
      "execution": { "retry": { "max_attempts": 2 }, "timeout": "4h" }
    },
    {
      "id": "transcode", "kind": "compute", "stageId": "annotate", "title": "clip_transcode",
      "compute": {
        "udf": "media.transcode_clips",
        "params": { "codec": "h264", "container": "mp4" },
        "provider": { "launcher": "EC2", "instance_type": "g5.xlarge", "dispatch": "daemon" }
      },
      "inputs": [{ "name": "in", "type": "samples" }],
      "outputs": [{ "name": "out", "type": "directory" }],
      "execution": { "retry": { "max_attempts": 3, "backoff": { "initial": "10s", "factor": 2.0, "max": "5m" } }, "timeout": "2h", "cache": { "enabled": true, "version": "1" } }
    },
    {
      "id": "review_gate", "kind": "control", "stageId": "publish", "title": "review_gate",
      "control": { "type": "approval", "message": "Review labels before publish", "timeout_s": 172800 },
      "inputs": [{ "name": "in", "type": "dataset" }]
    },
    {
      "id": "publish_ds", "kind": "compute", "stageId": "publish", "title": "dataset_publish",
      "compute": { "udf": "datasets.publish_version" },
      "inputs": [
        { "name": "in", "type": "dataset" },
        { "name": "media", "type": "directory" }
      ],
      "outputs": [{ "name": "out", "type": "dataset" }],
      "outputBinding": { "kind": "dataset", "project": "workflows", "pathTemplate": "workflows/{workflow}/{runId}/{nodeId}" }
    }
  ],
  "edges": [
    { "id": "e1", "from": "clip_source", "to": "take_sample" },
    { "id": "e2", "from": "take_sample", "to": "vlm_labeler" },
    { "id": "e3", "from": "clip_source", "to": "transcode" },
    { "id": "e4", "from": "vlm_labeler", "to": "review_gate" },
    { "id": "e5", "from": "review_gate", "to": "publish_ds" },
    { "id": "e6", "from": "transcode", "to": "publish_ds", "toPort": "media" }
  ]
}
```

Notes: sampler/control declare no `outputs` (derived, type-preserving);
`clip_source` broadcasts to sampler AND transcode (outputs broadcast freely);
assumed names to confirm: `catalog.list_clips`, `media.transcode_clips`,
`datasets.publish_version`, queue `gpu-a10g`.

---

## Example 2 — confidence routing with switch + XOR-merge + collect

> **User**: "Score label confidence; auto-accept above 0.95. Below that, split
> into high/mid/low tiers — high auto-accepts too, mid gets a second model
> pass, low goes to human review. Merge everything accepted into one dataset."

**Decomposition**: condition (binary ≥0.95) → switch (3 tiers + required
`default`). `auto_accept` receives `condition.true` AND `switch.high` — legal
without `collect` because the sources are **transitively exclusive** (the
switch only runs on `condition.false`). The final assembly receives THREE
independent producers → `collect: true` port.

```json
{
  "version": 1,
  "name": "confidence-routing",
  "stages": [
    { "id": "score", "title": "Score" },
    { "id": "route", "title": "Route" },
    { "id": "resolve", "title": "Resolve" }
  ],
  "nodes": [
    {
      "id": "score_conf", "kind": "compute", "stageId": "score", "title": "score_confidence",
      "compute": { "udf": "ml.score_confidence" },
      "outputs": [{ "name": "out", "type": "table" }]
    },
    {
      "id": "is_confident", "kind": "control", "stageId": "route", "title": "is_confident",
      "control": { "type": "condition", "expression": "confidence >= 0.95" },
      "inputs": [{ "name": "in", "type": "table" }]
    },
    {
      "id": "tier_switch", "kind": "control", "stageId": "route", "title": "tier_switch",
      "control": { "type": "switch", "cases": [
        { "name": "high", "expression": "conf >= 0.75" },
        { "name": "mid", "expression": "conf >= 0.40" },
        { "name": "low", "expression": "conf < 0.40" }
      ] },
      "inputs": [{ "name": "in", "type": "table" }]
    },
    {
      "id": "auto_accept", "kind": "compute", "stageId": "resolve", "title": "auto_accept",
      "compute": { "udf": "labels.auto_accept" },
      "inputs": [{ "name": "in", "type": "table" }],
      "outputs": [{ "name": "out", "type": "table" }]
    },
    {
      "id": "second_model", "kind": "uda", "stageId": "resolve", "title": "second_model",
      "uda": {
        "instructions": "Re-check mid-confidence labels; correct or confirm each.",
        "model": "claude-haiku", "tools": ["Read"],
        "permissions": ["dreamlake.datasets.read"], "queue": "cpu-lane"
      },
      "inputs": [{ "name": "in", "type": "table" }],
      "outputs": [{ "name": "out", "type": "table" }]
    },
    {
      "id": "human_review", "kind": "uda", "stageId": "resolve", "title": "human_review",
      "uda": {
        "instructions": "Queue low-confidence samples for expert annotation.",
        "permissions": ["dreamlake.datasets.update"], "queue": "review-queue"
      },
      "inputs": [{ "name": "in", "type": "table" }],
      "outputs": [{ "name": "out", "type": "table" }]
    },
    {
      "id": "assemble", "kind": "compute", "stageId": "resolve", "title": "assemble_accepted",
      "compute": { "udf": "datasets.assemble" },
      "inputs": [{ "name": "in", "type": "table", "collect": true }],
      "outputs": [{ "name": "out", "type": "dataset" }]
    }
  ],
  "edges": [
    { "id": "e1", "from": "score_conf", "to": "is_confident" },
    { "id": "e2", "from": "is_confident", "fromPort": "true", "to": "auto_accept" },
    { "id": "e3", "from": "is_confident", "fromPort": "false", "to": "tier_switch" },
    { "id": "e4", "from": "tier_switch", "fromPort": "high", "to": "auto_accept" },
    { "id": "e5", "from": "tier_switch", "fromPort": "mid", "to": "second_model" },
    { "id": "e6", "from": "tier_switch", "fromPort": "low", "to": "human_review" },
    { "id": "e7", "from": "tier_switch", "fromPort": "default", "to": "human_review" },
    { "id": "e8", "from": "auto_accept", "to": "assemble" },
    { "id": "e9", "from": "second_model", "to": "assemble" },
    { "id": "e10", "from": "human_review", "to": "assemble" }
  ]
}
```

Notes: every switch case AND `default` is routed (XOR totality);
`human_review` merges `low` + `default` (same switch — XOR-merge);
`auto_accept` merges `true` + `high` (transitive exclusivity);
`assemble.in` uses `collect: true` (three independent producers, delivered in
edge order e8, e9, e10).
