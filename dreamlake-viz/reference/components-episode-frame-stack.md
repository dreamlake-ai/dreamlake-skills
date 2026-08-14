# EpisodeFrameStack

The still-image sibling of [EpisodeVideoStack](reference/components-episode-video-stack.md):
the same tile chrome — REC-style stamp, label, auto-detected resolution,
scrub line, active ring — but each tile scrubs a sequence of `<img>` frames
instead of seeking a `<video>`. Moving the pointer across a tile snaps to the
**nearest frame** for the cursor position; the frame shown stays on screen
until the next one has decoded, so scrubbing doesn't flash.

Unlike the video stack, **there is no `duration` prop**. The total span is
derived from the earliest and latest frame `timestamp` across all sources.

## Derived span

Each frame carries a `timestamp` — a per-frame Unix time in **seconds**
(the upstream `_ts`). The component computes the cursor span from the first
and last frame and maps the pointer's X fraction onto it:

- **Timestamped** — when frames carry real times, `duration = lastTs − firstTs`
  and each tile shows the frame nearest the cursor's time.
- **No valid timestamp** — when a frame's time isn't a real recorded value
  (`0`, negative, `NaN`/`Infinity`, or out of the representable date range),
  frames fall back to uniform index spacing.

Keep a single stack homogeneous: all of its sources should either carry real
timestamps or none should. (A stack mixes one shared cursor span across every
tile, so combining recorded and unrecorded sources in the same stack isn't
meaningful.)

## Timestamped

Three cameras sharing one cursor. Hover any tile — every tile snaps to the
frame nearest that moment, and the top-left stamp shows the hovered frame's
wall-clock time (`YYYY-MM-DD HH:MM:SS`, local).

```tsx file="TimestampedSpec.tsx"

// Three cameras, each a sequence of stills with real per-frame Unix
// timestamps. Total span is derived from the first/last frame, so no
// `duration` prop is needed. The top-left stamp shows the hovered
// frame's wall-clock time.
const SOURCES: FrameImageSource[] = [
  { id: 'front', frames: TIMESTAMPED_FRAMES, title: 'front', subtitle: '/camera/front/image_compressed' },
  { id: 'wrist', frames: TIMESTAMPED_FRAMES, title: 'wrist', subtitle: '/camera/wrist/image_compressed' },
  { id: 'top',   frames: TIMESTAMPED_FRAMES, title: 'top',   subtitle: '/camera/top/image_compressed' },
]

export const TimestampedSpec = () => <EpisodeFrameStack sources={SOURCES} />
```

## Invalid timestamp → frame index

This specimen uses `timestamp: 0`, but the rule is general: any frame whose
time isn't a valid recorded value — `0`, negative, `NaN`/`Infinity`, or out of
the representable date range — is treated the same way. With no real times to
position by, the stack spaces frames uniformly by index and the stamp reads
`FRAME n / N` instead of a date.

```tsx file="FrameIndexSpec.tsx"

// Same frames, but with `timestamp: 0` (the upstream `_ts` was never
// recorded). The stack falls back to uniform index spacing and the
// top-left stamp reads `FRAME n / N` instead of a date.
const SOURCES: FrameImageSource[] = [
  { id: 'front', frames: UNTIMED_FRAMES, title: 'front', subtitle: '/camera/front/image_compressed' },
  { id: 'wrist', frames: UNTIMED_FRAMES, title: 'wrist', subtitle: '/camera/wrist/image_compressed' },
]

export const FrameIndexSpec = () => <EpisodeFrameStack sources={SOURCES} columns={2} />
```

## Bounding-box overlays

Each source can carry [annotation overlays](reference/components-media-overlay.md); on
a frame stack they key on the displayed image (`frameIndex ?? array index`)
and always describe the frame actually on screen. These synthetic
detections are **normalized** (`0..1` of the frame) — the `cup` box exists
only on frames 30–75, so it appears and disappears with the data:

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

## Frame source shape

```ts
interface FrameImage {
  timestamp: number   // per-frame Unix seconds; invalid (0, NaN, …) = no recorded time
  image: string       // URL — remote, data:, or blob:
  alt?: string
  frameIndex?: number // index in the ORIGINAL media, for subsampled sequences
}

interface FrameImageSource {
  id: string
  frames: FrameImage[]   // sorted ascending by timestamp
  title?: string         // bottom-left label, uppercased
  subtitle?: string      // bottom-left mono sub-label
  poster?: string        // shown before the first frame loads
  overlays?: MediaOverlay[] // annotation layers — see /components/media-overlay
}
```

The tile's top-left stamp is computed per hovered frame: a frame with a valid
recorded time shows the formatted wall-clock; any invalid time (`0`, negative,
`NaN`/`Infinity`, or out of the representable date range) shows its
`FRAME n / N` position instead.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `sources` | `FrameImageSource[]` | — | Frame sequences, one tile each, left-to-right. |
| `time` | `number \| null` | `null` | Controlled cursor time (seconds from start). Internal hover overrides it while the pointer is over the stack. |
| `onHover` | `(t: number) => void` | — | Fires on every hover move with the time-from-start at the cursor. |
| `onHoverEnd` | `() => void` | — | Fires when the cursor leaves the entire stack. |
| `activeId` | `string \| null` | — | Controlled active-tile id (the accent-ring tile). |
| `defaultActiveId` | `string \| null` | `null` | Uncontrolled initial active-tile id. |
| `onActiveChange` | `(id: string) => void` | — | Fires on hover-enter of a new tile, with that tile's id. |
| `columns` | `number` | `3` | Grid column count. |
| `gap` | `number` | `6` | Pixel gap between adjacent tiles. |
| `showRecTimestamp` | `boolean` | `true` | Top-left stamp — wall-clock time, or `FRAME n / N` when unrecorded. |
| `showLabel` | `boolean` | `true` | Bottom-left title + subtitle. |
| `showResolution` | `boolean` | `true` | Bottom-right resolution, auto-detected from the rendered `<img>`. |
| `showOverlays` | `boolean` | `true` | Master switch for all `FrameImageSource.overlays` layers. |
| `className` | `string` | — | Extra classes on the root grid. |
