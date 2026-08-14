# EpisodeLineChart

A single time-series plot rendered into a 100×100 SVG viewBox. Each series
is two parallel arrays — `x` (time in seconds, sorted ascending) and `y`
(value at that time) — plus stroke styling. Adjacent samples are connected
with a straight line. The tooltip header reports the **cursor's exact
time** — an interpolated x position between samples, freely landing
anywhere along the chart. Per-channel y values are the **nearest** x
sample to that cursor (no interpolation), so each value the user reads is
always a real recorded number rather than a synthesized one.

Like [EpisodeTimeline](reference/components-episode-timeline.md) and
[EpisodeVideoStack](reference/components-episode-video-stack.md), the cursor is
hover-driven and shared across surfaces via three controlled props:
`time`, `onHover`/`onHoverEnd`, and `isScrubOwner`. Hovering any chart in
a group moves the cursor on every peer, and **every chart in the group
shows its own tooltip** at the shared `time` — the readout pattern is
"compare values at one moment across N synced charts." Only the owner
draws the bright accent hairline; peers drop to a muted 22%-ink hairline
so the active chart still stands out.

## Basic

A single chart driving its own cursor. `isScrubOwner` defaults to `true`,
so the bright accent hairline + tooltip appear whenever the pointer is over
the plot.

```tsx file="BasicSpec.tsx"

export const BasicSpec = () => {
  const [time, setTime] = useState<number | null>(null)
  return (
    <div className="h-[180px]">
      <EpisodeLineChart
        title="Left arm"
        caption="signal · joints"
        series={LARM_JOINTS_SERIES}
        duration={DEMO_DURATION}
        unitHint="joint angles · target vs realized"
        time={time}
        onHover={setTime}
        onHoverEnd={() => setTime(null)}
      />
    </div>
  )
}
```

## Multi-chart sync

The canonical Episode-view bottom row: four plots sharing one
`time` + `ownerId` state, with the right-arm chart in disabled / NO SIGNAL
mode. Hovering any chart updates the cursor on every other, and **every
non-disabled chart renders its own tooltip** at the same `t` so you can
compare per-channel readings across plots at a glance.

```tsx file="MultiChartSyncSpec.tsx"

// Mirrors the design's Episode-view bottom row: four time-series plots
// (joints, motor temperatures, right-arm = NO SIGNAL, tactile) sharing
// one hover cursor. Hovering any chart updates the cursor on every
// other chart; only the one under the pointer renders the tooltip.
export const MultiChartSyncSpec = () => {
  const [time, setTime] = useState<number | null>(null)
  const [ownerId, setOwnerId] = useState<string | null>(null)

  const bind = (id: string) => ({
    time,
    isScrubOwner: ownerId === id,
    onHover: (t: number) => { setTime(t); setOwnerId(id) },
    onHoverEnd: () => { setTime(null); setOwnerId(null) },
  })

  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-2 [grid-auto-rows:160px]">
      <EpisodeLineChart
        {...bind('joints')}
        title="Left arm"
        caption="signal · joints"
        series={LARM_JOINTS_SERIES}
        duration={DEMO_DURATION}
        unitHint="joint angles · target vs realized"
        yRange={[-1, 1]}
      />
      <EpisodeLineChart
        {...bind('temp')}
        title="Left arm motors"
        caption="signal · temperature"
        series={LARM_TEMP_SERIES}
        duration={DEMO_DURATION}
        unitHint="motor temperature · per channel"
        yRange={[-1, 1]}
      />
      <EpisodeLineChart
        {...bind('rarm')}
        title="Right arm"
        caption="signal · joints"
        series={[]}
        duration={DEMO_DURATION}
        disabled
      />
      <EpisodeLineChart
        {...bind('touch')}
        title="Touch"
        caption="signal · tactile"
        series={TOUCH_SERIES}
        duration={DEMO_DURATION}
        unitHint="tactile force magnitude · per finger"
        yRange={[-1, 1]}
      />
    </div>
  )
}
```

