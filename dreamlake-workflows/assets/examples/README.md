# Worked examples — natural language → WorkflowSpec

Each example's spec is the sibling `.workflow.json` file; both validate against `../schema.json`.

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

Spec: [`bimanual-pretrain-set.workflow.json`](bimanual-pretrain-set.workflow.json)

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

Spec: [`confidence-routing.workflow.json`](confidence-routing.workflow.json)

Notes: every switch case AND `default` is routed (XOR totality);
`human_review` merges `low` + `default` (same switch — XOR-merge);
`auto_accept` merges `true` + `high` (transitive exclusivity);
`assemble.in` uses `collect: true` (three independent producers, delivered in
edge order e8, e9, e10).
