# Migration: dreamlake-lakeshore (integration split from dreamlake-cli)

**Decision — new skill, split out during integration.** After S2,
`dreamlake-cli` carried 74.6 KB of hand-written text in 15 actions, past both
soft caps (about 50 KB, about 12 actions). The compute loop — connecting
machines to DreamLake, inspecting and provisioning them, the infrastructure and
cloud connections behind them — is a distinct user goal, so it became
`dreamlake-lakeshore` (`requires: ["dreamlake-cli"]`). `dreamlake-cli` keeps
login, data, Projects, ownership, sessions, Vault, UDFs and workflow push and
routes compute here by name. No `renamed.json` entry: nothing was retired.

`docs[]`: the cli.dreamlake.ai pages the moved actions link (all verified
`.md` → 200): lakeshore, host-enrollment, sessions, runs, jobs, queues,
providers, providers/kubernetes, service-accounts, infrastructure, connect-aws,
skills. `sessions` and `skills` also stay in `dreamlake-cli` because its
`session-links` and `setup` actions link them; the other ten left
`dreamlake-cli`.

| Source (`dreamlake-cli/actions/`) | Destination | Notes |
| --- | --- | --- |
| `lakeshore.md` | `actions/lakeshore.md` | unchanged; `[setup](setup.md)` → "the `setup` action of `dreamlake-cli`"; `[host enrollment](hosts-jobs.md)` → `hosts.md` |
| `hosts-jobs.md` intro, operation table, "Connection and power commands", "Inspect the intended host", "Catalog visibility" | `actions/hosts.md` | one task per file: hosts, enrollments and terminal sessions. Jobs and Slurm references moved to `jobs.md`; the two job rows of the table point at `jobs.md`; closing session-links pointer is a name |
| `hosts-jobs.md` "Read Slurm scheduler jobs", "Track externally launched work" | `actions/jobs.md` | text unchanged plus a short intro; uploads and workflow push named as `dreamlake-cli` actions |
| `machines.md` | `actions/machines.md` | unchanged; launch-server rule is also stated prominently in `SKILL.md` |
| `infrastructure.md` | `actions/infrastructure.md` | unchanged; `dreamlake-cli/actions/projects.md` now names this action instead of linking it |
| `connect-aws.md` | `actions/connect-aws.md` | unchanged |
| `dreamlake-cli/SKILL.md` "Launch-server requirement" section | `SKILL.md` "Launch-server requirement" (verbatim rule, placed before the action table) | `dreamlake-cli/SKILL.md` keeps a one-line note pointing here |