## Synced with EpisodeTimeline + EpisodeVideoStack

The full Episode-view layout — video stack + timeline + four time-series
plots, all driven by one shared cursor.

```tsx file="EpisodeViewSpec.tsx"

// Full Episode-view replica: a three-camera video stack + a zoomable
// timeline + four time-series plots, all driven by one shared cursor.
// Mirrors the layout used by `_DLEpisodeDetailItem` in the design
// (videos row · timeline row · time-series row).
const SAMPLE = '/preview-fixtures/episode-demo.mp4'

const VIDEOS: VideoSource[] = [
  { id: 'front', src: SAMPLE, title: 'front', subtitle: '/camera/front/image_compressed' },
  { id: 'wrist', src: SAMPLE, title: 'wrist', subtitle: '/camera/wrist/image_compressed' },
  { id: 'top',   src: SAMPLE, title: 'top',   subtitle: '/camera/top/image_compressed' },
]

export const EpisodeViewSpec = () => {
  const [hover, setHover] = useState<number | null>(null)
  const [ownerId, setOwnerId] = useState<string | null>(null)
  const [activeVideoId, setActiveVideoId] = useState<string>(VIDEOS[0].id)

  // Hover binding shared by every surface in the episode view —
  // any pointer-move flips the cursor and the active surface id, so
  // every other surface re-renders its scrub line at the same time
  // with a muted tone.
  const bind = (id: string) => ({
    time: hover,
    isScrubOwner: ownerId === id,
    onHover: (t: number) => { setHover(t); setOwnerId(id) },
    onHoverEnd: () => { setHover(null); setOwnerId(null) },
  })

  // EpisodeVideoStack doesn't take `isScrubOwner` — it routes hover
  // through activeId. We funnel the stack's hover events into the
  // same shared state, marking the stack as the owner whenever any
  // tile is the active one.
  const stackBind = {
    time: hover,
    onHover: (t: number) => { setHover(t); setOwnerId('stack') },
    onHoverEnd: () => { setHover(null); setOwnerId(null) },
  }

  const framesLabel = activeVideoId
    ? `KEYFRAMES · ${activeVideoId.toUpperCase()}`
    : 'FRAMES'

  return (
    <div className="flex flex-col gap-2">
      <EpisodeVideoStack
        {...stackBind}
        videos={VIDEOS}
        duration={DEMO_DURATION}
        activeId={activeVideoId}
        onActiveChange={setActiveVideoId}
      />
      <EpisodeTimeline
        duration={DEMO_DURATION}
        frames={DEMO_FRAMES}
        tracks={DEMO_TRACKS}
        framesLabel={framesLabel}
        time={hover}
        onHover={(t) => { setHover(t); setOwnerId('timeline') }}
        onHoverEnd={() => { setHover(null); setOwnerId(null) }}
      />
      <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-2 [grid-auto-rows:160px]">
        <EpisodeLineChart
          {...bind('joints')}
          title="Left arm"
          caption="signal · joints"
          series={LARM_JOINTS_SERIES}
          duration={DEMO_DURATION}
          unitHint="joint angles · target vs realized"
          yRange={[-1, 1]}
        />
        <EpisodeLineChart
          {...bind('temp')}
          title="Left arm motors"
          caption="signal · temperature"
          series={LARM_TEMP_SERIES}
          duration={DEMO_DURATION}
          unitHint="motor temperature · per channel"
          yRange={[-1, 1]}
        />
        <EpisodeLineChart
          {...bind('rarm')}
          title="Right arm"
          caption="signal · joints"
          series={[]}
          duration={DEMO_DURATION}
          disabled
        />
        <EpisodeLineChart
          {...bind('touch')}
          title="Touch"
          caption="signal · tactile"
          series={TOUCH_SERIES}
          duration={DEMO_DURATION}
          unitHint="tactile force magnitude · per finger"
          yRange={[-1, 1]}
        />
      </div>
    </div>
  )
}
```

### Cursor sync protocol

