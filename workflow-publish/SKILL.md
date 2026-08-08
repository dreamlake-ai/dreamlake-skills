---
name: workflow-publish
description: >
  Validate a WorkflowSpec JSON file and push it to a DreamLake namespace with
  the dreamlake CLI, then report the canvas URL. Use after a spec has been
  written or edited and the user wants it "pushed / uploaded / published / live
  on the page", or asks for the link to open a workflow.
---

# Publish a workflow spec

Takes a finished spec file to a live, runnable workflow on the DreamLake canvas.
This is the only step that touches a server, so it validates first and reports
precisely — a spec that renders wrong is cheaper to fix here than after a user
has pressed Run.

CLI: `dreamlake`
(login is already done; do not attempt `dreamlake login`.)

## Procedure

**1. Settle the target namespace before pushing.** With no `--namespace` the
push goes to the active login's PERSONAL namespace. That is rarely what someone
means when the work belongs to a team — and the mistake is silent: the push
succeeds, the URL looks right, and it is only noticed later by a colleague who
cannot find the workflow.

```bash
dreamlake profile     # personal namespace
dreamlake org list    # orgs you belong to
```

Creating an organisation also creates a namespace of the same slug, so an org
slug IS a namespace: `--namespace acme` publishes into that org.

If the caller named a namespace, use it. If not and the user belongs to
organisations, say where it is about to go and offer them — one line, not an
interrogation.

**2. Push.** The CLI validates against the WorkflowSpec schema *and* the graph
rules before uploading; a failure here means the spec never left the machine.

```bash
dreamlake workflow push <file.workflow.json> \
    [--namespace <slug>]
```

Success prints the version, shape, and canvas URL:

```
workflow:  <name> v6 · 5 stages · 8 nodes · 9 edges
✓ pushed <name> v6
  open:  https://dreamlake.ai/<namespace>/workflows/<name>
```

**3. Report to the user**: the version, the node/edge counts (so they can see
the shape matches what was described), and the URL as a clickable link. Tell
them the page has a **Run** button and that node states light up live on the
canvas while it executes.

## When validation fails

The CLI prints `✗ spec failed validation` with a JSON-Pointer path such as
`nodes/4`. Read the pointer as an index into the array — `nodes/4` is the
**fifth** node. Common causes, all cheap to check:

- an unknown property where the schema sets `additionalProperties: false`
  (`provider` is strict: GPUs go in `resources: {gpu: 1}`, there is no
  `accelerator` key)
- a `control` node declaring `outputs` (control nodes are type-preserving and
  declare none)
- an edge naming a port that its source/target node does not declare
- a `udf` string that does not match `^[a-z0-9_]+(\.[a-z0-9_]+)+$`

Fix the spec and push again — versions are additive, so a bad push costs
nothing but a version number.

## Pushing again

Re-pushing the same name creates a **new version**; it never overwrites history,
and the page hot-reloads to the latest within a couple of seconds. The version
picker on the page can pin an older one. So iterate freely.

## Notes

- `--name <name>` overrides the spec's own `name` field.
- A run's DATASET lands in the workflow's namespace, beside the workflow. It
  used to follow the caller's token instead, so a workflow published to an org
  produced datasets in the personal namespace of whoever pressed Run — findable
  by one person, and not the one looking. The worker now qualifies the name with
  the namespace on the queue message (needs dreamlake >= 0.7.0 on the worker,
  where `namespace/name` is understood).
- Never edit a spec directly on the server — edit the file and push, so the
  file stays the source of truth.
