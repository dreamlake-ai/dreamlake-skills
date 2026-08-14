# EpisodeRecon3d

**A controlled 3D reconstruction view, shaped like the other Episode\***
**components**: pass a `scene` (geometry + its per-frame tracks) plus
`time`/`duration` and it animates — meshes move along their 6-DoF transform
tracks, deforming meshes get new vertices per frame, trails look ahead of the
playhead. Orbit with the mouse.
This is the same scene the platform's annotation viewer renders for
`recon3d` datasets; the example below loads a real exported scene (a ruler +
a toy with MANO hand meshes) from its glTF binary.

```tsx file="BasicSpec.tsx"
// EpisodeRecon3d standalone: a controlled 3D view driven by `time`/`duration`
// props — here a self-running clock; in an app, any shared player clock.
// Everything it renders comes from STANDARD files: geometry from a glTF
// binary (`scene.glb` — nodes `ruler`, `toy`, `left_hand`, `right_hand`),
// and this demo binds nothing per-frame, so the scene shows its rest pose.
// Orbit with the mouse.

const SCENE_URL =
  'https://huggingface.co/datasets/live9080/dreamlake-ceramics/resolve/main/episodes/episode_a/scene.glb'
const DURATION = 5

export function BasicSpec() {
  const [scene, setScene] = useState<Scene3dInput | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [time, setTime] = useState(0)
  const raf = useRef(0)

  useEffect(() => {
    let cancelled = false
    loadGltf(SCENE_URL, 'glb')
      .then((meshes) => {
        if (!cancelled)
          setScene({ meshes, transforms: [], vertexTracks: [], pointTracks: [], upVector: null })
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!scene) return
    const start = performance.now()
    const tick = (now: number) => {
      setTime(((now - start) / 1000) % DURATION)
      raf.current = requestAnimationFrame(tick)
    }
    raf.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf.current)
  }, [scene])

  if (error) return <div className="font-mono text-sm text-red-600">{error}</div>
  if (!scene) return <div className="text-sm opacity-60">Loading scene…</div>
  return (
    <div style={{ height: 360, borderRadius: 8, overflow: 'hidden' }}>
      <EpisodeRecon3d scene={scene} time={time} duration={DURATION} />
    </div>
  )
}
```

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
