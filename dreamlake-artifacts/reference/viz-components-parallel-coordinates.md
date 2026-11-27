<!-- generated from https://viz.dreamlake.ai/components/parallel-coordinates.md at 0.33.14 9ac89cf8; do not edit -->

# Parallel coordinates

Compare experiment settings and outcomes in one plot. Each line is a run;
its axes can mix continuous values such as learning rate with categories such
as optimizer.

## Experiment selection and table linkage

Select a trace, experiment-list row, or table checkbox below. They share
selected experiment IDs, which also survive hiding an axis.

```tsx file="ExperimentComparisonSpec.tsx"

const axes: ParallelCoordinatesAxis[] = [
  {
    id: "rate",
    label: "Learning rate",
    type: "continuous",
    formatValue: (v) => v.toExponential(1),
  },
  {
    id: "batch",
    label: "Batch size",
    type: "categorical",
    categories: ["32", "64", "128", "256"],
  },
  { id: "width", label: "Hidden units", type: "continuous" },
  {
    id: "optimizer",
    label: "Optimizer",
    type: "categorical",
    categories: ["SGD", "AdamW", "Adam"],
  },
  { id: "score", label: "Eval score", type: "continuous" },
];
// Synthetic fixed observations, shared by the explicit table-only baseline and enhanced view.
const experiments: ParallelCoordinatesSeries[] = [
  {
    id: "run-a",
    label: "run-a",
    values: {
      rate: 0.001,
      batch: "64",
      width: 256,
      optimizer: "AdamW",
      score: 84,
    },
  },
  {
    id: "run-b",
    label: "run-b",
    values: {
      rate: 0.0002,
      batch: "128",
      width: 512,
      optimizer: "Adam",
      score: 93,
    },
  },
  {
    id: "run-c",
    label: "run-c",
    values: {
      rate: 0.008,
      batch: "32",
      width: 128,
      optimizer: "SGD",
      score: 65,
    },
  },
  {
    id: "run-d",
    label: "run-d",
    values: {
      rate: 0.004,
      batch: "256",
      width: 384,
      optimizer: "AdamW",
      score: 78,
    },
  },
  {
    id: "run-e",
    label: "run-e",
    values: {
      rate: 0.0005,
      batch: "64",
      width: null,
      optimizer: "Adam",
      score: 89,
    },
  },
  {
    id: "run-f",
    label: "run-f",
    values: {
      rate: 0.002,
      batch: "128",
      width: 192,
      optimizer: "SGD",
      score: 72,
    },
  },
];
const controlClass =
  "rounded px-2 py-1 text-xs hover:bg-black/[0.04] dark:hover:bg-white/[0.05] focus-visible:outline-2 focus-visible:outline-[#3388aa]";

export function ExperimentComparisonSpec() {
  const [showChart, setShowChart] = useState(true);
  const [visibleAxisIds, setVisibleAxisIds] = useState(
    axes.map((axis) => axis.id),
  );
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [onlySelected, setOnlySelected] = useState(false);
  const rows = onlySelected
    ? experiments.filter((row) => selectedIds.includes(row.id))
    : experiments;
  const toggleRow = (id: string) =>
    setSelectedIds((ids) =>
      ids.includes(id) ? ids.filter((value) => value !== id) : [...ids, id],
    );
  return (
    <div data-testid="parallel-comparison-demo" className="min-w-0 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showChart}
            onChange={(event) => setShowChart(event.target.checked)}
          />
          Show comparison chart
        </label>
        <div className="flex items-center gap-1">
          <button
            className={controlClass}
            type="button"
            onClick={() =>
              setSelectedIds(
                [...experiments]
                  .sort(
                    (a, b) => Number(b.values.score) - Number(a.values.score),
                  )
                  .slice(0, 2)
                  .map((row) => row.id),
              )
            }
          >
            Select top 2
          </button>
          <button
            className={controlClass}
            type="button"
            onClick={() => setSelectedIds([])}
          >
            Clear selection
          </button>
        </div>
      </div>
      {showChart ? (
        <>
          <fieldset className="flex flex-wrap items-center gap-x-4 gap-y-2 border-0 p-0 text-[11px]">
            <legend className="mb-2 font-medium">Visible dimensions</legend>
            {axes.map((axis) => (
              <label key={axis.id} className="flex items-center gap-1.5">
                <input
                  type="checkbox"
                  checked={visibleAxisIds.includes(axis.id)}
                  onChange={() =>
                    setVisibleAxisIds((ids) =>
                      ids.includes(axis.id)
                        ? ids.filter((id) => id !== axis.id)
                        : [...ids, axis.id],
                    )
                  }
                />
                {axis.label}
              </label>
            ))}
          </fieldset>
          <ParallelCoordinates
            title="Training sweep · 6 experiments"
            axes={axes}
            series={experiments}
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            visibleAxisIds={visibleAxisIds}
          />
        </>
      ) : (
        <p className="rounded bg-black/[0.025] px-3 py-4 text-xs dark:bg-white/[0.035]">
          Table-only baseline — the same six synthetic experiments before adding
          ParallelCoordinates.
        </p>
      )}
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px]">
        <output aria-live="polite">
          {selectedIds.length} selected · {rows.length} shown
        </output>
        <label className="flex items-center gap-1.5">
          <input
            type="checkbox"
            checked={onlySelected}
            onChange={(event) => setOnlySelected(event.target.checked)}
          />
          Selected experiments only
        </label>
      </div>
      <div className="overflow-x-auto">
        <table
          className="w-full whitespace-nowrap text-left text-[11px]"
          aria-label="Experiment observations"
        >
          <thead>
            <tr className="border-b border-black/10 dark:border-white/10">
              <th scope="col" className="px-2 py-2 font-medium">
                Select
              </th>
              <th scope="col" className="px-2 py-2 font-medium">
                Experiment
              </th>
              {axes.map((axis) => (
                <th key={axis.id} scope="col" className="px-2 py-2 font-medium">
                  {axis.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.id}
                className={`border-b border-black/[0.05] dark:border-white/[0.06] ${selectedIds.includes(row.id) ? "bg-black/[0.035] dark:bg-white/[0.05]" : ""}`}
              >
                <td className="px-2 py-2">
                  <input
                    type="checkbox"
                    aria-label={`Select ${row.label} in table`}
                    checked={selectedIds.includes(row.id)}
                    onChange={() => toggleRow(row.id)}
                  />
                </td>
                <th scope="row" className="px-2 py-2 font-mono font-normal">
                  {row.label}
                </th>
                {axes.map((axis) => (
                  <td key={axis.id} className="px-2 py-2 font-mono">
                    {row.values[axis.id] == null
                      ? "Missing"
                      : axis.type === "continuous" && axis.formatValue
                        ? axis.formatValue(Number(row.values[axis.id]))
                        : String(row.values[axis.id])}
                  </td>
                ))}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} className="px-2 py-4 text-center opacity-60">
                  No selected experiments. Select a trace, experiment button, or
                  table checkbox.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <p className="text-[11px] leading-relaxed opacity-65">
        Synthetic data. run-e has no recorded hidden-unit value: its trace
        breaks at that axis. Axis visibility and table filtering preserve
        selection. Each row checkbox works with the keyboard.
      </p>
    </div>
  );
}
```

