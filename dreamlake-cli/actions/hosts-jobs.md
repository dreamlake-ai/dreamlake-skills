# Inspect hosts, Slurm jobs, and external tracking

Use [setup](setup.md) to authenticate and select the intended environment. Check
the installed CLI version and command help against the [Hosts reference](../reference/host-enrollment.md)
and the [Jobs](../reference/jobs.md) and [Slurm inventory](../reference/queues.md#read-slurm-scheduler-jobs)
references. The `hosts enrollments`, `hosts metrics`, `hosts check`, and
`queues slurm` routes require CLI 0.57.0+ and their matching backend APIs.
A merged source change, updated docs, or an installed skill does not establish
that the executable or server supports it. Updating the CLI does
not update installed skills; follow [skill installation](../reference/skills.md)
and preserve local customizations when reviewing conflicts.

## Choose the operation

| Task | Route |
| --- | --- |
| Find existing hosts across groups | `dreamlake hosts list`; select the authorized namespace |
| Inspect one host and its enrollments | `dreamlake hosts status` with its returned host ID or full name |
| Resolve enrollment identities and observed presence | `dreamlake hosts enrollments HOST`; retain its exact enrollment ID |
| Read CPU, RAM, and disk observations | `dreamlake hosts metrics HOST --enrollment ID` |
| Check observed SSH or tracked-run capability | `dreamlake hosts check HOST --enrollment ID --action ssh` or `--action tracked-run` |
| Register an existing computer | `dreamlake hosts enroll`; follow [machine identity setup](machines.md) |
| Provision a new machine | [Machine provisioning](machines.md); keep paid launches within the requested scope |
| Launch managed execution or inspect its output/control | [Managed runs](../reference/runs.md): `dreamlake run` and `dreamlake runs` |
| Track work another launcher already starts | `dreamlake jobs register`, `report`, `list`, and `status` |
| Inspect Slurm scheduler jobs | Discover `queues slurm clusters`, then `queues slurm jobs CLUSTER_ID --details` |

## Inspect the intended host

Use inventory results to resolve identity. Host IDs, enrollment IDs, cloud
instance IDs, and local Nymph supervisor IDs are different identifiers. Inspect
the returned enrollments rather than guessing which daemon belongs to a host.
An online connection does not prove SSH or workload readiness; retain unknown
or unverified states. Enrollment already starts its managed service, so do not
launch a second foreground daemon as an implicit readiness retry. Preserve the
request ID and original inputs when recovering pending enrollment.

For read-only inspection, select one host ID or full name in its authorized
namespace. `hosts enrollments` separates host, enrollment, and runtime machine
IDs; verified presence has a 60-second freshness window. Metrics and action
checks require an explicit enrollment from that result; never choose one
implicitly or combine multiple enrollments' observations. Metrics older than
90 seconds or marked stale remain historical; missing/invalid/future timestamps
and missing values remain unknown, not zero. Read the source sample time and
stale flag alongside client freshness.

`hosts check` reads advertised capability with a 30-second SSH or 60-second
tracked-run observation window. Exit zero means observed `ready`; `not_ready`,
`unknown`, and errors exit one. It performs no SSH handshake, job, grant, or
lifecycle action. Ordinary tracked-run capability does not establish private
setup or support for every runner. Preserve missing, stale, ambiguous, or
unverified observations as unknown rather than claiming successful execution.

For local daemon inspection, check the installed `nymph --version` and help.
Legacy supervisor diagnostics alone do not prove enrollment-ID selection support.
Nymph 0.1.20 adds read-only `nymph daemon list` and `nymph daemon status`; selection
requires trusted, reachable inspection of the same process and an enrollment
confirmed by hello. Verification covers Linux only and does not establish a fleet
upgrade, lifecycle controls, or a singleton guarantee. Do not treat an unavailable
inspection endpoint as proof that the daemon stopped.

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

This route does not replace [uploads](data.md), revision-aware [Notes](notes.md),
[artifact publication](artifacts.md), or [workflow management](workflows.md).
Use an SDK for requested SDK integration or a documented CLI gap, after checking
that the SDK and server actually support the operation; an SDK is not evidence
that a proposed daemon or runner capability exists.
