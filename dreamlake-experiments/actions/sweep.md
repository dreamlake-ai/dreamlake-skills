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

Evaluation and analysis — **unreleased**: only when the installed template has `play.py` and
`analysis.py` (the guide's "Evaluation and analysis" section); otherwise skip this part.

5. Keep evaluation a separate step after training completes: the launcher runs the user's plain
   `play.py` on the final checkpoint and records the checks on that attempt. Keep `play.py` free of
   DreamLake imports; give every check a human-readable `name`, an optional machine `id`, a `reason`,
   and `inconclusive` when the evidence is too thin. To evaluate an existing attempt again use
   `--launch.eval-only --launch.attempt <id>`; never start a new training attempt for that.
6. Run `analysis.py` after the evaluations you need are recorded. Exit 0: every criterion passed;
   1: a criterion failed or could not be judged; 2: no current verdict — the analysis failed, or its
   published report is stale, replaced or could not be read back (fix or re-run; do not quote a
   verdict). Each run publishes a new generation id; never reuse an id for changed content. Write the
   criteria with the user; they are reading aids, not significance tests.
7. On a worker, record evaluations with a write session bound to that attempt's run
   (`Attempt.existing(...)` with the known folder and run ids). A managed job session cannot record
   them: its run is not an experiment attempt.

Choosing an attempt kind:

- A crashed or failed run that should continue: a **resume** with the explicit parent attempt id,
  the checkpoint and the checkpoint's absolute step. Never infer the step from row counts.
- A launcher or upload that died mid-way: **reconnect** with the same attempt id (`folder.attach`, or
  the template's `--launch.sync-only`) and re-sync the same files; points already stored are not
  appended again and the run's status is not changed unless set explicitly. A refusal naming
  `params`, `config` or `seed` means a different attempt: start a new one, do not force it.
- A changed configuration or a clean re-run: a new **fresh** attempt. The previous one stays
  stored and is no longer compared.

Report the three answers separately: training state (`completed`), evaluation (`Fail`, `Eval error`,
`Not recorded`, `Stale`, ...) and the analysis outcome. A failed check never makes a run failed, an
`Eval error` is not a policy verdict, `Not recorded` and `Stale` are not passes, and "Criteria not met"
does not mean the hypothesis is disproven — quote the author's statement and the failing criterion.

Report states as the contract gives them. `unknown` (a read failed) is not "not started", and
`409 EXPERIMENT_INCOMPLETE` means no comparison exists yet: report the diagnostics, not partial numbers;
`invalid` and diagnostics such as `RESUME_ORPHAN` or `CONFIG_DRIFT` need the user's decision, not a
silent re-run. A retry never adds a seed. Synthetic or smoke runs only prove the path works.