The example implements “Select top 2” and table filtering outside the chart.
Reuse the reported IDs for your own table or detail view.

The experiment list uses `@dreamlake/uikit/list` (UIKit 0.2.11 or newer in the
0.2 release line) for virtualization and the shared selection controller
used by DreamLake's Experiments list. Click or tap selects one row. Cmd/Ctrl-click
toggles a row; Shift-click replaces the selection with the range from its anchor.
Drag with a mouse or pen to select a contiguous range. Cmd/Ctrl-drag adds the
range to the selection present when the drag started. A press without movement
is handled as a normal click. The list scrolls near the edges while dragging;
touch keeps native vertical scrolling.

Tab into the list, then use Up/Down, Home/End or Page Up/Page Down to navigate
and preview values. Space or Enter toggles the active row. Shift plus navigation
selects an anchored range; Ctrl/Cmd+A selects the current list. Escape clears the
selection and dismisses the preview. The list uses 24px rows, grows to 288px high,
and renders a window of rows while keeping its active accessible option mounted.

## Smooth exploration of a larger comparison

Hovering or focusing a run raises its trace without moving the pointer targets.
The example toggles use UIKit’s `Checkbox`: an accent-color checkmark at rest, with the box visible on hover or keyboard focus.

Selection remains controlled by stable IDs. Traces stay fully bright at rest
and during hover or keyboard preview. Selecting a visible run dims background
curves to 16% opacity while selected and previewed traces stay bright. Clearing
the selection restores full brightness; IDs outside the visible data do not dim
the chart. Emphasis changes immediately, without a fade animation. Width and a
contrast halo distinguish the active trace. Recorded positions and
missing-value gaps update immediately, without interpolating research data.

