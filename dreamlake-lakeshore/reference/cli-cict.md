<!-- generated from https://cli.dreamlake.ai/cict.md at 0.125.0 b8ca5e1; do not edit -->

# CI/CT with GitHub Actions

`dl cict` manages CI/CT channel A: GitHub Actions jobs that ask for a
DreamLake label (`runs-on: dreamlake-<pool>`) run on DreamLake machines
through single-use runners, and their declared evidence is written to a
Source. How the flow works, the workflow contract and the evidence files are
described in the product guide,
[CI/CT with GitHub Actions](https://docs.dreamlake.ai/lakeshore/cict).

These commands need a server with the GitHub runner integration enabled;
otherwise every command returns HTTP 404 `github_runners_disabled`. The same
operations are available in TypeScript as `dl.cict(namespace)` and in Python
as `client.cict`.

## Connect GitHub

```bash cli-help="cict github"
dl cict github connect my-team
dl cict github installations my-team
```

```bash cli-help="cict github connect"
dl cict github connect my-team
```

`connect` prints a GitHub App install link. Open it within 15 minutes in a
browser signed in to DreamLake as the same user, install the App on an
organization or account and select repositories. GitHub returns to the
DreamLake setup page, which binds the installation to the namespace after
checking that your GitHub user can access it. Starting the binding requires
the namespace's execution-admin permission.

```bash cli-help="cict github installations"
dl cict github installations my-team --json
```

An installation is bound to one namespace. Uninstalling or suspending the App
on GitHub deletes or suspends the binding.

## Runner pools

A pool maps `runs-on` labels to a Slurm provider and, optionally, to a Source
for evidence. Jobs whose labels match no pool are recorded as `unmatched` and
get no runner.

```bash cli-help="cict pools"
dl cict pools create my-team --name bos14-gpu \
  --provider 0123456789abcdef01234567 \
  --evidence-source 1123456789abcdef01234567
dl cict pools list my-team
dl cict pools delete my-team/2123456789abcdef01234567
```

```bash cli-help="cict pools create"
dl cict pools create my-team --name bos14-gpu \
  --provider 0123456789abcdef01234567 \
  --evidence-source 1123456789abcdef01234567 --evidence-prefix ci \
  --env DREAMLAKE_ROBOT_ASSETS_CACHE=/work/assets
```

- `--name` is lowercase letters, digits and hyphens. Without `--label`, the
  pool serves the single label `dreamlake-<name>`. Each `--label` must be
  `dreamlake` or start with `dreamlake-`; `self-hosted`, `linux` and `x64`
  are implicit. When several pools match a job, the most specific wins.
- `--provider` is a Slurm provider in the namespace on which you have your own
  association. Runners start as you (the pool creator) until service-account
  grants replace this.
- `--evidence-source` receives each run's evidence under
  `<prefix or ci>/<owner>/<repo>/<YYYY-MM-DD>/<HHMMSS>_<job>_<sha7>_<jobId>`.
- `--env NAME=value` adds a machine fact every job sees, such as a cache path
  on the cluster. Values are visible to anything running on the pool; never
  pass secrets. Names starting with `DREAMLAKE_GITHUB`, `DREAMLAKE_RUN`,
  `DREAMLAKE_RESULTS`, `DREAMLAKE_METRICS`, `DREAMLAKE_JOB`,
  `DREAMLAKE_CACHE`, `GITHUB_`, `RUNNER_` or `SLURM_` are refused. At most 32.

```bash cli-help="cict pools list"
dl cict pools list my-team --json
```

```bash cli-help="cict pools delete"
dl cict pools delete my-team/2123456789abcdef01234567
```

Deleting is refused with `runner_pool_busy` while the pool still serves
running jobs or collects their evidence; delete it after they finish.

```bash cli-help="cict pools update"
dl cict pools update my-team/2123456789abcdef01234567 --provider 0123456789abcdef01234567
dl cict pools update my-team/2123456789abcdef01234567 --no-evidence --clear-env
```

`update` changes a pool for the next job; running jobs keep the provider,
evidence location and environment they started with. `--env` replaces every
variable. The name cannot change.

```bash cli-help="cict pools targets"
dl cict pools targets my-team
```

`targets` lists the namespace's Slurm providers and whether a pool can start
runners on each: `usable`, or the reason it cannot (`no_association`: no host
is bound to it; `no_launch_layer`: no GPU, memory and time settings;
`legacy_provider`).

## Runs

A run is one GitHub Actions job that asked for a DreamLake label, joined with
the runner that served it. Its ID is `<installationId>-<jobId>`.

```bash cli-help="cict runs"
dl cict runs list my-team --limit 20
dl cict runs show my-team/91234567-48812345678 --result
```

```bash cli-help="cict runs list"
dl cict runs list my-team --limit 20 --json
```

Each line shows the run ID, status or conclusion, repository, job, commit,
routing (pool name, `unmatched`, `unbound` or `rejected:<reason>`) and the
evidence state (`pending`, `written`, `failed` or `none`).

```bash cli-help="cict runs show"
dl cict runs show my-team/91234567-48812345678
dl cict runs show my-team/91234567-48812345678 --result --json
```

`show` adds the GitHub job link, the runner and its Slurm job, a runner error
code when start failed, and the evidence location. `--result` also reads the
run's `result.json` from the evidence Source; it is `null` when the run wrote
none or evidence is not written yet.

```bash cli-help="cict runs compare"
dl cict runs compare my-team/91234567-48812345678
dl cict runs compare my-team/91234567-48812345678 --all --json
```

`compare` lists the cases that changed against the baseline: the latest
earlier run of the same repository, workflow and job on the default branch
whose evidence was written. Each case is `regressed`, `fixed`,
`still_failing`, `unchanged`, `added` or `removed`, with the change in its
score (such as normalized return) when both runs report one.

## DreamLake GPU

DreamLake GPU runs jobs on machines DreamLake provides, chosen by `runs-on`
label; no pool is needed. The DreamLake team enables it for a namespace.

```bash cli-help="cict platform"
dl cict platform show my-team
dl cict platform start my-team
dl cict usage my-team
```

```bash cli-help="cict platform show"
dl cict platform show my-team --json
```

`show` prints the machine catalog, whether the namespace may use it (not
enabled, enabled but not started, in use, or paused), its concurrency limit,
running and queued jobs, where results go and this month's GPU time.

```bash cli-help="cict platform start"
dl cict platform start my-team
dl cict platform start my-team --source 1123456789abcdef01234567
```

`start` creates the `cict-evidence` Source for results, or uses `--source`,
and records you as the person who authorizes those writes. Creating a Source
needs the namespace admin role.

```bash cli-help="cict platform source"
dl cict platform source my-team --source 1123456789abcdef01234567
```

```bash cli-help="cict usage"
dl cict usage my-team
dl cict usage my-team --month 2026-10 --json
```

`usage` reports DreamLake GPU time, from each job's start to its end, by
repository and workflow.

### Administer DreamLake GPU

These commands are for admins of the platform namespace.

```bash cli-help="cict platform admin"
dl cict platform admin list
dl cict platform admin allow robotics-lab --limit 2
dl cict platform admin pause robotics-lab
```

```bash cli-help="cict platform admin list"
dl cict platform admin list --json
```

```bash cli-help="cict platform admin allow"
dl cict platform admin allow robotics-lab --limit 2
```

`allow` lets a namespace use DreamLake GPU, or resumes a paused one. A
namespace whose admin already started keeps its results Source.

```bash cli-help="cict platform admin pause"
dl cict platform admin pause robotics-lab
```

```bash cli-help="cict platform admin limit"
dl cict platform admin limit robotics-lab 4
```

```bash cli-help="cict platform admin providers"
dl cict platform admin providers
```

`providers` lists the Slurm providers in the platform namespace and what one
job gets on each, read from its launch layer. A provider without a bound host,
a launch layer or a GPU in it cannot back a machine type.

```bash cli-help="cict platform admin machine"
dl cict platform admin machine gpu-rtx5090 --label dreamlake-gpu-rtx5090 \
  --provider 0123456789abcdef01234567 --limit 6 --enable \
  --env DREAMLAKE_ROBOT_ASSETS_CACHE=/work/shared/robot-assets
dl cict platform admin machine gpu-rtx5090 --disable
```

`machine` creates or changes a machine type. A machine type is what one job
gets, not one machine: jobs land on any free node of the provider's partition.
The GPUs, CPUs, memory and time limit come from the provider's launch layer,
so they always match what Slurm allocates; `--limit` caps jobs at once across
all namespaces. Runners start with the provider's association.

## Troubleshooting

| Symptom | Meaning |
| --- | --- |
| routing `unbound` | The repository's App installation is not bound to a namespace; run `dl cict github connect`. |
| routing `unmatched` | No pool or DreamLake GPU label covers every label in `runs-on`; check `dl cict pools list` and `dl cict platform show`. |
| `queued #N` | A DreamLake GPU job waiting for a slot in the namespace or on the machine type. |
| routing `refused:platform_not_activated` | DreamLake GPU is enabled but not started; run `dl cict platform start`. |
| routing `refused:platform_not_allowed` | DreamLake GPU is not enabled for the namespace. |
| routing `rejected:public_repository` | Public repositories are refused unless the server allows them. |
| runner `failed` with `target_not_supported` | The pool targets a host; only Slurm pools start runners today. |
| evidence `failed` | The run declared no readable `results.json`, or a declared path was invalid. See the product guide. |
