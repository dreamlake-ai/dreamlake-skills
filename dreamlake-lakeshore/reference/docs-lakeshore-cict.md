<!-- generated from https://docs.dreamlake.ai/lakeshore/cict.md at 0.1.158 3f90c7b1; do not edit -->

# CI/CT with GitHub Actions

Continuous testing for robotics usually needs GPUs, simulator assets and
minutes of compute per change. DreamLake lets a GitHub Actions job run on your
DreamLake machines by changing one line of the workflow:

```yaml
runs-on: dreamlake-gpu-rtx5090   # a DreamLake GPU, or your own pool's label
```

The job can run on either of two kinds of machines:

- **DreamLake GPU**: machines DreamLake provides. Pick one by its label from
  the machine catalog; there is nothing to register or configure.
- **Your own machines**: a runner pool on a Slurm cluster your namespace
  registered, labelled `dreamlake-<pool>`.

GitHub keeps orchestrating the workflow: checkout, steps, logs, the pass/fail
check on the pull request. DreamLake decides which machine takes the job,
starts a single-use runner there, and writes the evidence the job declares
(results, replays, metrics) to a Source, where the CI/CT page and the Source
viewers show it.

This is CI/CT **channel A** (triggered by GitHub). Submitting suites from
DreamLake itself, without GitHub, is planned separately.

## How a job runs

1. A pull request triggers a workflow job with a DreamLake label. GitHub queues
   it and sends a `workflow_job` webhook to DreamLake through the DreamLake CI/CT
   GitHub App.
2. DreamLake verifies the webhook, finds the namespace the App installation is
   bound to, and picks the namespace's **runner pool** whose labels cover the
   job's `runs-on`, or else the **DreamLake GPU** machine type it names. The
   job is recorded as a CI/CT run. A DreamLake GPU job waits in DreamLake's
   queue until the namespace and the machine type have a free slot.
3. DreamLake asks GitHub for a just-in-time runner configuration, valid for one
   job, and submits a Slurm allocation through the pool's provider. The
   allocation runs a small bootstrap: it downloads the pinned GitHub Actions
   runner once into the pool cache (checksum-verified), unpacks it into
   node-local scratch and starts it with that configuration.
4. The runner takes the job and runs the workflow steps on the GPU node. It
   exits after this one job and its scratch directory is removed.
5. When GitHub reports the job completed, DreamLake reads the run's evidence
   manifest and copies each declared file from the cluster straight into the
   pool's evidence Source. Files never pass through the DreamLake server.

Nothing is installed or kept running on the cluster for GitHub, and no GitHub
or DreamLake credential is stored in the repository.

## Set up (namespace admin, once)

You need the namespace's execution-admin permission.

**1. Connect GitHub.** In the CI/CT page, open **Setup** and choose
**Connect GitHub** (or run the command below). Open the install link, install the App on your
organization or account and select the repositories that may use DreamLake
machines. Open the link in a browser signed in to DreamLake as the same user,
within 15 minutes. GitHub returns to the DreamLake setup page, which binds the
installation to the namespace.

```bash
dl cict github connect my-team
dl cict github installations my-team      # after the browser step
```

Any GitHub organization or personal account can install the App. An
installation is bound to one namespace.

**2. Choose machines.** Use DreamLake GPU, your own machines, or both.

