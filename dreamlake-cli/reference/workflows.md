# Workflows

A workflow has two sides, and they use different commands:

- **The spec** — a `WorkflowSpec v1` JSON document describing stages, nodes,
  and edges. Managed with `workflow push`.
- **The runs** — traces produced while a workflow executes. Sent with
  `workflow push-run` and `workflow watch-run`.

## Pushing a spec

```bash file="terminal"
dreamlake workflow push ./pipeline.workflow.json
```

The `.workflow.json` (or `.json`) suffix is optional, so
`dreamlake workflow push ./pipeline` finds the same file.

The workflow name comes from the spec's own `name` field. `--name` overrides
it, which is how you push one spec under two names.

Every push appends a new version. The command prints the version it wrote.

## Validation

The spec is validated locally, before anything is uploaded. An invalid spec
costs you nothing but the error message.

Two layers run:

1. **The JSON Schema** — required fields, types, and the shape of each node
   family. This is the same schema the Python CLI and the server use, so all
   three accept and reject exactly the same specs.
2. **Graph rules** a schema cannot express — type compatibility across edges,
   fan-in legality, switch case coverage, and acyclicity.

```text file="output"
spec failed validation (3 problem(s)):
  - nodes/0: Instance does not have required property "title".
  - nodes/0: is not valid under any of the given schemas
  - stages/0: Instance does not have required property "title".
```

A failed `oneOf` reports one line rather than listing what each alternative
wanted. A compute node is not "missing `sampler`" — it simply is not a
sampler.

## Managing workflows

```bash file="terminal"
dreamlake workflow list
dreamlake workflow show my-flow
dreamlake workflow update my-flow --description "..." --tags a,b
dreamlake workflow delete my-flow          # soft — version history survives
```

`workflow create` and `workflow update --file` handle a separate,
script-based workflow format. They are unrelated to `push` and do not share
its versioning.

## Run traces

These are for the process executing a workflow, not for day-to-day use.

```bash file="terminal"
dreamlake workflow push-run my-flow ./wf_abc123.json
dreamlake workflow watch-run my-flow ./wf_abc123.json --interval 5
```

`push-run` sends one snapshot. `watch-run` keeps sending them until the run
leaves the `running` state, then sends a final one.

Snapshots are reduced to fit the server's body limit. When a run is large,
free-text previews are capped and older log lines are dropped first; the
status, the phase and agent skeleton, and the run totals always survive.

> **Note:** Like `artifact push`, `workflow push` brokers scoped credentials and writes
> the spec to object storage itself. The spec never passes through the API
> server.
