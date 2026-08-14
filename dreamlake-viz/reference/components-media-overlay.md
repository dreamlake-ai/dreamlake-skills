# Media overlays

[EpisodeVideoStack](reference/components-episode-video-stack.md) and
[EpisodeFrameStack](reference/components-episode-frame-stack.md) accept per-source
**overlays** — annotation layers drawn over the media: bounding boxes for
detections, keypoint skeletons for poses and hands. Attach them to the
source; the tile keeps them aligned with the pixels at any player size.

```tsx

const overlays: MediaOverlay[] = [handSkeletons, objectBoxes]

<EpisodeVideoStack
  videos={[{ id: 'ego', src, overlays }]}
  duration={67.5}
/>
```

A stack-level `showOverlays` prop (default `true`) is the master switch;
each overlay also has its own `visible` flag and `opacity`.

## Hand skeletons + captions on a video

Two layers on one video, each converted with one call: real 21-joint hand
detections (`handOverlayFromDetections` — reads pixel space, fps, and
skeleton from the file, applies the per-finger `HAND21_STYLE`) and
labelled subtask segments rendered as subtitle-style captions
(`tracksOverlayFromSubtasks`). Both stay glued to the frame during
playback and while scrubbing:

```tsx file="HandJointsSpec.tsx"

// Egocentric recording + two annotation files in STANDARD formats: COCO
// keypoints (21-joint hand skeletons) and WebVTT (subtitle-style captions).
// The overlay layer itself takes normalized shapes — a keypoint track and a
// list of labelled spans — so any parser can feed it.
const EPISODE =
  'https://huggingface.co/datasets/live9080/dreamlake-ceramics/resolve/main/episodes/episode_a'
const VIDEO = `${EPISODE}/cam_ego.mp4`
const KEYPOINTS = `${EPISODE}/annotations/hand_keypoints.json`
const SUBTASKS = `${EPISODE}/annotations/subtasks.vtt`

async function fetchText(url: string): Promise<string> {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.text()
}

export const HandJointsSpec = () => {
  const [overlays, setOverlays] = useState<MediaOverlay[]>()
  const [duration, setDuration] = useState(33.7)
  const [error, setError] = useState<string>()

  // One TimelineClock is the single playhead: play advances it, hovering a
  // tile SEEKS it (even mid-playback), pause parks it — playback always
  // resumes from wherever the playhead is. Inside <ClockProvider> the
  // <video> plays natively while the clock runs.
  const { clock, state, play, pause, seek, setLoop } = useTimeline(duration)
  const time = useClockValue(30, clock)
  useEffect(() => {
    setLoop(true)
    play()
  }, [setLoop, play])

  useEffect(() => {
    let cancelled = false
    Promise.all([fetchText(KEYPOINTS), fetchText(SUBTASKS)])
      .then(([cocoText, vtt]) => {
        if (cancelled) return
        const track = parseCocoKeypoints(JSON.parse(cocoText))
        const segments = parseWebVtt(vtt)
        setOverlays([
          keypointsOverlayFromTrack(track), // 21-joint skeletons
          tracksOverlayFromSegments(segments), // subtitle captions
        ])
        const lastFrame = Math.max(...track.frames.keys())
        if (Number.isFinite(lastFrame)) setDuration((lastFrame + 1) / track.fps)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e))
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="flex flex-col gap-2">
      <ClockProvider clock={clock}>
        <EpisodeVideoStack
          columns={1}
          videos={[
            {
              id: 'ego',
              src: VIDEO,
              title: 'Ceramics',
              subtitle: 'claru_ego · hand skeletons + subtask captions',
              overlays,
            },
          ]}
          duration={duration}
          time={time}
          onHover={seek}
        />
      </ClockProvider>
      <button
        type="button"
        onClick={state.playing ? pause : play}
        className="self-start rounded px-2 py-1 font-mono text-[11px] opacity-60 hover:opacity-100 hover:bg-current/10"
      >
        {state.playing ? '⏸ pause' : '▶ play'}
      </button>
      {error && (
        <p className="font-mono text-[11px] opacity-60">
          hand-joints fetch failed ({error}) — the demo bucket must allow
          cross-origin GET.
        </p>
      )}
    </div>
  )
}
```

## Bounding boxes on a frame stack

