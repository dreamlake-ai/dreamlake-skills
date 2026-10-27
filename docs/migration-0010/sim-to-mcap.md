# Migration: sim-to-mcap (kept as its own skill)

**Decision:** not merged into `dreamlake-datasets`. Rolling a trained policy out
in a local simulator and writing MCAP is a distinct user goal that an RL/sim
user installs on its own (merge-caution rule 2a). It `requires`
`dreamlake-datasets` (closure brings `dreamlake-cli`) and hands off by name to
that skill's `upload` / `connect` / `dreamrc` / `validate` actions. The
integrator may want `renamed.json` to leave `sim-to-mcap` unmapped.

| Source file / section | Destination |
|---|---|
| `SKILL.md` (when to use, install foxglove-sdk, three channels, hand-off, numeric-only runs use charts) | `SKILL.md` router + rules + boundaries |
| `references/write-rollout.md` §1 Emit three channels (table, install) | `actions/write-rollout.md` §1 |
| `references/write-rollout.md` §2 Roll out and write (loop, quaternion order, `/robot` once frame_locked) | `actions/write-rollout.md` §2 |
| `references/write-rollout.md` §3 Give it a body — embedded mesh OR a URDF (table, OBJ/GLB never STL, `live9080/dreamlake-robots` preset) | `actions/embody.md` |
| `references/handoff-and-debug.md` §4 Hand off (upload with provider tools, `.dreamrc` with `format: mcap`, `<file>.mcap.dreamrc`) | `actions/handoff.md` §top — "there is no upload-into-source API yet" updated: `dreamlake source upload` now exists (cli docs) |
| `references/handoff-and-debug.md` §Gotchas table | `actions/handoff.md` §Gotchas |
| `references/handoff-and-debug.md` §Reference (template, examples, viz reference/spec/views, Foxglove schemas) | `actions/handoff.md` §Reference; viz URLs → `docs[]`, Foxglove URL stays absolute |
| `reference/dreamrc-examples.md` intro + §Validate | `assets/dreamrc/README.md` |
| `reference/dreamrc-examples.md` §(a) Embedded mesh YAML | `assets/dreamrc/embedded-mesh.dreamrc` |
| `reference/dreamrc-examples.md` §(b) External URDF YAML | `assets/dreamrc/external-urdf.dreamrc` |
| `reference/render_mcap.py` | `tools/render_mcap.py` (git mv; two pure helpers `wxyz_to_xyzw`, `log_time_ns` extracted from `main()` so the file can carry a test — behaviour unchanged) |
| (no test existed) | `tools/test_render_mcap.py` added: compiles, quaternion reorder, nanosecond log time, OBJ/frame_locked/once rules present |
| docs URLs cited: viz reference/spec/views; `docs.dreamlake.ai/sim-rollouts` (the page that documents this skill) | `skill.json` `docs[]` (+ `docs/sources` for the hand-off, viz `dataset-viz/robots` for the URDF option) |
