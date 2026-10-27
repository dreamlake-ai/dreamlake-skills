# Push or list a workflow spec

Writing or validating a WorkflowSpec, fixed templates and the review after
publishing belong to `dreamlake-workflows`. This action covers only the CLI
push and listing of an existing spec file.

```bash
dreamlake workflow --help
dreamlake workflow push ./workflow.json
dreamlake workflow list
```

Inspect the spec schema and validate before pushing, and do not treat a
successful push as a workflow run. See [workflows](../reference/cli-workflows.md)
for spec shape, namespace and run-trace commands.

A Workflow mount or reference blocks a whole-Project ownership transfer, even
with a client and backend that support owned Notes, Artifacts and Envs. Do not
silently detach the Workflow, omit it from the manifest or copy and delete it to
claim a complete move; see [projects](projects.md). There is no standalone
Workflow transfer.