Hand-authored synthetic detections in **normalized** coordinates, keyed by
frame index. The `cup` only exists on frames 30–75 — sparse keys draw
nothing, so boxes appear and disappear with the data instead of going
stale:

```tsx file="BBoxOverlaySpec.tsx"

const FRAME_COUNT = UNTIMED_FRAMES.length

// Synthetic detections in NORMALIZED coordinates (0..1 of the frame), keyed
// by frame index. One "gripper" track orbits slowly; a "cup" exists only on
// frames 30–75 — sparse keys simply draw nothing, they never go stale.
function buildDetections(): BBoxOverlay {
  const frames: Record<number, BBoxItem[]> = {}
  for (let i = 0; i < FRAME_COUNT; i++) {
    const a = (i / FRAME_COUNT) * 2 * Math.PI
    const x = 0.38 + 0.22 * Math.cos(a)
    const y = 0.35 + 0.18 * Math.sin(a)
    const items: BBoxItem[] = [
      {
        box: [x, y, x + 0.22, y + 0.3],
        label: 'gripper',
        trackId: 'gripper-0',
        score: 0.93,
      },
    ]
    if (i >= 30 && i <= 75) {
      items.push({
        box: [0.66, 0.12, 0.92, 0.42],
        label: 'cup',
        trackId: 'cup-0',
        score: 0.81,
      })
    }
    frames[i] = items
  }
  return {
    id: 'detections',
    kind: 'bbox',
    space: { units: 'normalized' },
    data: { by: 'frame', frames },
    style: { showScore: true },
  }
}

export const BBoxOverlaySpec = () => {
  const overlays = useMemo(() => [buildDetections()], [])
  return (
    <EpisodeFrameStack
      columns={2}
      sources={[
        {
          id: 'front',
          frames: UNTIMED_FRAMES,
          title: 'front',
          subtitle: 'synthetic detections',
          overlays,
        },
        {
          id: 'top',
          frames: UNTIMED_FRAMES,
          title: 'top',
          subtitle: 'no overlay',
        },
      ]}
    />
  )
}
```

## Declaring coordinates

Overlay coordinates live in the **media's** space — never the player's.
Each overlay says which flavor via `space`:

```ts
type OverlaySpace =
  | { units: 'pixel'; width: number; height: number } // annotation-time frame size
  | { units: 'normalized' }                           // x, y already in 0..1
```

- **Pixel coordinates carry the frame size they were produced against**
  (not the runtime `videoWidth`, which can differ after transcode/rotation).
- **Out-of-frame points are legal** — partially visible detections draw and
  get clipped, never clamped.
- Stroke widths and dot radii are CSS px at render size, so a 2px bone
  reads as 2px on any player.

## What draws at time *t*

Each overlay's `data` field says how to look up "the items for right now".
Missing data draws nothing — stale items are never carried over.

```ts
type OverlayFrameData<T> =
  | { by: 'frame'; frames: Record<number, T[]>; fps?: number; frameOffset?: number }
  | { by: 'time'; entries: { time: number; items: T[] }[]; tolerance?: number }
```

| | `by: 'frame'` | `by: 'time'` |
| --- | --- | --- |
| **Video stack** | key = `round(time × fps)`; `fps` required (source fps is often fractional). | nearest entry within `tolerance` (default 0.1 s). |
| **Frame stack** | key = the displayed image's `frameIndex ?? array index`. | matched against `FrameImage.timestamp`. |

On a video, the lookup follows the frame the `<video>` actually presents
(`overlaySync: 'media'`, the default), so drawings never lead or lag the
pixels; `'cursor'` follows the `time` prop instead (deterministic — SSR,
tests).

## Reference

### `bbox`

```ts
interface BBoxItem {
  box: [number, number, number, number]  // [x1, y1, x2, y2]
  label?: string
  score?: number                         // 0..1
  trackId?: string | number              // same id ⇒ same color across frames
  color?: string                         // explicit override
}
```

| `BBoxStyle` | Default | |
| --- | --- | --- |
| `strokeWidth` | `1.5` | |
| `stroke` / `fill` | palette / `transparent` | |
| `showLabel` / `showScore` | `true` / `false` | `showScore` appends: `cup 0.92`. |
| `colorBy` | `'label'` | or `'trackId'` / `'fixed'`. |
| `palette` | built-in | cycled per `colorBy` key. |

### `keypoints`

