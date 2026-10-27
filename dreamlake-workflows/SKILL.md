---
name: dreamlake-workflows
description: Turn a natural-language data-production, labeling, or training goal into a complete DreamLake WorkflowSpec v1 JSON file (stages, typed compute/uda/sampler/control nodes, typed data edges), validate it against the bundled schema, publish it to the intended namespace with `dreamlake workflow push`, report the canvas URL, and recover from validation failures or version questions. Use for "create / generate / design a workflow", "turn this description into a workflow", "push / publish this spec", or "why did validation fail". Not for the fixed video subtask-labeling workflow (video-labeling-workflow), verifying source paths (the `check` action of dreamlake-datasets), or Python pipelines.
---

# DreamLake workflows

| User wants | Action |
|---|---|
| A new graph from a description | [design](actions/design.md) — mental model, authoring procedure, the rules generators get wrong, minimal example |
| The designed spec handed over as a file | [deliver](actions/deliver.md) — write `<name>.workflow.json`, check it against `assets/schema.json`, summarize assumptions; do not push |
| A finished spec pushed / published / live on the page | [publish](actions/publish.md) — settle the namespace first, push, report version + counts + canvas URL |
| A rejected spec, or a question about versions | [recover-validation](actions/recover-validation.md) — read the JSON-Pointer, common causes, re-push semantics |

Designing and publishing are separate user requests: generate when asked to
design, push only when asked to publish. Never silently publish to the personal
namespace because `--namespace` was omitted.

## Assets

- `assets/schema.json` — the WorkflowSpec v1 JSON Schema (the machine
  contract the CLI and server validate against).
- `assets/spec-reference.md` — the field reference with the semantic rules the
  schema cannot express (fan-in, sampler/control signatures, permission
  registry, execution, outputBinding).
- `assets/examples/` — two worked NL → spec examples with the decomposition
  reasoning (`README.md`) and the resulting `.workflow.json` files.

## Boundaries

- The fixed manipulation-video subtask-labeling workflow is a template, not a
  design job: `video-labeling-workflow`.
- Every `source` + path a spec names must be proven readable first: the
  `check` action of `dreamlake-datasets`. Raw URLs and local paths never go
  into a spec.
- Registering UDFs/agents, run traces, and other CLI operations:
  `dreamlake-cli`. Moving a whole Project (a Workflow mount blocks it): the
  `projects` action of `dreamlake-cli`.
- A Python pipeline is a different system from a workflow:
  [reference/docs-workflows-cjs-vs-python.md](reference/docs-workflows-cjs-vs-python.md).

## Canonical source

Product facts (node vocabulary, permission grammar, CLI flags, validation
output) live on the docs sites, not here: https://docs.dreamlake.ai,
https://cli.dreamlake.ai, https://viz.dreamlake.ai. Any page is readable as
Markdown at `<page-url>.md`; the whole corpus of a site is at
`<site>/llms-full.txt`. `reference/` holds CI-fetched copies of the pages
listed in `skill.json` `docs[]` — read them, never edit them.
