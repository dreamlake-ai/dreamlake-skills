# `.dreamrc` examples

Complete files to copy to a dataset root. None carries a `storage:` block —
the app injects the location; add one only while validating a draft locally
(`validate` action). Every key: `reference/viz-dataset-viz-spec.md`.

| file | use |
|---|---|
| `fields.dreamrc` | first drop-in: the `fields` view prints what the dataset holds (set `format`) |
| `lerobot.dreamrc` | LeRobot export: camera wall with 2D keypoint overlay, state chart, subtask timeline |
| `sim-mujoco.dreamrc` | sim-playback dataset with `episode.json.sim: "mujoco"` |
| `sim-urdf.dreamrc` | sim-playback dataset with `episode.json.sim: "urdf"` |
