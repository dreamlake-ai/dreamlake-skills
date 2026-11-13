<!-- generated from https://docs.dreamlake.ai/ml-dash/guides/experiment-workflow.md at 0.1.158 e3e61780; do not edit -->

# Experiment workflow

An experiment answers one question with a committed plan (configs × seeds). Dash
reconciles that plan with what actually ran and compares one effective curve per
seed. Needs a project whose `GET .../status` lists the `experiments` capability.

## Tested environment

The workflow was checked end to end with **Python 3.13.14, `dreamlake` 0.50.1 and
`params-proto` 3.3.0**.

On Python 3.14.5 with `params-proto` 3.3.0, the template's grid generator
(`python ppo_lr_generate.py`) fails with
`TypeError: cannot pickle 'itertools.product' object`, raised inside params-proto's
`Sweep(...).list`. This failure occurs in the template generator's params-proto
dependency. Use Python 3.13 for this template:

```sh
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install "dreamlake==0.50.1" "params-proto==3.3.0"
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
python -m dreamlake.experiments.workflow init my-sweep    # generator, plain train.py, launcher, README.md, .dashrc
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
| First launch | 9 completed, 9 attempts. |
| The same launch again | Each run starts a fresh attempt: 18 attempts, still 9 logical runs, 9 superseded, and still 3 seeds per config in every comparison. |
| `status` | `"complete": true`, completed 9, attempts 18, superseded 9, no diagnostics. |

`python -m dreamlake.experiments.workflow export --namespace <ns> --project <project> --folder <folder>`
(same placeholders) writes `results/runs.jsonl`, one line per attempt.

Work in the order **generate → commit → launch → review**:

- `*_generate.py` defines the combinations with params-proto v3 and writes
  `grids/<name>.jsonl`. Each line is `{slug, config, seed, params}`; the slug comes
  only from the configuration and seed. Commit it: it is the plan.
- `train.py` is plain training code that writes ordinary files with an absolute
  `step` column. It never imports DreamLake.
- `*_experiment_*_launch.py` selects slugs from the grid, runs training and records
  each attempt with the exact command and working directory it ran.

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

Both experiment routes are reads; anonymous on public projects.
