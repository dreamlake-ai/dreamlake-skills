# Manage workflows

For a workflow spec, inspect its schema and validate before pushing:

```bash
dreamlake workflow --help
dreamlake workflow push ./workflow.json
```

Do not treat a successful push as a workflow run. See [workflows](../reference/workflows.md)
for spec shape, namespace and run-trace commands.
