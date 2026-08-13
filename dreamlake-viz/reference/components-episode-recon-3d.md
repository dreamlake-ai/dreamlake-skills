# EpisodeRecon3d

**A controlled 3D reconstruction view, shaped like the other Episode\*
components**: pass `loaded` (the parsed reconstruction) plus `time`/`duration`
and it animates — meshes move along their 6-DoF pose tracks, hand meshes
deform per frame, trails look ahead of the playhead. Orbit with the mouse.
This is the same scene the platform's annotation viewer renders for
`recon3d` spaces; the example below plays a real exported episode (a ruler +
a toy with MANO hands).

## Data in

Build `loaded` from a **recon3d JSON doc** (see the
[dataset-viz authoring guide](reference/dataset-viz-authoring.md) for the shape — mesh /
pose / hands / gravity / camera in the camera's OpenCV frame):

```ts

const loaded = loadedFromReconDoc(await (await fetch(url)).json())
<EpisodeRecon3d loaded={loaded} time={t} duration={clipSeconds} />
```

Animated 3D **point sets** (hand keypoints, skeletons) ride along as
`pointTracks`:

```ts

loaded.pointTracks = [pointTrackFromPose3d('left_hand', { timestamps, joints })]
```

## Props

| prop | type | meaning |
| --- | --- | --- |
| `loaded` | `Loaded` | the parsed scene — `loadedFromReconDoc(doc)` |
| `time` | `number \| null` | playback position (seconds); null → first frame |
| `duration` | `number` | clip length — maps time onto the frame span |
| `showTrails` | `boolean` | forward-looking motion trails (default on) |
| `interactive` | `boolean` | orbit controls (default on; off for thumbnails) |

In a `.dreamrc`, the `recon3d` view component wraps this — `fields` binds
`recon3d`/`pose3d` tracks and the shared cursor drives `time`.
