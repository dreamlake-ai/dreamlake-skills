# Machine identities and provisioning

Use the installed CLI help and [service accounts reference](../reference/cli-service-accounts.md)
with the [providers reference](../reference/cli-providers.md). Authenticate and select
the intended environment using the `setup` action of `dreamlake-cli` before managing resources.
These APIs require a compatible server; an older CLI or server is not evidence
that a capability has shipped.

Before any workload or machine launch, verify the explicitly user-configured
launch server and its appropriate IAM role. Do not use or broaden control-plane
or service IAM, substitute ambient service credentials or an operator Vault IAM
user, or execute provider launches directly from the hosted backend. If the
server route is missing or unverified, stop new launch/provisioning actions and
report the gap. Preserve existing resources and unrelated service operation;
read-only inspection may continue. Current command/schema support and a direct
backend smoke do not prove this architecture is implemented. See the
[required launch boundary](../reference/cli-providers.md#required-launch-boundary).

With CLI 0.71.0 and the matching backend, enroll the server, read the provider's
current revision, then use `providers launch-server` with its exact enrollment,
expected role ARN, region and stable request ID. Follow the
[binding procedure](../reference/cli-providers.md#bind-a-launch-server); registration
alone does not prove execution readiness. A pending or uncertain cloud write
must be inspected through its durable operation receipt before another action.

A launch server manages cloud resources and must not consume shared jobs. An
enrolled worker claims from `default`, and removing `default` membership is not
supported. With CLI 0.92.0, run `dreamlake queues worker-claims <prefix>
<worker-id> --disable` and check that the printed value is `false`; heartbeat
and remote exec continue. See [stop a worker from claiming jobs](../reference/cli-queues.md#stop-a-worker-from-claiming-jobs).

For permission failures, use the [repair reference](../reference/cli-providers.md#fix-permission-limitations).
Record the actual role, denied action, region and request ID, then update the
dedicated role's Terraform policy with an identity authorized to administer it.
IAM policies can change after creation. Distinguish IAM from Kubernetes RBAC,
network access and explicit denies; never switch to service credentials.

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

Whether web terminal is enabled on host enrollment and on enrolled provider
launches, and since which CLI, is in [web terminal](../reference/cli-host-enrollment.md#web-terminal)
and [after an enrolled launch](../reference/cli-providers.md#web-terminal-after-an-enrolled-launch). The selected option enables Nymph SSH for that Unix user; the gateway discovers
the exact signed enrollment and authorizes bounded sessions through the owner account. Use `--no-web-terminal` to opt out;
never grant unrelated or previously enrolled workers as a side effect. This
requires the owner-scoped discovery/delegation API, a compatible control plane, Nymph 0.1.11+
and system OpenSSH. Report terminal readiness separately. A pending terminal
setup retains the launch receipt; retry the same request ID without creating
another instance. No personal login or SSH credentials go onto the host.

Check `hosts status` and the intended workload separately: launched, enrolled,
online, and workload-ready are distinct states. Never index terminal or workload
output automatically. Account revocation does not stop or terminate an instance;
if revocation delivery is pending, report it and retry rather than claim success.

This guide does not add SDK support, native filesystem capabilities, or an
arbitrary secret-export command. Use the corresponding task guides for uploads,
Notes, artifacts and workflows; their authorization and revision rules remain
unchanged.
