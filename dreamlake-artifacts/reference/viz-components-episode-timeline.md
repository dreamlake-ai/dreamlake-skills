<!-- generated from https://viz.dreamlake.ai/components/episode-timeline.md at 0.31.3 545152ca; do not edit -->

# Timeline

`EpisodeTimeline` combines thumbnails and labeled intervals on an episode
clock. Use it to inspect an event and seek paired video or charts.

The surface is transparent by default, so the timeline sits on its parent's
surface. Use `background="subtle"` when a separate tinted panel is useful.
Annotation and loading-range colors remain visible with either setting.
Short major and minor ruler ticks distinguish fractional seconds without a
full-height grid; labels adapt to the recording duration and available width.

## Basic usage

Hover to preview a moment; click to seek. Zoom in to reveal more thumbnails:

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

```tsx
<EpisodeTimeline
  duration={60}
  frames={frames}
  tracks={tracks}
  time={time}
  onHover={setHover}
  onHoverEnd={() => setHover(null)}
  onSeek={setTime}
/>
```

Hover temporarily overrides `time`. On pointer leave, the cursor returns to
that value, or disappears when it is `null`. Keep playback time separate when
hover should preview without committing a seek.

## Shared click-to-pin and hover preview

Use one shared clock and `useTimelinePreview(clock)` for linked plots, video or
3D views. Clicking pins a time; hover still previews other moments in every view.
Leaving the current preview returns all views to the pin. Without a pin, leave
restores the time from before the first preview.

```tsx file="SharedPinPreviewSpec.tsx"

const duration = 3;
const charts = [
  {
    id: "position",
    title: "Recorded position",
    series: [
      {
        id: "position",
        label: "Position",
        color: "#3388aa",
        data: { x: [0, 0.3, 0.8, 1.4, 2.1, 2.6, 3], y: [0, 2, 1, 4, 3, 5, 4] },
      },
    ],
  },
  {
    id: "force",
    title: "Recorded force",
    series: [
      {
        id: "force",
        label: "Force",
        color: "#418a61",
        data: { x: [0, 0.3, 0.8, 1.4, 2.1, 2.6, 3], y: [1, 1, 3, 2, 4, 2, 1] },
      },
    ],
  },
];

// This child reads the provider's clock, just as a paired video or 3D view can.
function SharedClockReadout() {
  const time = useClockValue(30);
  return (
    <output data-testid="shared-clock-time">
      All views: {time.toFixed(3)} s
    </output>
  );
}

export function SharedPinPreviewSpec() {
  const { clock, state, pause } = useTimeline(duration);
  const time = useClockValue(30, clock);
  const preview = useTimelinePreview(clock);
  const [selectedTime, setSelectedTime] = useState(1.5);
  const [viewport, setViewport] = useState({ zoom: 1, panPct: 0 });
  const bind = (owner: string) => ({
    time,
    onHover: (next: number) => preview.preview(owner, next),
    onHoverEnd: () => preview.endPreview(owner),
    onSeek: preview.pin,
  });
  const previewSelected = (next: number) => {
    setSelectedTime(next);
    preview.preview("time-control", next);
  };
  return (
    <ClockProvider clock={clock}>
      <div data-testid="shared-pin-preview-demo" className="min-w-0 space-y-3">
        <p className="text-xs opacity-65">
          Click either plot to pin all views. Hover another moment, then leave:
          every view returns to the pin. Hover keeps working after a click.
        </p>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,200px),1fr))] gap-2">
          {charts.map((chart) => (
            <EpisodeLineChart
              key={chart.id}
              title={chart.title}
              series={chart.series}
              duration={duration}
              size="compact"
              height={150}
              {...bind(chart.id)}
              isScrubOwner={preview.previewOwner === chart.id}
              {...viewport}
              onViewportChange={setViewport}
            />
          ))}
        </div>
        <EpisodeTimeline
          duration={duration}
          {...bind("timeline")}
          {...viewport}
          onViewportChange={setViewport}
        />
        <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
          <SharedClockReadout />
          <output data-testid="shared-pin-time" aria-live="polite">
            {preview.pinnedTime == null
              ? "No pin"
              : `Pinned: ${preview.pinnedTime.toFixed(3)} s`}
          </output>
          <span>
            {preview.previewOwner == null
              ? "No preview"
              : `Preview: ${String(preview.previewOwner)}`}
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <label className="flex items-center gap-2">
            Preview time
            <input
              aria-label="Preview time"
              type="range"
              min={0}
              max={duration}
              step={0.01}
              value={selectedTime}
              onFocus={() => preview.preview("time-control", selectedTime)}
              onPointerDown={() =>
                preview.preview("time-control", selectedTime)
              }
              onChange={(event) => previewSelected(Number(event.target.value))}
              onPointerUp={() => preview.endPreview("time-control")}
              onPointerCancel={() => preview.endPreview("time-control")}
              onBlur={() => preview.endPreview("time-control")}
              onKeyDown={(event) => {
                if (event.key === "Enter") preview.pin(selectedTime);
                if (event.key === "Escape") preview.endPreview("time-control");
              }}
            />
            {selectedTime.toFixed(2)} s
          </label>
          <button
            type="button"
            onClick={() => preview.pin(selectedTime)}
            className="rounded border border-black/15 px-2 py-1 dark:border-white/15"
          >
            Pin selected time
          </button>
          <button
            type="button"
            onClick={preview.clearPin}
            disabled={preview.pinnedTime == null}
            className="rounded border border-black/15 px-2 py-1 disabled:opacity-40 dark:border-white/15"
          >
            Clear pin
          </button>
          <button
            type="button"
            onClick={
              state.playing && preview.previewOwner == null
                ? pause
                : preview.play
            }
            className="rounded border border-black/15 px-2 py-1 dark:border-white/15"
          >
            {state.playing && preview.previewOwner == null
              ? "Pause"
              : "Play / resume"}
          </button>
        </div>
        <p className="text-xs opacity-65">
          The slider supports touch and arrow keys; Enter pins its selected
          time. Escape, blur or touch release ends its preview. Pin pauses
          playback; Play / resume clears pin and preview, then advances from the
          displayed time.
        </p>
      </div>
    </ClockProvider>
  );
}
```

