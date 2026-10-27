# Inspect hosts, enrollments and terminal sessions

Add Host is the Fabric layer for machine identity, connectivity and management,
including development, SSH, terminals and remote commands. No queue mount or
queue consumer is required. Select an authorized execution connection with the
same DreamLake owner as the host name prefix. A Runtime worker is a separate
process bound to a queue; the same Host can support development and workers.
Use the [Runtime worker route](lakeshore.md#runtime-attach-a-worker-process-to-a-queue)
for queue association, consumer readiness and job-consumption verification.

Verify that the selected connection's credential can mint host-enrollment
grants on the deployed control plane; an ordinary namespace access token,
`authMode: token`, or `legacy` label alone is insufficient evidence. A source-only
scoped capability is not deployment proof. Do not hand users a global admin token.
Retain pending host identity and request ID through grant-authorization failures;
resolve authority and use supported retries instead of renaming/recreating.

Authenticate and select the intended environment first (the `setup` action of
`dreamlake-cli`). Check the installed CLI version and command help against the
[Hosts reference](../reference/cli-host-enrollment.md). The `hosts enrollments`,
`hosts metrics` and `hosts check` routes require CLI 0.57.0+ and their matching
backend APIs. Slurm inventory and external job tracking are in [jobs](jobs.md).
A merged source change, updated docs, or an installed skill does not establish
that the executable or server supports it. Updating the CLI does
not update installed skills; follow [skill installation](../reference/cli-skills.md)
and preserve local customizations when reviewing conflicts.

## Choose the operation

| Task | Route |
| --- | --- |
| Archive or restore catalog visibility | Check installed support, read `hosts lifecycle HOST_ID`, then use explicit request ID and expected revision with `hosts archive` or `hosts restore`; this never retires runtime |
| Find active hosts across groups | `dreamlake hosts list`; select the authorized namespace (CLI 0.73.0+: verified online only) |
| Include offline or unknown hosts | CLI 0.73.0+ `dreamlake hosts list --all`; CLI 0.72.0 lists all states without this flag |
| Save or reopen an exact agent terminal session | [Terminal sessions](../reference/cli-sessions.md): `dreamlake sessions targets`, then `create` / `resume` / `open`; Codex requires CLI 0.74.1+ and matching terminal API/gateway; Claude requires CLI 0.77.0+ and provider-aware services |
| Inspect one host and its enrollments | `dreamlake hosts status` with its returned host ID or full name |
| Resolve enrollment identities and observed presence | `dreamlake hosts enrollments HOST`; retain its exact enrollment ID |
| Read CPU, RAM, and disk observations | `dreamlake hosts metrics HOST --enrollment ID` |
| Check observed SSH or tracked-run capability | `dreamlake hosts check HOST --enrollment ID --action ssh` or `--action tracked-run` |
| Register an existing computer | `dreamlake hosts enroll`; follow [machine identity setup](machines.md) |
| Provision and enroll one machine | CLI 0.72.0+ `hosts create PROVIDER --host-name NS/GROUP/HOST`; see [machine provisioning](machines.md) and the [Host power reference](../reference/cli-host-enrollment.md#provision-and-control-machine-power) |
| Inspect or change managed EC2 machine power | CLI 0.72.0+ `hosts power`, `start`, `stop`, `restart`, `terminate`; see [Host power](../reference/cli-host-enrollment.md#provision-and-control-machine-power) |
| Open an enrolled host shell | CLI 0.72.0+ `dreamlake ssh HOST` or `hosts ssh`; see [SSH](../reference/cli-host-enrollment.md#ssh-and-remote-commands) |
| Execute a command on an enrolled host | CLI 0.72.0+ `dreamlake exec HOST -- COMMAND` or `hosts exec`; see [remote commands](../reference/cli-host-enrollment.md#ssh-and-remote-commands) |
| Launch managed execution or inspect its output/control | [Managed runs](../reference/cli-runs.md): `dreamlake run` and `dreamlake runs` |
| Track work another launcher already starts | [jobs](jobs.md) |
| Inspect Slurm scheduler jobs | [jobs](jobs.md) |

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
`sessions open ID` opens the descriptor's exact remote conversation. Never
interpret a saved descriptor or successful list as a running process. Preserve
the configured account/environment; custom gateways require explicit trusted
`--gateway` and `--origin`. See the reference for deployment prerequisites. This
does not replace managed runs, uploads, artifacts, or Notes; it provides terminal
access only and does not synchronize Codex conversations across hosts.

CLI 0.75.0+ with the matching managed-session gateway adds `sessions status ID` for a
bounded runtime observation, `start ID` for detached start/resume, `reconnect ID`
for attachment without creating a process, and `stop ID --yes` for explicit
termination guarded by the observed runtime identity. These commands are not
in CLI 0.74.3 or earlier. `start --json` can execute a persistent process; `resume --json` remains
save-only. Stop affects all viewers but preserves the descriptor/conversation;
do not confuse detach with stop. Legacy unmarked runtimes may be attached, but
cannot be stopped or adopted by managed commands. Missing dependencies are
reported without installing packages. After an uncertain mutation response,
inspect status instead of retrying blindly.

With CLI 0.84.1+ and the matching gateway guard, `native_session_active` reports
positive writable-file evidence for that exact Codex conversation and refuses a
new terminal process. Continue in the existing Codex chat; do not terminate it or
automatically retry. Use `sessions reconnect` only for an already-running managed
terminal. Missing/unknown probe results do not establish exclusive access, and this
Codex-only guard does not adopt native sessions or read conversation contents.

With CLI 0.81.0+ and a direct-capable gateway, open/resume negotiate tmux when
available and otherwise an owner-only direct foreground connection. Direct
`start` reports ready and `executed:false`; use `open` to launch the process on
connection. Warn that disconnecting may end it. Direct mode has no persistence,
team viewer attachment, or managed stop; `reconnect` remains tmux attach-only
and must not launch a replacement. Never install tmux automatically or claim
screen support. Older gateways retain their existing dependency errors.

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
See the [catalog reference](../reference/cli-host-enrollment.md#archive-and-restore-catalog-records).

Uploading a session's conversation history (CLI 0.79.0+) and linking Note or
Artifact writes to a session are the `session-links` action of `dreamlake-cli`.
