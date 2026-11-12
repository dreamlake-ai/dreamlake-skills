<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/nymph-permissions.md at 0.1.158 3f90c7b1; do not edit -->

# Nymph permissions and commands

This is the permission-boundary record for Nymph. It distinguishes implemented behavior from a proposed dynamic-configuration design. For capacity configuration and usage reporting, see [SSH capacity and usage](docs-lakeshore-hosts-browser-terminal.md#ssh-capacity-and-usage) for release status and configuration options. No general remote config setter or live capacity reload is added by this work.

## Authority is layered

An authenticated control-plane response is not permission to execute every operation. The server authorizes an operation for a namespace, worker and credential; the daemon also applies local owner policy and the operation's own capability checks. The process's Unix account and OS permissions remain the final host boundary.

For a managed daemon, `access_file` names a separate local policy with version 1, a scope (`server`, `namespace`, `machine_id`), and explicit `upload` and `command_execution` booleans. Nymph checks that the path is absolute, is not a symlink (including parents), is a bounded regular file owned by the effective user, and has private permissions. Its scope must match the configured server/namespace/machine. Policy is loaded at startup; changes require restart. Without `access_file`, compatibility defaults permit both categories, but upload channels still require their own opt-ins. Omission is not deny-by-default.

Example structure for a managed host, using its actual existing scope:

```json
{"version":1,"scope":{"server":"https://control.example","namespace":"example","machine_id":"machine-id"},"permissions":{"upload":false,"command_execution":false}}
```

Do not replace an existing policy or invent a server/namespace binding while diagnosing access. `nymph access --config /absolute/path/to/udf-daemon.toml` reads and reports effective startup policy without running a worker. Its output does not attest to the configuration of an already-running PID.

## Commands and gates

The following inventory reflects `access.rs`, `drain.rs`, `ssh_runtime.rs`, and the corresponding server routes. It is a classification of effects and gates, not a grant to run the commands.

| Operation | Effect | Local boundary | Server/identity boundary |
|---|---|---|---|
| `nymph access` | Inspect policy and redacted settings | Local file read; no daemon launch | No remote execution grant |
| SSH usage GET | Read aggregate capacity | No local process start or config edit | Host ownership and namespace use in DreamLake; exact worker grant/admin on the control plane |
| SSH connection / forwarding tunnel | Start backend process and serve a bounded session | `[ssh].enabled`, `command_execution`, local capacity, allowed Unix user, backend probe | Exact enrollment/worker binding, SSH grant/delegation, signed daemon identity, current boot, key and ticket, expiry/revocation |
| `run` | Execute a queued invocation | `command_execution` plus configured runner/profile/resources | Authorized worker queue/claim and bound run |
| `exec` | Execute a remote command | `command_execution` plus exec/tracked/private-run constraints | Authorized worker command and applicable delivery/claim checks |
| `setup` and startup host setup | Execute host preparation | `command_execution`; denial clears startup host setup | Applicable server setup/launch authority; not implied by usage access |
| `ota_update` and automatic updates | Replace executable; restart behavior depends on build/supervisor path | Command execution gate; denial disables runtime automatic update | Existing signed/authorized update lifecycle and publication checks |
| `hibernate` | Suspend the polling lifecycle until its specified time | Explicitly allowed even with `command_execution=false` | Existing authenticated command channel |
| `drain` | Stop admitting work and run the shutdown/drain path | Explicitly allowed even with `command_execution=false` | Existing authenticated command channel |
| `reset_backoff` | Reset retry backoff | Explicitly allowed even with `command_execution=false` | Existing authenticated command channel |
| `rotate_key` | Rotate daemon signing identity, register under the old key and retain recovery behavior | Explicitly allowed even with `command_execution=false` | Existing daemon identity/key lifecycle |
| Session discovery, metrics, metrics objects, experiment reporting, job-output uploads | Send configured data | `upload` plus each channel's opt-in; denial disables them | Applicable authenticated upload destination and scope |
| Completion/control acknowledgments | Report control outcome, potentially without output | Control status can continue with uploads disabled | Bound command/run result channel |
| Unknown remote command | No supported operation | Ignored/rejected; never interpreted as config or shell | Does not gain authority from authentication alone |

`upload=false` is not a claim that no network traffic occurs: enrollment, heartbeats, command/control status and identity maintenance still need the service. `command_execution=false` is not a claim that every remote state change is disabled: the four lifecycle/key exceptions above remain. A capacity increase neither enables SSH nor grants workload execution. A saved terminal descriptor is not a running session.

SSH authorization and runtime configuration are separate from queue access. A queue mount does not grant host enrollment, exec or SSH delegation. A host's physical machine, worker ID, machine ID, host ID, enrollment ID, namespace and Unix user are distinct identities; retain exact bindings during diagnostics and changes.

## Configuration versus commands

Local TOML and the separate access policy define the startup snapshot. Existing server responses may supply protocol/runtime scheduling information, grants and typed commands; they are not a general permission to rewrite the local snapshot. When documenting a remotely mutable field, point to its actual parser and application path. Do not infer live mutability from a comment or an authenticated connection.

The SSH limit variables are control-plane operator settings, read once at startup. Nymph's `ssh.max_sessions` is local owner configuration, also startup-only. Environment/TOML edits alone do not alter an existing process. Local inspection is a read, an SSH Connect action is a session request, a restart is a lifecycle action, and a policy update is an authority change: interfaces and audit records must distinguish them.

For each future command or configuration field, record: name and version; caller; resource scope; local gate; server grant; effect; mutable phase; validation; idempotency/replay behavior; desired/effective state; audit fields; revocation; failure/rollback; and tests. Do not present desired configuration as applied or a successful write as a completed restart.

## Dynamic configuration proposal — not implemented

A future live-config command needs an explicit design and local opt-in before implementation. The owner should allowlist particular mutable fields and ceilings. A server operator cannot widen that local policy through the command it governs. Identity, credentials, executable paths, state directories and permission policy remain separate startup/admin operations unless explicitly designed otherwise.

A proposed update must include an authenticated actor, exact worker/enrollment scope, typed patch, expected configuration revision, stable idempotency key, expiry and reason. Reject unknown, unsupported, unauthorized and invalid fields atomically. Compare the expected revision before applying; a duplicate update returns its recorded outcome, and reconnect must not replay an expired or revoked update.

Expose desired and effective values, revisions, provenance, apply time and restart-required state. Record actor, scope, redacted changed fields, previous/new revision and outcome in an audit trail. Avoid credentials, full environment dumps and transcripts. Report partial application only if a future contract explicitly supports it; otherwise validate first and apply atomically with rollback on failure.

Define per-field semantics. Lowering a concurrent limit below current use should block new admissions and drain naturally by default. Terminating existing sessions is a separate operation with explicit authority. Increasing capacity must remain within local/OS limits and must not toggle execution/upload permissions. Define restart interruption, offline delivery, revocation, concurrent updates, controller failover and rollback before introducing automation.

Acceptance must prove that reads cannot mutate, capacity changes cannot enable SSH or bypass local execution denial, stale/unauthorized/unsupported updates cannot apply, retries do not duplicate effects, and users can distinguish pending from effective settings. This proposal does not authorize a config command, broader control-plane IAM, or changes to an existing owner's policy.

## Operating procedure and release evidence

Inspect exact identities, deployed versions, local effective startup settings and active usage before changing anything. Keep private paths/keys stable. Use existing service supervision for an authorized restart and verify the new PID/version and capability afterward. Re-enrollment may regenerate config; preserve or explicitly restore reviewed custom settings through its supported procedure.

Document source changes, tests, merge, rollout, live readback, docs deployment, skill release and installed-client version separately. A published document or skill does not establish a deployed capability. Changes to command authority or dynamic mutability require updating this inventory and its tests along with the implementation.
