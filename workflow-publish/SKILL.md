---
name: workflow-publish
description: Validate and publish a prepared WorkflowSpec v1 JSON file with the DreamLake CLI, then report its version and canvas link. Use when the user asks to push or publish a completed spec.
---
# Publish a WorkflowSpec

When the user asks to publish a finished WorkflowSpec, check the target namespace, then run `dreamlake workflow push <file.workflow.json> [--namespace <slug>]`. The CLI validates the schema and graph locally before any network or version write. Follow [push workflow](./references/push-workflow.md) and report the version, graph counts, and canvas URL.

Use [validation recovery](./references/recover-validation.md) for rejected specs or version questions. This skill publishes a prepared spec; it does not design workflow graphs.
