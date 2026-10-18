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
| Archive or restore catalog visibility | Check installed support, read `hosts lifecycle HOST_ID`, then use explicit request ID and expected revision with `hosts archive` or `hosts restore`; this never retires runtime |
| Find active hosts across groups | `dreamlake hosts list`; select the authorized namespace (CLI 0.73.0+: verified online only) |
| Include offline or unknown hosts | CLI 0.73.0+ `dreamlake hosts list --all`; CLI 0.72.0 lists all states without this flag |
| Save or reopen an exact agent terminal session | [Terminal sessions](../reference/sessions.md): `dreamlake sessions targets`, then `create` / `resume` / `open`; Codex requires CLI 0.74.1+ and matching terminal API/gateway; Claude requires CLI 0.77.0+ and provider-aware services |
| Inspect one host and its enrollments | `dreamlake hosts status` with its returned host ID or full name |
| Resolve enrollment identities and observed presence | `dreamlake hosts enrollments HOST`; retain its exact enrollment ID |
| Read CPU, RAM, and disk observations | `dreamlake hosts metrics HOST --enrollment ID` |
| Check observed SSH or tracked-run capability | `dreamlake hosts check HOST --enrollment ID --action ssh` or `--action tracked-run` |
| Register an existing computer | `dreamlake hosts enroll`; follow [machine identity setup](machines.md) |
| Provision and enroll one machine | CLI 0.72.0+ `hosts create PROVIDER --host-name NS/GROUP/HOST`; see [machine provisioning](machines.md) and the [Host power reference](../reference/host-enrollment.md#provision-and-control-machine-power) |
| Inspect or change managed EC2 machine power | CLI 0.72.0+ `hosts power`, `start`, `stop`, `restart`, `terminate`; see [Host power](../reference/host-enrollment.md#provision-and-control-machine-power) |
| Open an enrolled host shell | CLI 0.72.0+ `dreamlake ssh HOST` or `hosts ssh`; see [SSH](../reference/host-enrollment.md#ssh-and-remote-commands) |
| Execute a command on an enrolled host | CLI 0.72.0+ `dreamlake exec HOST -- COMMAND` or `hosts exec`; see [remote commands](../reference/host-enrollment.md#ssh-and-remote-commands) |
| Launch managed execution or inspect its output/control | [Managed runs](../reference/runs.md): `dreamlake run` and `dreamlake runs` |
| Track work another launcher already starts | `dreamlake jobs register`, `report`, `list`, and `status` |
| Inspect Slurm scheduler jobs | Discover `queues slurm clusters`, then `queues slurm jobs CLUSTER_ID --details` |

## Connection and power commands (CLI 0.72.0+)

The SSH/exec and Host create/power routes require CLI 0.72.0+ and matching
server capabilities. Check installed
`dreamlake --version`, `dreamlake hosts --help`, `dreamlake ssh --help`, and the
matching server before using them. An older executable is unsupported, not an
invitation to guess flags or bypass server authorization.

SSH/exec use the existing Terminal session delegation and Nymph relay with
native OpenSSH on Linux/macOS. Resolve an exact host and disambiguate enrollment;
preserve host-key pinning. Arguments after `--` are literal; use `sh -c` only
for intended shell syntax. A timeout disconnects and returns 124; it does not
prove detached remote work stopped. File copy remains deferred.

`hosts create` reuses provider launch and requires a host name, one instance,
and a stable request ID. Keep paid launches within the requested scope. Power
commands require a verified EC2 launch binding; they change machine power, not
local daemon state, catalog visibility, or enrollment access. They do not
support Kubernetes or manually enrolled machines. Explicit enrollment, stable
request identity, and termination volume disposition are required. Preserve
those inputs for uncertain-result recovery; do not blindly generate a new ID.
Recorded tracked-run checks do not establish that a machine is idle or drained.

## Inspect the intended host

For persistent Codex terminals (CLI 0.74.1+), select a target and its exact enrollment from
`sessions targets`, plus the user's requested remote directory and Codex UUID.
`sessions resume UUID` saves and attaches interactively; `--json` saves only.
`sessions open ID` reattaches to the descriptor's existing tmux identity. Never
interpret a saved descriptor or successful list as a running process. Preserve
the configured account/environment; custom gateways require explicit trusted
`--gateway` and `--origin`. See the reference for deployment prerequisites. This
does not replace managed runs, uploads, artifacts, or Notes; it provides terminal
access only and does not synchronize Codex conversations across hosts.

CLI 0.75.0+ with the matching managed-session gateway adds `sessions status ID` for a
bounded runtime observation, `start ID` for detached start/resume, `reconnect ID`
for attachment without creating a process, and `stop ID --yes` for explicit
termination guarded by the observed runtime identity. These commands are not
in CLI 0.74.3 or earlier. `start --json` still executes; `resume --json` remains
save-only. Stop affects all viewers but preserves the descriptor/conversation;
do not confuse detach with stop. Legacy unmarked runtimes may be attached, but
cannot be stopped or adopted by managed commands. Missing dependencies are
reported without installing packages. After an uncertain mutation response,
inspect status instead of retrying blindly.

For Claude Code sessions, use CLI 0.77.0+ and matching provider-aware API and
gateway. Select `--provider claude --session UUID` when creating a descriptor;
use `--claude-config-dir /absolute/path` only for its actual custom Claude configuration
root. `--codex-session` remains the Codex UUID option. The saved descriptor
determines the provider on later `open`, `start` and `reconnect` actions. Claude resumes with its
existing authentication and permissions; never add a permission-bypass flag.
Automatic Claude discovery requires Nymph 0.1.31+ and the matching product API.
Check installed and deployed support rather than treating a skill update as an
upgrade. The reference distinguishes registered history, process observations,
native working/waiting/idle/error states, and stale/unknown evidence; recent file
activity alone does not prove a running session or its model provider.

For conversations created directly in Codex, CLI 0.75.0+ `sessions sync`
requires explicit `--target` or `--all`. It reads one bounded recent-root index
page per selected enrolled host and idempotently saves descriptors, preserving
existing human names. It launches no terminal, reads no transcript, installs no
package, and never runs automatically during list/search/refresh. Continue a
target with its discovery cursor; registry list uses a separate cursor. Report
missing indexes/Python or unavailable hosts rather than claiming complete fleet
coverage. See the owning Sessions reference for scope and deployment gates.

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

## Catalog visibility

Catalog commands require CLI 0.73.0+ and the matching backend.
Check command help before use. Archive changes only default list visibility;
runtime, enrollments and credentials remain active and future work is still
permitted. Do not use archive as retirement, cleanup eligibility or proof of idle.
Exact ID/full-name status and history links remain available; use
`hosts list --all --archived include` or `hosts list --all --archived only` to discover archived records.

Select an exact lowercase Host ID and namespace, read `hosts lifecycle`, and
supply that revision plus an explicit request ID for archive/restore. After an
ambiguous failure retry the identical tuple. Never silently refresh the revision,
change the action or generate a new request ID to bypass a conflict. A replayed
receipt can predate a later opposite action; read lifecycle for current state.
See the [catalog reference](../reference/host-enrollment.md#archive-and-restore-catalog-records).

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
