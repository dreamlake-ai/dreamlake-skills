# `.dreamrc` for a robot rollout MCAP

Both files here were validated with `check-dreamrc.mts` against a real
rollout (`all N binding(s) decoded`). Place one at the dataset root as
`.dreamrc` (whole folder) or beside the file as `<name>.mcap.dreamrc` (one
mcap). At a real root, **omit `storage:`** — the app injects it; add a
`storage:` line only to validate a standalone draft locally.

| file | variant |
|---|---|
| `embedded-mesh.dreamrc` | **(a)** uses the OBJ meshes carried on `/robot` — one file, no external dependency |
| `external-urdf.dreamrc` | **(b)** tf-only MCAP (skip `/robot`) plus a URDF whose link names match the tf frame names; DreamLake's preset registry `live9080/dreamlake-robots` ships several — this one is Unitree G1 |

See the `dreamrc` and `validate` actions of `dreamlake-datasets` for the
write → validate → fix loop, and `reference/viz-dataset-viz-views.md` for
every view option.

## Validate

```bash
# from a checkout of dreamlake-ai/viz-workspace, in packages/viz/
npx tsx scripts/check-dreamrc.mts hf:your-name/your-repo     # a Hub dataset
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc            # a local draft (needs a storage: line)
```

Expect `/robot → mesh3d`, each `/tf::<body> → transform3d`, `/metrics → series`,
and `all N binding(s) decoded`.
