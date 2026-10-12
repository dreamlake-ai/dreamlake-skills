# Inspect hosts and track external jobs

Use [setup](setup.md) to authenticate and select the intended environment. Check
the installed CLI version and command help against the [Hosts reference](../reference/host-enrollment.md)
and [Jobs reference](../reference/jobs.md), including their version and backend
requirements. A merged source change, updated docs, or an installed skill does
not establish that the executable or server supports it. Updating the CLI does
not update installed skills; follow [skill installation](../reference/skills.md)
and preserve local customizations when reviewing conflicts.

## Choose the operation

| Task | Route |
| --- | --- |
| Find existing hosts across groups | `dreamlake hosts list`; select the authorized namespace |
| Inspect one host and its enrollments | `dreamlake hosts status` with its returned host ID or full name |
| Register an existing computer | `dreamlake hosts enroll`; follow [machine identity setup](machines.md) |
| Provision a new machine | [Machine provisioning](machines.md); keep paid launches within the requested scope |
| Launch managed execution or inspect its output/control | [Managed runs](../reference/runs.md): `dreamlake run` and `dreamlake runs` |
| Track work another launcher already starts | `dreamlake jobs register`, `report`, `list`, and `status` |

## Inspect the intended host

Use inventory results to resolve identity. Host IDs, enrollment IDs, cloud
instance IDs, and local Nymph supervisor IDs are different identifiers. Inspect
the returned enrollments rather than guessing which daemon belongs to a host.
An online connection does not prove SSH or workload readiness; retain unknown
or unverified states. Enrollment already starts its managed service, so do not
launch a second foreground daemon as an implicit readiness retry. Preserve the
request ID and original inputs when recovering pending enrollment.

For local daemon inspection, check the installed `nymph --version` and help.
Read-only supervisor diagnostics do not implement the proposed enrollment-ID
`nymph daemon` command group. Do not infer enrollment selection, duplicate-owner
protection, or lifecycle controls from those diagnostics, and do not treat an
unavailable inspection endpoint as proof that the daemon stopped.

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
