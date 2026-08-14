# EpisodeTimeline

A zoomable episode-detail timeline: time ruler on top, a frame thumbnail strip
beneath it, and N rows of labelled track blocks under that. The cursor is
**hover-driven** — the user's pointer position is the single source of truth
for the highlighted time. An optional `time` prop provides a fallback position
to display when the pointer leaves (e.g., for syncing with a running video
clock).

Pair with [EpisodeVideoStack](reference/components-episode-video-stack.md) when you have
multi-camera footage that should scrub against the same cursor.

## Basic usage

Pure hover-driven: the cursor follows the pointer; when it leaves, the cursor
disappears.

```tsx file="BasicSpec.tsx"

export const BasicSpec = () => {
  const [t, setT] = useState<number | null>(null)
  return (
    <EpisodeTimeline
      duration={DEMO_DURATION}
      frames={DEMO_FRAMES}
      tracks={DEMO_TRACKS}
      time={t}
      onHover={setT}
      onHoverEnd={() => setT(null)}
    />
  )
}
```

## Frames

`frames` is an **ascending-time-sorted** list of `{ time, image }`. The
component does not re-sort — sorting on every render would be wasteful and
the contract is documented in the type. Frames at the same time deduplicate
naturally because the greedy culler keeps the first one and drops any
followers within `frameWidth + 4px`.

When `frames` is empty, the strip and its footer label collapse entirely —
there's no empty band and no `0 OF 0 FRAMES` readout; the track rows sit
directly beneath the ruler.

Each frame's **left edge** sits at its time on the axis
(`fx = timeToX(f.time)`) — the frame visually represents the chunk starting
at `time`. This keeps the `t = 0` cell fully visible at the timeline's left
edge instead of half-clipped.

```ts
type FrameSample = {
  time: number       // seconds; 0 ≤ time ≤ duration
  image: string      // URL
  alt?: string       // reserved for future a11y surfacing
}

const frames: FrameSample[] = [
  { time: 0,    image: '/keyframes/000.jpg' },
  { time: 0.5,  image: '/keyframes/030.jpg' },
  { time: 1.0,  image: '/keyframes/060.jpg' },
]
```

### Greedy culling

When the visible window is wide (low zoom), many frames would overlap in
screen space. The component sweeps left-to-right and renders a frame only
when its `time` is at least `(frameWidth + 4px) / pxPerSec` later than the
previous rendered frame. Off-screen frames are skipped.

As you zoom in, the visible time window shrinks and `pxPerSec` grows, so the
stride between renderable frames shrinks too — more of the supplied frames
qualify until eventually every one is shown. The footer readout
`{visible} OF {total} FRAMES` updates live as you scrub.

Time positions are exact — each frame's left edge sits at the X
corresponding to its actual `time`, no quantization to evenly-spaced slots.

## Tracks and blocks

Each track is a row; each block is a labelled span `{ start, end, label }`.
Blocks outside the visible window are skipped entirely; blocks that straddle
the edge render with a dashed border on the clipped side to signal
"continues off-screen."

```ts
type TrackBlock = {
  id?: string        // stable key for hover + click callbacks
  start: number
  end: number
  label: string
}

type TimelineTrack = {
  id: string
  name?: string      // accessibility only — not rendered
  blocks: TrackBlock[]
}

const tracks: TimelineTrack[] = [
  {
    id: 'phases',
    blocks: [
      { id: 'p1', start: 0,   end: 2.4, label: 'idle' },
      { id: 'p2', start: 2.4, end: 9.1, label: 'approach' },
    ],
  },
]
```

Provide stable `id` on each block to get reliable hover highlight + callback
identity.

## Interaction model

| Gesture | Effect |
| --- | --- |
| **Hover** | Bright accent cursor pinned to the pointer X; highlights every track block whose `[start, end]` contains the cursor time AND the frame whose visual extent contains it. Fires `onHover(time)` on every move, `onHoverEnd()` on leave. |
| **Click** on empty area | `onSeek(time)` — separate "commit" event distinct from continuous hover. |
| **Click** on a block | `onBlockClick(block, trackId)` — does NOT fire `onSeek`. |
| **Drag** (≥ 4px) | Pans the viewport (when zoomed in). |
| **Shift + drag** vertical | Drag-zoom: drag up to zoom in, down to zoom out. Anchors the time under the cursor. |
| **Wheel + alt/⌘/ctrl** | Zoom at cursor (also fires on trackpad pinch — macOS dispatches `ctrlKey + wheel`). |
| **Wheel** (horizontal-dominant) | Pan when zoomed in. Two-finger horizontal swipes are always swallowed, so a trackpad gesture on the timeline never triggers the browser's back/forward navigation. |
| **ZoomBar** `‹` / `›` | Step zoom by ×1.4 / ÷1.4. |
| **ZoomBar** drag readout | Continuous zoom via `exp(dx × 0.008)`. |

