<!-- generated from https://viz.dreamlake.ai/components/episode-line-chart.md at unknown; do not edit -->

# Line charts

`EpisodeLineChart` plots recorded signals against seconds. Hover to compare
sample values; use `onSeek` to send a clicked time to playback.

## Compact embeds

Charts and timelines use transparent surfaces by default. Set
`background="subtle"` to opt into a panel tint; semantic ranges and uncertainty
bands keep their own colors. `size="compact"` supplies a 150px **total** chart
height and fewer y-axis labels. Use `height={130}` through `height={170}` to fit
an embedded 2×2 chart grid, or `height="100%"` inside explicitly sized grid rows
with `min-height: 0`. The normal size continues to fill its parent.

The example uses a three-second recording, fractional-second labels and short
major/minor tick marks. All four charts share `time`, `onHover`, zoom and pan;
only the hovered chart shows a readout. No new cursor callback is needed.
Use `onHoverEnd` to clear the preview. `isScrubOwner={false}` explicitly
suppresses a readout. The readout follows both pointer axes in a body portal,
stays 12px below and to the right of the pointer and can extend beyond the chart.
Only browser edges clamp it into view. It passes pointer events through; Escape dismisses it. Keyboard zoom/pan shows the focused
chart's readout when `time` is set. Recorded sample values are never interpolated.

