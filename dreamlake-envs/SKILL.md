---
name: dreamlake-envs
description: Compatibility entrypoint for requests naming the old DreamLake Environments skill. Use dreamlake-scenes for scene packaging, versioning and composition.
---

# DreamLake Scenes (legacy skill name)

The canonical skill is `dreamlake-scenes` in this same public catalog. Install or
open that skill for packaging, push, pull, versioning and composition procedures.
Do not guess paths or upload resources while resolving this handoff. If it is not
available locally, use the owning [Scenes documentation](https://docs.dreamlake.ai/scenes/).

CLI 0.45.0 uses `dreamlake scene`; `dreamlake env` remains a command alias.
Canonical web and API paths use `/scenes`; existing `/envs` bookmarks and API
clients remain compatible. Login environments and RL environment interfaces
retain their technical names.
