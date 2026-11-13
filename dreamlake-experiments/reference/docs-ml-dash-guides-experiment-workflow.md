<!-- generated from https://docs.dreamlake.ai/ml-dash/guides/experiment-workflow.md at 0.1.158 f5167273; do not edit -->

# Experiment workflow

An experiment answers one question with a committed plan (configs × seeds). Dash
reconciles that plan with what actually ran and compares one effective curve per
seed. Needs a project whose `GET .../status` lists the `experiments` capability.

## Tested environment

The workflow was checked end to end with **Python 3.13.14, `dreamlake` 0.51.0 and
`params-proto` 3.3.0**.

On Python 3.14.5 with `params-proto` 3.3.0, the template's grid generator
(`python ppo_lr_generate.py`) fails with
`TypeError: cannot pickle 'itertools.product' object`, raised inside params-proto's
`Sweep(...).list`. This failure occurs in the template generator's params-proto
dependency. Use Python 3.13 for this template:

```sh
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install "dreamlake==0.51.0" "params-proto==3.3.0"
```

The SDK uses your saved `dl login`. The project must already exist; the workflow
commands do not create it. Create it in the app or with
`dl create project <name> --namespace <ns>` (`--slug <project>` sets its URL slug;
without it the slug is derived from the name).

## Start from the template

The Python SDK ships the template and a small command line. There is no `dl`
command for this workflow: planning and launching are Python (params-proto v3),
so the SDK owns them.

```sh
python -m dreamlake.experiments.workflow init my-sweep    # generator, plan, launcher, analysis.py, plain train.py/play.py, README.md, .dashrc
cd my-sweep
python ppo_lr_generate.py                                 # writes the plan: 9 rows (3 configs × 3 seeds) -> grids/lr.jsonl
```

Publish, launch, and check with the template's launcher. Before running, replace
`<ns>` with your namespace, `<project>` with the existing project's slug, and
`<folder>` with the experiment folder to create in it (for example `ppo/lr-sweep`):

```sh
python ppo_experiment_lr_launch.py --launch.namespace <ns> --launch.project <project> --launch.folder <folder> --launch.publish
python ppo_experiment_lr_launch.py --launch.namespace <ns> --launch.project <project> --launch.folder <folder>
python ppo_experiment_lr_launch.py --launch.namespace <ns> --launch.project <project> --launch.folder <folder>
python -m dreamlake.experiments.workflow status --namespace <ns> --project <project> --folder <folder>
```

| After | The experiment shows |
| --- | --- |
| `--launch.publish` | The manifest, README and plan only — nothing is launched: 9 planned, 9 not started. |
| First launch | 9 completed, 9 attempts. Evaluations: 6 Pass, 3 Fail — lr 1e-4 completes training but fails its `Mean play return` check. |
| The same launch again | Each run starts a fresh attempt: 18 attempts, still 9 logical runs, 9 superseded, and still 3 seeds per config in every comparison. |
| `status` | `"complete": true`, completed 9, attempts 18, superseded 9, no diagnostics. |

`python -m dreamlake.experiments.workflow export --namespace <ns> --project <project> --folder <folder>`
(same placeholders) writes `results/runs.jsonl`, one line per attempt.

Work in the order **generate → commit → launch (train, then evaluate) → review → analyse**:

- `*_generate.py` defines the combinations with params-proto v3 and writes
  `grids/<name>.jsonl`. Each line is `{slug, config, seed, params}`; the slug comes
  only from the configuration and seed. Commit it: it is the plan.
- `train.py` is plain training code that writes ordinary files with an absolute
  `step` column. It never imports DreamLake.
- `*_experiment_*_launch.py` selects slugs from the grid, runs training and records
  each attempt with the exact command and working directory it ran.
- After training **completes**, the launcher's evaluate step
  runs plain `play.py` on the final checkpoint and records its named checks on that
  attempt (`--launch.skip-eval` skips it; `--launch.eval-only --launch.attempt <id>`
  evaluates an existing attempt again). A failed check or a crashed `play.py` never
  changes the training run's status.
- `analysis.py` reads the server's contract and series,
  judges the experiment's own criteria, writes `analysis/out/<id>/` (report.md, SVG
  figures, report.json) and publishes it. Exit status: 0 every criterion passed, 1 a
  criterion failed or could not be judged, 2 the analysis itself failed. The template
  needs nothing beyond `params-proto`; its data is synthetic.

## In Dash

The experiment is a run folder whose metadata carries `experiment` (its manifest:
question, metrics, step column, full budget, baseline, changed and fixed
parameters, seed key, media, Memo link). Its identity is the folder's id, so
renaming or moving the folder keeps every link (`?folder=<id>`). The Conclusion
section of `README.md` in the folder is shown above the primary result; the Memo
holds the full analysis. Ordinary folders are unchanged.