```tsx file="DenseComparisonSpec.tsx"

const axes: ParallelCoordinatesAxis[] = [
  { id: "rate", label: "Learning rate", type: "continuous", domain: [0, 0.01] },
  {
    id: "optimizer",
    label: "Optimizer",
    type: "categorical",
    categories: ["SGD", "Adam", "AdamW"],
  },
  {
    id: "batch",
    label: "Batch",
    type: "categorical",
    categories: ["32", "64", "128"],
  },
  { id: "score", label: "Score", type: "continuous", domain: [0, 100] },
  { id: "hours", label: "Hours", type: "continuous", domain: [0, 24] },
];
// Synthetic demonstration records, not measured research results.
const experiments: ParallelCoordinatesSeries[] = Array.from(
  { length: 100 },
  (_, i) => ({
    id: `sweep-${i}`,
    label: `Run ${i + 1}`,
    values: {
      rate: (((i * 17) % 100) + 1) / 10000,
      optimizer: ["SGD", "Adam", "AdamW"][i % 3],
      batch: ["32", "64", "128"][Math.floor(i / 3) % 3],
      score: i % 17 === 0 ? null : 40 + ((i * 23) % 60),
      hours: 1 + ((i * 7) % 23),
    },
  }),
);

export function DenseComparisonSpec() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  return (
    <div data-testid="parallel-dense-demo" className="min-w-0 space-y-3">
      <p className="text-xs opacity-65">
        100 synthetic runs. Move across traces, or Tab through runs and press
        Space to select. Escape dismisses the preview. Open an axis label to
        configure its scale. The plot fits the available width.
      </p>
      <button
        type="button"
        className="rounded border border-black/15 px-2 py-1 text-xs dark:border-white/15"
        onClick={() => setSelectedIds([])}
      >
        Clear selection
      </button>
      <ParallelCoordinates
        title="Synthetic training sweep · 100 runs"
        axes={axes}
        series={experiments}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
    </div>
  );
}
```

Use Tab to focus the experiment list, arrow keys to preview a run, Space or
Enter to toggle it, and Escape to clear selection and dismiss its preview. Moving the pointer onto a different trace previews that trace even
when the experiment list retains focus; moving away restores the focused run. A new
keyboard focus takes over from a previous pointer preview. Touch users can tap experiment controls and axis labels. Set `minAxisSpacing`
when you want a horizontally scrollable plot. Hovering never selects a run. Keep `axes` and `series` references
stable when their contents have not changed so cached geometry can be reused.

This example uses 100 synthetic records. For larger studies, filter the comparison
set in the host table: the experiment list is virtualized, but every run still
has an SVG trace. Plot geometry is not virtualized or numerically smoothed.

## Line width and active emphasis

Runs default to **2 CSS pixels**, matching `EpisodeLineChart`. Set chart-wide
`lineWidth` or override one run with `series.width`; 1.5–3px are useful explicit
choices, with 2px the recommended starting point. Stroke widths stay in CSS
pixels when the chart resizes or scrolls, rather than scaling with SVG viewBox
units. Dense plots retain readable traces; filter the comparison set when needed.

```tsx file="LineWidthSpec.tsx"

const axes: ParallelCoordinatesAxis[] = [
  { id: "score", label: "Score", type: "continuous", domain: [0, 100] },
  { id: "hours", label: "Hours", type: "continuous", domain: [0, 24] },
  {
    id: "size",
    label: "Model",
    type: "categorical",
    categories: ["Small", "Medium", "Large"],
  },
];
const experiments: ParallelCoordinatesSeries[] = [
  {
    id: "run-a",
    label: "Run A",
    values: { score: 72, hours: 6, size: "Small" },
  },
  {
    id: "run-b",
    label: "Run B",
    values: { score: 89, hours: 18, size: "Large" },
  },
  {
    id: "run-c",
    label: "Run C",
    values: { score: 84, hours: 12, size: "Medium" },
  },
];

export function LineWidthSpec() {
  const [lineWidth, setLineWidth] = useState(2);
  const [activeWidth, setActiveWidth] = useState("auto");
  const [override, setOverride] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const series = useMemo(
    () =>
      experiments.map((experiment, index) => ({
        ...experiment,
        width: override && index === 0 ? 3 : undefined,
      })),
    [override],
  );
  return (
    <div data-testid="parallel-line-width-demo" className="min-w-0 space-y-3">
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
          Run A: 3px override
        </label>
      </div>
      <ParallelCoordinates
        title="Line width · three synthetic runs"
        axes={axes}
        series={series}
        lineWidth={lineWidth}
        activeLineWidth={
          activeWidth === "auto" ? undefined : Number(activeWidth)
        }
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
      <p className="text-xs opacity-65">
        Hover or focus a run to preview it. Select a run to keep its emphasis.
        Width controls change only presentation; recorded values and stable
        pointer targets stay the same.
      </p>
    </div>
  );
}
```

