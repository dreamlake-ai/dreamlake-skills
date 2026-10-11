# Machine identities and provisioning

Use the installed CLI help and [service accounts reference](../reference/service-accounts.md)
with the [providers reference](../reference/providers.md). Authenticate and select
the intended environment using [setup](setup.md) before managing resources.
These APIs require a compatible server; an older CLI or server is not evidence
that a capability has shipped.

Create one namespace-owned service account for each Nymph daemon. Give it only
explicit project or host grants needed by its workload; the namespace owner
manages access. A service account is not a human login and does not inherit the
owner's access. Retrying account creation with identical name and description
recovers the same account; revoked names cannot be reused.

For automatic EC2 setup, pass `--host-name` to
`providers instances launch`, with `--count 1` and an explicit request ID. The
matching server creates a dedicated account, installs Nymph and the pinned CLI,
and delivers an instance-bound capability through KMS at runtime. Verify the
protected-delivery prerequisites before a billed launch; never put credentials
in user data. Use `--service-account` to select an unused account prepared with grants. Never copy human
login tokens or cloud credentials to a worker for this flow. Cloud launch is
billed and must be within the user's requested scope. Do not create extra hosts
as an implicit retry. Inspect a lost launch by its request ID before retrying
identical input.

Select workload software explicitly in the existing launch layers with
`agentSetup`: pinned `nodeVersion`, optional `codexVersion`/`claudeVersion`, and
opt-in `startCodexDaemon`. See the providers reference for the supported schema.
Omission installs no Node or harness and starts no agent daemon. Keep hardware,
software and startup choices in the user's project/preset; never invent cloud
values or inject vendor credentials. Preflight first and verify the matching
backend supports the field. Existing machines/retry receipts preserve their
original setup; changed choices require a new request ID. Readiness verifies
selected harnesses/skills plus signed machine access, independently of vendor
inference authentication.

For an existing enrolled host, create its dedicated account and use
`service-accounts bind --enrollment` to associate it without restarting Nymph.
Both identities must be in the same namespace; existing different bindings cannot
be replaced.

Use `dreamlake machine self` and a granted `machine host` or `machine project`
read on the provisioned host. Human login uses separate Unix credentials and
`--identity user`; it must not replace background machine credentials.

For current-computer registration, use `dreamlake hosts enroll --local --name
<namespace/group/host>`. Enrollment prints readable text by default; add `--json`
when a program needs the structured result, including pending and error receipts.
`--quiet` suppresses progress, not the final result. Text-output behavior requires
CLI 0.52.1; consult the host enrollment reference for local
Linux/macOS prerequisites. Keep the request ID for identical-input retries and
never treat a pending receipt as online.

Check `hosts status` and the intended workload separately: launched, enrolled,
online, and workload-ready are distinct states. Never index terminal or workload
output automatically. Account revocation does not stop or terminate an instance;
if revocation delivery is pending, report it and retry rather than claim success.

This guide does not add SDK support, native filesystem capabilities, or an
arbitrary secret-export command. Use the corresponding task guides for uploads,
Notes, artifacts and workflows; their authorization and revision rules remain
unchanged.
