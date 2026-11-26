<!-- generated from https://docs.dreamlake.ai/lakeshore/cict.md at 0.1.233 ebffa13ba; do not edit -->

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

This is CI/CT **channel A** (triggered by GitHub). To start a suite when a
container image is pushed to GHCR, Google Artifact Registry or Amazon ECR, see
[Run a suite when an image is pushed](https://docs.dreamlake.ai/lakeshore/cict/registry-triggers).
Submitting suites from DreamLake itself, without GitHub, is planned separately.

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
because it may create a Source. Each run writes with that person's edit right
on the Source: if they leave the namespace or lose it, jobs wait in the queue
and Setup says so until another namespace admin chooses **Re-authorize**.
Then add credit: DreamLake GPU is paid from the namespace's prepaid credit.
A namespace owner opens **Settings → Billing**, sets up billing (one click)
and buys a credit pack ($10, $50 or $100); the credit arrives within a minute.
Billing currently runs on Stripe and Metronome sandboxes: pay with a Stripe
test card such as `4242 4242 4242 4242`, and no real money moves. Without
credit, DreamLake GPU jobs wait in the queue and say why. After that, copy a
label from the machine catalog in Setup. See [DreamLake GPU](#dreamlake-gpu)
for limits, prices and how jobs are charged.

*Your own machines.* Only Slurm clusters are supported. The cluster needs a
login node that can run `sbatch`, a directory shared between it and the compute
nodes, `uv` and Python on the compute nodes, and outbound internet from them
(the runner talks to GitHub). Setup → **Your own machines** lists six steps and
shows which are done:

1. **Enroll the login node** (Compute → **Enroll a Host**): run the shown
   command from a terminal that can SSH to it. Jobs run as the Unix user you
   enroll, with that user's files, quota and priority.
2. **Bind a service account** (the host in Compute → **Service account → Bind
   service account**): the machine's own DreamLake identity. Without it jobs
   run but cannot save evidence; revoking it stops that machine's writes. A
   namespace owner does this.
3. **Register a [Slurm provider](https://docs.dreamlake.ai/lakeshore/providers/slurm)** (Providers →
   **Register**): the cluster name and the partitions jobs may use.
4. **Associate the login node** (the provider → **Hosts → Associate an
   enrolled host**): which enrolled Unix account submits, the partition, the
   shared directory as seen by the login node and by compute nodes, and uv and
   Python on compute nodes.
5. **Set the launch layer** (the provider → **Configuration → Set launch
   layer**): what each job asks for, such as
   `{"partition": "gpu", "gres": "gpu:1", "cpusPerTask": 8, "memGiB": 32, "time": "02:00:00"}`.
   **Check** validates it without launching anything.
6. **Create a runner pool** (Setup → **New pool**) or with the CLI. The pool
   name becomes the default label `dreamlake-<name>`. Setup only offers
   providers that can start runners and Sources you can edit, and warns when
   the provider's machine cannot save evidence.

Another spec on the same cluster (more time, another GPU type) is steps 3–6
again with a different launch layer; another cluster is all six.

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

Each machine type is what **one job** gets, not one machine: jobs land on any
free node of the cluster partition behind it.

Machine labels, limits and prices are deployment configuration. The table below
describes the documented profiles; use Setup’s currently offered catalog for
your namespace before choosing a label. A listed profile does not establish
that it is enabled for your namespace.

| Label | Per job: GPU | CPU | Memory | Time limit | Price |
| --- | --- | --- | --- | --- | --- |
| `dreamlake-gpu-rtx5090` | 1 × RTX 5090 | 8 | 32 GB | 2 h | $1.20 / GPU-hour |
| `dreamlake-gpu-rtx5090-8h` | 1 × RTX 5090 | 8 | 32 GB | 8 h | $1.20 / GPU-hour |
| `dreamlake-gpu-rtxpro6000` | 1 × RTX PRO 6000 | 8 | 32 GB | 2 h | $2.40 / GPU-hour |

- **Concurrency.** Each namespace runs a limited number of DreamLake GPU jobs
  at once (2 by default), and each machine type has a limit across all
  namespaces. Further jobs wait in DreamLake's queue, oldest first. GitHub
  shows them as queued; the run page shows their place in line.
- **Results.** Evidence goes to your namespace's Source (`cict-evidence` unless
  you choose another in Setup), under the same folder layout as pools.
- **Cache.** `DREAMLAKE_CACHE_DIR` (kept on the cluster) and
  `DREAMLAKE_NODE_CACHE_DIR` (kept on the node's own disk) are separate for
  each namespace, so no other namespace's jobs reuse or clear yours. Jobs run
  under one cluster account, so this is a separation by path, not a
  permission boundary: keep secrets out of caches. A node cache that no job is
  using may be removed when the node runs short of disk.
- **Usage.** Setup shows a month's GPU time and what it was charged: by the
  GitHub user who triggered each job, by repository and workflow, and job by
  job with a link to each run. `dl cict usage` prints the same; Settings →
  Billing has the statement.
- **How GPU time is measured.** From the moment Slurm gives the job its node
  until it lets go, times the job's GPUs. Waiting in DreamLake's queue or in
  Slurm's queue is not counted. Right after a job ends its time is an estimate
  from GitHub's job times; within a few minutes Slurm's accounting replaces it.
  A job the infrastructure failed (Slurm `NODE_FAIL` or `BOOT_FAIL`) is not
  priced.
- **Prices.** Each machine type has a price per GPU-hour, in credits (one
  credit = $0.005; the catalog shows dollars). A job keeps the price it ran
  at, so a later price change does not change past jobs. A machine type
  priced at 0 is free.
- **Paying for a job.** Every DreamLake GPU job is paid from the namespace's
  prepaid credit (Settings → Billing). Before Slurm is asked for a node, the
  most the job can cost — its machine type's time limit, on every GPU it
  holds, at its price — is held from the credit (for example $2.40 for a
  2-hour RTX 5090 job). When the job ends, the GPU time Slurm measured is
  charged (capped at the time limit; GitHub's job times if Slurm never
  reports) and the rest is returned. Not charged: a job that never got a node,
  a job cancelled before its runner picked it up (even if Slurm had already
  given the runner a node), and a job the infrastructure failed.
- **Without credit.** A job the namespace cannot pay for — no billing account,
  or less credit than the job holds — waits in DreamLake's queue without
  taking a GPU. Its GitHub check and its run page say why, and it starts
  within a minute of credit being added. Credit is the namespace's balance in
  Metronome, less what running jobs hold.
- **Sandbox.** Billing runs against Stripe and Metronome sandboxes: credit is
  bought with Stripe test cards and no real money moves.
- **Availability.** DreamLake GPU is enabled per namespace by the DreamLake
  team. Until runners are isolated per job (every namespace's jobs currently
  run under one service identity on a shared cluster), it stays an allowlist of
  trusted namespaces, whatever credit a namespace has. A paused namespace
  starts no new jobs; running ones finish.

## Check where a namespace stands

`dl cict status` (or `GET /namespaces/:ns/cict/onboarding`) reports every
step above, whether it is done, and the next one with the page, CLI command
and API call that does it. It is the same for people and agents: an agent can
take a namespace from nothing to running jobs by repeating it and doing
`next`. On DreamLake GPU the last step is **Set up billing and add credit**,
with the credit available. Only these need a person: installing the GitHub App
(in a browser), enabling DreamLake GPU (the DreamLake team), setting up billing
and buying credit (a namespace owner), enrolling a login node (a terminal
with SSH to it; an agent with such a shell can run the command) and binding
its service account (a namespace owner; DreamLake's built-in agent cannot).
`alsoNeeded` lists person-only steps that can happen alongside `next`.
`route` is the path being followed (DreamLake GPU once it is enabled or
nothing else has started, otherwise your own machines); `readyVia` says which
one is ready.

```bash
dl cict status my-team          # ready / next step
dl cict status my-team --json   # every step, with ui, cli and api hints
```

## Write the workflow (developers)

**Start from the template.** [dreamlake-ai/cict-template](https://github.com/dreamlake-ai/cict-template)
has three workflows that run as they are on DreamLake GPU: a GPU check
(PyTorch), a MuJoCo control task with a rendered video, and headless Isaac Sim
with RTX rendering. For a new project choose **Use this template** on GitHub
and create the repository **private**. For an existing one, two changes to a
workflow are enough: the `runs-on` label, and a step that keeps your output
directory as the run's evidence,
[`dreamlake-ai/cict-evidence`](https://github.com/dreamlake-ai/cict-evidence).
Your code needs no DreamLake imports or paths. The template's README covers
headless rendering, large installs and system libraries on these machines.

```yaml
name: cict
on: [pull_request, workflow_dispatch]
jobs:
  sim-suite:
    runs-on: dreamlake-gpu-rtx5090         # or a pool's label
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - run: uv sync --frozen               # uv is on PATH, its cache already set
      - run: uv run python ci/run_suite.py --out outputs
      - uses: dreamlake-ai/cict-evidence@v1 # keep outputs/, pass or fail
        if: always()
        with:
          path: outputs
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
| `DREAMLAKE_CACHE_DIR` | Persistent cache on the cluster, kept between runs (per namespace on DreamLake GPU). |
| `DREAMLAKE_NODE_CACHE_DIR` | Cache on the node's own disk, kept between runs on that node, per namespace: large installs and models. Removed when the node runs short of disk and no job is using it. |
| `DREAMLAKE_RUN_URL` | This run's page in DreamLake, for links in the step summary. |
| Pool `env` | Whatever the pool admin set, such as asset cache paths. |

Set by default, unless the pool or your workflow sets them first:

| Variable | Default |
| --- | --- |
| `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR`, `PIP_CACHE_DIR` | under `DREAMLAKE_CACHE_DIR` |
| `HF_HOME`, `TORCH_HOME` | under `DREAMLAKE_NODE_CACHE_DIR` |
| `MUJOCO_GL`, `PYOPENGL_PLATFORM` | `egl`: nodes have no display |
| `PATH` | includes `uv` (a checksum-verified release) |

So `uv`, `pip`, Hugging Face and PyTorch downloads are paid once and reused
by later runs without any setup in the workflow.

## Declare evidence

The [`dreamlake-ai/cict-evidence`](https://github.com/dreamlake-ai/cict-evidence)
step does this for you from any output directory (with `include`/`exclude`
globs). To do it yourself: only files listed in the manifest are copied to the
Source. Write them under `$DREAMLAKE_RUN_DIR`, then write the manifest last:

```json
[".dreamrc", "metrics.json", "render.png", "replays/walk_01/episode.json", "replays/walk_01/frames.parquet"]
```

- `results.json` is a JSON array of paths relative to `$DREAMLAKE_RUN_DIR`.
  No absolute paths, `..` segments or empty segments; dotfiles such as
  `.dreamrc` are allowed. At most 1024 files, each at most 2 GiB.
- `metrics.json` (optional) is an array of points,
  `[{"step": 0, "values": {"pass_rate": 1.0}}]`: at most 128 points of at most
  16 finite numbers each.
- Any other file is yours: logs your job writes, renders, checkpoints, a
  suite result in whatever format you use. The run page lists them and opens
  each one beside the run.
- `.dreamrc` makes the run folder open as a visualization in the Source viewer,
  for example a MuJoCo replay with a timeline and line charts. A `.dreamrc`
  in a run sub-folder applies to that folder.

Each run's files land at
`<prefix or ci>/<owner>/<repo>/<YYYY-MM-DD>/<HHMMSS>_<job>_<sha7>_<jobId>/`
in the evidence Source, so people browsing the Source find runs by repository
and date.

## See results

CI/CT shows every job the same way, whatever it runs: how it ended, how long
it took, where it ran, what it cost on DreamLake GPU and the files it declared.
It does not read or compare a result format; your job's own steps decide pass
or fail.

- **GitHub:** a `DreamLake CI/CT` check on the commit. A DreamLake GPU job
  that has to wait shows it at once as queued, with why (`Waiting on
  DreamLake: not enough credit`, waiting for a GPU slot, …) and what lets it
  start. The check moves to in progress when the runner starts and completes
  with how the job ended (`Passed on DreamLake · 4m`), where it ran, where its
  evidence is and, on DreamLake GPU, what it cost (rewritten with the final
  charge once Slurm has reported). Its Details link opens the run in
  DreamLake. The job log and step summary are there too; `DREAMLAKE_RUN_URL`
  holds the run's DreamLake link for the summary.
- **CI/CT page** (`/<namespace>/cict`): one row per job, with its status,
  branch and commit, machine, duration, GPU time and cost, who triggered it
  and when; re-runs fold into the job's row. Open a run for its progress, run
  details and evidence; each evidence file opens in a tab beside it. **Setup**
  on the same page connects GitHub and manages runner pools.
- **Run page, GitHub side:** the job's steps with the one that failed, and
  the end of its GitHub log (read from GitHub when you open it, never stored
  by DreamLake; GitHub masks secrets in it), so a failure can be read without
  leaving DreamLake. **Cancel** stops the run's whole GitHub workflow run
  (GitHub cancels every job in it, including jobs waiting in DreamLake's
  queue); it needs `lakeshore:use`.
- **Source:** the run folder, with replays and charts from its `.dreamrc`.
- **CLI and SDKs:** `dl cict runs list my-team` and
  `dl cict runs show my-team/<run-id>`.

## Run a workflow from DreamLake

**Run workflow** on the CI/CT page starts a repository's workflow without a
push or a pull request: pick the repository, the workflow file and the branch,
optionally add inputs, and confirm. It is GitHub's own `workflow_dispatch`,
sent through your bound App installation, so the workflow must declare
`workflow_dispatch:` (and every input you send). Its DreamLake jobs then run,
queue and are billed like any other. Before you confirm, the dialog lists the
workflow's jobs and the DreamLake GPU machine each runs on, with the most each
job holds from the credit while it runs; when `runs-on` comes from an input
(`runs-on: ${{ inputs.machine }}`), it follows the machine chosen in the form.

- Needs `lakeshore:use` in the namespace, the same as registry push triggers.
  Whoever can run a workflow this way can run any branch of any repository the
  installation reaches, with that repository's secrets: grant `lakeshore:use`
  accordingly.
- GitHub shows the run as started by the DreamLake App; the CI/CT page shows
  who asked for it in DreamLake.
- The form shows the inputs the workflow declares under
  `workflow_dispatch.inputs` in the chosen branch's file, with their
  descriptions, defaults and choices, and says when that version of the
  workflow cannot be run by hand. Reading the file needs the App's
  **Contents: read** permission; an installation that has not granted it gets
  free-form `name = value` inputs instead (GitHub refuses names the workflow
  does not declare, and the page shows why). Inputs are sent as text. Never use
  `${{ inputs.… }}` inside `run:`; pass inputs through `env:` and quote them.
- Only private repositories can run DreamLake jobs (unless the server allows
  public ones). At most 10 runs a minute per namespace.
- When GitHub's answer is lost, the run is marked *outcome unknown*: check the
  repository's Actions page before running it again.
- Branches are listed when the App has Contents: read; otherwise type the
  branch name. A GitHub owner grants a new App permission on the
  installation's settings page (GitHub asks them to review it).

CLI: `dl cict dispatch my-team --repo acme/sim --workflow cict.yml --ref main
--input sim_seconds=120`.

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
| Waiting for re-authorization | The person who authorized result writes can no longer edit the Source. A namespace admin chooses **Re-authorize** in Setup (or runs `dl cict platform source`); waiting jobs then start. |
| Waiting: not enough credit | The credit cannot cover what the job holds while it runs (its time limit at its price). A namespace owner adds credit in Settings → Billing; it starts within a minute. |
| Waiting: billing not set up | The namespace has no billing account. A namespace owner sets it up and buys credit in Settings → Billing. |
| Waiting: billing unavailable | DreamLake could not reach Metronome to check the credit; the job starts once it can. |
| Waiting: machine type has no price | The DreamLake team has not priced that machine type yet. |
| Not started: DreamLake GPU not enabled | Ask the DreamLake team to enable it for the namespace. |
| Not started: DreamLake GPU not set up | Open Setup and choose **Start using**. |
| Not started: DreamLake GPU paused | New jobs are paused for the namespace; contact the DreamLake team. |
| Routing `rejected` | A public repository or an inactive installation. |
| Runner `failed` | The allocation could not be submitted; `dl cict runs show` gives the error code. |
| Evidence `failed` | The manifest was missing, unreadable or listed an invalid path. |
| Evidence `pending` for long | The runner may still be flushing files, or the cluster connection blipped. DreamLake persists up to five attempts and resumes interrupted evidence collection after a server restart. |

## API

| Method | Path | Permission |
| --- | --- | --- |
| POST | `/namespaces/:ns/github/installations/start` | execution admin |
| GET | `/namespaces/:ns/github/installations` | read |
| GET / POST | `/namespaces/:ns/github/runner-pools` | read / execution admin |
| PATCH / DELETE | `/namespaces/:ns/github/runner-pools/:poolId` | execution admin (DELETE answers `409 runner_pool_busy` while jobs still need it) |
| GET | `/namespaces/:ns/github/runner-targets` | read: Slurm providers and whether a pool can start runners on each |
| GET | `/namespaces/:ns/cict/onboarding` | read: every setup step, done or not, and the next one with UI, CLI and API hints |
| GET | `/namespaces/:ns/cict/platform` | read: DreamLake GPU catalog, access, occupancy, month GPU time |
| POST | `/namespaces/:ns/cict/platform/activate` | execution admin + namespace admin: start using DreamLake GPU |
| PATCH | `/namespaces/:ns/cict/platform` | execution admin: change the evidence Source, or re-authorize with the same one (the caller becomes the authorizer) |
| GET | `/namespaces/:ns/cict/usage?month=YYYY-MM&sender=&limit=` | read: totals, by repository and workflow, by the GitHub user who triggered each job, and the jobs (newest first); each with `credits` (not charged), and per job `source` (`github` estimate or `slurm`) |
| GET | `/namespaces/:ns/github/jobs?limit=` | read |
| GET | `/namespaces/:ns/cict/runs?limit=` | read |
| GET | `/namespaces/:ns/cict/runs/:run` | read |
| GET | `/namespaces/:ns/cict/runs/:run/log?lines=` | read: the job's GitHub steps (`failedStep`) and the last lines of its GitHub log (1–1000, default 300), read from GitHub on demand; `available: false` until the job finishes |
| POST | `/namespaces/:ns/cict/runs/:run/cancel` | `lakeshore:use`: cancel the run's GitHub workflow run (every job in it); `already: true` when it had finished |
| GET | `/namespaces/:ns/cict/runs/:run/comparison` | removed: always `410 comparison_removed` |
| GET | `/namespaces/:ns/cict/dispatch/repositories?installationId=` | `lakeshore:read`: repositories the installation reaches, for Run workflow |
| GET | `/namespaces/:ns/cict/dispatch/workflows?installationId=&repository=` | `lakeshore:read`: the repository's active workflow files |
| GET | `/namespaces/:ns/cict/dispatch/branches?installationId=&repository=` | `lakeshore:read`: branches, default first (`null` when the App may not list them) |
| GET | `/namespaces/:ns/cict/dispatch/inputs?installationId=&repository=&workflow=&ref=` | `lakeshore:read`: whether the workflow at that ref can be run by hand and its declared inputs; `inputs: null` with a `reason` when the file cannot be read (`contents_permission_required`, `workflow_not_found`, `workflow_unreadable`); `jobs` gives each job's `runs-on` label sets (a literal matrix expands; `null` when an expression decides; `input`/`fallback` when a workflow_dispatch input decides, with its options as the sets) |
| POST | `/namespaces/:ns/cict/dispatches` | `lakeshore:use`: run a workflow (`installationId`, `repository`, `workflow`, `ref`, `inputs`, `requestId`); a retry with the same `requestId` returns the first answer |
| GET | `/namespaces/:ns/cict/dispatches?limit=` | `lakeshore:read`: workflows run from DreamLake and what came of each |
| GET / POST | `/namespaces/:ns/github/registry-triggers` | `lakeshore:read` / `lakeshore:use`: registry push triggers |
| DELETE | `/namespaces/:ns/github/registry-triggers/:triggerId` | `lakeshore:use` |
| GET | `/namespaces/:ns/github/registry-evaluations?limit=` | `lakeshore:read`: registry-triggered runs; the ECR secret and reconcile routes are in [Run a suite when an image is pushed](https://docs.dreamlake.ai/lakeshore/cict/registry-triggers#api) |

The built-in agent can call these through its resource API tools. Creating or
deleting a pool is a control operation. Completing a GitHub binding is not
available to the agent: it needs the user's browser on GitHub, so the agent
hands the user the install link.