```tsx
<ParallelCoordinates
  axes={axes}
  series={[
    { ...runA, width: 3 }, // Per-run override.
    runB, // Inherits 2px.
  ]}
  lineWidth={2}
  activeLineWidth={4}
  selectedIds={selectedIds}
  onSelectionChange={setSelectedIds}
/>
```

Hovered, focused and selected runs use 1.65 times their resolved base width by
default. Set `activeLineWidth` for an explicit CSS-pixel width: the final width
is `max(baseWidth, activeLineWidth)`, so activation cannot thin a wider run.
The example's 3px Run A becomes 4px when active. Selection and hover still use
stable IDs and pointer targets; a wider painted stroke does not move those targets.

A zero base width hides the stroke even when active, while recorded values,
isolated recorded point markers and experiment controls remain available. Negative or non-finite per-run widths
inherit the chart width; an invalid chart width falls back to 2px, and an invalid
active width uses the automatic multiplier. Line widths never alter axis domains,
recorded positions or missing-value gaps.

## Curves, padding and axis values

Smooth connectors (`curve="smooth"`) use the original Vuer parallel-axis
Catmull–Rom curve with tension **0.5**. Two connected points use a straight
segment; three or more use cubic Bézier segments through the exact recorded
axis positions. Missing values split the trace into separate connected runs.
The curve can overshoot between axes; those connectors are not additional
measurements. Set `curve="linear"` for straight segments. Hover and focus update immediately
without fades or animated geometry. Neither style creates observations or
numerically smooths research data.

The control points match Vuer's [`generateSmoothPath`](https://github.com/vuer-ai/vuer-viz/blob/8a8b988f6763d079743a4e4733214900428c1b07/vuer-viz/src/charts/parallel-axis/ParallelAxis.tsx):
for a segment from `p1` to `p2`, use `c1 = p1 + (p2 - p0) / 6 * 0.5`
and `c2 = p2 - (p3 - p1) / 6 * 0.5`, duplicating the nearest endpoint
when `p0` or `p3` is absent. The formula operates on screen coordinates; it
does not alter the stored observations, domains or ticks.

```tsx
// Default: original Vuer curve and immediate hover feedback.
<ParallelCoordinates axes={axes} series={series} />
// Optional straight connectors, with independent explicit insets.
<ParallelCoordinates axes={axes} series={series} curve="linear" paddingLeft={17} paddingRight={39} />
```

Normal strokes default to 2px and highlights retain the proportional width contract above. The active trace
has a wider surface-colored halo; `activeHaloColor` matches a custom host surface
without adding a chart background.

Both `paddingLeft` and `paddingRight` default to **0**. The first and last axes
sit at the edges of the available plot, including after a resize. Insets are
independent pixels and clamp to fit. Labels align inward at the edges; long
labels expose their full text through the button title and accessible name.
`minAxisSpacing={112}` opts into a minimum gap and horizontal scrolling; its
zero default keeps all axes within the available width.

Hover or focus shows the raw formatted value at **every visible axis**, including
values whose points are outside the displayed limits. The full text below the
plot explains missing, nonnumeric, nonpositive-log and out-of-domain values.
`labelPlacement` is `"above"` or `"below"`; `hoverLayout` accepts `"above"`,
`"below"`, or `"auto"` (opposite the labels).

## Axis modes and custom functions

Click or tap an axis line or its label to advance to the next axis mode.
Focus its label and press Enter or Space for the same action. Hold Shift while
clicking or pressing Enter/Space to cycle backward. Custom functions
and exact limits are supplied by the caller through axis definitions or
`axisModes`.

