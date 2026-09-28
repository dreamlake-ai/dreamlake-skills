# Recover Validation

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

Fix the local file and retry. The CLI validates before making any network
request, so rejected local input leaves the remote catalog and version history
unchanged. A successful push of an existing workflow name creates the next
version; the first successful push is version 1.

## Pushing again

Each accepted re-push of the same name creates a **new version**; it never
overwrites history. Invalid local pushes do not create versions. The version
picker on the page can pin an older successful version.

## Notes

- `--name <name>` overrides the spec's own `name` field.
- A run's DATASET lands in the workflow's namespace, beside the workflow. It
  used to follow the caller's token instead, so a workflow published to an org
  produced annotations in the personal namespace of whoever pressed Run — findable
  by one person, and not the one looking. The worker now qualifies the name with
  the namespace on the queue message (needs dreamlake >= 0.7.0 on the worker,
  where `namespace/name` is understood).
- Never edit a spec directly on the server — edit the file and push, so the
  file stays the source of truth.