## Controlled vs uncontrolled viewport

`zoom` and `panPct` are optional. Omit them → the component owns viewport
state internally. Provide **either** one → the component flips into
controlled mode for **both** (the omitted value falls back to its default,
but the component no longer writes to its internal state).
`onViewportChange` always fires when the user gestures, so the parent can
persist the new values.

```tsx
// Uncontrolled
<EpisodeTimeline duration={duration} time={t} onSeek={setT} />

// Controlled — persist viewport in URL / localStorage
const [vp, setVp] = useState({ zoom: 1, panPct: 0 })
<EpisodeTimeline
  duration={duration}
  time={t}
  onSeek={setT}
  zoom={vp.zoom}
  panPct={vp.panPct}
  onViewportChange={setVp}
/>
```

```ts
type ViewportState = {
  zoom: number       // ≥ 1
  panPct: number     // 0 ≤ panPct ≤ 1 - 1/zoom
}
```

## Design rules

User-visible behaviour the component enforces:

- **0s strict left edge** — the ruler picks tick steps from a fixed ladder
  (`0.05, 0.1, 0.25, 0.5, 1, 5, 10, …` seconds) and starts ticking at `0`;
  the chart never shows negative time. The `0s` and duration labels stay
  visible at the very edges instead of getting clipped.
- **Anchor zoom** — `⌘` (or `alt` / `ctrl`) + wheel zooms about the cursor:
  the time directly under the pointer stays fixed across the zoom step.
- **Three-tier ruler** — `major / minor / micro`. As zoom changes, ticks
  cross-fade smoothly between tiers instead of popping.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `duration` | `number` | — | Episode duration in seconds. Must be `> 0`. |
| `frames` | `FrameSample[]` | — | Frame thumbnails, sorted ascending by time. |
| `tracks` | `TimelineTrack[]` | — | Track rows, drawn top-to-bottom in array order. |
| `time` | `number \| null` | `null` | Fallback cursor position when the user is NOT hovering. Hover always overrides. `null` → pure hover-driven cursor that disappears on leave. |
| `onHover` | `(t: number) => void` | — | Called continuously on every hover move with the time at the cursor. |
| `onHoverEnd` | `() => void` | — | Called when the cursor leaves the timeline. |
| `onSeek` | `(t: number) => void` | — | Called on click in an empty area (single commit). Clicks on a track block fire `onBlockClick` instead and do NOT fire `onSeek`. |
| `zoom` | `number` | `1` | Controlled zoom level. Clamped to `[minZoom, maxZoom]`. Pairing with `panPct` flips the component into controlled mode for both. |
| `panPct` | `number` | `0` | Controlled pan as fraction of duration. Clamped to `[0, 1 - 1/zoom]`. |
| `onViewportChange` | `(v: ViewportState) => void` | — | Fires when the user changes zoom or pan via wheel/drag. |
| `onBlockClick` | `(block, trackId) => void` | — | Click on a track block (suppresses `onSeek`). |
| `onBlockHover` | `(block \| null, trackId \| null) => void` | — | Hover enter/leave on a track block. Receives `null` on leave. |
| `framesLabel` | `string` | `'FRAMES'` | Left-side uppercase caption under the frame strip. The right side is auto-generated as `{visibleCount} OF {totalCount} FRAMES`. |
| `frameHeight` | `number` | auto | Frame thumbnail height in pixels (width auto from 16:9). When omitted, sized to fit 12 cells with 4px gaps. |
| `trackRowHeight` | `number` | `28` | Track row height. |
| `minZoom` | `number` | `1` | Minimum zoom factor. |
| `maxZoom` | `number` | `20` | Maximum zoom factor. |
| `className` | `string` | — | Extra classes on the root wrapper. |
