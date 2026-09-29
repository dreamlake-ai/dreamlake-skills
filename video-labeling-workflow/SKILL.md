---
name: video-labeling-workflow
description: Prepare the fixed video subtask-labeling workflow from connected-source video and reference annotation paths. Use for this specific labeling workflow; check source inputs and get confirmation of resolved paths and destination before publishing.
---
# Create a Video Labeling Workflow

For manipulation-video subtask labeling, fill the supplied fixed workflow template; do not design a new graph. Read [collect and name](./references/collect-and-name.md), [check source inputs](./references/check-inputs.md), then [fill and confirm the spec](./references/fill-and-confirm.md). Publishing is a distinct step: proceed only after the user confirms the resolved source paths, task description, and publishing namespace, then use [publish and hand off](./references/publish-and-handoff.md).

This skill is for the fixed video-labeling shape; use [workflow-generator](../workflow-generator/SKILL.md) for other workflow designs. Install the companion [remote-source-check](../remote-source-check/SKILL.md) and [workflow-publish](../workflow-publish/SKILL.md) skills.
