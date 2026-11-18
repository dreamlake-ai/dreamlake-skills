---
name: dreamlake-experiments
description: Log ML experiments with the DreamLake Python SDK, run planned config × seed sweeps with fresh/resume/reconnect attempts, and configure per-run Dash dashboards; not implementing training algorithms or provisioning compute.
---

# DreamLake experiments

Use this skill to instrument training code, create a mock logging fixture, inspect
recorded run data, or configure what a Dash run displays. It does not implement a
training algorithm or provision compute. Pick the action that matches the task.

| Request | Action |
| --- | --- |
| Record parameters, metrics, logs, Tracks and artifacts through Python; prepare an RL logging fixture | [Record an experiment](actions/record.md) |
| Missing curves, partial overview, images/video or a per-run `.dashrc` | [Configure the dashboard](actions/dashboard.md) |
| A planned sweep (configs × seeds) with retries, resumes or reconnects, and comparing seeds | [Plan and run a sweep](actions/sweep.md) |

Use the setup action of `dreamlake-cli` for installation and login. Instrumentation
is an SDK task; ordinary resource operations use the CLI where it supports them.
Preserve the user's target, execution scope and choice of mock or real data.

## Canonical source

Product facts and runnable examples live at docs.dreamlake.ai; CLI syntax lives at
cli.dreamlake.ai. The pages in `skill.json` are fetched into `reference/` by CI.
Do not edit those generated files or copy their API/flag tables into actions.