From the default linear mode, the cycle is **linear automatic → categorical →
log automatic → linear uniform automatic → repeat**. A distinct configured/default
mode (for example, explicit limits) starts its cycle, followed by categories,
linear automatic, log automatic and linear uniform automatic. A categorical
default starts with categories followed by those numeric modes. Named
`axisModeOptions` follow the built-ins; duplicate effective modes are skipped. Log is skipped when there are no positive numeric values;
wholly nonnumeric axes omit numeric modes unless a caller's `numericValue`
accessor supplies numeric positions.

```tsx file="AxisModesSpec.tsx"

const axes: ParallelCoordinatesAxis[] = [
  { id: "rate", label: "Learning rate", type: "continuous" },
  {
    id: "batch",
    label: "Batch",
    type: "categorical",
    categories: ["32", "64", "128"],
  },
  {
    id: "optimizer",
    label: "Optimizer",
    type: "categorical",
    categories: ["SGD", "Adam", "AdamW"],
  },
  {
    id: "score",
    label: "Score",
    type: "continuous",
    formatValue: (v) => `${v}%`,
  },
  { id: "hours", label: "Hours", type: "continuous" },
];
const series: ParallelCoordinatesSeries[] = [
  {
    id: "a",
    label: "Synthetic A",
    values: {
      rate: 0.001,
      batch: "32",
      optimizer: "SGD",
      score: 81.25,
      hours: 0,
    },
  },
  {
    id: "b",
    label: "Synthetic B",
    values: {
      rate: 0.01,
      batch: "128",
      optimizer: "AdamW",
      score: 93.75,
      hours: 12,
    },
  },
  {
    id: "c",
    label: "Synthetic C",
    values: {
      rate: 0.0001,
      batch: "64",
      optimizer: "Adam",
      score: 76.5,
      hours: 8,
    },
  },
  {
    id: "d",
    label: "Synthetic D",
    values: {
      rate: 0.003,
      batch: "64",
      optimizer: "AdamW",
      score: null,
      hours: 3,
    },
  },
];
const strategies: ParallelAxisModeOption[] = [
  {
    id: "sqrt",
    label: "Square root + function limits",
    mode: {
      type: "continuous",
      domain: ({ extent }) => [0, Math.max(1, extent?.[1] ?? 1)],
      scale: {
        label: "Square root",
        transform: Math.sqrt,
        inverse: (v) => v * v,
      },
    },
  },
  {
    id: "categories",
    label: "Reverse distinct categories",
    mode: {
      type: "categorical",
      categories: ({ values }) =>
        [
          ...new Set(
            values.filter(
              (v): v is string | number =>
                typeof v === "string" ||
                (typeof v === "number" && Number.isFinite(v)),
            ),
          ),
        ].reverse(),
    },
  },
  {
    id: "numeric-text",
    label: "Parse numeric text explicitly",
    mode: {
      type: "continuous",
      scale: "linear",
      domain: "auto",
      numericValue: (value) =>
        typeof value === "number"
          ? value
          : typeof value === "string" &&
              value.trim() !== "" &&
              Number.isFinite(Number(value))
            ? Number(value)
            : null,
    },
  },
];

export function AxisModesSpec() {
  const [modes, setModes] = useState<ParallelAxisModes>({
    score: { domain: [60, 100] },
  });
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [padding, setPadding] = useState(false);
  const [below, setBelow] = useState(false);
  const [linear, setLinear] = useState(false);
  return (
    <div data-testid="parallel-modes-demo" className="min-w-0 space-y-3">
      <p className="text-xs opacity-65">
        Synthetic records. Click an axis or its label to cycle modes. Caller
        strategies demonstrate category, domain and transform functions; exact
        limits are configured in the host.
      </p>
      <div className="flex flex-wrap gap-3 text-xs">
        <label className="inline-flex items-center gap-1.5">
          <Checkbox checked={padding} onCheckedChange={setPadding} />
          Left 20px / right 44px
        </label>
        <label className="inline-flex items-center gap-1.5">
          <Checkbox checked={below} onCheckedChange={setBelow} />
          Labels below
        </label>
        <label className="inline-flex items-center gap-1.5">
          <Checkbox checked={linear} onCheckedChange={setLinear} />
          Straight connectors
        </label>
        <button
          type="button"
          onClick={() => {
            setModes({ score: { domain: [60, 100] } });
            setSelectedIds([]);
          }}
          className="rounded border border-black/15 px-2 dark:border-white/15"
        >
          Reset example
        </button>
      </div>
      <ParallelCoordinates
        title="Axis modes and caller strategies"
        axes={axes}
        series={series}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
        axisModes={modes}
        onAxisModesChange={setModes}
        axisModeOptions={strategies}
        paddingLeft={padding ? 20 : 0}
        paddingRight={padding ? 44 : 0}
        labelPlacement={below ? "below" : "above"}
        hoverLayout="auto"
        curve={linear ? "linear" : "smooth"}
      />
    </div>
  );
}
```

