# Give it a body: embedded mesh or a URDF

Two ways to get the mesh onto the skeleton. Pick one.

| | **(a) Embed the mesh** | **(b) Point at a URDF** |
|---|---|---|
| where the mesh lives | inside the `.mcap`, on `/robot` | an external `.urdf` named in the `.dreamrc` |
| `.dreamrc` binding | `geometry: ["/robot::*"]` | `models: ["…/robot.urdf"]` |
| file size | larger (carries geometry) | smaller (tf-only rollout) |
| self-contained | ✅ one file, no external dep | needs the URL reachable + link names = tf frame names |

**(a) Embed as OBJ or GLB — never STL.** DreamLake's mesh loader accepts
`glb` / `gltf` / `obj` only. If your sim's mesh assets are STL, convert per
body at write time (e.g. read `mesh_vert`/`mesh_face` from the model, apply
each geom's `pos`/`quat`, `trimesh.export(file_type="obj")`), and set the
`ModelPrimitive` `media_type="model/obj"`. STL bytes are silently dropped and
the robot renders as bare axes. `robot_mesh_entities()` in
[`tools/render_mcap.py`](../tools/render_mcap.py) does this for a MuJoCo model.

**(b) Reuse a URDF preset.** If DreamLake's robot registry
(`live9080/dreamlake-robots`) has your robot and its link names match your tf
frame names, skip embedding entirely — emit a tf-only MCAP and let the
`.dreamrc` load the URDF:
`models: ["https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf"]`.
How the viewer resolves a URDF and its package paths:
[reference/viz-dataset-viz-robots.md](../reference/viz-dataset-viz-robots.md).

Both are covered as complete, validated `.dreamrc` files in
[`assets/dreamrc/`](../assets/dreamrc/README.md).

Next: [handoff](handoff.md).
