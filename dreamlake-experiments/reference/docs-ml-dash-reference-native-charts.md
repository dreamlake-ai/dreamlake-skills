<!-- generated from https://docs.dreamlake.ai/ml-dash/reference/native-charts.md at 0.1.147 24acba47; do not edit -->

# Native Experiment charts and rows

DreamLake computes chart series and run summary rows from native project
Tracks. These endpoints read DreamLake data only; historical Dash runs continue
to use Dash. Both require a signed-in user with read access to the project. As
with ml-dash, there is no limit on the number of runs, Tracks, stored points or
returned cells: every requested Track is read chunk by chunk, keeping only the
requested numeric columns. A [reduced series](#reduced-series-for-long-runs)
keeps its own budget. A missing or unreadable Track chunk returns
`503 NATIVE_METRIC_UNAVAILABLE` instead of a partial result.

## Chart series

`POST /native-experiments/ns/:namespace/projects/:project/chart-series`

```json
{
  "experiments": ["<run-id>"],
  "x_key": "step",
  "y_keys": ["train.loss"],
  "agg": ["MEAN", "STD"],
  "filters": {"index_range": {"start": 0, "end": 5000}}
}
```

Select runs with `experiments` (run IDs) or `glob` (a run-name pattern using
`*` and `?`). With neither, every active run in the project is used. A glob is
matched against every active run whose name starts with the glob's text before
its first wildcard. `metric_names` limits which Tracks are read. A column is named
either bare (`loss`) or with its Track name (`train.loss`). `index` is the
stored point index, and ISO `timestamp` strings become epoch milliseconds.

Without `agg`, `data` has one entry per run with `experiment_id`,
`experiment_name`, and arrays for `x_key` and each `y_keys` entry, sorted by x.
A missing value is `null`. With `agg`, `data` pools every selected run and has
the raw arrays plus one value per `<y_key>_<function>` (for example
`loss_mean`). The supported functions are `MEAN`, `MEDIAN`, `STD` (population),
`MIN`, `MAX`, `SUM`, `PERCENTILE_25`, and `PERCENTILE_75`.
`filters.index_range` keeps points with `start <= index < end`, and
`filters.columns` limits the returned columns.

With `"response_format": "ARROW"`, the response is an Arrow IPC file
(`application/vnd.apache.arrow.file`) holding the same values as float64
columns. The `X-Data-Points-Processed`, `X-Compute-Time-Ms`, and
`X-Data-Fetch-Time-Ms` headers carry the compute metadata. Without `agg`, the table has one row per point,
with `experiment_id` and `experiment_name` columns. Those two names cannot be
used as chart keys in this format. With `agg`, each aggregate value repeats on
every row of the pooled raw columns. If the pooled raw columns have different
lengths, the request returns `422 NATIVE_CHART_NOT_TABULAR`; use JSON instead, or
use `filters.columns` to return only the aggregates. Errors are JSON in both formats.

### Reduced series for long runs

Add `"max_points": N` (2 to 10,000, JSON only, not with `agg`) to get a reduced
series per run instead of every point. Each Track's stored index range,
narrowed by `filters.index_range`, is split into equal bins: `max_points`
divided by the run's Track count. Each bin returns the mean `x_key` and the mean
of each `y_keys` column in `data`, and that column's minimum and maximum in
`low` and `high`. The minimum and maximum are exact: every stored point in the
range is read. When a bin holds at most one point, the values are the stored
values. Each run also reports `reduced` (true if any bin averaged more than one
point) and `points` (the number of bins returned, never more
than `max_points`). A run with more selected Tracks than `max_points` returns
`413 NATIVE_COMPUTE_TOO_LARGE`; use `metric_names` to read only the charted Tracks.

A reduced request may read up to 2,000,000 stored points, counted from the
chunks that overlap `index_range`. To look closer, send a narrower
`index_range` with the same `max_points`; only chunks in that range are read.
Bins average x, so x must not decrease as the stored index grows; otherwise the
request returns `422 NATIVE_CHART_NOT_MONOTONIC`.

```json
{"experiments": ["<run-id>"], "x_key": "step", "y_keys": ["train.loss"], "max_points": 2000}
```

## Run summary row

`POST /native-experiments/ns/:namespace/projects/:project/runs/:runId/row`
accepts `{"max_plot_points": 1000, "metric_names": ["train"]}`. Both fields are
optional. `max_plot_points` can be 1 to 5,000; a value of 1 returns summary
values only.

The response has `row.single_values`, `row.plots`, and `row.metadata`. For each
numeric `track.column`, a single value is chosen from its name: the minimum for
losses and errors, the maximum for accuracy and scores, the latest for learning
rates and counters, and the mean for time, resources, and gradients. Values for
unrecognized names are classified from the data. `step` is the stored point
index of the chosen value. Each plot has `x`, `y`, `high`, and `low` arrays and
summary `statistics`. A series longer than twice `max_plot_points` is divided
into equal bins, with the mean and the minimum and maximum of each bin.

## Per-run dashboard configuration

A run's `.dashrc` is a YAML document (JSON is also valid) stored as a file on
**that run**. A project-root or parent-folder `.dashrc` does not configure its
child runs. The dashboard uses `metrics.fields` for header values and `charts`
for its chart list; `header` is not a supported configuration block.

Without that file, the dashboard currently chooses up to six charts and two
summary values. Its naming heuristic prioritizes train/eval loss and return
fields, so a run may have recorded `rollout` and `system` data that the overview
does not show. Stored metric groups, charted fields and header summaries are
different counts. A missing chart alone is not evidence of a failed write.

An explicit chart list replaces that automatic selection; it is not truncated
to six entries:

```yaml
metrics:
  fields: [eval.return_mean, eval.return_std]
charts:
  - ctype: line
    title: Rollout reward
    xKey: rollout.global_step
    yKey: rollout.episode_reward_mean
    bins: 200
  - ctype: line
    title: Policy loss
    xKey: train.global_step
    yKey: train.policy_loss
    bins: 200
  - ctype: image
    glob: '**/*'
    nCols: 1
    nRows: 1
    sort: name
  - ctype: video
    glob: '**/*'
    nCols: 1
    nRows: 1
    sort: name
```

Use keys the run actually recorded. For grouped metrics, qualify the field as
`group.column`, and log an x value in each group. `xKey: default` lets the
server choose an axis; an explicit key makes an RL environment-step axis
unambiguous. `bins` is a chart data-reduction budget, not the number of charts.

Image and video entries filter files by media kind and match `glob` against
the project-relative file path, including the run path. `**/*` includes the
selected run's media regardless of its folder. Each grid requests
`nCols * nRows` files, capped at 100; size the grid for the files you want to
show. A grid limit is not a request to display every future upload.

The [RL logging example](docs-ml-dash-examples-rl-logging.md) includes a complete
28-field dashboard and image/video previews. Refresh the run page after
uploading or replacing the configuration outside that page. File readback
confirms the saved configuration; rendered-page acceptance is a separate check.
