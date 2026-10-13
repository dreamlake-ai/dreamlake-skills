---
name: dreamlake-scenes
description: Package, push, pull, version, and manage MJCF or URDF scenes with the DreamLake CLI, or compose a layered scene from a stack file. Use for simulation scenes and robot models; recordings belong in dreamlake-source.
---
# DreamLake Scenes

For a prepare-only request, scan scene includes/assets, stage a self-contained directory and compile-check it using [prepare a scene](./references/prepare-environment.md); stop and report missing paths. Do not upload unless the user asked to publish. For an explicitly requested push, continue with [push a scene](./references/push-environment.md), then verify by pulling a copy. Use [version and remove](./references/version-and-remove.md) for later revisions or lifecycle operations. For layer stacks, first read [compose layers](./references/compose-layers.md).

Commands require DreamLake CLI 0.45.0 or later; check `dreamlake --version` before publishing.

A Scene is a versioned world or robot model; recordings belong in a source. See [dreamlake-source](../dreamlake-source/SKILL.md) for dataset files. Owning guide: https://docs.dreamlake.ai/scenes/.
