# Handoff And Debug

## 4. Hand off — upload, then write the `.dreamrc`

The `.mcap` is data like any other. Finish with the two companion skills:

1. **[`dreamlake-source`](../../dreamlake-source/SKILL.md)** — put the `.mcap` in
   linkable storage (HF repo, S3 bucket, …) with that provider's tools, and
   connect it as a source. There is no upload-into-source API yet; the file
   goes up with e.g. `hf upload <name>/<repo> ./rollout.mcap --repo-type dataset`.
2. **[`dreamlake-dataset-viz`](../../dreamlake-dataset-viz/SKILL.md)** — drop a
   `.dreamrc` (`format: mcap`, `episodes: auto`) that binds `/tf`, `/robot`
   (or `models:`), and `/metrics`. Validate with `check-dreamrc.mts` until
   `all N binding(s) decoded`, then open the folder in DreamLake.

Config file name: `.dreamrc` covers a whole folder; **`<file>.mcap.dreamrc`**
scopes a config to one mcap (use this when the folder will hold several).

## Gotchas

| symptom | cause → fix |
|---|---|
| robot is bare colored axes, no mesh | mesh was STL, or bound as `/robot` → embed **OBJ/GLB** and bind `/robot::*` |
| `"/robot is not a field of this episode"` | SceneUpdate is addressed per entity — bind `/robot::<body>` / `/robot::*`, not bare `/robot` |
| robot rotates / faces wrong | quaternion left as `wxyz` → reorder to Foxglove `xyzw` |
| file huge / meshes flicker | `/robot` logged every step → log once at `t=0`, `frame_locked=True` |
| viewer says the file is unindexed | write through `foxglove-sdk` (indexes automatically); don't hand-assemble MCAP |
| charts empty | `/metrics` logged as text/other → log a plain JSON dict of floats |

## Reference

- Runnable template (mjlab shown, generic hooks marked): [`reference/render_mcap.py`](../reference/render_mcap.py)
- The two `.dreamrc` variants, both validated: [`reference/dreamrc-examples.md`](../reference/dreamrc-examples.md)
- MCAP reader — which schemas decode, and how: https://viz.dreamlake.ai/dataset-viz/reference.md
- Every `.dreamrc` key and view option: https://viz.dreamlake.ai/dataset-viz/spec.md · https://viz.dreamlake.ai/dataset-viz/views.md
- Foxglove well-known schemas: https://docs.foxglove.dev/docs/visualization/message-schemas/introduction