All three surfaces — `EpisodeLineChart`, `EpisodeTimeline`, `EpisodeVideoStack` —
accept the same `time` + `onHover` + `onHoverEnd` triple, so a single
`useState<number | null>` drives them all. `isScrubOwner` is the
EpisodeLineChart-specific knob that decides which chart in a group renders the
bright hairline + tooltip; peer charts render a muted hairline at the same
`time` with no tooltip:

```tsx
const [hover, setHover] = useState<number | null>(null)
const [ownerId, setOwnerId] = useState<string | null>(null)

const bind = (id: string) => ({
  time: hover,
  isScrubOwner: ownerId === id,
  onHover: (t: number) => { setHover(t); setOwnerId(id) },
  onHoverEnd: () => { setHover(null); setOwnerId(null) },
})

<EpisodeLineChart {...bind('joints')} series={joints} duration={d} ... />
<EpisodeLineChart {...bind('temp')}   series={temp}   duration={d} ... />
```

Every chart with non-null `time` renders its tooltip, regardless of
`isScrubOwner`. Owner-only effects: the bright accent hairline, and the
tooltip's vertical anchor following the pointer Y (peers anchor at
chart-centre).

`EpisodeTimeline` and `EpisodeVideoStack` plug into the same `hover` state
without `isScrubOwner` — the timeline auto-derives its tone from its own
internal hover, and the stack uses `activeId` for the focused tile. The
`bind('timeline')` flow simply marks the timeline as the cursor owner so
every EpisodeLineChart in the group drops to the muted hairline while the user
scrubs on the timeline.

## Series shape

Each `EpisodeLineChartSeries` carries two parallel arrays plus stroke styling:

```ts
interface EpisodeLineChartSeries {
  id: string
  label?: string                            // shown in the tooltip readout row
  data: { x: number[]; y: number[] }        // x = seconds, sorted ascending; y = value
  color: string                             // any CSS color — EPISODE_LINE_CHART_PALETTE.* recommended
  width?: number                            // viewBox units; default 1.4
  dash?: string                             // e.g. '3 2.4'
  opacity?: number                          // 0..1
  linecap?: 'butt' | 'round' | 'square'
  readout?: boolean                         // include in tooltip; default true
  ghost?: boolean                           // target / reference trace — dimmed row, "tgt" label suffix
  formatValue?: (v: number) => string       // tooltip cell text; default v.toFixed(2)
}
```

The sample density is the caller's choice — the chart draws a polyline
through every point, so a 60-sample series is rougher than a 600-sample
one but both work. Non-finite y values (`NaN` / `Infinity`) break the line:
the polyline stops at the last good sample and restarts at the next one,
so a gap in the recording reads as a gap on screen.

The tooltip looks up the nearest x sample to the cursor and displays
that sample's actual y — no interpolation. `x` must be sorted ascending
for the lookup to work.

## Palette

A six-hue oklch palette is exported as `EPISODE_LINE_CHART_PALETTE`. The hues are
hardcoded — the library doesn't ship CSS tokens for them, and the values
don't theme-flip (chart series colours stay legible against both light and
dark backgrounds at these lightness levels).

| Token | Value |
| --- | --- |
| `EPISODE_LINE_CHART_PALETTE.blue` | `oklch(60% 0.13 235)` |
| `EPISODE_LINE_CHART_PALETTE.orange` | `oklch(63% 0.13 50)` |
| `EPISODE_LINE_CHART_PALETTE.green` | `oklch(58% 0.12 150)` |
| `EPISODE_LINE_CHART_PALETTE.purple` | `oklch(58% 0.13 295)` |
| `EPISODE_LINE_CHART_PALETTE.red` | `oklch(58% 0.17 25)` |
| `EPISODE_LINE_CHART_PALETTE.teal` | `oklch(60% 0.10 200)` |

For "ghost" / target traces, pass `color: 'currentColor'` and `opacity: 0.5`
so the dashed line inherits the chart's ink-tinted foreground and matches
in both themes.

## Tooltip behaviour

The tooltip flips against the chart's own midline:

- **Cursor in the left half** → tooltip on the **right** of the hairline.
- **Cursor in the right half** → tooltip on the **left** of the hairline.

Vertically, the owner chart's tooltip follows the pointer Y and flips
above the cursor when it crosses 55% down the chart. Peer charts have no
live pointer Y, so their tooltip anchors at the chart's vertical centre.

The tooltip floats above any clipping ancestor and follows the chart
on scroll, so a user hovering a chart while scrolling the page sees
the tooltip glide with the hairline. The tooltip is **not** clamped
to the viewport — when scrolling pushes part of it off-screen, that's
accepted rather than letting the tooltip jump unpredictably to stay
visible.

## Disabled state

`disabled` renders the chart with a hatched canvas and a centred "NO
SIGNAL" label. No pointer events, no tooltip. The chart still occupies
its grid cell so the surrounding layout doesn't reflow when a sensor
drops out, and the hatch tone follows the chart's text color in both
themes.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `series` | `EpisodeLineChartSeries[]` | — | Channel definitions, drawn in array order. |
| `duration` | `number` | — | Total time span in seconds. Must be `> 0`. |
| `title` | `string` | — | Top-left title (UI weight). |
| `caption` | `string` | — | Uppercase mono eyebrow above the title. |
| `yRange` | `[number, number]` | auto-fit | Y-axis domain. Computed from sampled series + 5% padding when omitted. |
| `time` | `number \| null` | `null` | Shared cursor time in seconds. `null` hides the cursor. |
| `onHover` | `(t: number) => void` | — | Fires continuously on hover with the time at the cursor. |
| `onHoverEnd` | `() => void` | — | Fires when the cursor leaves. |
| `isScrubOwner` | `boolean` | `true` | When `true`, the chart draws the bright accent hairline and its tooltip follows the pointer Y. When `false`, the hairline is a muted 22%-ink stroke and the tooltip anchors at chart-centre. Both states still render their tooltip whenever `time` is non-null. |
| `unitHint` | `string` | — | Sub-label under the tooltip's time header — explains units. |
| `showMidline` | `boolean` | `true` | Render the y-axis midline reference. |
| `disabled` | `boolean` | `false` | Render hatched canvas + "NO SIGNAL"; no interaction. |
| `className` | `string` | — | Extra classes on the wrapper. |

### EpisodeLineChartSeries

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `id` | `string` | — | Stable identifier; React key + tooltip readout row key. |
| `label` | `string` | — | Legend label shown in the tooltip readout row. Series with no `label` are drawn on the chart but omitted from the tooltip. |
| `data` | `{ x: number[]; y: number[] }` | — | Sample points. `x` is time in seconds, sorted ascending; `y` is the value at each x. Arrays must be the same length. Adjacent samples are connected with a straight line; `NaN` y values break the line. |
| `color` | `string` | — | Stroke color. Any CSS color string; prefer `EPISODE_LINE_CHART_PALETTE.*` for parity across charts. |
| `width` | `number` | `1.4` | Stroke width in viewBox units (the viewBox is 100×100, so 1.4 ≈ 1.4px when the chart fills 100px wide). |
| `dash` | `string` | — | SVG `stroke-dasharray` pattern, e.g. `'3 2.4'`. Solid when omitted. |
| `opacity` | `number` | `1` | Stroke opacity 0..1. |
| `linecap` | `'butt' \| 'round' \| 'square'` | `'butt'` | SVG `stroke-linecap`. |
| `readout` | `boolean` | `true` | Include this series in the tooltip readout. Set `false` for decorative / per-axis traces that would crowd the legend (e.g. y / z axes when only fx is the headline reading). |
| `ghost` | `boolean` | `false` | Marks the series as a target / reference trace — dims the readout row, suffixes the label with `"tgt"`, and renders the swatch at width 1 instead of 1.6. |
| `formatValue` | `(v: number) => string` | `v => v.toFixed(2)` | Tooltip cell text. Use this to map a normalized signal back to physical units (e.g. `v => (v * 90).toFixed(1) + '°'`). |
