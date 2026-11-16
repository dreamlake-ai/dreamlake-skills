# CI/CT with GitHub Actions

Let a repository's GitHub Actions jobs run on DreamLake machines, then read
what each run did. Authenticate and select the intended environment first (the
`setup` action of `dreamlake-cli`). How the flow works, the workflow and
evidence contract and every limit are in the
[product guide](../reference/docs-lakeshore-cict.md); commands and flags are in
the [CLI reference](../reference/cli-cict.md). These commands need CLI
0.123.0 or later (`dl cict status` needs 0.126.0); check `dl cict --help`
before using them. A `github_runners_disabled`
answer means the server has the integration off: stop and report that; there
is no other route.

## Set up end to end (start here)

`dl cict status NS --json` reports every setup step (GitHub, DreamLake GPU,
and the six own-machine steps), whether each is `done`, and `next`: the first
open step with `how.cli`, `how.api`, `how.ui` and, when a person must act,
`how.human`. To set a namespace up, repeat:

1. Run `dl cict status NS --json`. If `ready` is true, hand the developer the
   `workflow` line (the `runs-on` label and the evidence contract) and stop.
2. Do `next`: run its `how.cli` after filling every `<placeholder>` from the
   user or from earlier output. When `how.human` is set, do the part you can
   (for GitHub, create the install link) and give the user exactly what they
   must do; then wait for them and run status again.
3. Run status again and confirm the step is now `done` before moving on. If it
   is not, read its `detail`; do not repeat the same command in a loop.

What only a person can do: install the GitHub App in a browser; ask the
DreamLake team to enable DreamLake GPU; enroll a cluster login node (needs an
SSH-capable terminal; you may run it if you have one and the user agrees);
bind the machine's service account (a namespace owner). Everything else has a
command. Confirm before any step that grants access or spends shared GPUs.

There are two kinds of machines. Ask which the user wants if it is not clear:
**DreamLake GPU** (machines DreamLake provides, chosen by label, nothing to
register) or **their own machines** (a runner pool on a Slurm cluster their
namespace registered).

## Connect GitHub (namespace admin)

1. `dl cict github installations NS`. If the repository's organization or
   account is not bound, run `dl cict github connect NS` and give the user the
   printed link. The user opens it in their own browser, signed in to
   DreamLake as the same user, within 15 minutes, installs the App and selects
   the repository. You cannot complete this step for them. Re-run
   `installations` to confirm the binding.
2. An installation belongs to one namespace. If the user wants a GitHub
   account that is already bound elsewhere, say so; do not suggest
   uninstalling it without their explicit decision.

## Use DreamLake GPU

1. `dl cict platform show NS`.
   - *Not offered on this server* (`available: false`): DreamLake GPU is off
     for the whole server, not just this namespace. Report it; nothing the
     user runs changes that.
   - *Not enabled*: tell the user the DreamLake team enables it per namespace;
     there is nothing to run.
   - *Enabled, not started*: `dl cict platform start NS` (or `--source ID` for
     an existing Source). It needs the namespace admin role and makes the
     caller the person who authorizes evidence writes; confirm that with the
     user first.
   - *Paused*: report it; new jobs will not start.
2. Give the developer a label from the catalog in `show` (for example
   `runs-on: dreamlake-gpu-rtx5090`) and point them to
   [Write the workflow](../reference/docs-lakeshore-cict.md#write-the-workflow-developers)
   and [Declare evidence](../reference/docs-lakeshore-cict.md#declare-evidence).
3. `dl cict usage NS` reports the month's GPU time by who triggered each job
   and by workflow; `--jobs [--sender LOGIN]` lists the jobs.
4. If `platform show` says the authorizer can no longer write, jobs wait in
   the queue. A namespace admin re-authorizes with `dl cict platform source NS
   --source <current Source>`; say who can do it rather than retrying.

## Use their own machines

Only Slurm clusters are supported. The six steps, in order (`dl cict status`
shows which are done): enroll the login node (`hosts` action), bind its
service account (`dl service-accounts create` and `bind`, a namespace owner),
register a Slurm provider, associate the login node with it, set its launch
layer (all three in the `machines` action), create a runner pool (below).
Check the cluster's real nodes (`sinfo -o '%P %G %c %m'` on the login node)
before writing a launch layer: ask only for resources one node has.

1. `dl cict pools targets NS` lists the Slurm providers and whether a pool can
   start runners on each. If none is usable, the reason says what is missing
   (no bound host, no launch layer); that is the provider setup in the
   `machines` action, not something to work around here. `evidenceReady:
   false` means the host has no service account, so runs could not save
   evidence: bind one first.
2. Pick or create the evidence Source (the `sources` action of
   `dreamlake-cli`) and keep its ID.
3. `dl cict pools list NS`. Reuse a pool whose label fits; otherwise create one
   with `dl cict pools create NS --name ... --provider ... --evidence-source ...`.
   Put only machine facts in `--env` (cache or asset paths); never secrets.
4. To change a pool, use `dl cict pools update NS/POOL_ID`; tell the user it
   applies to the next job. Deleting (`dl cict pools delete NS/POOL_ID`) stops
   new runners for its labels: confirm first. `runner_pool_busy` means jobs
   still need it; wait for them, do not retry in a loop.
5. Hand the developer `runs-on: <pool label>` and the same two guide sections.

## Check a run

1. `dl cict runs list NS --limit 20` and find the run by repository, job and
   commit. The text output has no branch; use `--json` and its `headBranch`
   field to find a pull request's runs.
2. `dl cict runs show NS/RUN_ID` for routing, runner, Slurm job, evidence
   state, who triggered it and GPU time; add `--result` for the suite's
   `result.json`.
3. `dl cict runs compare NS/RUN_ID` shows which cases regressed or were fixed
   against the baseline: the latest earlier run of the same repository,
   workflow and job on the default branch whose evidence was written (`--all`
   for every case).
4. Explain the state with the guide's
   [Troubleshooting](../reference/docs-lakeshore-cict.md#troubleshooting)
   table. `queued #N` is a DreamLake GPU job waiting for a slot, not a fault.
   `refused:<reason>` (shown as `not started: <reason>` in `runs show`) is
   DreamLake GPU access (not enabled, not started, paused).
   `rejected:<reason>` is a public repository or an inactive installation. `unbound` and `unmatched` are setup problems. A red GitHub check
   with evidence `written` is a test result, not an infrastructure failure.

## Administer DreamLake GPU

Only for admins of the platform namespace, and only when the user asks.
`dl cict platform admin list [--month YYYY-MM]` shows namespaces, machine
types and the platform total. `providers` lists the platform's Slurm
providers and what one job gets on each. `allow NS [--limit N]`, `pause NS`,
`limit NS N` and `machine ID --label ... --provider ... --limit N --enable`
change them; a machine type's spec comes from the provider's launch layer. Each changes who can run on shared GPUs: confirm the exact change with
the user before running it.

## Exceptions

- Public repositories are refused unless the server allows them. Do not
  suggest making a repository public, or a workaround, to get a runner.
- Runners share the cluster's machine identity. Before creating a pool or
  enabling a namespace, tell the user to route only repositories whose
  contributors they trust.
- Python (`client.cict`) and TypeScript (`dl.cict(namespace)`) expose the same
  operations; follow the product guide's links for their signatures.
- Running a suite without GitHub, from DreamLake itself, is not available yet;
  say so instead of improvising a queue submission.
