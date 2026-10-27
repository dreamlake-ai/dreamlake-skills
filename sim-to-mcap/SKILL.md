---
name: sim-to-mcap
description: Roll a trained policy out in a local Python physics simulator (mjlab, raw MuJoCo, Isaac, or a logged trajectory) and write an indexed MCAP with Foxglove /tf, /robot and /metrics channels that DreamLake plays natively — the mesh moving through the scene, every reward and joint as a cursor-synced chart. Use for "visualize my policy / rollout", "the robot shows as bare axes", or "use the preset G1 URDF instead". Not for recordings that already exist on disk and not for linking storage or authoring a general .dreamrc — that is dreamlake-datasets, which this skill hands off to.
---

# Simulation rollout → MCAP

Use this local Python workflow when you have a trained policy and a physics
simulator and need a DreamLake-playable MCAP. A numeric-only run without a
body pose should use chart views instead (`dreamlake-datasets`).

| Step | Action |
|---|---|
| Emit `/tf`, `/robot`, `/metrics` in Foxglove schemas from the rollout loop | [write-rollout](actions/write-rollout.md) |
| Put a body on the skeleton: embed OBJ/GLB meshes, or point at a URDF | [embody](actions/embody.md) |
| Upload, connect, bind a `.dreamrc`, and debug the common symptoms | [handoff](actions/handoff.md) |

## Bundled

- `tools/render_mcap.py` — runnable template (mjlab shown; the three
  `# === mjlab-specific ===` hooks are the only simulator-bound code). Needs
  `pip install foxglove-sdk trimesh`; `tools/test_render_mcap.py` covers the
  sim-agnostic helpers.
- `assets/dreamrc/` — the two validated `.dreamrc` variants (embedded mesh,
  external URDF) with placement and validation notes.

## Rules that hold across actions

- Quaternion order: MuJoCo/mjlab store `wxyz`; Foxglove `Quaternion` is
  `xyzw`. Reorder or the robot spins wrong.
- `/robot` is logged once at `t=0`, `frame_locked=True`, no lifetime; each
  entity's `frame_id` is a body name so the meshes ride the per-step `/tf`.
- Meshes are OBJ or GLB/glTF — never STL; STL bytes are silently dropped and
  the robot renders as bare axes.
- Write through `foxglove-sdk` so the file is indexed; never hand-assemble MCAP.

## Boundaries

- Getting the `.mcap` into storage, linking it as a Source, and the general
  `.dreamrc` grammar: the `dreamlake-datasets` skill (`upload`, `connect`,
  `dreamrc`, `validate` actions). This skill only ships the two MCAP bindings.
- Sim data that is already a qpos / joint trajectory (no policy to roll out):
  the `sim-playback` action of `dreamlake-datasets`.

## Canonical source

Product facts (channel decoding, `.dreamrc` keys, view options) live on the
docs sites, not here: https://docs.dreamlake.ai, https://cli.dreamlake.ai,
https://viz.dreamlake.ai. Any page is readable as Markdown at
`<page-url>.md`; the whole corpus of a site is at `<site>/llms-full.txt`.
`reference/` holds CI-fetched copies of the pages listed in `skill.json`
`docs[]` — read them, never edit them. Foxglove's well-known schemas are
Foxglove's own: https://docs.foxglove.dev/docs/visualization/message-schemas/introduction
