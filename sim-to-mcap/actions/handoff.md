# Hand off: upload, connect, bind — and debug

The `.mcap` is data like any other. Finish with the `dreamlake-datasets`
skill:

1. **`upload` + `connect` actions** — put the `.mcap` in linkable storage
   (HF repo, S3 bucket, …) with that provider's tools, or into an existing
   managed Source with `dreamlake source upload`, and connect it as a source.
   The dashboard flow is in [reference/docs-sources.md](../reference/docs-sources.md).
2. **`dreamrc` + `validate` actions** — drop a `.dreamrc` (`format: mcap`,
   `episodes: auto`) that binds `/tf`, `/robot` (or `models:`), and
   `/metrics`; start from [`assets/dreamrc/`](../assets/dreamrc/README.md).
   Validate with `check-dreamrc.mts` until `all N binding(s) decoded`, then
   open the folder in DreamLake.

Config file name: `.dreamrc` covers a whole folder; **`<file>.mcap.dreamrc`**
scopes a config to one mcap (use this when the folder will hold several).
The end-to-end walkthrough: [reference/docs-sim-rollouts.md](../reference/docs-sim-rollouts.md).

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

- Runnable template (mjlab shown, generic hooks marked): [`tools/render_mcap.py`](../tools/render_mcap.py)
- The two `.dreamrc` variants, both validated: [`assets/dreamrc/`](../assets/dreamrc/README.md)
- MCAP reader — which schemas decode, and how: [reference/viz-dataset-viz-reference.md](../reference/viz-dataset-viz-reference.md)
- Every `.dreamrc` key and view option: [reference/viz-dataset-viz-spec.md](../reference/viz-dataset-viz-spec.md) · [reference/viz-dataset-viz-views.md](../reference/viz-dataset-viz-views.md)
- Foxglove well-known schemas: https://docs.foxglove.dev/docs/visualization/message-schemas/introduction
