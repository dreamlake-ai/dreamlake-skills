---
name: dreamlake-envs
description: Package, push, pull, version, and manage MJCF or URDF environments with the DreamLake CLI, or compose a layered env from a stack file. Use for simulation scenes and robot models; recordings belong in dreamlake-source.
---
# DreamLake Environments

For a prepare-only request, scan scene includes/assets, stage a self-contained directory and compile-check it using [prepare an environment](./references/prepare-environment.md); stop and report missing paths. Do not upload unless the user asked to publish. For an explicitly requested push, continue with [push an environment](./references/push-environment.md), then verify by pulling a copy. Use [version and remove](./references/version-and-remove.md) for later revisions or lifecycle operations. For layer stacks, first read [compose layers](./references/compose-layers.md).

An env is a scene or robot model; recordings belong in a source. See [dreamlake-source](../dreamlake-source/SKILL.md) for dataset files. Owning guide: https://docs.dreamlake.ai/envs/.