```ts
interface KeypointsItem {
  points: ([number, number] | [number, number, number])[] // z reserved for 3D
  pointScores?: number[]
  score?: number
  box?: [number, number, number, number]  // drawn when style.showBox
  group?: string                          // coloring key, e.g. 'left' / 'right'
  color?: string
}

interface KeypointsOverlay {
  kind: 'keypoints'
  skeleton?: [number, number][]  // bones as index pairs into points
  jointNames?: string[]
  data: OverlayFrameData<KeypointsItem>
  style?: KeypointsStyle
  // …common fields: id, space, visible, opacity, minScore
}
```

| `KeypointsStyle` | Default | |
| --- | --- | --- |
| `jointRadius` / `boneWidth` | `2.5` / `1.5` | |
| `boneColors` | — | per-bone, same order as `skeleton` — how per-finger coloring works. |
| `jointColors` | derived | each joint takes the color of the bone ending at it. |
| `rootColor` | `#ffffff` | joints no bone ends at (the wrist). |
| `groupColors` | — | whole-instance color per `group` — the simple mode. |
| `showBox` | `false` | also draw the detection `box`. |
| `minPointScore` | `0` | hide low-confidence joints. |

### `tracks` — subtitle-style captions

Labelled time ranges rendered like video subtitles: whichever block spans
the current time draws as an outlined caption at the bottom of the tile.
The data shape is the same `TimelineTrack` / `TrackBlock` that
[EpisodeTimeline](reference/components-episode-timeline.md) takes, so one dataset feeds
both the caption overlay and a timeline track row:

```ts
interface TracksOverlay {
  kind: 'tracks'
  tracks: { id: string; name?: string; blocks: TrackBlock[] }[]
  style?: { fontSize?: number; color?: string } // default 12px / white
  // …common fields: id, visible, opacity
}

type TrackBlock = { id?: string; start: number; end: number; label: string } // seconds
```

Time-range based — no coordinate `space`, no frame keys.

## Data formats

Each converter — and the matching schema `format:` value — expects
**exactly** the JSON shape below. Data in any other shape needs
`format: raw` (a file that already contains `MediaOverlay` JSON) or a
custom conversion in code.

### `handJoints` → keypoints overlay

`HandJointsFile` — the hand-detection pipeline output (this is the format
of the live example's `claru_ego__Ceramics.json`). Frames are keyed by
**0-based index of the original video**; coordinates are full-resolution
pixels in upright orientation. Field-by-field, the conversion is:

```jsonc
{
  "width": 1920, "height": 1080,       // → space { units: "pixel", width, height }
  "src_fps": 29.987,                   // → data.fps (playback time → frame key)
  "joint_order": ["wrist", "…21"],     // → jointNames
  "bones": [[0, 1], "…20 pairs"],      // → skeleton (4 per finger, thumb → pinky)
  "frames": {                          // sparse → data.frames (missing key = no hands)
    "0": [{
      "is_right": 1,                   // → group "right" | "left"
      "det_conf": 0.98,                // → score
      "bbox": [x1, y1, x2, y2],        // → box
      "keypoints_2d": [[x, y], "…21"]  // → points
    }]
  },
  "total_frames": 2024
}
```

```tsx

const overlay = handOverlayFromDetections(file) // + per-finger HAND21_STYLE
```

### `subtasks` → caption overlay + timeline track

`SubtasksFile` — subtask segment annotations: one labelled range per
segment, in **seconds from video start**:

```jsonc
{
  "video": "713488",
  "task": "mount a wall shelf",        // → track name
  "labeled_subtasks": [
    { "start_sec": 0.0, "end_sec": 2.5, "subtask": "pick up shelf board" },
    { "start_sec": 2.5, "end_sec": 10.5, "subtask": "mount shelf board on wall tracks" }
  ]
}
```

Two converters read it — the **same blocks** drive the subtitle overlay
and an `EpisodeTimeline` track:

```tsx

const overlay = tracksOverlayFromSubtasks(file) // kind: 'tracks' captions
const timelineTracks = [
  { id: 'subtasks', blocks: trackBlocksFromSubtasks(file) }, // <EpisodeTimeline tracks>
]
```

See both live in the
[schema example](reference/schema-viz-schema.md#end-to-end-hand-skeletons-via-overlays):
a `videoStack` panel names the files by field ref with
`format: handJoints` / `format: subtasks`, and a `timeline` panel shows
the same subtasks as a track row.