Each attempt is an ordinary run in that folder:

- **Fresh** starts a new attempt; older attempts keep their data. The newest fresh
  attempt, even a failed one, is the one compared.
- **Resume** continues an explicit parent attempt from a checkpoint at an absolute
  step. The checkpoint step belongs to the parent; the resume owns the steps after it.
- **Reconnect** reopens the same attempt by id with its stored kind, parent and
  step. Only the first request creates the run; a request with a different config,
  seed or parameters is refused. Re-uploading files appends only what is missing,
  and does not change the run's status unless asked to.

A retry never adds a seed. A run whose parameters differ from the plan, or a plan
with two rows for one config × seed, is **Invalid**: listed with the reason, never
averaged. If any run or plan line cannot be read, every run is **Unknown**, counts
that depend on it are not shown as numbers, and no comparison is drawn until the
records are fixed.

The full-budget table uses each completed run's value **logged at exactly the
budget step** (no interpolation, never a later step); runs without that value are
listed with the reason. It is separate from the learning curves, which show the
number of seeds behind every step.

Manifest media (`media: [{label, run, file}]`) appear with the primary result as
Uploaded, Planned (the run has not finished), Missing, or Unknown.

## Evaluation and analysis

**Evaluation** is one attempt's own record of named checks on one checkpoint: the
checkpoint's absolute step and path (and its SHA-256 when recorded; a path alone is
shown as unverified), the evaluation config, each check's result (pass, fail or
inconclusive), value, threshold and reason, and its evidence files under
`/eval/<id>/` on that run. Only the active chain's **last** attempt counts. A run
shows **Pass**, **Fail** (some check failed), **Inconclusive** (a check could not be
judged, or none was recorded), **Eval error** (the evaluation could not run),
**Pending** or **Evaluating** (as recorded; Refresh reads again), **Unreadable**,
**Stale** (only an earlier or superseded attempt was evaluated) or **Not recorded**.
Execution and evaluation are separate columns in Runs.

**Analysis** is `analysis/report.json` in the experiment folder, with its report and
figures in `analysis/<id>/`; earlier generations stay. When it exists, the Overview
shows its assessment first and the README moves below it. The outcome is derived from
the author's criteria — **Criteria met**, **Criteria not met** or **Inconclusive** —
and the author's statement is shown as written; a failed analysis shows **Analysis
failed**, never a verdict.

A report records the server's inputs fingerprint it read. It is **Stale**, with each
change named, when any of these differ: the selected attempts and chains, run states,
the plan and manifest, an evaluation record's content, or a selected run's metric
data (each metric's id, row count and last write; a metric's description or tags
edit counts too). The fingerprint covers what the analysis can read through these
APIs; files the analysis read elsewhere, run files other than evaluation records, and
the analysis code itself are not observed — the report's command, commit and dirty or
untracked state are recorded as evidence, not guaranteed reproduction. A report whose
fingerprint was edited or truncated, or whose files are missing, is Unreadable.

## API

- `GET /native-experiments/ns/:namespace/projects/:project/experiments/:folderId`
  returns the reconciled contract: logical runs with state, active chain,
  `(from, to]` segments on the step column, attempts and their roles, parameter
  drift, counts, media and diagnostics.
- `POST .../experiments/:folderId/series` with `{ "metric": 0, "configs": [...], "bins": 200 }`
  returns per-config mean, s.d., min, max and seed count per step, each seed's
  composed curve, and the full-budget endpoint; `409 EXPERIMENT_INCOMPLETE` while
  the contract is incomplete.
- `PUT .../run-paths/<path>` accepts `createOnly: true`: only the creating request
  writes the body; others receive the stored run unchanged.

- `GET .../experiments/:folderId?inputs=1` also returns `inputs`, the fingerprint an
  analysis copies verbatim into its report. Each run carries `evaluation`
  (`state`, `current`, `earlier`); the contract carries `evaluations` (counts by
  state, null when incomplete) and, with a report, `analysis` (`state`: current,
  stale, error or unreadable; `outcome`; `changes`; file ids).
- `PUT .../experiments/:folderId/attempts/:runId/evaluation` with
  `{ "evaluation": {...}, "replaces"?: "<id>" }` sets only that attempt's evaluation
  (strict schema, at most 16 KiB); the attempt's identity and other metadata are kept.
  The same record again is a no-op; a finished evaluation id is final
  (`409 EVALUATION_FINAL`); a new id replaces the current one only with `replaces`
  (`409 EVALUATION_CONFLICT`); another attempt's run is refused. Needs write access:
  a login, or on a worker a write session bound to that run (or unbound). A managed
  job session cannot call it: a job's own run is not an experiment attempt. A later
  whole-metadata `PATCH` of the run can still replace the record; a malformed one then
  shows as Unreadable.

The `GET` and `series` routes are reads; anonymous on public projects.
