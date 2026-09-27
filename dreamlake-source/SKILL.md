---
name: dreamlake-source
description: Prepare data for a DreamLake source, connect external storage, upload to an existing managed source, and verify the stored paths. Use when data needs to become reachable in DreamLake; use dreamlake-dataset-viz to configure its views.
---
# Connect Dataset Sources

Prepare robot data for DreamLake by inspecting its actual layout, putting it in supported storage, connecting that storage as a source, and verifying the paths the viewer will read. If a source already exists, discover its name with `dreamlake source list`; use [connect and verify](./references/connect-and-verify.md) to inspect its paths. For new data, start with [prepare data](./references/prepare-data.md), then connect and verify. For bytes going into an existing managed source, use `dreamlake source upload <path> --source <name>`; this CLI operation does not create or connect a source. External S3/Hugging Face/Dropbox storage is linked through the dashboard. Sources retain data in place; they do not convert an unsupported container.

To render a connected dataset, continue with [dreamlake-dataset-viz](../dreamlake-dataset-viz/SKILL.md). Source help: https://docs.dreamlake.ai/sources/; format requirements: https://viz.dreamlake.ai/dataset-viz/requirements.md.
