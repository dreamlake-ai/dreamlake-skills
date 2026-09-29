---
name: dreamlake-annotations
description: Write or read annotations with the DreamLake Python SDK, using the video preset or a custom schema. Use for annotation ingestion and data operations through Python; there is no matching annotation CLI workflow.
---
# DreamLake Annotations (Python SDK)

Use the `dreamlake.annotation` Python SDK to upload annotated video episodes or write custom-schema records. This is an SDK workflow; it has no equivalent annotation CLI procedure. For robot video, follow [video episodes](./references/video-episodes-python.md); for arbitrary tracks and rows, follow [custom schema](./references/custom-schema-python.md). For catalog reads and visualization, use [read and visualize](./references/read-and-visualize.md).

Choose one writer per annotation, preserve the schema and anchor constraints, and read back writes before relying on them. Full API reference: https://docs.dreamlake.ai/annotations/reference.
