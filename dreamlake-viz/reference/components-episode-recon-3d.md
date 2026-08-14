# EpisodeRecon3d

**A controlled 3D reconstruction view, shaped like the other Episode\***
**components**: pass a `scene` (geometry + its per-frame tracks) plus
`time`/`duration` and it animates — meshes move along their 6-DoF transform
tracks, deforming meshes get new vertices per frame, trails look ahead of the
playhead. Orbit with the mouse.
This is the same scene the platform's annotation viewer renders for
`recon3d` datasets; the example below loads a real exported scene (a ruler +
a toy with MANO hand meshes) from its glTF binary.

## Data in

Geometry comes from a **glTF / GLB** file; everything per-frame comes from the
dataset as separate tracks. **The glTF node name is the join key** — a
`transform3d` track named `ruler` (or `ruler_pose`, `poses[ruler]`) drives the
node named `ruler`.

```ts

const meshes = await loadGltf(url, 'glb')       // nodes: ruler, toy, left_hand, …
const scene: Scene3dInput = {
  meshes,
  transforms: [],    // { name, timestamps, values (rows×7), layout }
  vertexTracks: [],  // { name, count, fps?, vertexCount, at(i) } — deforming meshes
  pointTracks: [],   // animated 3D point sets (21 points draw a hand skeleton)
  upVector: null,    // gravity in the data's frame → upright grid
}
<EpisodeRecon3d scene={scene} time={t} duration={clipSeconds} />
```

`pointTrackFromPose3d(name, payload)` turns a `pose3d` read into a point
track.

## Props

| prop | type | meaning |
| --- | --- | --- |
| `scene` | `Scene3dInput` | meshes + per-frame tracks (see above) |
| `time` | `number \| null` | playback position (seconds); null → first frame |
| `duration` | `number` | clip length — maps time onto each track's own span |
| `showTrails` | `boolean` | forward-looking motion trails (default on) |
| `interactive` | `boolean` | orbit controls (default on; off for thumbnails) |

In a `.dreamrc`, the `recon3d` view component wraps this — `fields` binds the
`mesh3d` / `transform3d` / `vertices3d` / `pose3d` tracks and the shared
cursor drives `time`.