Axis modes keep local component state by default. To control them, pass
`axisModes` and `onAxisModesChange`; the callback receives the next complete
map keyed by axis ID. A controlled map without a callback is read-only.
`defaultAxisModes` seeds uncontrolled settings. Modes survive hiding an axis
and are scoped to this component instance; they do not write browser storage.
Caller updates to limits or strategies take effect directly.

```tsx
const [axisModes, setAxisModes] = useState<ParallelAxisModes>({
  rate: { type: "continuous", scale: "log", domain: "auto" },
  score: { domain: [60, 100] },
});

<ParallelCoordinates
  axes={axes}
  series={experiments}
  axisModes={axisModes}
  onAxisModesChange={setAxisModes}
/>;
```

Numeric mode accepts finite numbers. Strings remain categorical unless a caller
explicitly supplies `numericValue`. Log mode leaves zero and negative values as
gaps while retaining their raw readouts. A logarithmic axis with nonpositive
explicit or uniform limits reports an unavailable scale: choose positive limits
or per-axis automatic limits. Uniform mode pools the finite numeric observations
of all visible numeric axes; use it when comparing compatible units. When a uniform log axis
participates and every pooled value is positive, all uniform axes share positive
decade bounds. Nonpositive pooled values cannot be displayed on that log axis.