The example has two transparent 150px charts, a timeline and a child readout
subscribed through `ClockProvider`. A 3D scene or video should consume the same
clock with `useClockValue(fps, clock)` or through the provider. Do not copy the
pin into independent state for each chart, and do not guard hover with
`if (!pinnedTime)`: a pin is the return time, not a hover lock.

```tsx

const { clock } = useTimeline(duration);
const time = useClockValue(30, clock);
const preview = useTimelinePreview(clock);
const bind = (owner: string) => ({
  time,
  onHover: (time: number) => preview.preview(owner, time),
  onHoverEnd: () => preview.endPreview(owner),
  onSeek: preview.pin,
});

<EpisodeLineChart {...bind("position")} series={position} duration={duration} />
<EpisodeLineChart {...bind("force")} series={force} duration={duration} />
<EpisodeTimeline {...bind("timeline")} duration={duration} />
```

Assign each view a stable owner ID. A new owner's preview takes over immediately;
a late `endPreview` from the previous owner is ignored. All owners share the
original return time until the current preview ends. The hook resolves an
explicit clock or the surrounding `ClockProvider`; hook consumers of the same
clock share its controller. Prefer creating it once at the linked group's root.

The hook restores an active preview and releases its hold when its last consumer
unmounts. For non-React integrations, `new TimelinePreviewController(clock)`
exposes the same actions plus `getSnapshot()` and `subscribe(listener)`; call
`dispose()` when finished. Construction and server rendering do not seek or
subscribe to the clock.

### Preview controller API

| Member                 | Meaning                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| `pinnedTime`           | Committed return time in seconds, or `null`.                                             |
| `previewTime`          | Current transient preview time, or `null`.                                               |
| `previewOwner`         | Current string or symbol owner ID, or `null`.                                            |
| `preview(owner, time)` | Move the shared clock to a transient time; works while pinned.                           |
| `endPreview(owner)`    | Restore the pin or pre-preview time if this owner is still current.                      |
| `pin(time)`            | Pause and commit a shared return time; preserve current ownership so hover continues.    |
| `clearPin()`           | Remove the pin without changing the displayed time or ending an ongoing preview.         |
| `play()`               | Clear pin and preview, release the controller's hold, then play from the displayed time. |

Times are episode seconds. Non-finite inputs are ignored; finite times clamp to
the clock's duration. This changes only the displayed clock time: charts still
read nearest recorded samples and keep exact data and domains.

### Playback, keyboard and touch

Preview temporarily holds clock advancement without changing its `playing`
flag or other holds. Leaving restores the return time and releases that hold;
playback then continues if it was running. Pinning pauses playback. The
controller's `play()` is the explicit resume action: it clears pin and preview
before calling `clock.play()`, including when playback was already logically
running but held by preview. An external seek clears the controller's pin and
preview as a navigation override; use `preview()` for transient inspection.

The native slider and buttons in the example make the same actions available
to keyboard and touch users. Arrow keys preview the selected time, Enter pins,
and Escape or blur ends the slider preview. Touch release ends its preview;
"Pin selected time" commits it. Plot and timeline clicks also call `pin`.
Chart zoom/pan keyboard controls keep their existing behavior. If another
component implements its own controls, route them through this same controller.

## Frames

Supply thumbnails in ascending time order. Their left edges mark their
timestamps. Omit `frames` to show only the ruler and annotation tracks.

```ts
interface FrameSample {
  time: number; // seconds, from 0 to duration
  image: string;
  alt?: string; // retained in data; not currently surfaced by the canvas
}

const frames: FrameSample[] = [
  { time: 0, image: "/keyframes/000.jpg" },
  { time: 0.5, image: "/keyframes/030.jpg" },
  { time: 1, image: "/keyframes/060.jpg" },
];
```

<span id="greedy-culling" />

### Reveal more frames

