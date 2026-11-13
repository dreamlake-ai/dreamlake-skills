# Plan and run an experiment sweep

Read [the experiment workflow guide](../reference/docs-ml-dash-guides-experiment-workflow.md) first. Check that
the project's `GET .../status` lists `experiments`; without it, record ordinary runs with
[Record an experiment](record.md) and say the workflow view is unavailable.

1. Start from the SDK example `docs/examples/experiment_workflow/` (generator, plain `train.py`,
   launcher, `README.md`, `.dashrc`). Keep the user's training code plain: it writes files with an
   absolute step column; only the launcher imports DreamLake.
2. Generate the grid with params-proto v3 and commit it before launching. Slugs come from the
   configuration and seed only; never regenerate them with dates or scheduler ids.
3. Publish the folder (manifest, `README.md`, grid), then launch selected slugs. Write the question,
   conclusion and limitations only in `README.md`; link a Memo for the full analysis.
4. Review through the server contract (`folder.contract()`) or the Dash experiment view, not by
   averaging every run in the folder.

Choosing an attempt kind:

- A crashed or failed run that should continue: a **resume** with the explicit parent attempt id,
  the checkpoint and the checkpoint's absolute step. Never infer the step from row counts.
- A launcher or upload that died mid-way: **reconnect** with the same attempt id and re-sync the
  same files; points already stored are not appended again.
- A changed configuration or a clean re-run: a new **fresh** attempt. The previous one stays
  stored and is no longer compared.

Report states as the contract gives them. `unknown` (a read failed) is not "not started";
`invalid` and diagnostics such as `RESUME_ORPHAN` or `CONFIG_DRIFT` need the user's decision, not a
silent re-run. A retry never adds a seed. Synthetic or smoke runs only prove the path works.
