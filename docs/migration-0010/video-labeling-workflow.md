# Migration: video-labeling-workflow (kept as its own skill)

**Decision:** not folded into `dreamlake-workflows` as "one asset + one action".
The procedure is four distinct user-facing steps (~14 KB of prose) with
confirmation gates, plus an 11 KB measured template; it is a product demo a user
installs on its own (merge-caution rules 2a, 3, 4). It `requires`
`dreamlake-workflows` (publish) and `dreamlake-datasets` (the `check` action).
The integrator may want `renamed.json` to leave `video-labeling-workflow` unmapped.

| Source file / section | Destination |
|---|---|
| `SKILL.md` (fixed template, four references in order, publish only after confirmation, precedence over workflow-generator, companion skills) | `SKILL.md` router + rules + boundaries |
| `references/collect-and-name.md` (talk like a product, the workflow diagram/table, §1 collect inputs in zh/en, defaults from `profile`/`org list`, `dreamlake` not on PATH, why each input matters, namespaces independent, §2 fresh time-stamped name) | `actions/collect-and-name.md` (git mv; template path and `workflow-generator` reference updated) |
| `references/check-inputs.md` (§3 validate via remote-source-check, stop on failure) | `actions/check-inputs.md` (git mv; now says "run the `check` action of `dreamlake-datasets`") |
| `references/fill-and-confirm.md` (§4 placeholders, substitute only these, worker-side `test_spec_params`, review_gate after publish, omitted-parameter table, execution blocks, 15 fps no cap, WiLoR jitter, §4b show the data back and wait) | `actions/fill-and-confirm.md` (git mv; template path updated) |
| `references/publish-and-handoff.md` (§5 publish via workflow-publish, §6 two-line handover, what the run needs, per-run annotation) | `actions/publish-and-handoff.md` (git mv; now says "run the `publish` action of `dreamlake-workflows`") |
| `reference/template.workflow.json` | `assets/templates/video-labeling.workflow.json` (git mv; validates against `dreamlake-workflows/assets/schema.json` with placeholders substituted) |
| docs URLs (none cited by the sources) | `skill.json` `docs[]` = docs workflows, cli workflows |