Both axes have short 6px major and 3px minor ticks. Y-axis marks extend into
the gutter without moving the plot or adding minor grid lines. Their numeric
values follow the [nice-number selection guide](https://viz.dreamlake.ai/components/numeric-axis#nice-numbers-and-tick-selection);
explicit `yRange` bounds and custom formatters stay authoritative. Compact axes
normally target three majors; if a nonconstant range leaves fewer than two,
they retry a target of five. For `[13, 87]`, majors are 20, 40, 60 and 80 without
expanding the exact domain. Minor ticks remain short and unlabelled.

```tsx file="CompactSpec.tsx"

const series = [
  {
    id: "position",
    label: "Recorded position",
    color: "#3388aa",
    data: { x: [0, 0.3, 0.8, 1.4, 2.1, 2.6, 3], y: [0, 2, 1, 4, 3, 5, 4] },
  },
];
const markers = [
  { id: "event", time: 1.4, label: "Correction", color: "#b05a3c" },
];
const ranges = [
  { id: "range", start: 1.4, end: 2.1, label: "Response", color: "#418a61" },
];

/** Four 150px charts share exact times and a viewport, but only the hovered
 * chart shows a floating readout. No owner/cursor-position wiring is needed. */
export function CompactSpec() {
  const [time, setTime] = useState<number | null>(null);
  const [seek, setSeek] = useState<number | null>(null);
  const [viewport, setViewport] = useState({ zoom: 1, panPct: 0 });
  return (
    <div data-testid="compact-chart-demo">
      <div data-testid="compact-chart-scroll" style={{ overflow: "auto" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(0, 0.9fr) minmax(0, 1.1fr)",
            gap: 12,
          }}
        >
          <video
            src="/preview-fixtures/episode-demo.mp4"
            controls
            muted
            playsInline
            aria-label="Example recording"
            style={{
              width: "100%",
              height: "100%",
              minHeight: 0,
              objectFit: "contain",
            }}
          />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: 8,
            }}
          >
            {["Position", "Velocity", "Force", "Correction"].map((title) => (
              <EpisodeLineChart
                key={title}
                title={title}
                series={series}
                duration={3}
                size="compact"
                height={150}
                markers={markers}
                ranges={ranges}
                time={time}
                onHover={setTime}
                onHoverEnd={() => setTime(null)}
                onSeek={setSeek}
                {...viewport}
                onViewportChange={setViewport}
              />
            ))}
          </div>
        </div>
      </div>
      <output data-testid="compact-chart-seek">
        {seek == null ? "Click a chart to seek" : `Seek: ${seek}`}
      </output>
    </div>
  );
}
```

## Basic

Hover the signals below. Each readout uses the nearest recorded sample,
including when the cursor falls between measurements.

```tsx file="BasicSpec.tsx"

export const BasicSpec = () => {
  const [time, setTime] = useState<number | null>(null)
  return (
    <div className="h-[180px]">
      <EpisodeLineChart
        title="Left arm"
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

For the data props, supply matching `x` and `y` arrays. This fragment omits
the container height and controlled cursor; expand the live example above for
the complete wiring:

```tsx

<EpisodeLineChart
  duration={3}
  unit="°C"
  series={[
    {
      id: "temperature",
      label: "Temperature",
      color: "#3388aa",
      data: { x: [0, 1, 2, 3], y: [20, 22, 21, 23] },
    },
  ]}
/>;
```

The y-axis fits the data automatically. Set `yRange` to compare several charts
on a fixed scale; [Numeric axes](https://viz.dreamlake.ai/components/numeric-axis) explains tick labels.

## Line width and active emphasis

Primary traces default to **2 CSS pixels**, including compact charts. Set
`lineWidth` once for the chart; a finite, non-negative `series.width` overrides
it for that series. Values such as `1.5`, `2`, `2.5` and `3` are supported.
Start at 2px and check both themes at the final embed size. Distinguish a
reference with `dash`, `opacity` and a label instead of making it a hairline.

```tsx file="LineWidthSpec.tsx"

const signals: EpisodeLineChartSeries[] = [
  {
    id: "recorded",
    label: "Recorded position",
    color: "#3388aa",
    data: { x: [0, 0.3, 0.8, 1.4, 2.1, 2.6, 3], y: [0, 2, 1, 4, 3, 5, 4] },
  },
  {
    id: "reference",
    label: "Reference position",
    color: "currentColor",
    ghost: true,
    dash: "4 3",
    opacity: 0.55,
    data: { x: [0, 0.3, 0.8, 1.4, 2.1, 2.6, 3], y: [1, 1, 2, 3, 4, 4, 5] },
  },
];

export function LineWidthSpec() {
  const [lineWidth, setLineWidth] = useState(2);
  const [activeWidth, setActiveWidth] = useState("auto");
  const [override, setOverride] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [time, setTime] = useState<number | null>(null);
  const series = useMemo(
    () =>
      signals.map((signal, index) => ({
        ...signal,
        width: override && index === 0 ? 3 : undefined,
      })),
    [override],
  );
  return (
    <div data-testid="episode-line-width-demo" className="min-w-0 space-y-3">
      <div className="flex flex-wrap items-center gap-4 text-xs">
        <label className="flex items-center gap-2">
          Line width
          <select
            aria-label="Line width"
            value={lineWidth}
            onChange={(event) => setLineWidth(Number(event.target.value))}
          >
            {[1.5, 2, 2.5, 3].map((width) => (
              <option key={width} value={width}>
                {width}px
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          Active width
          <select
            aria-label="Active width"
            value={activeWidth}
            onChange={(event) => setActiveWidth(event.target.value)}
          >
            <option value="auto">Auto · 1.65×</option>
            <option value="3">3px floor</option>
            <option value="4">4px floor</option>
          </select>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={override}
            onChange={(event) => setOverride(event.target.checked)}
          />
          Recorded series: 3px override
        </label>
        <button
          type="button"
          aria-pressed={activeId === "recorded"}
          onClick={() =>
            setActiveId(activeId === "recorded" ? null : "recorded")
          }
          className="rounded border border-black/15 px-2 py-1 dark:border-white/15"
        >
          Highlight recorded series
        </button>
      </div>
      <EpisodeLineChart
        title="Line width · three-second recording"
        series={series}
        duration={3}
        size="compact"
        height={150}
        lineWidth={lineWidth}
        activeLineWidth={
          activeWidth === "auto" ? undefined : Number(activeWidth)
        }
        highlightOnHover
        activeSeriesId={activeId}
        onActiveSeriesChange={setActiveId}
        time={time}
        onHover={setTime}
        onHoverEnd={() => setTime(null)}
      />
      <p className="text-xs opacity-65">
        Widths stay in CSS pixels at every chart size and zoom. The dashed
        reference uses the same base width; dash and opacity distinguish it.
        Hover a trace or use the highlight button to compare active emphasis.
      </p>
    </div>
  );
}
```

```tsx
<EpisodeLineChart
  series={[
    { ...recorded, width: 3 }, // Overrides lineWidth for this trace.
    { ...reference, dash: "4 3", opacity: 0.55 }, // Inherits 2px.
  ]}
  duration={3}
  size="compact"
  height={150}
  lineWidth={2}
  activeLineWidth={4}
  highlightOnHover
/>
```

Identification through `highlightOnHover` or `activeSeriesId` normally raises
that series to 1.65 times its resolved base width (2px becomes 3.3px).
`activeLineWidth` replaces that automatic width with a CSS-pixel floor:
`max(baseWidth, activeLineWidth)`. It can never make a thick series thinner.
The example's 3px override becomes 4px when active, while `activeLineWidth={2}`
would leave it at 3px. This prop controls emphasis; it does not enable hover
identification by itself.

These are non-scaling SVG strokes measured in **CSS pixels**, not SVG viewBox
units or device pixels. Zoom and chart resizing do not shrink them. A zero base
width hides the stroke and stays hidden when active; data, bands, readouts and
interaction remain available. Negative or non-finite overrides fall back to the
chart width; an invalid chart width falls back to 2px, and an invalid active
width uses the automatic multiplier. Width changes never alter sample values,
axis domains or seek times.

## Uncertainty bands

Turn the bands off to isolate the center traces. Between 24 and 28 seconds,
missing bounds leave a gap in the band without interrupting the center line.

```tsx file="UncertaintyBandSpec.tsx"

// Synthetic, deterministic samples; bounds are observations, not a calculated CI.
const x = Array.from({ length: 121 }, (_, i) => i / 2);
const y = x.map((t) => 22 + 2 * Math.sin(t / 7) + t / 30);
const low = x.map((t, i) =>
  t >= 24 && t <= 28 ? NaN : y[i] - 1 - 0.5 * Math.cos(t / 5),
);
const high = x.map((t, i) =>
  t >= 24 && t <= 28 ? NaN : y[i] + 1.4 + 0.6 * Math.sin(t / 6) ** 2,
);
const signal: EpisodeLineChartSeries = {
  id: "temperature",
  label: "Temperature",
  color: EPISODE_LINE_CHART_PALETTE.blue,
  data: { x, y, low, high },
  formatValue: (v) => `${v.toFixed(2)} °C`,
};
const peer: EpisodeLineChartSeries = {
  id: "reference",
  label: "Reference sensor",
  color: EPISODE_LINE_CHART_PALETTE.green,
  data: { x, y: y.map((v, i) => v - 0.8 + 0.2 * Math.cos(x[i] / 3)) },
  formatValue: (v) => `${v.toFixed(2)} °C`,
};

export function UncertaintyBandSpec() {
  const [showBand, setShowBand] = useState(true);
  const [time, setTime] = useState<number | null>(null);
  const [owner, setOwner] = useState("signal");
  const [playhead, setPlayhead] = useState<number | null>(null);
  const bind = (id: string) => ({
    time,
    isScrubOwner: owner === id,
    onHover: (t: number) => {
      setOwner(id);
      setTime(t);
    },
    onHoverEnd: () => setTime(null),
    onSeek: setPlayhead,
  });
  return (
    <div data-testid="uncertainty-band-demo" className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="checkbox"
            checked={showBand}
            onChange={(e) => setShowBand(e.target.checked)}
          />
          Show recorded range
        </label>
        <output aria-live="polite">
          {playhead === null
            ? "Click a chart to set playhead"
            : `Playhead: ${playhead.toFixed(2)} s`}
        </output>
      </div>
      <div className="h-[210px]">
        <EpisodeLineChart
          title="Temperature · recorded range"
          caption="Synthetic · 121 samples · 60 seconds"
          series={[showBand ? signal : { ...signal, data: { x, y } }]}
          duration={60}
          yRange={[17, 28]}
          unitHint="Center value · shaded lower/upper observations"
          {...bind("signal")}
        />
      </div>
      <div className="h-[160px]">
        <EpisodeLineChart
          title="Reference sensor · shared cursor"
          series={[peer]}
          duration={60}
          yRange={[17, 28]}
          {...bind("reference")}
        />
      </div>
      <p className="text-xs opacity-70">
        Blue fill: supplied lower/upper range. Bounds unavailable at 24–28 s;
        center values remain recorded. No confidence level is inferred.
      </p>
    </div>
  );
}
```

Supply `low` and `high` at the same timestamps as `y`:

```tsx
const series = [{
  id: 'temperature', label: 'Temperature', color: '#3388aa',
  data: {
    x: [0, 1, 2, 3], y: [20, 22, 21, 23],
    low: [18, 19, 20, 21], high: [22, 25, 23, 26],
  },
}]
<EpisodeLineChart series={series} duration={3} unit="°C" />
```

Calculate intervals before passing them in. Valid bounds expand the automatic
y-domain; `yRange` clips the line and band together. Missing, non-finite, or
inverted bounds leave gaps. Invalid center samples also break the band.
`fillColor` and `fillOpacity` override the default series-colored, 16% fill;
tooltips report center values.

## Events and time ranges

The force trace below places contact and release markers alongside a shaded
grasp interval. The timeline uses the same intervals to show task phases.

```tsx file="AnnotationsSpec.tsx"

const duration = 60;
const x = Array.from({ length: 121 }, (_, i) => i / 2);
const series = [
  {
    id: "force",
    label: "Force",
    color: EPISODE_LINE_CHART_PALETTE.blue,
    data: {
      x,
      y: x.map((t) => 4 + 2 * Math.sin(t / 8) + (t >= 18 && t <= 34 ? 3 : 0)),
    },
    formatValue: (v: number) => `${v.toFixed(2)} N`,
  },
];
const markers = [
  { id: "start", time: 0, label: "Start" },
  { id: "contact", time: 18, label: "Contact" },
  { id: "release", time: 34, label: "Release" },
];
const ranges = [
  { id: "grasp", start: 18, end: 34, label: "Grasp" },
  { id: "settle", start: 46, end: 65, label: "Settle (clipped)" },
];

export function AnnotationsSpec() {
  const [shown, setShown] = useState(true);
  const [time, setTime] = useState<number | null>(null);
  const [owner, setOwner] = useState("chart");
  const [seek, setSeek] = useState<number | null>(null);
  const hover = (id: string) => (t: number) => {
    setOwner(id);
    setTime(t);
  };
  return (
    <div data-testid="annotations-demo" className="flex flex-col gap-4">
      <div className="flex flex-wrap justify-between gap-3 text-xs">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={shown}
            onChange={(e) => setShown(e.target.checked)}
          />
          Show events and ranges
        </label>
        <output aria-live="polite">
          {seek === null
            ? "Click chart or timeline to seek"
            : `Playhead: ${seek.toFixed(2)} s`}
        </output>
      </div>
      <div className="h-[260px]">
        <EpisodeLineChart
          title="Gripper force"
          caption="Synthetic · 121 samples · 60 seconds"
          series={series}
          duration={duration}
          yRange={[0, 10]}
          markers={shown ? markers : []}
          ranges={shown ? ranges : []}
          time={time}
          onHover={hover("chart")}
          onHoverEnd={() => setTime(null)}
          onSeek={setSeek}
          isScrubOwner={owner === "chart"}
        />
      </div>
      <div
        style={{
          marginLeft: TIME_AXIS_INSET_L,
          marginRight: TIME_AXIS_INSET_R,
        }}
      >
        <EpisodeTimeline
          duration={duration}
          frames={[]}
          tracks={[{ id: "phases", name: "Episode phases", blocks: ranges }]}
          time={time}
          onHover={hover("timeline")}
          onHoverEnd={() => setTime(null)}
          onSeek={setSeek}
        />
      </div>
      <p className="text-xs opacity-70">
        The same Grasp interval (18–34 s) aligns in the chart and timeline.
        Start at 0 s remains visible. Settle extends to 65 s in data and is
        clipped at 60 s. Annotation overlays preserve hover and seek.
      </p>
    </div>
  );
}
```

```tsx
const markers = [{ id: 'contact', time: 18, label: 'Contact' }]
const ranges = [{ id: 'grasp', start: 18, end: 34, label: 'Grasp' }]
<EpisodeLineChart series={series} duration={60} markers={markers} ranges={ranges} />
```

Use episode seconds, stable IDs, and labels. Invalid markers and empty,
inverted, or non-finite ranges are omitted. Ranges clip to the visible window.
Crowded labels may disappear visually but remain in the accessible list.
Annotations do not capture clicks or select intervals.

## Shared zoom and pan

Zoom into an event below: both charts and the timeline keep the same window.
Video continues to use episode time.

```tsx file="SharedViewportSpec.tsx"

const duration = 20
const x = Array.from({ length: 81 }, (_, index) => index / 4)
const force = [{ id: 'force', label: 'Force', color: EPISODE_LINE_CHART_PALETTE.blue,
  data: { x, y: x.map(t => 4 + 2 * Math.sin(t / 2)) }, formatValue: (value: number) => `${value.toFixed(2)} N` }]
const position = [{ id: 'position', label: 'Position', color: EPISODE_LINE_CHART_PALETTE.green,
  data: { x, y: x.map(t => 0.5 + 0.25 * Math.cos(t / 3)) }, formatValue: (value: number) => `${value.toFixed(2)} m` }]
const markers = [{ id: 'contact', time: 6, label: 'Contact' }, { id: 'release', time: 14, label: 'Release' }]
const ranges = [{ id: 'grasp', start: 7, end: 12, label: 'Grasp' }]
const videos = [{ id: 'camera', src: '/preview-fixtures/episode-demo.mp4', title: 'Recorded camera' }]

/** One unchanged fixture for baseline and integrated viewport screenshots. */
export function SharedViewportSpec() {
  const [viewport, setViewport] = useState<ViewportState>({ zoom: 2, panPct: 0.25 })
  const [hover, setHover] = useState<number | null>(null)
  const [playhead, setPlayhead] = useState<number | null>(null)
  const [owner, setOwner] = useState('')
  const [disabled, setDisabled] = useState(false)
  const start = viewport.panPct * duration
  const end = start + duration / viewport.zoom
  const bind = (id: string) => ({
    time: hover ?? playhead,
    onHover: (time: number) => { setOwner(id); setHover(time) },
    onHoverEnd: () => setHover(null),
    onSeek: setPlayhead,
    isScrubOwner: owner === id,
  })
  const shared = { ...viewport, onViewportChange: setViewport, maxZoom: 1000 }
  return (
    <div data-testid="shared-viewport-demo" className="flex flex-col gap-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="w-[180px] shrink-0" data-testid="viewport-video">
          <EpisodeVideoStack videos={videos} columns={1} duration={duration} showResolution={false} {...bind('video')} time={hover ?? playhead ?? 0} />
        </div>
        <div className="flex min-w-0 flex-1 flex-col items-end gap-2 text-xs">
          <div className="flex flex-wrap justify-end gap-2">
            <button type="button" className="rounded border border-current/20 px-2 py-1" onClick={() => setViewport({ zoom: 1, panPct: 0 })}>Reset full episode</button>
            <button type="button" className="rounded border border-current/20 px-2 py-1" onClick={() => setViewport({ zoom: 2, panPct: 0.25 })}>Inspect 5–15 s</button>
          </div>
          <output data-testid="viewport-readout">Window: {start.toFixed(2)}–{end.toFixed(2)} s · Zoom: {viewport.zoom.toFixed(3)}×</output>
          <output data-testid="viewport-hover">Preview: {hover === null ? '—' : `${hover.toFixed(2)} s`}</output>
          <output data-testid="viewport-playhead">{playhead === null ? 'Click a plot to seek' : `Playhead: ${playhead.toFixed(2)} s`}</output>
          <label className="flex items-center gap-2"><input type="checkbox" checked={disabled} onChange={event => setDisabled(event.target.checked)} />Disable charts</label>
        </div>
      </div>
      <div className="h-[165px]" data-testid="viewport-force">
        <EpisodeLineChart title="Gripper force" caption="Synthetic · 81 samples · 20 seconds" series={force} duration={duration} yRange={[0, 8]} markers={markers} ranges={ranges} disabled={disabled} {...shared} {...bind('force')} />
      </div>
      <div className="h-[150px]" data-testid="viewport-position">
        <EpisodeLineChart title="Gripper position" series={position} duration={duration} yRange={[0, 1]} markers={markers} ranges={ranges} disabled={disabled} {...shared} {...bind('position')} />
      </div>
      <div style={{ marginLeft: TIME_AXIS_INSET_L, marginRight: TIME_AXIS_INSET_R }} data-testid="viewport-timeline">
        <EpisodeTimeline duration={duration} frames={[]} tracks={[{ id: 'phase', name: 'Episode phase', blocks: ranges }]} {...shared} {...bind('timeline')} />
      </div>
      <p className="text-xs opacity-70">One shared window for both charts and timeline. Event times stay absolute: Contact 6 s, Grasp 7–12 s, Release 14 s. The camera follows the same absolute preview/playhead time.</p>
      <p className="text-xs opacity-70">Alt/Ctrl/Meta + wheel zooms at the pointer. Drag pans; Shift-drag zooms. Focus a plot for + / −, arrow keys, or Home. Plain vertical scrolling stays with the page.</p>
    </div>
  )
}
```

Share `zoom`, `panPct`, and their change callback:

```tsx
const [viewport, setViewport] = useState({ zoom: 1, panPct: 0 })
const viewportProps = { ...viewport, onViewportChange: setViewport }

<EpisodeLineChart {...viewportProps} series={series} duration={duration} />
<EpisodeTimeline {...viewportProps} duration={duration} />
```

The window starts at `panPct * duration` and spans `duration / zoom`. Omit both
props for local viewport state. Reset a controlled group to `{ zoom: 1, panPct: 0 }`.

| Gesture                        | Result                                               |
| ------------------------------ | ---------------------------------------------------- |
| Alt, Ctrl, or Meta + wheel     | Zoom around the pointer.                             |
| Horizontal wheel or drag       | Pan a zoomed chart. A drag begins after four pixels. |
| Shift + vertical drag          | Zoom around the initial pointer position.            |
| Click without dragging         | Call `onSeek` with the clicked time.                 |
| Focus the plot, then `+` / `-` | Zoom in / out.                                       |
| Left / right arrow             | Pan by 10% of the visible window.                    |
| `Home`                         | Reset the viewport.                                  |

A completed drag does not seek. Ordinary vertical scrolling scrolls the page.
All chart layers follow the viewport; a cursor outside it is hidden.

## Dense series

Increase the sample count, then zoom into a spike:

```tsx file="DenseSeriesSpec.tsx"

export const DENSE_DURATION = 60;
export function denseFixture(count: number) {
  const x = Array.from(
    { length: count },
    (_, i) => (i * DENSE_DURATION) / (count - 1),
  );
  const spike = Math.floor((count - 1) / 2);
  const y = x.map((t, i) =>
    t >= 42 && t <= 46
      ? NaN
      : i === spike
        ? 9
        : 3 + Math.sin(t / 3) + 0.15 * Math.sin(t * 23),
  );
  return [
    {
      id: "sensor",
      label: "Recorded sensor",
      color: EPISODE_LINE_CHART_PALETTE.blue,
      data: { x, y, low: y.map((v) => v - 0.4), high: y.map((v) => v + 0.65) },
      formatValue: (v: number) => `${v.toFixed(3)} N`,
    },
    {
      id: "reference",
      label: "Reference",
      color: EPISODE_LINE_CHART_PALETTE.purple,
      dash: "3 2.4",
      ghost: true,
      data: { x: [0, 60], y: [5, 5] },
    },
  ];
}

export function DenseSeriesSpec() {
  const [count, setCount] = useState(10000);
  const [exact, setExact] = useState(false);
  const [viewport, setViewport] = useState<ViewportState>({
    zoom: 1,
    panPct: 0,
  });
  const [time, setTime] = useState<number | null>(null);
  const [seek, setSeek] = useState<number | null>(null);
  const series = useMemo(() => denseFixture(count), [count]);
  const rendering: "auto" | "exact" = exact ? "exact" : "auto";
  return (
    <div data-testid="dense-demo" className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-4 text-xs">
        <label className="flex items-center gap-2">
          Samples
          <select
            aria-label="Recorded sample count"
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="rounded border border-current/20 bg-transparent px-2 py-1"
          >
            <option value={10000}>10,000</option>
            <option value={100000}>100,000</option>
            <option value={1000000}>1,000,000</option>
          </select>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={exact}
            onChange={(e) => setExact(e.target.checked)}
          />
          Exact vertices
        </label>
        <button
          type="button"
          className="rounded border border-current/20 px-2 py-1"
          onClick={() => {
            setViewport({ zoom: 20, panPct: 0.475 });
            setTime(series[0].data.x[Math.floor((count - 1) / 2)]);
          }}
        >
          Inspect spike
        </button>
        <button
          type="button"
          className="rounded border border-current/20 px-2 py-1"
          onClick={() => setViewport({ zoom: 1, panPct: 0 })}
        >
          Reset window
        </button>
        <output>
          {seek === null ? "Click to seek" : `Playhead: ${seek.toFixed(3)} s`}
        </output>
      </div>
      <div className="h-[280px]">
        <EpisodeLineChart
          title="Dense recording"
          caption={`${count.toLocaleString("en-US")} original samples · 60 seconds`}
          series={series}
          duration={DENSE_DURATION}
          yRange={[0, 10]}
          {...{ rendering }}
          {...viewport}
          onViewportChange={setViewport}
          time={time}
          onHover={setTime}
          onHoverEnd={() => setTime(null)}
          onSeek={setSeek}
          markers={[
            {
              id: "spike",
              time: series[0].data.x[Math.floor((count - 1) / 2)],
              label: "Single-sample spike",
            },
          ]}
          ranges={[
            {
              id: "missing",
              start: 42,
              end: 46,
              label: "Missing observations",
            },
          ]}
        />
      </div>
      <p className="m-0 text-xs opacity-70">
        One recorded sample reaches 9 N. The 42–46 s gap stays empty in both the
        line and supplied bounds. The dashed reference stays at 5 N. Hover reads
        original samples; zoom in to inspect the spike.
      </p>
    </div>
  );
}
```

`rendering="auto"` reduces dense display geometry while preserving local
extrema and gaps. Axis fitting and tooltip lookup still use the original
samples. Use `rendering="exact"` to retain every visible sample after the
browser measures the plot. Both modes use a bounded preview before measurement.

Supply finite, ascending timestamps and matching array lengths. Unsorted data
uses a slower fallback and is not reordered. Replace the `data` object when
changing its arrays so cached timestamp metadata refreshes.

## Series identification

Enable `highlightOnHover` to emphasize a nearby trace and its tooltip row.
Use `activeSeriesId` to connect that emphasis to another view. The
[seven-signal example](https://viz.dreamlake.ai/components/series-identification) adds keyboard and
touch controls.

## Shared pin and hover preview

Clicking can pin one time across every linked plot while hover continues to
preview other moments. Use one `useTimelinePreview(clock)` controller for the
whole group: `preview(ownerId, time)` on hover, `endPreview(ownerId)` on leave,
and `pin(time)` on seek. Ending the current preview returns every view to the
pin. Do not give each chart its own pin or stop forwarding hover when pinned.

The [shared timeline example](viz-components-episode-timeline.md#shared-click-to-pin-and-hover-preview)
connects two compact charts, a timeline and a shared clock readout, with keyboard
and touch controls and an explicit playback policy.

## Multi-chart sync

Hover an available chart to read its values at the shared time. The
unavailable channel keeps its space with “NO SIGNAL”.

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
        series={LARM_JOINTS_REALIZED}
        duration={DEMO_DURATION}
        unitHint="joint angles · per channel"
        yRange={[-1, 1]}
      />
      <EpisodeLineChart
        {...bind('temp')}
        title="Left arm motors"
        series={LARM_TEMP_SERIES}
        duration={DEMO_DURATION}
        unitHint="motor temperature · per channel"
        yRange={[-1, 1]}
      />
      <EpisodeLineChart
        {...bind('rarm')}
        title="Right arm"
        series={[]}
        duration={DEMO_DURATION}
        disabled
      />
      <EpisodeLineChart
        {...bind('touch')}
        title="Touch"
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

Move across the video, timeline, or charts to inspect the same recorded moment:

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
          series={LARM_JOINTS_REALIZED}
          duration={DEMO_DURATION}
          unitHint="joint angles · per channel"
          yRange={[-1, 1]}
        />
        <EpisodeLineChart
          {...bind('temp')}
          title="Left arm motors"
          series={LARM_TEMP_SERIES}
          duration={DEMO_DURATION}
          unitHint="motor temperature · per channel"
          yRange={[-1, 1]}
        />
        <EpisodeLineChart
          {...bind('rarm')}
          title="Right arm"
          series={[]}
          duration={DEMO_DURATION}
          disabled
        />
        <EpisodeLineChart
          {...bind('touch')}
          title="Touch"
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

Share `time` across charts. Each chart detects local hover automatically; peers
show shared hairlines without duplicate readouts. Optionally track the owner
with `isScrubOwner` to also distinguish bright and muted hairlines.

```tsx
const [time, setTime] = useState<number | null>(null)
const [ownerId, setOwnerId] = useState<string | null>(null)
const bind = (id: string) => ({
  time,
  isScrubOwner: ownerId === id,
  onHover: (t: number) => { setTime(t); setOwnerId(id) },
  onHoverEnd: () => { setTime(null); setOwnerId(null) },
})

<EpisodeLineChart {...bind('joints')} series={joints} duration={duration} />
<EpisodeLineChart {...bind('temperature')} series={temperatures} duration={duration} />
```

[Timeline](viz-components-episode-timeline.md) and [Video](https://viz.dreamlake.ai/components/episode-video-stack)
share the hover callbacks but do not use `isScrubOwner`. Video tracks camera
identity through `activeId`. Keep a separate playback time if leaving a hover
should restore the committed playhead.

## Series shape

```ts
interface EpisodeLineChartSeries {
  id: string;
  label?: string;
  data: { x: number[]; y: number[]; low?: number[]; high?: number[] };
  color: string;
  fillColor?: string;
  fillOpacity?: number;
  width?: number;
  dash?: string;
  opacity?: number;
  linecap?: "butt" | "round" | "square";
  readout?: boolean;
  ghost?: boolean;
  formatValue?: (value: number) => string;
}
```

Non-finite values break the line. Add `label` for a normal tooltip row; use
`formatValue` to format that signal's readout.

## Palette

Assign CSS colors directly or use these exports consistently across views.
The palette is unchanged between light and dark themes.

| Export                              | Value                 |
| ----------------------------------- | --------------------- |
| `EPISODE_LINE_CHART_PALETTE.blue`   | `oklch(60% 0.13 235)` |
| `EPISODE_LINE_CHART_PALETTE.yellow` | `oklch(80% 0.15 95)`  |
| `EPISODE_LINE_CHART_PALETTE.green`  | `oklch(66% 0.12 150)` |
| `EPISODE_LINE_CHART_PALETTE.purple` | `oklch(58% 0.13 295)` |
| `EPISODE_LINE_CHART_FAILURE`        | `oklch(58% 0.17 25)`  |

Keep signal labels alongside color. Use `EPISODE_LINE_CHART_FAILURE` with an
error label; a dashed, lower-opacity trace can distinguish reference data.

## Tooltip behaviour

Tooltips show time and up to five labeled signals. Identifying a series keeps
its row inside that limit and wraps its full label. The hovered chart's
readout follows both pointer coordinates with a fixed lower-right offset:
its top-left corner is 12px to the right and 12px below the pointer. Crossing a
chart's middle or edges does not flip it above or to the left. The body portal
can extend outside the plot and any clipping ancestor. Only the browser viewport
clamps it as needed to keep an 8px margin. Moving the pointer still moves the
readout when controlled `time` is frozen; sample selection continues to use the
chart's time semantics. Scrolling updates its position without anchoring it to
the chart corner. Peers show only the shared hairline. Hover readouts always
pass pointer events through.

## Disabled state

Set `disabled` for an unavailable channel. It retains its size, shows
“NO SIGNAL”, and disables chart layers and pointer interaction.

## Props

| Prop                   | Type                           | Default                | Purpose                                                                                                                                           |
| ---------------------- | ------------------------------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `series`               | `EpisodeLineChartSeries[]`     | required               | Signals, drawn in array order.                                                                                                                    |
| `duration`             | `number`                       | required               | Episode length in seconds; greater than zero.                                                                                                     |
| `title` / `caption`    | `string`                       | —                      | Chart title and optional caption above it.                                                                                                        |
| `lineWidth`            | `number`                       | `2`                    | Default non-scaling trace width in CSS pixels; per-series `width` takes precedence. Zero hides inherited strokes.                                 |
| `activeLineWidth`      | `number`                       | base × 1.65            | Active trace width in CSS pixels, never less than its resolved base width.                                                                        |
| `rendering`            | `'auto' \| 'exact'`            | `'auto'`               | Reduce dense display geometry or retain visible vertices after measurement.                                                                       |
| `yRange`               | `[number, number]`             | auto-fit               | Explicit y bounds. Auto-fit includes valid bands, adds 5% padding, and rounds outward.                                                            |
| `time`                 | `number \| null`               | `null`                 | Shared cursor time; null hides it.                                                                                                                |
| `onHover`              | `(t: number) => void`          | —                      | Receive the hovered time.                                                                                                                         |
| `onHoverEnd`           | `() => void`                   | —                      | Receive pointer leave.                                                                                                                            |
| `onSeek`               | `(t: number) => void`          | —                      | Receive a click's time.                                                                                                                           |
| `size`                 | `"default" \| "compact"`       | `"default"`            | Compact sets a 150px total height and fewer y ticks.                                                                                              |
| `height`               | `number \| string`             | parent / 150px compact | Total chart height, including title and axes.                                                                                                     |
| `background`           | `"none" \| "subtle"`           | `"none"`               | Opt into a tinted chart surface.                                                                                                                  |
| `isScrubOwner`         | `boolean`                      | `true`                 | Emphasize this cursor; false suppresses its readout. Only a local pointer or keyboard interaction shows a readout.                                |
| `zoom` / `panPct`      | `number`                       | `1` / `0`              | Controlled visible window.                                                                                                                        |
| `onViewportChange`     | `(v: ViewportState) => void`   | —                      | Receive requested zoom and pan.                                                                                                                   |
| `minZoom` / `maxZoom`  | `number`                       | `1` / `Infinity`       | Viewport zoom limits.                                                                                                                             |
| `markers`              | `EpisodeLineChartMarker[]`     | `[]`                   | Named event times.                                                                                                                                |
| `ranges`               | `EpisodeLineChartRange[]`      | `[]`                   | Labeled intervals.                                                                                                                                |
| `highlightOnHover`     | `boolean`                      | `false`                | Identify the nearest visible trace.                                                                                                               |
| `highlightThresholdPx` | `number`                       | `8`                    | Maximum pointer-to-trace distance in CSS pixels.                                                                                                  |
| `activeSeriesId`       | `string \| null`               | local hover            | Controlled series identity; null clears it.                                                                                                       |
| `onActiveSeriesChange` | `(id: string \| null) => void` | —                      | Receive requested identification changes.                                                                                                         |
| `unit`                 | `string`                       | derived                | Y-axis unit. Derived from a readout formatter when available; `''` hides it.                                                                      |
| `formatTick`           | `(v: number) => string`        | derived                | Tick text. Uses a readout's custom formatter with trailing unit removed, or step-aware numeric precision. An explicit formatter is used verbatim. |
| `unitHint`             | `string`                       | —                      | Explanation below the tooltip time.                                                                                                               |
| `showMidline`          | `boolean`                      | `true`                 | Draw the zero gridline, or midpoint tick if zero is absent. False leaves its label visible.                                                       |
| `disabled`             | `boolean`                      | `false`                | Show the unavailable-channel state.                                                                                                               |
| `className`            | `string`                       | —                      | Root CSS classes.                                                                                                                                 |

### EpisodeLineChartSeries

| Field                       | Type                                                            | Default                 | Purpose                                                        |
| --------------------------- | --------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------- |
| `id`                        | `string`                                                        | required                | Stable signal identifier.                                      |
| `label`                     | `string`                                                        | —                       | Tooltip label; omit to exclude the readout.                    |
| `data`                      | `{ x: number[]; y: number[]; low?: number[]; high?: number[] }` | required                | Aligned timestamps, values, and optional bounds.               |
| `color`                     | `string`                                                        | required                | CSS stroke color.                                              |
| `fillColor` / `fillOpacity` | `string` / `number`                                             | series color / `0.16`   | Band styling, independent of line opacity.                     |
| `width`                     | `number`                                                        | chart `lineWidth` (`2`) | Non-scaling CSS-pixel stroke width; zero hides the stroke.     |
| `dash`                      | `string`                                                        | solid                   | SVG dash pattern, such as `'3 2.4'`.                           |
| `opacity`                   | `number`                                                        | `1`                     | Line opacity.                                                  |
| `linecap`                   | `'butt' \| 'round' \| 'square'`                                 | `'butt'`                | Stroke end shape.                                              |
| `readout`                   | `boolean`                                                       | `true`                  | Include a labeled series in the tooltip.                       |
| `ghost`                     | `boolean`                                                       | `false`                 | Dim its readout and add a `tgt` suffix for reference signals.  |
| `formatValue`               | `(v: number) => string`                                         | `v => v.toFixed(2)`     | Format tooltip values, including any physical-unit conversion. |

## Readable axes and readout placement

Axis labels use 11px monospace at full opacity, with darker ink in light mode and brighter ink in dark mode. UIKit hosts can customize `--uikit-axis`; standalone charts use the same fallback colors. Gridlines remain faint.

Readouts follow the cursor by default (see Tooltip behaviour), with a borderless, translucent background and backdrop blur in both themes. They are portalled to the page body, so a small tile's `overflow` never clips them. `ChartTooltip` accepts `placement="outside"` with `boundaryRef` for the whole figure to keep the readout beside the figure instead. That readout follows the cursor only along the figure's external edge and never covers a plotted line. A figure that fills the viewport leaves no external space, so that readout is hidden. `clampToViewport` is deprecated and has no effect, because the cursor readout always stays inside the viewport.

Ordinary vertical wheel and touch scrolling belong to the page. Hold Alt, Ctrl or Command while scrolling to zoom; horizontal gestures pan a zoomed chart. Interactive readout lists allow scroll chaining at their boundaries.
