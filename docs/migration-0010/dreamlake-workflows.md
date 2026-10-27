# Migration: dreamlake-workflows

Merged from `workflow-generator` and `workflow-publish` (design → deliver →
publish → recover is one workflow for one user goal). **Decision:**
`video-labeling-workflow` is kept as its own skill (merge-caution rule 2 and 4):
its procedure is four distinct steps (~14 KB of prose) plus an 11 KB template,
which does not fit "one asset + one small action". See
`_migration/video-labeling-workflow.md`.

| Source file / section | Destination |
|---|---|
| `workflow-generator/SKILL.md` (NL goal → spec, validate locally, pushing is a separate request, routing to publish / video-labeling) | `SKILL.md` router + boundaries; `actions/design.md` intro |
| `workflow-generator/references/prepare-spec.md` (mental model, four families, authoring procedure, rules generators get wrong, minimal example) | `actions/design.md` |
| `workflow-generator/references/validate-publish.md` (write `<name>.workflow.json`, schema check, do not push, summarize assumptions, standalone CLI vs Python SDK) | `actions/deliver.md` |
| `workflow-generator/reference/workflow-spec.schema.json` | `assets/schema.json` (git mv; `$id` left as in the schema) |
| `workflow-generator/reference/schema.md` (field reference: envelope, types, ports & fan-in, stage/compute/uda/sampler/control, permission registry, ProviderRef, execution, outputBinding) | `assets/spec-reference.md` (verbatim; schema file name updated) |
| `workflow-generator/reference/examples.md` prose + decomposition notes | `assets/examples/README.md` |
| `examples.md` Example 1 JSON | `assets/examples/bimanual-pretrain-set.workflow.json` (validates against `assets/schema.json`) |
| `examples.md` Example 2 JSON | `assets/examples/confidence-routing.workflow.json` (validates) |
| `workflow-publish/SKILL.md` (push command, local validation first, report version/counts/URL, does not design graphs) | `actions/publish.md` intro |
| `workflow-publish/references/push-workflow.md` §Procedure 1–3 (settle namespace, `profile`/`org list`, org slug is a namespace, never silently personal, push output, Run button) | `actions/publish.md` §Procedure |
| `push-workflow.md` §Project-derived access (CLI ≥ 0.62.0, SDK ≥ 0.29.0, READ/WRITE/ADMIN boundaries, no Run from publish, `DELEGATED_UPLOAD_UNSUPPORTED`, `canBind`) | `actions/publish.md` §Project-derived access; cited `docs.dreamlake.ai/api/project-queries` added to `docs[]` |
| `push-workflow.md` §Whole-Project transfer boundary | `actions/publish.md` §Whole-Project transfer — one sentence pointing to the `projects` action of `dreamlake-cli` |
| `workflow-publish/references/recover-validation.md` (JSON-Pointer reading, common causes, re-push creates versions, `--name`, run DATASET namespace needs worker dreamlake ≥ 0.7.0, never edit on the server) | `actions/recover-validation.md` |
| Cross-skill links to `workflow-publish`, `video-labeling-workflow`, `remote-source-check` | action links / skill names (`video-labeling-workflow`, `check` action of `dreamlake-datasets`) |
| docs URLs: docs workflows, node-types, agent-permissions, cjs-vs-python, cli workflows, api/project-queries | `skill.json` `docs[]` |
