---
name: remote-source-check
description: Verify that a connected DreamLake source contains each file a remote workflow will read. Use before putting source paths into a spec; reject raw URLs and local filesystem paths.
---
# Verify Workflow Source Inputs

Before putting data paths into a WorkflowSpec, prove that the connected source and every path are readable by this account. Start with [check source paths](./references/check-source-paths.md); report the source, namespace, path, size, and result for each input. Stop and request corrected inputs when any check fails.

This checks connected-source references only. URLs and local paths cannot be consumed by a remote worker.
