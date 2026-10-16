# Register definitions and manage workflows

For UDFs and agents, check installed help first; registration/editor commands
require CLI 0.71.1. Preview the explicit definition files before registration:

```bash
dreamlake runnable register .dreamrc --dry-run
dreamlake runnable register .dreamrc --namespace YOUR_NAMESPACE
dreamlake agents list --plain
dreamlake agents edit YOUR_AGENT --web
```

See [registration](../reference/runnable-upload.md), [all `.dreamrc` fields](../reference/dreamrc.md),
and [agent editing](../reference/agents.md). Registration and Save do not execute
or publish an agent. Retain partial upload receipts and inspect existing entries
before retrying; differing declarations are refused. Context is not an access grant.

For a workflow spec, inspect its schema and validate before pushing:

```bash
dreamlake workflow --help
dreamlake workflow push ./workflow.json
```

Do not treat a successful push as a workflow run. See [workflows](../reference/workflows.md)
for spec shape, namespace and run-trace commands.

Workflow references remain blockers for a whole-Project ownership transfer,
even with a client/backend that supports owned Notes, Artifacts and Envs. Do not
silently detach the Workflow, omit it from the manifest or copy/delete it to
claim a complete move. See [Projects](../reference/projects.md); this adds no
standalone Workflow transfer.
