<!-- generated from https://docs.dreamlake.ai/ml-dash/examples/rl-logging.md at 0.1.144 afeb8337; do not edit -->

# RL logging on DreamLake

Record a complete, synthetic PPO / HalfCheetah experiment with the **`dreamlake`**
Python package and your existing DreamLake login. This example does not train a
policy or require MuJoCo, PyTorch, a GPU or a worker. Its rewards, losses and
hardware measurements marked `mock` are simulated; logger timing is observed.

This is the DreamLake-native path. The other examples in this section use the
standalone `ml_dash` package and dash.ml; those are separate backends.

## Run the example

Use an existing namespace in which you may create a project, or an existing
project in which you may write. Install and [log in with the DreamLake CLI](https://cli.dreamlake.ai/installation):

```bash
dl login
```

Download both files into one directory:

```bash
curl -fLO https://docs.dreamlake.ai/examples/rl-logging/mock_rl_experiment.py
curl -fLO https://docs.dreamlake.ai/examples/rl-logging/rl-dashboard.dashrc
uv run --python 3.12 mock_rl_experiment.py --project my-workspace/rl-demo
```

Replace `my-workspace/rl-demo` with your namespace and project. The script pins
`dreamlake[video]==0.46.2` in its inline dependency metadata; `uv` installs those
dependencies. Alternatively, install that package and run the script with
Python 3.12. The [Python source](https://docs.dreamlake.ai/examples/rl-logging/mock_rl_experiment.py) and
[dashboard file](https://docs.dreamlake.ai/examples/rl-logging/rl-dashboard.dashrc) are the maintained
example; the script uploads both its source and the dashboard to the run.

The default creates a unique run name. Use `--seed` for another trial and
`--updates` to change its length. `--run` chooses an explicit name; opening the
same prefix again reuses that run and can append more data, rather than giving
you an independent trial.

For a local-only rehearsal:

```bash
uv run --python 3.12 mock_rl_experiment.py --project demo/rl-demo --updates 3 --interval 0 --local-root ./rl-local
```

Local mode does not create a remote project. The script retains production
runs for inspection; remove disposable test runs separately when finished.

## Existing login and project creation

The high-level remote entry used by the script is:

```python
from dreamlake import Experiment

with Experiment(
    prefix="my-workspace/rl-demo/ppo-seed42",
    url="https://api.dreamlake.ai",
    root=None,
    tags=["rl", "ppo", "mock"],
    metadata={"mock": True},
) as exp:
    exp.params.set(algorithm="PPO", seed=42)
    exp.metrics("train").log(global_step=8192, policy_loss=-0.1, value_loss=60.0)
    exp.logs.info("PPO update recorded")
```

With this remote `Experiment` entry, a project reported missing is created as
**private**, using the signed-in person's namespace permissions. An existing
project is reused. The SDK does not create a missing namespace or bypass an
access refusal. `root=None` selects remote-only storage; omitting `url` instead
selects local storage by default.

If you construct `NativeConnection.from_login(...)` yourself, opt into project
creation with `auto_create_project=True`; that lower-level option defaults to
false. An existing platform job has its own pinned run and broker connection:
see [workload credentials](docs-ml-dash-reference-native-workload-credentials.md)
instead of replacing it with this standalone login example.

## What gets recorded

| Data              | Contents at the default 60 updates                                                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parameters        | PPO hyperparameters, seed, environment dimensions, policy architecture, optimizer and evaluation settings                                                      |
| `rollout` metrics | 60 rows of episode returns, episode length and reward components                                                                                               |
| `train` metrics   | 60 rows of policy/value loss, entropy, KL, clipping, learning rate, gradient norm and action standard deviation                                                |
| `eval` metrics    | 12 rows of evaluation returns and a custom success rate, defined as return at least 4000                                                                       |
| `system` metrics  | 60 rows of logger timing and explicitly simulated environment/GPU measurements                                                                                 |
| Logs              | Start, evaluation, a labelled mock warning and completion messages                                                                                             |
| Tracks            | `rollout/state` and `rollout/action`, 60 timestamped entries each, including observations, joint state, actions and termination flags                          |
| Files             | Config, runtime information, source, three mock checkpoint JSON files, best-checkpoint selection, summary JSON, evaluation CSV, README, PNG, MP4 and `.dashrc` |

A metric **group** contains multiple fields: `train` is one group, while
`train.policy_loss` and `train.value_loss` are different chart keys. These four
groups contain 192 rows and 28 value fields, not four curves. The two Tracks
are separate timestamped streams, not two metrics.

Checkpoints are labelled mock JSON and are not loadable policy weights. The
preview is a synthetic animation, not a MuJoCo rendering. The best checkpoint
uses file **tags**; tags and canonical Bindr membership are different things.

## Dashboard configuration

The script writes `rl-dashboard.dashrc` into the run root as **`.dashrc`**. It
requests one chart per value field and includes the uploaded image and video.
Each metric group logs its own `global_step`, so each chart uses that group's
explicit x key. Update counters and timestamps are axes/bookkeeping, not extra
value charts.

The supplied file contains 28 line charts, one image grid and one video grid.
The header keeps two evaluation summaries; those two numbers do not describe
how many metrics were stored. See [per-run dashboard configuration](docs-ml-dash-reference-native-charts.md#per-run-dashboard-configuration)
for the format and the difference from automatic selection.

For an existing run, upload the configuration under the exact name `.dashrc`:

```bash
dl experiments runs files upload RUN_ID ./rl-dashboard.dashrc --name .dashrc --prefix / --content-type text/plain --namespace my-workspace --project rl-demo
```

Use CLI 0.118.1 or newer for native disk-backed file uploads. Inspect an existing
run configuration before replacing it; do not create several competing
`.dashrc` files. After an out-of-page write, refresh the run page so it reloads
the file list. CLI operations are documented in the [Experiments reference](https://cli.dreamlake.ai/experiments).

## SDK file Bindr limitation

SDK 0.46.0 was observed to ignore `bindrs=[...]` on native high-level file
uploads; the same missing forwarding remains in the inspected 0.46.2 source.
Run-level Bindrs work. This example therefore uses file tags rather than
claiming those uploads create file membership.

When canonical membership is needed, flush the upload, obtain the stored file
ID, and use the explicit project API:

```python
# project is an authenticated client's experiments.project(namespace, project).
project.bindrs.attach("file", file_id, name="best-policy", run_id=run_id)
membership = project.bindrs.list("file", file_id, run_id=run_id)
```

Read the membership back. An explicit attachment repairs that file's data; it
does not mean the high-level SDK forwarding defect has been fixed.
