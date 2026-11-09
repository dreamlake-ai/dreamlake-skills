# CI/CT with GitHub Actions

Let a repository's GitHub Actions jobs run on DreamLake machines
(`runs-on: dreamlake-<pool>`), then read what each run did. Authenticate and
select the intended environment first (the `setup` action of `dreamlake-cli`).
How the flow works, the workflow and evidence contract and every limit are in
the [product guide](../reference/docs-lakeshore-cict.md); commands and flags
are in the [CLI reference](../reference/cli-cict.md). Check
`dl cict --help` exists in the installed CLI before using it. A
`github_runners_disabled` answer means the server has the integration off:
stop and report that; there is no other route.

## Set up a repository (namespace admin)

1. Pick the Slurm provider: `dl providers list NS`. The user must have their
   own association on it, because runners start as the pool creator. Confirm
   with the user which partition and GPU its launch layers give.
2. Pick or create the evidence Source (the `sources` action of
   `dreamlake-cli`) and keep its ID.
3. `dl cict github installations NS`. If the repository's organization or
   account is not bound, run `dl cict github connect NS` and give the user the
   printed link. The user opens it in their own browser, signed in to
   DreamLake as the same user, within 15 minutes, installs the App and selects
   the repository. You cannot complete this step for them. Re-run
   `installations` to confirm the binding.
4. `dl cict pools list NS`. Reuse a pool whose label fits; otherwise create
   one with `dl cict pools create NS --name ... --provider ... --evidence-source ...`.
   Put only machine facts in `--env` (cache or asset paths); never secrets.
5. Hand the developer the workflow line `runs-on: <pool label>` and point them
   to [Write the workflow](../reference/docs-lakeshore-cict.md#write-the-workflow-developers)
   and [Declare evidence](../reference/docs-lakeshore-cict.md#declare-evidence).

## Check a run

1. `dl cict runs list NS --limit 20` and find the run by repository, job and
   commit.
2. `dl cict runs show NS/RUN_ID` for routing, runner, Slurm job and evidence
   state; add `--result` for the suite's `result.json`.
3. Explain the state with the guide's
   [Troubleshooting](../reference/docs-lakeshore-cict.md#troubleshooting) table:
   `unbound` and `unmatched` are setup problems (steps 3 and 4 above), a
   `failed` runner is an allocation problem on the provider, a `failed`
   evidence state is the job's manifest. A red GitHub check with evidence
   `written` is a test result, not an infrastructure failure.

## Exceptions

- Public repositories are refused unless the server allows them. Do not suggest
  making a repository public, or a workaround, to get a runner.
- Runners currently share the machine identity of the cluster's Nymph user.
  Before creating a pool, tell the user to route only repositories whose
  contributors they trust.
- Deleting a pool (`dl cict pools delete NS/POOL_ID`) stops new runners for
  its labels; confirm with the user first.
- Python (`client.cict`) and TypeScript (`dl.cict(namespace)`) expose the same
  operations; follow the product guide's links for their signatures.
- Running a suite without GitHub, from DreamLake itself, is not available yet;
  say so instead of improvising a queue submission.
