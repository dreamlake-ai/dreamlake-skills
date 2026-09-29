# Validate and Publish

## Deliver a prepared spec

Write the validated spec to `<name>.workflow.json` (pretty-printed, two-space indent). Check it against the bundled [JSON Schema](../reference/workflow-spec.schema.json); use a JSON Schema validator when available. The CLI performs both schema and graph validation before any network request.

A generated spec is the deliverable when the user asked to design or generate it. If the user also explicitly asks to publish, use [workflow-publish](../../workflow-publish/SKILL.md). Do not push as an assumed part of generation. The standalone CLI is supported; the Python package provides the SDK, not the CLI. Check `dreamlake workflow --help` for current syntax.

When handing over an unpublished file, summarize stages, node-family choices and reasons, human gates, and assumptions about available UDFs or queues. Mark assumed names for user verification.
