# Track Slurm and externally launched jobs

Read-only scheduler inventory and tracking records for work this CLI did not
launch. Authenticate and select the intended environment first (the `setup`
action of `dreamlake-cli`) and resolve host identities with [hosts](hosts.md).
Check the installed CLI version and command help against the
[Jobs](../reference/cli-jobs.md) and
[Slurm inventory](../reference/cli-queues.md#read-slurm-scheduler-jobs)
references; `queues slurm` requires CLI 0.57.0+ and its matching backend API.
Managed runs (`dreamlake run`, `dreamlake runs`) are a different thing: see
[hosts](hosts.md) and the [Managed runs reference](../reference/cli-runs.md).

## Read Slurm scheduler jobs

Discover configured clusters with `dreamlake queues slurm clusters --namespace NS`,
then use the returned cluster ID with `dreamlake queues slurm jobs CLUSTER_ID
--namespace NS --details`. The default table includes usernames, job names,
partitions, and observed states. No user filter is added; inspect snapshot scope,
effective Unix user, workload visibility, and completeness before claiming which
jobs are visible. Configured clusters do not establish access to every cluster.

Use `--details` for all 18 scheduler detail fields covering user identity,
name/partition, reason/account/QoS/priority, resources, and times, plus canonical
job/attempt, queue, allocation, and array metadata. `--json` retains the full
snapshot. Missing, unset, invalid, or older-server fields stay `Unknown`. Keep
raw TRES/GPU labels and per-CPU/per-node memory units; do not invent a GPU total
or total memory. Scheduler node counts are distinct from verified node mappings.
Start/end times may be forecasts, not proof of execution or completion.

Reading does not refresh the observation. Check its timestamps, freshness, and
cache errors: stale values are historical, and unavailable or incomplete
workloads return nonzero with unknown job count, not an empty queue. These
commands inspect scheduler inventory; they do not submit, cancel, or modify jobs.
`jobs list` instead reads explicit external tracking reports, and `queues jobs`
reads Lakeshore invocations. Do not interchange their IDs or register a tracking
record merely to inspect an existing scheduler job.

## Track externally launched work

1. Resolve an accessible host with `hosts list` in the intended namespace. Use
   the actual `Host.id` returned by the API for `jobs register --host`, not a
   host name, enrollment ID, or illustrative design-note ID.
2. Register with an explicit request ID. Retain the namespace, host, name, and
   request ID for identical retries after an uncertain result. Registration
   creates only a tracking record; it does not launch or discover a process.
3. Report only conditions observed by the external runner. For retryable reports,
   retain `--reported-at` and the same payload; follow the reference's timestamp
   and terminal-state rules. Reporting `cancelled` does not stop a process.
4. Inspect `jobs status` and the report age/freshness. A fresh report still does
   not verify live execution; an old `running` report does not prove failure.
   `jobs list` reads one page, so continue pagination when needed. Preserve
   access errors rather than presenting them as an empty inventory.

General Jobs logs, cancellation, waiting, artifacts, and execution lifecycle
controls are not supplied by external tracking. Use `runs` commands only for
actual managed runs; do not pass external job IDs to them. Do not automatically
capture or index program, tool, or terminal output.

This route does not replace uploads (the `data` action of `dreamlake-cli`),
revision-aware Notes (skill `dreamlake-notes`), artifact publication (skill
`dreamlake-artifacts`) or workflow push (the `workflows` action of `dreamlake-cli`).
Use an SDK for requested SDK integration or a documented CLI gap, after checking
that the SDK and server actually support the operation; an SDK is not evidence
that a proposed daemon or runner capability exists.

