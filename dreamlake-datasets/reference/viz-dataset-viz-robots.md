<!-- generated from https://viz.dreamlake.ai/dataset-viz/robots.md at unknown; do not edit -->

<span id="ros-bags--robot-models" />

# Robot motion

An MCAP recording may contain link poses in `/tf`, joint angles in
`/joint_states`, or both. Link poses can be drawn directly. Joint angles need
a robot description to determine where each link goes.

<span id="open-a-recording" />
<span id="the-tf-tree-is-the-3d-scene" />
<span id="what-decodes-with-zero-config" />

## Inspect the frame tree

For a recording with tf messages, add these views to its `.dreamrc`:

```yaml
views:
  - view: recon3d
    up: z
    tracks: [{ field: '/tf::*', as: transform3d }]
  - view: timeline
```

The scene shows axes at tracked frames and connections between them. The reader
composes parent-relative transforms across `/tf` and `/tf_static`. Scrub the
timeline to check the motion; drag the scene to change the viewpoint.

<span id="from-skeleton-to-robot-urdf-models" />

<span id="add-a-urdf" />

## Add the robot geometry

Add `models` to the same `recon3d` entry. For a G1 recording:

```yaml
models:
  - https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf
```

URDF link names match the recorded frame names. Mesh paths resolve relative to
the URDF; supported assets include STL, OBJ, DAE, and glTF. Expand a Xacro file
before loading it. If the meshes appear but do not move, compare the link names
with the fields listed for your recording.

<span id="joint-angles-are-3d-too-forward-kinematics" />

<span id="drive-the-model-with-joint-angles" />

## Use joint states

For a recording of joint angles, bind the topic to `joints` alongside `models`:

```yaml
joints: [/joint_states]
tracks: [{ field: '/tf::pelvis', as: transform3d }]
```

The model supplies the joint axes and link structure for forward kinematics.
Values are matched by joint name, mimic joints follow their source, and bounded
joints use the URDF limits. The optional pelvis track places this robot's base;
without a base pose, it stays at the origin. A link's recorded pose takes
precedence over a computed pose.

<span id="package--pointing-at-a-description-where-it-lives" />

<span id="resolve-ros-package-paths" />
<span id="preset-robots-applied-by-name-match" />
<span id="pointers" />

## Resolve package paths

For `package://` mesh references, provide the package URL when the URDF's own
path does not identify it:

```yaml
models:
  - url: https://example.com/robot/panda.urdf
    packages:
      franka_description: https://example.com/franka_description
```

The generated MCAP layout can choose a preset from matching frame or joint
names. Inspect its `models` entry to see which description was selected, then
replace it if your recording uses a different model. Supported message and
container encodings are listed in the [reader reference](viz-dataset-viz-reference.md#mcap).