The strip hides overlapping thumbnails with a four-pixel gap between visible
images. Zooming reveals more of the supplied frames; the footer reports visible
and total counts. The first frame at a duplicate timestamp is kept.

## Tracks and blocks

Place task phases or actions in separate rows. Dashed edges mark intervals
that continue outside the visible window.

```ts
interface TrackBlock {
  id?: string;
  start: number;
  end: number;
  label: string;
}
interface TimelineTrack {
  id: string;
  name?: string; // accessible name, not a visible row label
  blocks: TrackBlock[];
}

const tracks: TimelineTrack[] = [
  {
    id: "phases",
    name: "Task phases",
    blocks: [
      { id: "idle", start: 0, end: 2.4, label: "Idle" },
      { id: "approach", start: 2.4, end: 9.1, label: "Approach" },
    ],
  },
];
```

Use stable block IDs for callbacks. A block click calls `onBlockClick` instead
of `onSeek`, allowing annotation inspection without moving playback.

## Interaction model

| Gesture                    | Result                                                                         |
| -------------------------- | ------------------------------------------------------------------------------ |
| Hover                      | Show the cursor and call `onHover(time)`; call `onHoverEnd` on leave.          |
| Click empty space          | Call `onSeek(time)`.                                                           |
| Click a block              | Call `onBlockClick(block, trackId)`.                                           |
| Drag at least four pixels  | Pan when zoomed in.                                                            |
| Shift + vertical drag      | Zoom around the initial pointer position.                                      |
| Alt, Ctrl, or Meta + wheel | Zoom around the pointer; trackpad pinch also uses this path.                   |
| Horizontal wheel           | Pan. The timeline consumes this gesture to prevent browser history navigation. |
| Zoom controls              | Step zoom or drag the readout for continuous adjustment.                       |

## Controlled vs uncontrolled viewport

A standalone timeline manages zoom and pan. Share viewport state to align it
with other panels:

```tsx
const [viewport, setViewport] = useState({ zoom: 1, panPct: 0 })
<EpisodeTimeline
  duration={duration}
  {...viewport}
  onViewportChange={setViewport}
/>
```

```ts
interface ViewportState {
  zoom: number; // 1 shows the full episode
  panPct: number; // 0 through 1 - 1 / zoom
}
```

The window starts at `panPct * duration` and spans `duration / zoom`. Providing
either value controls both; an omitted value uses its default. Apply gestures
through `onViewportChange` and reset to `{ zoom: 1, panPct: 0 }`. Try the
[shared viewport example](viz-components-episode-line-chart.md#shared-zoom-and-pan).

<span id="design-rules" />

## Loading ranges

Zoom anchors to the pointer and stays inside the episode. For chunked data,
pass `loadedRanges` and `pendingRanges` as `{ from, to }` intervals in episode
seconds to mark available and loading regions.

## Props

| Prop                  | Type                                                           | Default          | Purpose                                                                      |
| --------------------- | -------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------- |
| `duration`            | `number`                                                       | required         | Episode duration in seconds, greater than zero.                              |
| `frames`              | `FrameSample[]`                                                | `[]`             | Thumbnails in ascending time order.                                          |
| `tracks`              | `TimelineTrack[]`                                              | `[]`             | Track rows, in display order.                                                |
| `time`                | `number \| null`                                               | `null`           | Cursor position when the pointer is not hovering.                            |
| `onHover`             | `(t: number) => void`                                          | —                | Receive the pointer's time.                                                  |
| `onHoverEnd`          | `() => void`                                                   | —                | Receive pointer leave.                                                       |
| `onSeek`              | `(t: number) => void`                                          | —                | Receive a click in empty space.                                              |
| `loadedRanges`        | `{ from: number; to: number }[] \| null`                       | —                | Available spans, shown below the ruler.                                      |
| `pendingRanges`       | `{ from: number; to: number }[]`                               | —                | Spans currently loading.                                                     |
| `zoom` / `panPct`     | `number`                                                       | `1` / `0`        | Controlled visible window.                                                   |
| `onViewportChange`    | `(v: ViewportState) => void`                                   | —                | Receive requested viewport changes.                                          |
| `onBlockClick`        | `(block: TrackBlock, trackId: string) => void`                 | —                | Receive a block click.                                                       |
| `onBlockHover`        | `(block: TrackBlock \| null, trackId: string \| null) => void` | —                | Receive block hover changes; null on leave.                                  |
| `framesLabel`         | `string`                                                       | `'FRAMES'`       | Caption below the thumbnails.                                                |
| `frameHeight`         | `number`                                                       | auto             | Thumbnail height in pixels; width uses 16:9. Automatic sizing fits 12 cells. |
| `trackRowHeight`      | `number`                                                       | `28`             | Track height in pixels.                                                      |
| `minZoom` / `maxZoom` | `number`                                                       | `1` / `Infinity` | Zoom limits.                                                                 |
| `className`           | `string`                                                       | —                | Root CSS classes.                                                            |
| `background`          | `"none" \| "subtle"`                                           | `"none"`         | Opt into a tinted panel surface.                                             |
