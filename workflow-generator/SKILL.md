---
name: workflow-generator
description: Generate a WorkflowSpec v1 JSON file from a data-production, labeling, or training goal. Use when the user wants a new graph designed; the separate video-labeling skill handles its fixed workflow shape, and workflow-publish handles publishing.
---
# Generate a WorkflowSpec

Turn a natural-language data-production goal into a complete WorkflowSpec v1 JSON file. For a new spec, follow [prepare a spec](./references/prepare-spec.md) and return the named file with assumptions about UDFs and queues clearly marked. Validate it locally where possible using [the bundled schema](./reference/workflow-spec.schema.json); the CLI repeats schema and graph validation before writing.

Pushing creates or adds a version and is a separate user-requested action. If the user asks to publish, use [workflow-publish](../workflow-publish/SKILL.md). The fixed video-labeling workflow belongs to [video-labeling-workflow](../video-labeling-workflow/SKILL.md).
