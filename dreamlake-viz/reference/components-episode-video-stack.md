# EpisodeVideoStack

A grid of N camera-view tiles that share a cursor time with each other and
(optionally) with a sibling [EpisodeTimeline](reference/components-episode-timeline.md).
Hovering any tile updates one shared `time` value; every other tile re-renders
its scrub line at that same time, with a **muted** tone so the actively-hovered
tile stays visually unambiguous.

The caller wires two pieces of state to make this work: a shared **`hover`**
time, and an **`activeId`** marking which tile carries the accent ring. The
component exposes both as controlled props — see
[Combined with EpisodeTimeline](#combined-with-episodetimeline) for the
canonical pattern.

## Tile anatomy

```
┌──────────────────────────────────────────┐
│ REC · 00:10.602              ● LIVE      │
│                                          │
│                  <video>                 │
│                                          │
│ FRONT                          1280×720  │
│ /camera/front/image_compressed           │
└──────────────────────────────────────────┘
```

Four overlays sit on top of the `<video>` element (all are optional via
`show*` props). The scrub line, when present, lives above everything at
`z-index: 4`.

The **bottom-right resolution** is auto-detected from
`<video>.videoWidth × videoHeight` once the metadata loads — there is no
caller-provided field, so the display is always real or absent.

## Standalone stack

Hover any tile to see the per-tile active state (full accent ring + bright
1.5px scrub line); the other two tiles drop to a muted 1px ink scrub line at
the same time.

> All three tiles render the same `episode-demo.mp4` fixture shipped under
> `docs/public/preview-fixtures/` (21.205s, 1280×720). Each `<video>`
> element seeks independently as you hover. Real apps pass distinct camera
> URLs via `VideoSource.src`. Omit `src` to fall back to the built-in
> placeholder grid (a neutral lattice + crosshair + two demo detection
> boxes in the tile's accent color).

## Playback

The stack has no play state of its own — playback comes from the shared
**`TimelineClock`** (rAF-driven, with `play` / `pause` / `seek` /
`setRate` / `setLoop`), and there is exactly **one playhead**: the clock's
time.

- `time` comes from the clock (`useClockValue`), so every scrub line and
  a paired timeline follow the same playhead.
- **Hover seeks the clock** (`onHover={seek}`) — scrubbing works the same
  paused or mid-playback, and play always resumes from wherever the
  pointer left the playhead. No separate hover state to fall out of sync.
- Provide the clock via `` and the tiles follow its
  play/pause events with the **native** `<video>` controls — smooth
  sequential decode instead of seek-per-update — re-syncing only on real
  jumps (a seek, a loop wrap, &gt;0.3 s drift).
- **A buffering tile holds the clock.** While any playing video is
  stalled for data (slow network, a fresh play, a mid-play seek), the
  playhead *waits* — like a normal video player — instead of running
  ahead and skipping content when data arrives. In a multi-camera stack
  the clock waits for the slowest stream, so every tile stays in sync.
  The play state doesn't change while held (no pause/play flicker).

```tsx
const { clock, state, play, pause, seek } = useTimeline(duration)
const time = useClockValue(30, clock) // the playhead, sampled at 30fps

<ClockProvider clock={clock}>
  <EpisodeVideoStack
    videos={videos}
    duration={duration}
    time={time}
    onHover={seek}
  />
</ClockProvider>
<button onClick={state.playing ? pause : play}>▶ / ⏸</button>
```

`DatasetPreview` wires this same clock behind every schema panel, so
schema-driven video stacks scrub and play the same way. The overlay
example below autoplays with this pattern; the
[combined example](#combined-with-episodetimeline) adds a play button and
a timeline driven by the same playhead.

## Hand keypoint overlays

Each `VideoSource` can carry [annotation overlays](reference/components-media-overlay.md)
— bounding boxes, keypoint skeletons, and subtitle-style caption tracks;
the tile keeps them glued to the presented frame during playback and
scrubbing. Here, real 21-joint hand detections plus subtask captions, each
converted with one adapter call:

See [Media overlays](reference/components-media-overlay.md) for the data model —
coordinate spaces, by-frame / by-time lookup, and styling.

## Combined with EpisodeTimeline

Two pieces of caller state wire the pair:

- **`hover`** — the shared cursor time. Hovering anywhere updates it; either
  component leaving clears it.
- **`activeId`** — which video tile is currently the focused camera. Set on
  hover-enter; **deliberately not cleared on leave**, so the last-hovered
  tile keeps its accent ring while the pointer moves onto the timeline below.

### Active vs muted coordination

`EpisodeTimeline` and `EpisodeVideoStack` use different mechanisms to decide
which is the "actively scrubbed" surface — they coordinate via shared state,
not via a `tone` prop or `activeSource` flag:

| Component | How it picks active vs muted |
| --- | --- |
| `EpisodeTimeline` | **Auto-derived** from its own internal hover state. When the pointer is on the timeline, its own cursor lights up; when the pointer is elsewhere, an external `time` paints in the muted tone. |
| `EpisodeVideoStack` | **Caller-controlled** via `activeId`. The tile with `activeId === video.id` draws the 2px accent ring + 1.5px bright scrub line; peer tiles draw a 1px ink hairline at the same time. The component never auto-clears `activeId`. |

So when the pointer is over a video tile:
- The actively-hovered tile draws its accent ring + bright scrub line.
- Other tiles in the same stack: 1px 22% ink scrub line at the same time.
- The sibling `EpisodeTimeline` below: 1px 22% ink cursor at the same time
  (because its own internal hover state is empty).

When the pointer moves to the timeline, the roles swap — except the focused
video tile (`activeId`) keeps its **ring** (because `onActiveChange` was set
on hover-enter and the caller never cleared `activeId`), while its scrub line
drops to the muted treatment because the timeline is now the one being
scrubbed.

### Sticky active is a caller pattern, not a component default

The component itself doesn't decide whether to clear `activeId` on leave —
that's the caller's choice:

| Caller code | Behaviour |
| --- | --- |
| `activeId={id}` + `onActiveChange={setId}`, never call `setId(null)` | **Sticky** (recommended). Last-hovered tile keeps its ring forever. |
| Same as above, **plus** `onHoverEnd={() => setId(null)}` | Clear on leave. All tiles drop to muted when the pointer leaves the stack. |
| No `activeId` / `onActiveChange` (uncontrolled) | Sticky by default. First tile is active only if `defaultActiveId` is passed. |

## Notes on the design

- **Native `<video>` only** — supports MP4 / WebM / Ogg via the browser's
  built-in loader. HLS / DASH would require an extra peer-dep and is out of
  scope; pair this with an HLS-aware playlist engine externally if needed.
- **Truthful metadata** — the bottom-right resolution comes straight from
  `<video>.videoWidth × videoHeight` after metadata loads. There is no
  caller-provided fallback, so the display is always real or absent.
- **Seek tolerance** — the component only writes `video.currentTime` when
  the desired time differs by more than 50 ms. Avoids re-seeking on every
  sub-frame hover update.
- **Hover boundary** — `onPointerLeave` is attached to the outer grid, so
  moving between tiles via the 6 px gap doesn't fire `onHoverEnd` (only
  leaving the entire stack does).
- **No `onSeek`** — clicks on a tile are no-ops by design. Tiles are a
  preview surface, not a commit target; listen for clicks on the paired
  `EpisodeTimeline` instead.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `videos` | `VideoSource[]` | — | One entry per tile, rendered left-to-right. |
| `duration` | `number` | — | Total duration in seconds. MUST match the sibling timeline. |
| `time` | `number \| null` | `null` | Shared cursor time. Drives `<video>.currentTime` and scrub-line X. `null` hides the cursor. Feed it from a `TimelineClock` for [playback](#playback). |
| `onHover` | `(t: number) => void` | — | Fires on every hover move with the time at the cursor. |
| `onHoverEnd` | `() => void` | — | Fires when the cursor leaves the entire stack (the gap between tiles does not count). |
| `activeId` | `string \| null` | — | Controlled active tile id. When provided, the component does NOT manage internal active state. |
| `defaultActiveId` | `string \| null` | `null` | Uncontrolled initial active tile id. Ignored when `activeId` is provided. |
| `onActiveChange` | `(id: string) => void` | — | Fires on hover-enter a new tile, with that tile's id. Does NOT fire on leave. |
| `columns` | `number` | `3` | Grid column count. |
| `gap` | `number` | `6` | Pixel gap between adjacent tiles. |
| `showRecTimestamp` | `boolean` | `true` | Top-left REC + cursor-time stamp. |
| `showLive` | `boolean` | `false` | Top-right red pulsing dot + "LIVE" label. |
| `showLabel` | `boolean` | `true` | Bottom-left title + subtitle. |
| `showResolution` | `boolean` | `true` | Bottom-right auto-detected resolution. Hidden until metadata loads or when `src` is omitted. |
| `showOverlays` | `boolean` | `true` | Master switch for all `VideoSource.overlays` layers. |
| `overlaySync` | `'media' \| 'cursor'` | `'media'` | What overlay lookup follows: the presented video frame (rVFC) or the `time` prop. See [Media overlays](reference/components-media-overlay.md#video-sync-modes). |
| `className` | `string` | — | Extra classes on the root grid. |

### VideoSource

| Field | Type | Description |
| --- | --- | --- |
| `id` | `string` | Stable identifier; React key + the value `activeId` matches against. |
| `src` | `string?` | Video URL. Native `<video>` only — MP4 / WebM / Ogg. Omit to render the built-in placeholder grid. |
| `title` | `string?` | Bottom-left primary label; rendered uppercase. Typically the camera name. |
| `subtitle` | `string?` | Bottom-left mono sub-label. Transport-agnostic — ROS topic, HTTP path, file name, anything. |
| `poster` | `string?` | `<video poster>`. Shown before the first frame loads. |
| `overlays` | `MediaOverlay[]?` | Annotation layers (boxes / skeletons) drawn over this video, back-to-front. See [Media overlays](reference/components-media-overlay.md). |

> **Why no `resolution` field?** It used to be a caller-provided string,
> which made it easy for the displayed value to drift from the actual
> encoded stream. Resolution is now auto-detected from
> `<video>.videoWidth × videoHeight` after metadata loads.
