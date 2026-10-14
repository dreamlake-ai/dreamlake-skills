# Manage workflows

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