*DreamLake GPU.* The DreamLake team enables it for a namespace. Setup then
shows it as ready: choose **Start using**. That picks or creates the
`cict-evidence` Source, where runs save their results, and records you as the
person who authorizes those writes. Starting needs the namespace admin role,
because it may create a Source. After that, copy a label from the machine
catalog in Setup. See [DreamLake GPU](#dreamlake-gpu) for limits and usage.

*Your own machines.* You need a [Slurm provider](https://docs.dreamlake.ai/lakeshore/providers/slurm)
registered in the namespace with a host bound to it, and a launch layer that
sets the partition, GPU type, memory, time limit and excluded nodes. Create a
runner pool in Setup (**Your own machines → New pool**) or with the CLI. The
pool name becomes the default label `dreamlake-<name>`. Setup only offers
providers that can start runners and Sources you can edit.

```bash
dl cict pools create my-team --name bos14-gpu \
  --provider <slurm-provider-id> \
  --evidence-source <source-id> \
  --env DREAMLAKE_ROBOT_ASSETS_CACHE=/work/shared/assets
```

`--env` adds machine facts every job on the pool sees, such as where a
read-only dataset cache lives on this cluster. Values are visible to anything
running on the pool; never use them for secrets.

A pool can be edited in Setup: its provider, evidence Source and folder, and
environment. Edits apply to the next job; running jobs keep what they started
with. A pool still serving running jobs, or still collecting their evidence,
cannot be deleted until they finish.

The same steps are available in [Python](https://py.dreamlake.ai/cict)
(`client.cict`) and TypeScript (`dl.cict(namespace)` from
`@dreamlake/dreamlake-cli/api`). See the [CLI reference](https://cli.dreamlake.ai/cict)
for every flag.

## DreamLake GPU

| Label | GPU | CPU | Memory | Time limit |
| --- | --- | --- | --- | --- |
| `dreamlake-gpu-rtx5090` | 1 × RTX 5090 | 8 | 32 GB | 2 h |

- **Concurrency.** Each namespace runs a limited number of DreamLake GPU jobs
  at once (2 by default), and each machine type has a limit across all
  namespaces. Further jobs wait in DreamLake's queue, oldest first. GitHub
  shows them as queued; the run page shows their place in line.
- **Results.** Evidence goes to your namespace's Source (`cict-evidence` unless
  you choose another in Setup), under the same folder layout as pools.
- **Cache.** `DREAMLAKE_CACHE_DIR` is private to your namespace; other
  namespaces cannot read or change it.
- **Usage.** Setup shows this month's GPU time, from each job's start to its
  end, by repository and workflow.
- **Availability.** DreamLake GPU is enabled per namespace by the DreamLake
  team. A paused namespace starts no new jobs; running ones finish.

## Write the workflow (developers)

```yaml
name: cict
on: [pull_request, workflow_dispatch]
jobs:
  sim-suite:
    runs-on: dreamlake-bos14-gpu
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Install uv, cached on the cluster
        run: |
          command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
          echo "UV_CACHE_DIR=$DREAMLAKE_CACHE_DIR/uv" >> "$GITHUB_ENV"
      - run: uv sync --frozen
      - run: uv run python ci/run_suite.py --out "$DREAMLAKE_RUN_DIR"
```

The job's exit code decides the GitHub check. A suite usually exits `0` when
every check passed, `1` when a check failed and `2` when it could not run, and
writes evidence in every case.

### Environment on the runner

| Variable | Meaning |
| --- | --- |
| `DREAMLAKE_RUN_DIR` | Absolute directory for this run's evidence. It outlives the runner. |
| `DREAMLAKE_RESULTS_PATH` | `$DREAMLAKE_RUN_DIR/results.json`, the evidence manifest. |
| `DREAMLAKE_METRICS_PATH` | `$DREAMLAKE_RUN_DIR/metrics.json`, optional headline metrics. |
| `DREAMLAKE_CACHE_DIR` | Persistent cache shared by the pool's runs: package caches, downloaded models. |
| `DREAMLAKE_RUN_URL` | This run's page in DreamLake, for links in the step summary. |
| Pool `env` | Whatever the pool admin set, such as asset cache paths. |

Use `DREAMLAKE_CACHE_DIR` for anything worth keeping between runs; the first
environment install is slow and later runs reuse it.

## Declare evidence

Only files listed in the manifest are copied to the Source. Write them under
`$DREAMLAKE_RUN_DIR`, then write the manifest last:

```json
[".dreamrc", "result.json", "metrics.json", "replays/walk_01/episode.json", "replays/walk_01/frames.parquet"]
```

- `results.json` is a JSON array of paths relative to `$DREAMLAKE_RUN_DIR`.
  No absolute paths, `..` segments or empty segments; dotfiles such as
  `.dreamrc` are allowed. At most 1024 files, each at most 2 GiB.
- `metrics.json` (optional) is an array of points,
  `[{"step": 0, "values": {"pass_rate": 1.0}}]`: at most 128 points of at most
  16 finite numbers each.
- `result.json` is the suite verdict the CI/CT page shows: a `verdict`,
  `passed`/`total` counts and a `cases` array with per-case checks.
- `.dreamrc` makes the run folder open as a visualization in the Source viewer,
  for example a MuJoCo replay with a timeline and line charts. A `.dreamrc`
  in a run sub-folder applies to that folder.

Each run's files land at
`<prefix or ci>/<owner>/<repo>/<YYYY-MM-DD>/<HHMMSS>_<job>_<sha7>_<jobId>/`
in the evidence Source, so people browsing the Source find runs by repository
and date.

## See results

Every finished run is compared case by case with its **baseline**: the latest
earlier finished run of the same repository, workflow and job on the
repository's default branch whose evidence was written. A case that passed in
the baseline and fails now is a regression; the reverse is a fix. Add
`push: branches: [main]` (your default branch) to the workflow's triggers so
baselines exist.

- **GitHub:** a `DreamLake CI/CT` check on the commit, opened when the runner
  starts and completed with `N/M cases passed · K regressions vs main@sha`;
  its Details link opens the run in DreamLake. The job log and step summary
  are there too; `DREAMLAKE_RUN_URL` holds the run's DreamLake link for the
  summary.
- **CI/CT page** (`/<namespace>/cict`): runs grouped by repository with their
  regressions against the baseline; open a run for its progress, the case
  comparison (changed cases first, each check's observed values in both runs)
  and its evidence. **Setup** on the same page connects GitHub and manages
  runner pools.
- **Source:** the run folder, with replays and charts from its `.dreamrc`.
- **CLI and SDKs:** `dl cict runs list my-team` and
  `dl cict runs show my-team/<run-id> --result`.

## Report metrics

Two ways are supported by design:

1. **Write files, DreamLake copies them** (available): declare `metrics.json`
   and any other files in the manifest, as above. Nothing in the job needs a
   DreamLake credential.
2. **Log directly through the logging API** (recommended, not yet available
   for CI jobs): the test logs metrics and files to a DreamLake Experiment
   while it runs. It needs a short-lived workload credential that GitHub's OIDC
   token is exchanged for; until that exchange ships, use files.

## Limits and safety

- Only private repositories are routed unless the server explicitly allows
  public ones. A pull request's code runs on your machines, so route only
  repositories whose contributors you trust.
- Runners currently run as the provider association's Unix user, the same user
  as the cluster's Nymph daemon, so repository code can read that machine
  identity. Use pools only for trusted repositories until runners are isolated.
- Slurm allocations for a pool run with its creator's identity, until
  service-account grants replace this.
- DreamLake GPU runs every namespace's jobs on a shared cluster under one
  service identity. Until runners are isolated per job, it is enabled only for
  trusted namespaces.
- Only Slurm pools and DreamLake GPU start runners. Runner nodes are x86_64 Linux.

## Troubleshooting

| What you see | What it means |
| --- | --- |
| The job waits in GitHub for a runner | Check the run's routing with `dl cict runs list`. |
| Routing `unbound` | The App installation is not bound to a namespace. Run `dl cict github connect`. |
| Routing `unmatched` | No pool or DreamLake GPU label covers every `runs-on` label. Check the machine catalog and `dl cict pools list`. |
| Waiting for a GPU | The namespace or the machine type is at its limit; the job starts when a slot frees. |
| Not started: DreamLake GPU not enabled | Ask the DreamLake team to enable it for the namespace. |
| Not started: DreamLake GPU not set up | Open Setup and choose **Start using**. |
| Not started: DreamLake GPU paused | New jobs are paused for the namespace; contact the DreamLake team. |
| Routing `rejected` | A public repository or an inactive installation. |
| Runner `failed` | The allocation could not be submitted; `dl cict runs show` gives the error code. |
| Evidence `failed` | The manifest was missing, unreadable or listed an invalid path. |
| Evidence `pending` for long | The runner may still be flushing files, or the cluster connection blipped; DreamLake retries for a few minutes. |

## API

| Method | Path | Permission |
| --- | --- | --- |
| POST | `/namespaces/:ns/github/installations/start` | execution admin |
| GET | `/namespaces/:ns/github/installations` | read |
| GET / POST | `/namespaces/:ns/github/runner-pools` | read / execution admin |
| PATCH / DELETE | `/namespaces/:ns/github/runner-pools/:poolId` | execution admin (DELETE answers `409 runner_pool_busy` while jobs still need it) |
| GET | `/namespaces/:ns/github/runner-targets` | read: Slurm providers and whether a pool can start runners on each |
| GET | `/namespaces/:ns/cict/platform` | read: DreamLake GPU catalog, access, occupancy, month GPU time |
| POST | `/namespaces/:ns/cict/platform/activate` | execution admin + namespace admin: start using DreamLake GPU |
| PATCH | `/namespaces/:ns/cict/platform` | execution admin: change the evidence Source |
| GET | `/namespaces/:ns/cict/usage?month=YYYY-MM` | read |
| GET | `/namespaces/:ns/github/jobs?limit=` | read |
| GET | `/namespaces/:ns/cict/runs?limit=` | read |
| GET | `/namespaces/:ns/cict/runs/:run` | read |
| GET | `/namespaces/:ns/cict/runs/:run/comparison` | read (and Source use) |

The built-in agent can call these through its resource API tools. Creating or
deleting a pool is a control operation. Completing a GitHub binding is not
available to the agent: it needs the user's browser on GitHub, so the agent
hands the user the install link.
