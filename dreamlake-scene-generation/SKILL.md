---
name: dreamlake-scene-generation
description: 'Create or edit MuJoCo scenes with DreamLake: source assets from any origin — internet model repositories (e.g. the MuJoCo Menagerie), user-provided files, procedural MJCF authoring, or DreamLake asset libraries — measure them, design physically valid layouts, build the scene as raw MJCF or a layered scene (v3 stack), validate contacts/support/stability, render previews, and publish versioned scenes you can keep editing. Use when a user wants to build a simulation scene, place objects on surfaces without clipping or floating, wrap a raw OBJ/STL mesh for physics, or modify and republish an existing scene.'
---

# DreamLake Scene Generation

Build a scene in this order, using the matching action guide:

- [Source assets](actions/find-assets.md) — from any origin: internet
  models (MuJoCo Menagerie), user files, procedural MJCF, or DreamLake
  libraries; verify closure, license, and measurements per model.
- [Design and inspect the scene](actions/design-and-inspect.md) — derive
  placements from measured geometry; author lights, cameras, materials;
  wrap raw OBJ/STL meshes with simple collision.
- [Compose and validate](actions/compose-and-validate.md) — raw MJCF or a
  layer stack with stable instance keys; physical validation with explicit
  per-body checks either way.
- [Publish and iterate](actions/publish-and-iterate.md) — push, browser
  preview, hash-verified readback, edit the pinned stack, reuse scenes.

The bundled `tools/` directory has three standalone helpers (inspection,
rendering, physics validation) that run on any MJCF file or pulled scene —
setup and contract in the action guides. The bundled `reference/` pages are
the complete product documentation: [scene generation](reference/scene-generation.md),
[libraries](reference/libraries.md), [scenes](reference/scenes.md), and the
[scene layers grammar](reference/scenes-layers.md).

Commands here are tested with the `dreamlake` CLI ≥ 0.45.0 and
`dreamlake[compose]` (dreamlake-py ≥ 0.23); check `dreamlake --version`
first and prefer `dreamlake <command> --help` for flag details.

Generated from the workspace scene-generation guide and action guides.
Procedures belong in source docs; the public sync records their commits and
hashes.