Automatic linear limits use the shared [Numeric axes](https://viz.dreamlake.ai/components/numeric-axis)
1/2/5 grid. Explicit bounds stay exact. An invalid explicit tuple follows that
contract's automatic fallback; a failing custom strategy reports an unavailable
axis rather than inventing positions.

Functions are first-class strategies in `ParallelAxisMode`:

```tsx
const rootScale: ParallelAxisMode = {
  type: "continuous",
  domain: ({ extent }) => [0, Math.max(1, extent?.[1] ?? 1)],
  scale: {
    label: "Square root",
    transform: Math.sqrt,
    inverse: (value) => value * value,
    // Optional ticks are raw numeric positions, not normalized fractions.
    ticks: ({ domain }) => [domain[0], domain[1] / 4, domain[1]],
  },
};
const ordered: ParallelAxisMode = {
  type: "categorical",
  categories: ({ values }) =>
    [
      ...new Set(
        values.filter((value): value is string => typeof value === "string"),
      ),
    ].reverse(),
};

<ParallelCoordinates
  axes={axes}
  series={experiments}
  axisModeOptions={[
    { id: "root", label: "Square-root strategy", mode: rootScale },
    { id: "ordered", label: "Reverse category order", mode: ordered },
  ]}
/>;
```

These caller options apply the supplied functions to geometry and ticks. `categories` receives the original axis and raw values.
`domain` and custom `ticks` receive the axis, finite numeric values, their
`extent`, and the pooled `uniformExtent`; `ticks` also receives the resolved
domain. A transform must be finite and strictly increasing throughout that
domain, with a matching inverse. Bounds, observations and supplied ticks are
validated. Keep strategy objects and data references stable between changes.
Ticks, curves, point markers and pointer hit targets all use the resolved scale;
hover descriptions continue to use the original observations and formatter.

## Data and controlled state

Define axes in display order and key each run's values by axis ID:

```tsx
const axes: ParallelCoordinatesAxis[] = [
  { id: 'rate', label: 'Learning rate', type: 'continuous' },
  { id: 'optimizer', label: 'Optimizer', type: 'categorical', categories: ['SGD', 'Adam'] },
  { id: 'score', label: 'Score', type: 'continuous', domain: [0, 100] },
]
const experiments = [{
  id: 'run-a', label: 'Run A',
  values: { rate: 0.001, optimizer: 'Adam', score: 89 },
}]
const [selectedIds, setSelectedIds] = useState<string[]>([])

<ParallelCoordinates
  axes={axes} series={experiments}
  selectedIds={selectedIds} onSelectionChange={setSelectedIds}
/>
```

Keep axis and experiment IDs unique and stable. Continuous values must be
numbers; convert numeric strings before rendering. Categorical values follow
`categories` from bottom to top.

<span id="behavior-contract" />

## Axes and missing values

Continuous axes fit finite data with [readable ticks](https://viz.dreamlake.ai/components/numeric-axis).
Set a finite, increasing `domain` for a fixed scale. Invalid domains fall back
to automatic fitting; constant and empty data still receive a finite range.

Missing or non-finite values, unknown categories, and values outside a fixed
domain break the trace. A lone valid value appears as a point. Experiment-list
options retain the values in accessible text.

Wire both `selectedIds` and `onSelectionChange` to apply selection changes.
Without the callback, selection is read-only. `visibleAxisIds` filters the axes
without changing their declared order.

## Props

| Prop                               | Default                   | Meaning                                                                  |
| ---------------------------------- | ------------------------- | ------------------------------------------------------------------------ |
| `axes`, `series`                   | required                  | Stable-ID axis definitions and raw observations.                         |
| `selectedIds`, `onSelectionChange` | `[]`, absent              | Controlled experiment multi-selection.                                   |
| `visibleAxisIds`                   | all                       | Visible subset, in declared axis order.                                  |
| `axisModes`, `onAxisModesChange`   | uncontrolled              | Controlled mode map and next-map callback.                               |
| `defaultAxisModes`                 | `{}`                      | Initial uncontrolled mode map.                                           |
| `axisModeOptions`                  | `[]`                      | Named caller strategies included in direct axis cycling.                 |
| `paddingLeft`, `paddingRight`      | `0`, `0`                  | Independent horizontal pixel insets.                                     |
| `minAxisSpacing`                   | `0`                       | Optional minimum pixel gap; enables horizontal scrolling when necessary. |
| `curve`                            | `"smooth"`                | Original Vuer Catmull–Rom connectors; `"linear"` uses straight segments. |
| `lineWidth`, `activeLineWidth`     | `2`, base × 1.65          | Normal and highlighted stroke widths in pixels.                          |
| `activeHaloWidth`                  | active width + 4          | Full active halo stroke width, at least the active stroke width.         |
| `activeHaloColor`                  | white / dark surface      | CSS color override for a custom host surface.                            |
| `labelPlacement`                   | `"above"`                 | Axis labels `"above"` or `"below"`.                                      |
| `hoverLayout`                      | `"auto"`                  | Values `"above"`, `"below"`, or opposite the labels.                     |
| `title`                            | `"Experiment comparison"` | Visible and accessible chart name.                                       |
| `className`                        | `""`                      | Root CSS classes.                                                        |

`ParallelAxisMode` accepts optional `type`, `scale`, `domain`, `categories` and
`numericValue` fields. `scale` is `"linear"`, `"log"`, or a
`ParallelScaleTransform`; `domain` is `"auto"`, `"uniform"`, a two-number tuple,
or a function. Categories can be a typed string/number array or a function.
All related types are exported from `@dreamlake/viz` and
`@dreamlake/viz/parallel-coordinates`.

Use at least two visible axes. Brushing and axis-reordering controls are not
included. For dense studies, filter the comparison set in the host table.

### ParallelCoordinatesSeries

| Field    | Type                                                    | Default                 | Purpose                                                           |
| -------- | ------------------------------------------------------- | ----------------------- | ----------------------------------------------------------------- |
| `id`     | `string`                                                | required                | Stable experiment identity for hover and selection.               |
| `label`  | `string`                                                | required                | Visible experiment label.                                         |
| `values` | `Record<string, number \| string \| null \| undefined>` | required                | Recorded values keyed by axis ID; missing values break the trace. |
| `color`  | `string`                                                | palette                 | Optional CSS trace color.                                         |
| `width`  | `number`                                                | chart `lineWidth` (`2`) | Per-run width in CSS pixels; zero hides its stroke.               |

## Related API comparison

See the [current two-site API comparison](https://viz.dreamlake.ai/guides/api-comparison) for source-linked contracts, migration examples, intentional differences, and remaining capabilities.
