# Plan and run an experiment sweep

Read [the experiment workflow guide](../reference/docs-ml-dash-guides-experiment-workflow.md) first. Check that
the project's `GET .../status` lists `experiments`; without it, record ordinary runs with
[Record an experiment](record.md) and say the workflow view is unavailable.

Create the environment with Python 3.13, the tested combination (Python 3.13.14, `dreamlake` 0.50.1,
`params-proto` 3.3.0); see the guide's "Tested environment". With Python 3.14.5 and params-proto 3.3.0
the template's grid generator fails with `TypeError: cannot pickle 'itertools.product' object`: if a user
hits that, switch the environment to Python 3.13 rather than editing the generator. The project must
already exist (`dl create project <name> --namespace <ns>`).

1. Scaffold with `python -m dreamlake.experiments.workflow init <dir>` (generator, plain `train.py`,
   launcher, `README.md`, `.dashrc`; there is no `dl` command for this). Keep the user's training code
   plain: it writes files with an absolute step column; only the launcher imports DreamLake, and it
   records the exact argv and working directory it runs.
2. Generate the grid with params-proto v3 and commit it before launching. Slugs come from the
   configuration and seed only; never regenerate them with dates or scheduler ids.
3. Publish the folder (manifest, `README.md`, grid), then launch selected slugs. Write the question,
   conclusion and limitations only in `README.md`; link a Memo for the full analysis.
4. Review through the server contract (`folder.contract()`) or the Dash experiment view, not by
   averaging every run in the folder.

Choosing an attempt kind:

- A crashed or failed run that should continue: a **resume** with the explicit parent attempt id,
  the checkpoint and the checkpoint's absolute step. Never infer the step from row counts.
- A launcher or upload that died mid-way: **reconnect** with the same attempt id (`folder.attach`, or
  the template's `--launch.sync-only`) and re-sync the same files; points already stored are not
  appended again and the run's status is not changed unless set explicitly. A refusal naming
  `params`, `config` or `seed` means a different attempt: start a new one, do not force it.
- A changed configuration or a clean re-run: a new **fresh** attempt. The previous one stays
  stored and is no longer compared.

Report states as the contract gives them. `unknown` (a read failed) is not "not started", and
`409 EXPERIMENT_INCOMPLETE` means no comparison exists yet: report the diagnostics, not partial numbers;
`invalid` and diagnostics such as `RESUME_ORPHAN` or `CONFIG_DRIFT` need the user's decision, not a
silent re-run. A retry never adds a seed. Synthetic or smoke runs only prove the path works.
