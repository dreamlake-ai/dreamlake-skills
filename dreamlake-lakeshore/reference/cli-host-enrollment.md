<!-- generated from https://cli.dreamlake.ai/host-enrollment.md at 0.146.3 08ef5bd; do not edit -->

# Host enrollment

## Fabric: Add Host

Add Host establishes machine identity, connectivity and management for SSH,
browser terminals and remote commands. It does not require creating a queue,
mounting a queue server, or starting a queue consumer. The current backend uses
an authorized execution connection owned by the same DreamLake namespace as the
host name prefix; choose that connection before [enrollment](#enrollment).

A Runtime worker is a process that associates with a queue and consumes jobs.
The same Host can be used for development and run worker processes. Configure
worker queue association and consumption separately, then verify an actual job
completes; Host online status does not establish Runtime worker readiness. A
queue mount is client queue-access configuration, not Host or worker registration.
Its execution rejection is not evidence that Add Host is globally unavailable.
See [the layer boundaries](cli-queues.md#host-worker-and-queue-access-are-separate-layers).

An execution connection and matching owner namespace are necessary but not
sufficient. Its credential must explicitly authorize minting host-enrollment
grants on the deployed control plane. A normal namespace access token, an
`authMode: token` response, or a `legacy` connection label does not prove this
authority. Verify the deployed enrollment API and its credential capabilities
before claiming readiness; local source containing a scoped capability does not
prove that production supports it. Do not distribute the global admin token to
users as a workaround. If enrollment fails at grant minting, retain the existing
host identity and request ID, diagnose the authorization failure, and use the
supported retry flow after it is resolved. Do not rename or recreate the host
to bypass it.

SSH, remote commands and Session terminals have a separate authorization check.
On control-plane versions supporting scoped SSH delegation, an administrator
must grant the execution connection's namespace token access to the exact enrolled
worker using `POST /v1/namespaces/:ns/workers/:workerId/ssh-grants` with
`{"token_id":"<connection-token-id>"}`. `canEnrollHosts` alone does not grant SSH.
The connection can then request a short-lived, identity-bound SSH delegation;
revoking its token or worker grant invalidates derived sessions. Do not share the
admin credential or grant unrelated workers as a workaround. Verify a real SSH
command after deployment; online status or a terminal target listing is insufficient.
A stale/offline daemon must reconnect before execution can be verified.

## List and inspect hosts

In CLI 0.76.0 and later, bare `dl hosts` defaults to `hosts list`,
and accepts the same list options directly. `dl hosts -h` shows both
listing options and host commands; `dl hosts list -h` shows only listing
help. See [collection defaults](https://cli.dreamlake.ai/command-reference#collection-defaults-and-help).
Earlier releases require explicit `list`.

CLI 0.73.0 adds active-only listing and `--all`. Earlier versions list all
connection states without that flag.

`hosts list` reads every page of your hosts in one namespace, across all groups,
and shows only active hosts with at least one verified online enrollment. Use
`--all` to include offline hosts and hosts with unknown connection state.
Omit `--namespace` to use the signed-in personal namespace, or select another authorized namespace explicitly. `--group` accepts a single group name.

```bash cli-help="hosts list"
dl hosts list
dl hosts list --namespace geyang --group workstations
dl hosts list --json
dl hosts list --all
dl hosts list --wide
dl hosts --fields
dl hosts --format '{name} {user} {ips} {network_freshness}'
dl hosts --probe --format '{name} {ip} {public_ip} {macs} {uptime}'
```

The expanded inventory (CLI 0.104.3+) shows host ID, full name, catalog state,
verified connection state, hostname, Unix user, and IP addresses by default.
Use `dl hosts --wide` (or `hosts list --wide`) to add enrollment ID,
OS, architecture, CPU core count, Nymph version, and last-seen timestamp.
Each enrollment has its own row so observations from different daemons or Unix
users stay separate. The host total still counts distinct hosts. An active host
may have additional offline enrollments shown alongside its online enrollment.

Network and system inventory require the matching backend. Network addresses
also require Nymph 0.1.36+ reporting `capabilities.network`; Nymph 0.1.35 and
earlier do not report them. Older backends or daemons display `unknown` for
missing fields. No extra flag reveals information an older server does not send.
Default listings only read inventory; they never SSH to machines or probe public-IP services.

IP addresses are IPv4 and IPv6 interface observations from the daemon's network
namespace, including LAN, VPN, and container interfaces. Down, loopback,
link-local, unspecified, and multicast addresses are excluded. They are not a
promise of reachability or a NAT public-IP lookup. A successful empty observation
shows `none`; unavailable or invalid observations show `unknown`. Samples older
than 90 seconds, or from an offline enrollment, are marked `(stale)`.

`hosts status HOST` includes interface names, address families, network sample
time and freshness, CPU model, and machine ID for each enrollment. OS, CPU, and
version information is reported inventory, not live utilization; use
[`hosts metrics`](#inspect-resource-samples) for timestamped resource usage.

`--format '<template>'` prints only one formatted line per enrollment, without
headers or footers. Use `--fields` to list the complete placeholder catalog
offline, or `--fields --json` for its machine-readable form. Unknown fields and
unbalanced braces fail before contacting the service. `--format` cannot be
combined with `--wide` or `--json`; `--fields` cannot be combined with `--wide`,
`--format`, or `--probe`. Templates are literal text, never shell commands.

Common fields are `{name}`, `{id}`, `{enrollment}`, `{user}`, `{hostname}`,
`{ip}` (first IPv4, then IPv6), `{ips}`, `{ip_source}` (`inventory` or `ssh`),
`{interfaces}`, `{network_observed_at}`, `{network_freshness}`, `{platform}`,
`{arch}`, `{cpu_model}`, `{cpu_cores}`, `{nymph_version}`, and `{seen_ago}`.
Custom address fields retain plain IPs; include `{network_freshness}` to show
whether they are stale. IPs are never inferred from hostnames.

For older daemons or additional network diagnostics, explicitly request `--probe`.
It opens pinned DreamLake SSH sessions for verified online enrollments, at most
two concurrently, and runs a read-only Python 3 script. The script uses Linux
`ip` or macOS `ifconfig` for non-loopback interface IPs and MAC addresses, reads
system uptime, and calls `curl https://ifconfig.me/ip` for public egress IP.
No packages are installed. Unlike the default listing, this contacts each
selected online host and an external public-IP service. Public egress IP may be
shared by machines behind NAT. Use `--group` to limit the inspected hosts.

Probed tables add public IP, MAC, uptime, and connection-duration columns.
`{public_ip}`, `{mac}`, `{macs}`, `{uptime}`, and `{uptime_seconds}` are probe
fields. `{online_for}` is connection duration, and stays unknown unless the
backend supplies `connectedAt`; it is never inferred from uptime or heartbeat
age. `{observed_at}`, `{probe_status}`, and `{probe_error}` describe the probe.
Results are attached to the exact enrollment's `probe` object in JSON and are
not persisted. Offline and unverified enrollments are skipped. Failed or partial
probes remain in the output and cause a nonzero exit without discarding successes.
The command timeout is 30 seconds after relay setup; delegation can take longer.
A failed interface probe falls back to available reported inventory, retaining
its original timestamp and freshness.

An older backend without catalog metadata shows catalog state as unknown. JSON returns
`namespace`, optional `group`, `hosts` (the original host/enrollment records), and
`total` (the number of distinct hosts shown after filtering). With the matching
backend, enrollment records add `network` (`observedAt`, `addresses` with
`interface`, `address`, and `family`) and `system` (`os`, `arch`, `cpuModel`,
`cpuCores`, `nymphVersion`). Missing observations are nullable. `--wide` affects
text formatting only; JSON always retains all available fields. A failed page fails
the command; it does not emit a successful partial listing. Pagination reads a live inventory,
not an atomic snapshot; hosts added or removed during the read can change results.

Inspect a full name or the 24-character host ID returned by the API. An ID uses
the personal namespace unless `--namespace` is supplied; a full name already
contains its namespace, and a conflicting flag is rejected.

```bash cli-help="hosts status"
dl hosts status geyang/workstations/worker
dl hosts status HOST_ID --namespace geyang --json
dl hosts status 'geyang/workstations/*' --page 2 --page-size 100 --json
```

Exact status shows a readable enrollment table by default; `--json` preserves the
backend detail response. The existing wildcard status continues to return one
paginated JSON response even without `--json`. Use `hosts list --all` for all
pages and connection states.

Connection is `online` when an enrollment has a verified online observation,
`offline` when every enrollment is verified offline, and otherwise `unknown`.
The enrollment table separately shows the reported state, verification flag, and
last-seen timestamp. A stored offline/pending state without runtime verification
does not establish current availability. The `hosts status` response does not
report power, SSH readiness, or job readiness; status displays these as `unknown`.
An online connection alone does not prove that SSH or any particular workload can run.

## Archive and restore catalog records

Catalog commands require CLI 0.73.0+ and the matching backend API. Archiving only hides a Host from the default catalog list. Runtime,
enrollments and credentials remain active, and archiving does not prevent future
work. It does not retire a machine, verify inactivity, stop a service, cancel a
job, revoke access or terminate a cloud resource.

Host and enrollment IDs, reserved names and job/history links remain unchanged.
Exact `hosts status` and `hosts enrollments` lookups by ID or full name still work.
List filters affect visibility, never authorization:

```bash
dl hosts list --namespace geyang --all --archived include
dl hosts list --namespace geyang --all --archived only
```

`--all` controls connection state; `--archived` controls catalog visibility.
Use both flags to include offline archived hosts. Permanent entry deletion is
not supported.

Read the catalog revision before submitting a change. Lifecycle commands require
one exact full `namespace/group/host[/user]` name or lowercase 24-character Host ID.
Full names supply the namespace; an explicit `--namespace` must match. Name lookup
includes offline and archived hosts and rejects ambiguous matches. Partial names
and wildcards are not accepted. Use the revision returned by the read; `0` below illustrates a record with no prior catalog changes.

```bash cli-help="hosts lifecycle"
dl hosts lifecycle geyang/dev/my-host --json
dl hosts lifecycle HOST_ID --namespace geyang --json
```

```bash cli-help="hosts archive"
dl hosts archive geyang/dev/my-host --request-id archive-example-1 --expected-revision 0 --json
```

```bash cli-help="hosts restore"
dl hosts restore geyang/dev/my-host --request-id restore-example-1 --expected-revision 1 --json
```

Every accepted new request increments the revision, including archiving an
already archived record or restoring an active record. The original archive
timestamp is retained by repeated archive actions. Restore clears that timestamp.
All responses state `executionAffected:false` and `retirementSupported:false`.

Retain the request ID, Host ID, namespace, action and expected revision. After an
ambiguous transport failure, use the resolved Host ID and namespace reported in
the error to repeat that exact request, even if the host name has changed; the CLI never retries or
refreshes the revision automatically. Reusing a request ID with different inputs
returns `409 request_id_conflict`. A stale revision returns
`409 catalog_revision_conflict`; inspect the current catalog state before choosing
a new operation. Request IDs are scoped to the authenticated user across hosts
and namespaces and are distinct from enrollment request IDs.

A retry returns the stored original receipt even after a later opposite action.
`replayed:true` describes that receipt, not the Host's current catalog state;
use `hosts lifecycle` for current state. Current namespace and Host ownership are
required for retries as well as new actions. JSON retains operation/request IDs,
revision, catalog state and timestamps. Runtime or work admission is unchanged.

## Inspect enrollments

The read-only `enrollments`, `metrics`, and `check` commands below require CLI
0.57.0 or later. Metrics and action checks also require the matching backend with
revoked-enrollment metrics protection and action checks. Availability depends on
both deployments.

`hosts enrollments` inspects your enrollments on one host using its full name or
host ID. The namespace rules match `hosts status`; wildcards are not accepted.
This is read-only and does not retire, revoke, restart, or delete anything.

```bash cli-help="hosts enrollments"
dl hosts enrollments geyang/workstations/worker
dl hosts enrollments HOST_ID --namespace geyang --json
```

The output separates the host ID, canonical enrollment ID, and runtime machine
ID. Check the installed `nymph --version` and `nymph daemon --help` before local
inspection. Nymph 0.1.20 provides read-only `nymph daemon list` and
`nymph daemon status` with enrollment-ID selection; neither host ID nor machine
ID is a substitute. Selection requires trusted, reachable inspection of the same
process and an enrollment confirmed by hello. Verification covers Linux only
and does not establish a fleet upgrade, lifecycle controls, or a singleton
guarantee. An unavailable inspection endpoint does not prove the daemon stopped.
Each enrollment shows the backend's observed `state`, `lastSeenAt`, and
`statusVerified`, including unknown values.

Observed-presence freshness is `fresh` only when `statusVerified` is true and
`lastSeenAt` is at most 60 seconds before the CLI's read time, matching the
backend's presence window. A verified older observation is `stale`. Missing,
invalid, future, or unverified observations are `unknown`; the client does not
rewrite the reported state. Fresh observed presence does not establish SSH or
job readiness, and stale presence does not establish that a daemon has stopped.

JSON returns `host`, `readAt` (the CLI's clock), `presenceWindowSeconds`, and an
`enrollments` array. Each entry retains the identity and observation fields above
and adds `presenceFreshness` and `lastSeenAgeSeconds` (null when unknown).
An empty enrollment array is a successful read. Access or transport failures
exit nonzero without claiming an empty result.

## Inspect resource samples

Select a host and an exact enrollment ID from `hosts enrollments`; the CLI does
not choose an enrollment or combine readings across enrollments.

```bash cli-help="hosts metrics"
dl hosts metrics geyang/workstations/worker --enrollment ENROLLMENT_ID
dl hosts metrics HOST_ID --namespace geyang --enrollment ENROLLMENT_ID --resolution 60 --json
```

Text shows the latest CPU percentage, RAM and disk bytes, source sample timestamp,
source `stale` flag, and sample freshness at the CLI's read time. Source-backed
enrollments require CLI 0.65.1 or later: the command follows a short-lived signed
GET directly to Source storage, bounded to 2 MiB and 30 seconds. JSON includes
the requested history tier and readings, never the capability URL or headers.
Pending uploads and a missing first snapshot remain empty; denied or failed
Source reads fail without a legacy data proxy. Unconfigured enrollments keep
the existing transport. Missing metrics
are `unknown`, including when `latest` is null; an actual zero stays zero.
Samples older than 90 seconds or marked stale by the source are `stale`.
Missing/invalid timestamps and timestamps ahead of the client clock are `unknown`.
Readings do not establish SSH or workload readiness.

JSON retains the backend's `latest`, `tiers`, and `stale` fields and adds
`hostId`, `enrollmentId`, `resolution`, `readAt`, `sampleFreshness`, and
`sampleAgeSeconds` (null when unknown). Source timestamps are Unix seconds;
CPU is percent, memory/filesystem values are bytes. History resolution accepts
10, 60, 900, or 3600 seconds (default 60). A missing sample is a successful read;
access, revoked enrollment, identity, or transport failures exit nonzero.

## Check observed action capability

```bash cli-help="hosts check"
dl hosts check geyang/workstations/worker --enrollment ENROLLMENT_ID --action ssh
dl hosts check HOST_ID --namespace geyang --enrollment ENROLLMENT_ID --action tracked-run --json
```

Both `--enrollment` and `--action` are required. The command reads the backend's
exact enrollment verdict: `ready`, `not_ready`, or `unknown`, with its reason,
`checkedAt`, `observedAt`, and observation age. `ready` means a recently observed
advertised capability; it does not verify an SSH handshake or execute a job.
`tracked-run` covers ordinary uv-run/uvx capability, not private setup or every
runner. SSH checks retain the backend's personal-owner access policy.

The backend applies a 30-second observation window for SSH and 60 seconds for
tracked runs. Missing, stale, ambiguous, unverified, or unavailable observations
remain `unknown`; a fresh explicit lack of capability is `not_ready`.
JSON preserves this verdict and its identity/timestamp fields. Exit status is
zero only for `ready`; `not_ready`, `unknown`, and request failures exit one.
No grant, handshake, job, enrollment change, or machine lifecycle action occurs.

## Set a Ripple upgrade target

**CLI and TypeScript 0.142.0+:** requires the matching server Ripple target API.

A Ripple host-metrics collector that was started with automatic updates turned
on installs the version its enrollment's target names. `hosts ripple-target`
reads, sets, or clears that target for one exact enrollment, with no
redeployment. Only the Host owner who holds `lakeshore:use` in the namespace
can read or change it. Callers without `lakeshore:use`, including connection
grantees, get `forbidden`; other members who hold it but do not own the Host
get `host_not_found`. Setting the target on one enrollment never changes any
other.

```bash cli-help="hosts ripple-target get"
dl hosts ripple-target get geyang/workstations/worker --enrollment ENROLLMENT_ID
dl hosts ripple-target get HOST_ID --namespace geyang --enrollment ENROLLMENT_ID --json
```

```bash cli-help="hosts ripple-target set"
dl hosts ripple-target set geyang/workstations/worker --enrollment ENROLLMENT_ID --version v0.5.0
```

```bash cli-help="hosts ripple-target clear"
dl hosts ripple-target clear geyang/workstations/worker --enrollment ENROLLMENT_ID
```

The host selector and `--namespace` follow `hosts metrics`; `--enrollment` is
required and the CLI never picks or fans out to other enrollments. `--version`
accepts only a stable release tag, `vMAJOR.MINOR.PATCH` without leading zeros,
of at most 32 characters. `latest`, pre-release and build suffixes are refused
before any request is sent. Neither the CLI nor the server checks that the
version is published, so set only a released Ripple version.

Text output shows `Ripple target:` with the version or `none`, the Host ID, the
enrollment ID, and when the target last changed. JSON returns `hostId`,
`enrollmentId`, `targetVersion` (null when there is no target), and `updatedAt`
(null when it was never set). `set` and `clear` are idempotent: after an
uncertain outcome, rerun the same command or read the target with `get`.
Refusals exit 1 and name the server's code, such as `invalid_target_version`,
`forbidden`, `host_not_found`, or `enrollment_not_found`.

The collector sees a change on its next accepted delivery, within about 30
seconds. A collector without automatic updates ignores the target. A collector
with automatic updates installs only a version strictly newer than the version
it is running, so clearing a target or setting an older version never rolls a
host back. The TypeScript API exposes the same operations as
`hosts(namespace).rippleTarget(hostId, enrollmentId)` and
`hosts(namespace).setRippleTarget(hostId, enrollmentId, version | null)`.

## Enrollment

`dl hosts enroll` bootstraps a user-owned nymph on this computer with
`--local`, or over an existing SSH connection with `--ssh`. It waits for the
backend to confirm that exact enrollment online.
Provider registration is not required. It requires the new authenticated Hosts
API and a control plane supporting identity-bound grants and signed reconnect;
these changes must be deployed together. `--dry-run` only validates inputs and
does not contact the server or target.

The target needs Python 3 and OpenSSL with Ed25519 support. Linux additionally
needs an accessible systemd user manager and user linger for persistence after
logout. macOS uses the logged-in user’s launchd GUI domain (see below).
Enrollment never uses sudo.
It reuses an installed `nymph`, or downloads the official installer into the
user-local binary directory. `--nymph-version` selects an installer version when
the binary is absent. The target generates and retains its nymph private key;
only its public key and Unix username go to the enrollment API. Short-lived
grants travel through bootstrap process stdin (over SSH only for remote
enrollment), not process arguments or logs.

For a Linux SSH target, check the account before enrollment:

```shell
ssh bos14-ctrl 'systemctl --user show-environment >/dev/null && loginctl show-user "$(id -un)" -p Linger --value'
```

If this prints `no`, enable lingering for that account:

```shell
ssh bos14-ctrl 'loginctl enable-linger "$(id -un)"'
```

If local policy denies this operation, ask the host administrator to enable it.
Enrollment checks these prerequisites before creating an identity or requesting
a grant.

Use `--lakeshore-id` when your namespace has multiple control-plane connections.
Select an execution connection owned by the same DreamLake namespace as the
host's `--name` prefix. An org-owned connection for `acme` can enroll an authorized
`acme/workstations/alice-mac` host; `alice/workstations/alice-mac` requires an
`alice`-owned execution connection. The server filters connections by that owner
namespace, so a cross-namespace ID can return `lakeshore_not_found` despite being
visible in the UI. Remote Lakeshore namespaces and connection labels do not
change this rule.

A Vault-backed queue mount is not an execution connection. Even when queue
inspection is online, enrollment rejects that mount with HTTP 409
`queue_mount_execution_unsupported`. Resolve the intended host owner and its
authorized execution connection before running enrollment. See
[connection ownership](cli-queues.md#ownership-execution-and-namespace-names).

The command prints a request ID once the target identity is known. A rerun of
the same logical enrollment reuses it automatically. A logical enrollment is the
same DreamLake API, host name and transport (`--local`, or the same `--ssh`
arguments) for the same target identity. Without `--request-id`, the rerun
behaves as follows:

- If the backend already confirmed the enrollment online, the rerun sends no
  new enrollment request and gets no grant. It refreshes the target's
  configuration and repeats only the remaining steps, such as Ripple or the web
  terminal. The receipt reports `resumed: true`.
- Otherwise it repeats the saved request. If that request has expired on the
  server, it is replaced once by a new one.

The saved state is `~/.dreamlake/host-enrollments/<key>.json` (mode 0600). It
holds identifiers only (request, host, enrollment and machine IDs, the public
key, Unix user and control-plane URL), never a grant, token, private key or SSH
credential. A different target identity, name, transport or API never uses it,
and an explicit `--request-id` is never replaced.

A pending, partial or failed result includes `retry.command`, printed as
`Retry (resumes this enrollment): …` or `Retry: …`. It rebuilds the command from
the validated inputs with `--request-id`, for `--local` or with the exact
`--ssh` arguments. It never includes passwords, Vault entries, key exports,
password descriptors or credential-saving consent. If the API returns `retryAt`,
wait until that time before starting a new request. JSON errors retain the
request ID and available operation/retry fields.
`--wait-seconds` bounds readiness polling (default 60). A timeout reports
`pending` and exits nonzero; it does not claim enrollment succeeded. Repeat
execution preserves the target identity and reuses the user service. Runner/job
readiness is a separate check from a connected nymph.

## Web terminal

Starting in CLI 0.53.0, web terminal access is enabled by default. `--web-terminal` explicitly selects
it; `--no-web-terminal` opts out. Enrollment JSON accepts `"webTerminal": false`.
The enabled choice configures Nymph for browser SSH as this exact Unix user.
The gateway discovers the signed enrollment automatically. Opening a terminal
authorizes a bounded session through your owner account; setup needs no manual
per-worker grant. Your SSH credentials stay local and no inbound port is opened.

Web terminal setup requires Nymph 0.1.11 or newer and an installed OpenSSH server.
On Linux, the host administrator must provide OpenSSH's root-owned `/run/sshd`
directory. Enrollment reports terminal setup separately from Nymph's online
status and gives a retry action if terminal readiness is still pending.

```bash
dl hosts enroll --local --name geyang/dev/my-mac --web-terminal
# Enroll without browser shell access.
dl hosts enroll --local --name geyang/dev/my-mac --no-web-terminal
```

## Ripple metrics collector

**CLI 0.144.0+:** requires a server that accepts Ripple
enrollment bindings and the published Ripple v0.6.0 release.

After the backend confirms the enrollment online, `dl hosts enroll` (`--local`
or `--ssh`) installs the Ripple host-metrics collector on a new enrollment.
`--no-ripple` skips it; `--ripple` installs it explicitly. The web Compute
**Enroll** dialog builds the same command and adds `--no-ripple` when you turn
metrics off.

```bash
# Enroll without the metrics collector; later runs remember this choice.
dl hosts enroll --local --name geyang/dev/my-mac --no-ripple
# Install the collector on an existing enrollment.
dl hosts enroll --local --name geyang/dev/my-mac --ripple
```

The choice belongs to the enrollment and is stored on the target, next to the
enrollment's identity key. Without either flag:

- A new enrollment installs Ripple.
- A rerun keeps the recorded choice, so an earlier `--no-ripple` stays off.
- An enrollment created before this setting has no recorded choice and gets
  nothing installed until you pass `--ripple`.

Listing, sharing, upgrading or inspecting a host never installs Ripple, and
`dl nymph setup` does not install it. Choosing Ripple turns off Nymph's own
`[metrics]` readings in this enrollment's generated `nymph.toml` only, and
`--no-ripple` removes only the table enrollment added; see
[Nymph's own metrics](#nymphs-own-metrics). When that file changes, only this
enrollment's Nymph service restarts to read it. The choice never changes
another enrollment's Nymph service or identity, or the Nymph access policy.

Enrollment creates any missing directory it needs with an exact mode. Its
state directories are 0700, and `~/.config/systemd/user`,
`~/Library/LaunchAgents` and `~/.local/bin` are 0755. This holds under any
umask, including Ubuntu's default 0002. Existing directories are never changed.
Before Ripple runs, enrollment checks the directories Ripple will use: the user
service directory and Ripple's state directories. Each must be a real
directory owned by the enrolled user that no one else can write. Otherwise
Ripple is not run, and the result is `failed` with `reason` `state_unsafe` and
the exact repair in `action`, for example
`chmod go-w '/home/alice/.config/systemd/user'`. Run it as that user, then rerun
the same command.

Setup runs on the target as the enrolled Unix user. It downloads
`setup-compute.sh` from the immutable Ripple `v0.6.0` release directory. The CLI
pins that script's SHA-256
(`87ed45d3ca0ba38958b0bffbb92ee7892dd6fbfa8fdcf2c70417b1421614282d`). Setup runs
the script only when the downloaded bytes match this pin and the release's
`setup-compute.sh.sha256` and `SHA256SUMS` both name them. On any mismatch
nothing runs and the result is `failed` with `reason` `helper_digest_mismatch`.
Setup identifies itself to the release host with the User-Agent
`DreamLake-CLI (dl hosts enroll; Ripple setup)`. The script receives the
DreamLake API URL, the enrollment ID and machine ID issued by the server, and
the path of the enrollment's existing `identity.key`. It binds the collector
to that enrollment with a signature from this key. The private key, the
collector token and your DreamLake login never leave the target or appear in
arguments. Setup does not log in to DreamLake on the target. Setup also stops
if the target's key or Nymph machine ID does not match this enrollment.

The receipt reports Ripple separately from the core enrollment, as `ripple` in
JSON and a `Ripple metrics:` line in text. A Ripple result never changes the
core result or the exit code. To retry, rerun the same `dl hosts enroll`
command.

| `ripple.status` | Meaning |
| --- | --- |
| `ready` | The server returned a fresh Ripple sample, taken after this install, with CPU and memory readings. |
| `awaiting_data` | Installed and bound, but the server cannot yet show a fresh Ripple sample. `reason` is `no_fresh_sample` or `origin_unsupported`; see below. |
| `pending` | Bound, but the collector's service is not running yet, for example because the Linux user has no systemd user manager or the Mac has no logged-in session. `action` says what to do on the target. |
| `failed` | Not installed. `reason` is the setup step or the helper's own reason, for example `helper_unavailable`, `helper_digest_mismatch`, `server_unsupported`, `binding_conflict` or `clock_skew`. `retryable` and `action` come from the helper when it reports them. |
| `disabled` | `--no-ripple` now or on an earlier run, or `reason` `host_opted_out` when the host opted out with `setup-compute.sh --opt-out`. |
| `not_requested` | An enrollment from before this setting, or a managed `dl nymph setup`. |
| `skipped` | The core enrollment is still pending, so Ripple was not started. |

Readiness is read from the server, never from the target. Only this check asks
the enrollment's metrics with `origin=ripple`. The server must label the answer
`metricsOrigin: "ripple"`, so a Nymph metrics Source or other readings on the
same enrollment never count. A ready sample must be fresh (at most 90 seconds
old and not stale). It must carry `cpu_percent`, `memory_used_bytes` and
`memory_total_bytes`, and be taken after the install started. If a Ripple sample
was already on the server, for example on a retry, the new one must be newer.

The `awaiting_data` reasons:

- `no_fresh_sample`: no qualifying sample arrived during the wait. The wait is
  90 seconds, or `--wait-seconds` when you pass it.
- `origin_unsupported`: the server does not label Ripple samples, so the CLI
  cannot confirm delivery and never reports `ready`.

### Nymph's own metrics

Ripple replaces Nymph's built-in resource readings. When Ripple is on for an
enrollment, enrollment adds this table to that enrollment's own generated
`nymph.toml`:

```toml
[metrics]
# dl hosts enroll: Ripple reports this enrollment's host metrics
enabled = false
```

Nymph 0.1.9 to 0.1.33 turns these readings on by default, and 0.1.34 and later
turn them off. Nymph 0.1.8 and earlier has no `[metrics]` table and rejects
unknown tables, so enrollment never adds it there. The version is read from the
installed Nymph binary, including one installed with `--nymph-version`.

The table is added when Ripple is chosen, before the collector is set up. If
Ripple setup then fails, Nymph 0.1.9 to 0.1.33 still sends no readings of its
own until Ripple runs or you turn Ripple off.

A `[metrics]` table that you wrote yourself, including `enabled = true` or an
opt-out, is carried over unchanged. Enrollment stops without changing anything
if it cannot carry the table over exactly. Turning Ripple off later removes
only the table that enrollment added. Managed `dl nymph setup` configurations
never get this table.

Check later samples with `dl hosts metrics`.

## Agent session metadata

A new enrollment turns on Nymph's agent-session metadata channel by writing
`[sessions] enabled = true` to its `nymph.toml`. This covers the standard
`dl hosts enroll` (`--local` or `--ssh`, as shown in the web Compute guide) and
`dl nymph setup`. Nymph then lists your local Codex and Claude sessions in
DreamLake as private entries. It sends only metadata: provider, session ID,
working directory, title, activity times, run state and repository root/status.
The title is the one the agent app records (a name you set, or a title or summary
the app generated), so it can describe the conversation. Nymph never sends
transcripts, prompt or message text, tool output or Git remote URLs, and it never
changes a session's visibility. Uploading a full transcript remains a separate
action that you start yourself.

The channel is still gated by Nymph at startup:

- **Local consent:** `dl nymph setup` starts with uploads denied in its
  `access.json`, so no session metadata is sent until
  `dl nymph access grant upload` and a restart. A local policy with `upload = false` always wins.
- **Destination:** only the production control plane
  (`https://api.lakeshore.dreamlake.ai`) has a default destination. Other
  control planes stay silent unless `api_origin` is set.
- **Enrollment:** each request is signed by the enrolled identity. A daemon
  without a confirmed enrollment binding sends nothing, and the API rejects
  revoked enrollments.

Nymph turns on no other automatic uploads (metrics, experiment reporting, job
output). Host metrics come from the separate Ripple collector; see
[Ripple metrics collector](#ripple-metrics-collector).

Existing enrollments keep their settings. Repeating enrollment preserves the
current `[sessions]` table exactly: absent stays off, `enabled = false` stays
off, and `enabled = true` keeps its roots and options. Existing settings must
also pass the installed Nymph's own check (Nymph 0.1.32 or newer). Enrollment
cannot preserve them in some cases: multi-line values, quoted or dotted keys,
duplicates or unknown keys. It then stops without changing anything; simplify
`[sessions]` and retry. A brand-new enrollment on an installed Nymph older than
0.1.32 gets no default.

Enrollment also stops, before changing anything, rather than replace a local
access policy:

- `dl hosts enroll` does not re-enroll a computer that has a policy from
  `dl nymph setup`; use `dl nymph setup` for that enrollment.
- `dl nymph setup` does not re-enroll a computer whose `nymph.toml` points
  `access_file` anywhere other than that enrollment's own `access.json`.

To opt out, set `enabled = false` under `[sessions]` and restart the service.
Later enrollments keep that choice.

## Output format

Enrollment prints a readable summary by default, including the host name,
verified connection state, and recovery identifiers. Errors also use readable
text. Use `--json` for a structured success, pending, validation, or error receipt;
JSON mode suppresses the introductory request-ID progress line. `--quiet`
suppresses progress only and does not select JSON or hide the final receipt.
These output changes require CLI 0.52.1.

```bash cli-help="hosts enroll"
# Human-readable output (default).
dl hosts enroll --local --name geyang/dev/my-mac
# Structured output for scripts.
dl hosts enroll --local --name geyang/dev/my-mac --json
# Enroll without the Ripple metrics collector.
dl hosts enroll --local --name geyang/dev/my-mac --no-ripple
```

A successful default summary starts with:

```text
Registered geyang/dev/my-mac. Nymph is online.
Host ID: <host-id>
Enrollment ID: <enrollment-id>
Machine ID: <machine-id>
Request ID: <request-id>
```

A pending result exits nonzero and explicitly says enrollment is pending;
it does not report the host online. JSON field names and exit codes are unchanged.

## Register this computer

On Linux or macOS with Python 3 and OpenSSL Ed25519 support, register the
current Unix account directly. Linux uses a systemd user manager with linger;
macOS uses a LaunchAgent in your logged-in graphical user session. macOS support
is added in CLI 0.52.0. No loopback connection or SSH credentials are needed.
The default web terminal option additionally requires the system OpenSSH server.

```bash
dl hosts enroll -n geyang/lab/current-computer --local --dry-run
dl hosts enroll -n geyang/lab/current-computer --local \
  --request-id current-computer-001
dl hosts status geyang/lab/current-computer --json
```

`--local` is mutually exclusive with `--ssh` and SSH credential-saving options.
Enrollment JSON can use `"local": true` instead of `"ssh": {...}`. The identity
key stays on this computer, grants travel through process stdin, and the same
user service and exact enrollment verification are used for both transports.
Windows local enrollment is not supported. macOS enrollment must run as your
normal logged-in user, without sudo. A headless SSH session without a graphical
login is not sufficient. Dry-run validates input and does not install or register anything.

Once status is verified online, run a small job (requires a Nymph build with
tracked-run support and `uv` available to the user service):

```bash
printf 'import socket; print("Hello from", socket.gethostname())\n' > hello.py
dl run --target geyang/lab/current-computer --include hello.py \
  --request-id local-hello-001 --timeout-seconds 60 --uv-run python hello.py
```

The command waits for the result and displays its output. Registration alone
does not prove job execution readiness; use the completed run as the check.

## macOS prerequisites and service lifecycle

Use CLI 0.52.0 or newer. Install Python 3, `uv` and OpenSSL 3 using your chosen
package manager if they are absent. For Homebrew:

```shell
brew install python uv openssl@3
dl hosts enroll --local --name YOUR_NAMESPACE/dev/my-mac \
  --nymph-version v0.1.11
dl hosts status YOUR_NAMESPACE/dev/my-mac --json
```

Starting with CLI 0.71.0, a version such as `0.1.26` is normalized to the published
`v0.1.26` installer tag; already prefixed tags and `latest` are preserved.

An existing Nymph binary on PATH is reused; `--nymph-version` selects the
installer version only when Nymph is missing. To move an enrolled host to another release,
use [`hosts upgrade`](#upgrade-nymph-on-enrolled-hosts). Check an existing daemon's version
before relying on tracked-run support. Homebrew's OpenSSL 3 is discovered under
both `/opt/homebrew` (Apple Silicon) and `/usr/local` (Intel). Apple's bundled
LibreSSL may not support the required Ed25519 operation; enrollment checks this
before creating identity material. No package manager is invoked automatically.

The agent lives at `~/Library/LaunchAgents/ai.dreamlake.host.<hash>.plist`;
`<hash>` is the first 24 hex characters of SHA-256 of the full host name.
Nymph runs as you, restarts on failure, starts at login and survives closing
Terminal. It is available while your graphical user session is active; logout,
sleep or shutdown can make the host unavailable. It does not run as root or
promise execution while the Mac is asleep. Review background-item permissions
in System Settings if macOS blocks the agent.

The service PATH includes `~/.local/bin`, `/opt/homebrew/bin`, `/usr/local/bin`
and system binaries, so standard `uv` installations are visible. Key, grant,
config and plist are private (0600); grants stay out of argv and the plist.
Daemon stdout/stderr are discarded rather than saved to an unreviewed log file.
Tracked job status and output remain available through `runs status`/`runs logs`.

Re-enrollment preserves the identity key. An unchanged loaded agent is started
without killing a healthy process; changed configuration reloads only that
agent. If launchd fails, enrollment exits unsuccessfully and preserves identity
material for retry. Reuse the printed request ID after an interrupted request.

To stop one local agent, identify its exact label from that host's plist and run
`launchctl bootout "gui/$(id -u)/ai.dreamlake.host.<hash>"`. This stops local
execution; it does not revoke the server enrollment or remove credentials.
Preserve the key for recovery and use the owning host's revocation procedure
when retiring it. Do not remove other LaunchAgents or identity directories.

Apple's [LaunchAgent documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
describes the per-user service model. Portable adapter regressions exercise
failure/retry behavior; the macOS CI job separately uses real launchd with an
offline worker fixture. Neither replaces authenticated end-to-end acceptance on
a real Mac against the deployed control plane.

## Register another computer

```shell
dl hosts enroll -p fortyfive/bos14 -n bos14-ctrl --ssh bos14-ctrl
dl hosts status fortyfive/bos14/bos14-ctrl --json
dl hosts status 'fortyfive/bos14/*' --json
```

For configuration-only validation:

```shell
dl hosts enroll -p fortyfive/bos14 -n bos14-ctrl \
  --ssh bos14-ctrl --dry-run

# Equivalent full name, with structured output:
dl hosts enroll -n fortyfive/bos14/bos14-ctrl \
  --ssh '-i "/Users/ge/My Keys/key" \
    -J ge@bastion.example.com \
    -p 2222 geyang@bos14-ctrl.internal' --dry-run --json
```

Names accept `namespace/group/host/user` (preferred) and legacy `namespace/group/host`. A matching explicit
prefix and embedded prefix are accepted; conflicting prefixes and wildcards are
rejected. The first three components are 1–64 letters, digits, underscores or hyphens and start
with a letter or digit. The optional final user is a Unix account name and must match
the account reported by the enrolled daemon; it permits dots and a trailing `$`. A namespace in a name does not grant access to it.
The control-plane namespace comes from the selected connection and can differ
from the DreamLake namespace.

## JSON input

```shell
dl hosts enroll --config ./bos14-host.json --dry-run --json
```

```json
{
  "name": "fortyfive/bos14/bos14-ctrl",
  "ssh": {
    "host": "bos14-ctrl.internal",
    "user": "geyang",
    "port": 2222,
    "identityFile": "/Users/ge/.ssh/bos14_ed25519",
    "jumpHost": "ge@bastion.example.com",
    "options": { "ServerAliveInterval": "30" }
  }
}
```

The file may also contain `prefix`. Explicit CLI name/prefix fields override
those file fields, then prefix conflicts are checked. `--ssh` replaces the
entire file SSH object. Unknown fields are rejected. Identity files are local
paths, never embedded key contents. Use either `ssh.user` or `user@host`, not both.
`--json` controls output only.

SSH argument text is tokenized without shell expansion or evaluation; multiline
whitespace, line continuations, and quoted paths are supported. Do not include
`ssh` itself or a remote command. The initial supported flags are `-i`, `-J`,
`-p`, `-o`, `-l`, and `-F`, each followed by a separate value. Supported `-o`
settings are BatchMode, ServerAliveInterval, ServerAliveCountMax, ConnectTimeout,
IdentitiesOnly, StrictHostKeyChecking, and UserKnownHostsFile. Use an existing
SSH config alias for more advanced transport settings. Preview validates syntax,
not whether an identity file exists, an SSH alias resolves, or SSH authentication works.
Passwords are not accepted in arguments or JSON. Future interactive enrollment
should let OpenSSH prompt for target/jump-host passwords locally; the preview
does not attempt authentication and does not require agent forwarding.

Group status accepts `--page` (1–100000) and `--page-size` (1–100). Exact host
lookup starts at the first page and follows matching pages automatically.

Host status is read from the backend; enrollment succeeds only when the returned
enrollment ID reports online. Infrastructure provisioning and workload execution
remain separate from this operation.

## Save selected credentials after enrollment

**Available in CLI 0.15.0; hosted acceptance pending.** Requires the matching host-binding backend. enrollment succeeds
independently of saving. After confirmed enrollment, an interactive command asks
whether to save selected credentials for your other devices, defaulting to N.
`--save-credentials` gives consent; `--no-save-credentials` declines. `--quiet`
only suppresses progress. JSON/noninteractive calls never prompt automatically.

```shell
# Re-enter the target password securely after enrollment (masked prompt).
dl hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
  --save-credentials --target-password ge/bos14/login

# Explicit, separate target and jump-key exports.
dl hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh '-J jump bos14-ctrl' \
  --save-credentials --target-key ge/bos14/key=/secure/target-key \
  --jump-key jump=ge/jump/key=/secure/jump-key

# Automation: exact UTF-8 bytes from a protected file/pipe, never argv secrets.
dl hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
  --save-credentials --target-password ge/bos14/login \
  --password-fd ge/bos14/login=3 --json 3</secure/target-password
```

Selecting a target never selects its jump credentials or other keys. Personal
vault paths are independent of the host namespace. Missing selection on an
interactive save opens source selection; automation must supply it explicitly.
Only selected private regular files are read; encrypted key files retain their
original bytes and still require their existing passphrase on use.

Saving does not authorize backend SSH. Do not put passwords/private keys in
configuration JSON. OpenSSH password input cannot be recovered: saving requires
secure re-entry. Cancellation/failure retains successful enrollment and writes;
requested incomplete saving exits nonzero with separate `credentials` outcomes.

An `unknown` entry write includes a stable request ID for `vault write-status`.
A `saved_unbound` result includes exact `binding` metadata for retry without SSH
or secret rereads:

```shell
dl vault bind --host-id HOST_ID --enrollment-id ENROLLMENT_ID \
  --entry-id ENTRY_ID --entry-revision 1 --role target --endpoint bos14-ctrl \
  --kind password
dl vault bindings --host-id HOST_ID --enrollment-id ENROLLMENT_ID
```

Binding management is account-only, idempotent for identical references and
rejects replacement with a different entry/revision. Host setup, remote key
rotation/revocation and explicit binding release are separate follow-up work.

## Cross-component integration check

The repository includes a repeatable check against an isolated local Hosts API,
control plane, persistent databases, and a compiled nymph binary:

```shell
pnpm build
node scripts/test-hosts-integration.mjs \
  /path/to/protected-test-environment.json /path/to/nymph
```

The protected JSON supplies `remote`, `namespace`, `token`, `outsiderToken`, and
`lakeshoreId`; use test-only credentials and a loopback server. The test launches
the actual CLI and nymph subprocesses, verifies online status, stable explicit
request replay, consumed-token and token-absent reconnect, and forbidden access
before target mutation. It uses local SSH/service adapters, so this is not a
live-network SSH or actual-systemd test. Real target access and runner execution
need their own acceptance checks. Test processes are stopped and temporary
identity files removed afterward.

## Paired Python API

Python 0.12.0 is the paired released SDK. Its library never prompts;
application code may collect a password explicitly before enrollment:

```python
from getpass import getpass
from dreamlake import DreamLakeClient
from dreamlake.host_credentials import HostCredential

client = DreamLakeClient()
result = client.hosts.enroll(
    "fortyfive/bos14/bos14-ctrl", ssh="-J jump bos14-ctrl",
    request_id="bos14-save-001", save_credentials=True,
    credentials=[
        HostCredential("target", "bos14-ctrl", "ge/bos14/login", "password",
                       password=getpass("Password to save: ")),
        HostCredential("jump", "jump", "ge/jump/key", "private_key",
                       key_file="/secure/jump-key"),
    ],
)
# Inspect redacted outcomes even when enrollment succeeded.
print(result["credentials"])
with client.http() as http:
    from dreamlake.vault import Vault
    vault = Vault(http)
    for item in result["credentials"]["entries"]:
        if item["status"] == "unknown":
            receipt = vault.write_status(request_id=item["requestId"])
        elif item["status"] == "saved_unbound":
            binding = vault.bind_host_credential(**item["binding"])
```

A missing receipt does not prove failure. Interrupting a Python entry write
retains `unknown`; interruption after saving retains `saved_unbound` and its
binding arguments. Neither recovery operation rereads a secret or reconnects SSH.

Enrolled hosts use a persistent user service with `runtime.keep_alive_s = -1`, so an idle host remains available instead of exiting after five minutes. Re-enrolling the same host with the fixed client updates the generated configuration. Nymph’s default idle policy for other launch modes is unchanged. This fix is unreleased; deployed hosts require the updated client and reconfiguration.

Re-enrollment regenerates the service configuration. Restore reviewed custom settings, including `private_tracked`, after re-enrollment and verify a fresh signed capability poll before private submission. Re-enrollment does not preserve custom configuration.

## Provision and control machine power

Requires CLI **0.72.0+** and the matching Host power API. Older installed
clients do not expose these commands; check `dl --version` and command help.

`hosts create` uses the existing provider launch flow and requires automatic
Nymph enrollment. Choose an existing provider and a full host name in its
namespace. One host is created per request (`--count 1`); a stable request ID
allows the same request to recover its instance after an interrupted response.
Provider configuration, launch layers, credentials and bootstrap prerequisites
are the same as for `providers instances launch`.

```bash cli-help="hosts create"
dl hosts create geyang/PROVIDER_ID --host-name geyang/dev/worker \
  --layer development --request-id create-worker-01
```

A launch receipt does not prove enrollment or SSH readiness. By default, the
shared launch flow waits for enrollment and web terminal setup; pending setup
returns a receipt with recovery instructions. `--no-web-terminal` disables that
terminal setup and its wait, so inspect enrollment separately.

Inspect the provider binding and cloud-observed power state before choosing a
power operation. Use the exact enrollment ID reported by this command.

```bash cli-help="hosts power"
dl hosts power geyang/dev/worker
dl hosts power HOST_ID --namespace geyang --json
```

Power commands apply to the machine, not just the Nymph process. They require a
verified AWS EC2 provider launch binding with its configured launch server.
Kubernetes and other provider kinds, and manually enrolled laptops or servers,
are unsupported by the Host power API.
Names, online status and matching tags cannot establish a cloud-instance binding.
Start, stop, restart and terminate preserve the Host catalog record and do not
revoke enrollment credentials. `restart` uses the provider's reboot operation.

```bash cli-help="hosts start"
dl hosts start geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id start-worker-01
```

```bash cli-help="hosts stop"
dl hosts stop geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id stop-worker-01
```

```bash cli-help="hosts restart"
dl hosts restart geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id restart-worker-01
```

```bash cli-help="hosts terminate"
dl hosts terminate geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id terminate-worker-01 --volumes delete-on-termination
```

Termination destroys the instance. The required `--volumes delete-on-termination`
uses AWS's per-volume settings: volumes marked for deletion are deleted; other
volumes are retained. This is not an all-volumes-retained policy.

Stop, restart and terminate reject recorded active tracked runs unless
`--allow-active-work` is supplied. That check does not cover all interactive or
externally launched work and is not an atomic drain. A successful power receipt
records the provider operation; use `hosts power` to observe the resulting
instance state. After an uncertain response, reuse the same request ID and
identical inputs; the CLI never automatically resubmits with a fresh ID.

## SSH and remote commands

Requires CLI **0.72.0+**, deployed Terminal session delegation, and an enrolled
Nymph with SSH enabled. Linux and macOS clients use the local native OpenSSH
client with an authenticated host-key pin and a temporary per-session key.
No inbound SSH port is required on the target for the Nymph relay path.

```bash cli-help="ssh"
dl ssh geyang/dev/worker
dl ssh HOST_ID --namespace geyang --enrollment ENROLLMENT_ID
```

```bash cli-help="hosts ssh"
dl hosts ssh geyang/dev/worker --duration 900
```

Select an exact host by ID or full name. A single ready SSH enrollment is selected
automatically. With CLI 0.96.0+, when several are ready, an interactive terminal offers a chooser
showing each Unix user, UID, readiness and enrollment ID. Without a terminal, the
CLI prints those choices with copyable commands and exits without connecting.
`--enrollment` selects an exact enrollment directly; scripts can use it to avoid
prompts. Cancelling the chooser opens no session.

### Keyboard-idle disconnect

Nymph 0.1.42+ separates `max_duration_s` (total lifetime; `0` disables it) from `idle_timeout_s` (keyboard inactivity). `dl` uses the shorter of the host inactivity limit and its 30-minute request, and reports keyboard activity often enough for that limit. A total lifetime limit still closes an actively used session. Equal settings such as 1800 seconds are valid; timing grace is internal.

**CLI 0.127.0+.** An interactive `dl ssh` or `dl tmux` session ends 30 minutes
(or the shorter negotiated host limit in CLI 0.129.0+) after the last keystroke or paste (or, before the first one, after the session
was requested), not at a fixed time. It is disconnected at
once, with no warning, and the CLI prints
`dl: disconnected after 30 minutes without keyboard input.` and exits 124. A
session in which you keep typing stays on the same connection, shell and
foreground program while you work, up to any configured total lifetime: renewing it never reconnects.

Only keystrokes and pastes count. Remote output (a log you are watching, a
progress bar, a tmux status line), mouse movement and clicks, focus changes,
terminal replies to the remote program's queries, window resizes and SSH
keepalives never postpone the disconnect, even when the terminal delivers a
report in several pieces. Some encodings are byte-for-byte identical, so they
are read the way terminal programs read them: a modified F3 key that some
terminals send exactly like a cursor-position reply (`ESC[1;5R`) does not
count, and an Escape key followed within 50 ms by `[`, `]`, `O`, `P`, `_`, `^`
or `X` is read as the start of one sequence. The CLI reads keyboard input only
from its own terminal.

How it works: the native `dl` build runs OpenSSH inside a pseudo-terminal it
owns, so it can see keystrokes before they are encrypted; OpenSSH still sets its
own terminal mode, follows window resizes and handles Ctrl-C and the `~` escape
as before. While you type, the CLI reports activity to the DreamLake backend at
most about once a minute. The backend rechecks your current access to that host
enrollment, exactly as for a new connection, and the control plane extends the
session and its credential to 30 minutes 10 seconds from that report. If your
access is revoked, renewals stop and the session ends within that window;
revoking a host access grant closes it at once unless another current grant
(person or team) still authorizes you.

The CLI falls back to a fixed 30-minute session, and says so, when keyboard
observation or renewal is not available:

- `dl: keyboard-idle sessions need the native dl build; this session ends after 30 minutes.`
  The npm package runs on Node, which has no pseudo-terminal support.
- `dl: this host does not support keyboard-idle sessions yet; this session ends after 30 minutes.`
  The host's Nymph does not yet follow renewed deadlines (or the backend is older).

Without a terminal on stdin and stdout (input piped in), `dl ssh` keeps the
fixed lifetime. `--duration SECONDS` (120–1800) asks for that fixed lifetime
explicitly instead of the keyboard rule. `--timeout SECONDS` is an absolute,
opt-in limit in either mode (up to 604800 seconds with the keyboard rule, up to
the duration otherwise) and returns 124. `dl exec` is unchanged: a fixed
lifetime of 120–1800 seconds (`--duration`, default 1800).

When a session ends, the CLI restores the local terminal and switches off modes
a remote program may have left on (mouse reporting, focus events, bracketed
paste, application keys, a hidden cursor and, when one was entered, the
alternate screen), so an abrupt disconnect no longer leaves mouse movement
printing as text such as `35;1;36M`. A session the server already ended is
cleaned up without a warning.

With CLI 0.100.0+, when the selector names no host (a keyword such as
`dl ssh gpu`, a misspelled or missing `namespace/group/host[/user]`, or an
unknown ID) and the command runs in a terminal, a host picker opens in place
of a bare error:

<video src="/images/ssh-picker/ssh-picker.mp4" autoPlay loop muted playsInline controls style={{ maxWidth: "100%", borderRadius: "8px" }} />

The picker is the `hosts list` table filtered to hosts whose name or ID
contains the keyword, case-insensitively, with every match highlighted and the
best match first: an exact name or host segment, then one the keyword starts,
then any containing name, then IDs. The top row is selected. Typing filters
further, `↑`/`↓` move the selection, and Tab completes what you typed toward
the selected host one `/` segment at a time (`gpu14` → `lakeco/gpu14/` →
`lakeco/gpu14/gpu14-ctrl`). Enter connects to the selected host and prints the
full command it ran, so the next call can skip the picker. Esc or Ctrl-C
cancels with the original error and exit code. A `namespace/group/host[/user]`
selector that matches nothing as a whole falls back to its last segment, and
the namespace is taken from the selector when it has one. Twenty rows are shown
at a time, offline hosts included; `NO_COLOR` drops the highlight and the
inverse selection bar.

When stderr is a terminal but stdin is not (input piped in), the error is
followed by the same filtered table as static text and nothing is connected;
rerun with the full name or ID. Without a terminal, and on sign-in, namespace
or network errors, the error is printed alone and the inventory is not read.
The 120-second minimum avoids a legacy control-plane deadline mismatch for
60-second delegations. Use `--timeout` for shorter attached commands.

When the control plane answers HTTP 503 `controlplane_busy`, it refused the
delegation before creating a session, so the client resubmits it: up to four
attempts within 25 seconds, waiting `Retry-After` (at most 5 seconds) or an
exponential backoff, whichever is longer. Any other delegation failure is
reported without resubmission, because it may have created a session.

**CLI 0.119.2+.** `dl exec`, `dl ssh` and `dl tmux` look up SSH targets for the
selected host only, so the rest of the namespace's catalog never blocks a
connection. An archived host stays reachable by its full name or ID: archiving
changes list visibility, not access. A revoked enrollment is never a target.
Terminal API failures name their stage, for example
`Host API request failed (HTTP 409): terminal_not_ready` when the enrollment is
not online with SSH. Earlier CLIs read the whole terminal catalog first and fail
with `Host API request failed (HTTP 503)` when the namespace has more than 100
connectable enrollments; update the CLI.

```bash cli-help="exec"
dl exec geyang/dev/worker -- uname -a
dl exec geyang/dev/worker --timeout 30 -- sh -c 'printf "%s\n" "$HOME"'
```

```bash cli-help="hosts exec"
dl hosts exec geyang/dev/worker -- python3 -c 'print("hello")'
```

Place the remote command after `--`. Arguments are passed literally; invoke
`sh -c` explicitly when shell expansion or pipelines are wanted. Output streams
to local stdout/stderr and the command returns the remote exit status. SSH
transport failures return the native SSH error status. `--timeout` closes the
session and returns 124; it does not guarantee termination of detached remote
processes. SSH session cleanup removes temporary local keys and closes the
session. File copy and forwarding remain outside these commands.

## Named tmux references and creation

**CLI 0.137.0+.** The explicit tmux commands share their action syntax with the command palette
and tmux action directives. They require a server, terminal gateway and enrolled
Nymph that advertise the named-tmux capability. An older deployment returns
`terminal_reference_unsupported`; local CLI support does not prove that a host
has received this capability.

```bash cli-help="tmux new"
# Create only; a pre-existing name is a conflict, never an attachment
dl tmux new work --host geyang/dev/worker
# Omit the name to request a fresh generated name
dl tmux new --host geyang/dev/worker
# Explicitly attach to the result once creation succeeds
dl tmux new work-2 --host geyang/dev/worker --open
```

`new` creates a detached named session and prints its durable directive when
successful. `--host` is required and accepts an exact Host ID or
`namespace/group/host[/user]`. For a Host ID, use the configured namespace or
`--namespace`. If multiple enrolled accounts match, select `--enrollment`;
the command never chooses an arbitrary account. A requested name collision
returns a conflict without attaching, replacing, or sending input to it. New
names contain 1–64 letters, digits, underscores or hyphens. A connection grant
may add a server-controlled ownership prefix; use the exact name and directive
returned by the operation.

The CLI prints a lowercase request UUID before submitting creation. If a response is lost,
retry the identical name and host with `--request-id UUID`. Reusing the UUID
observes the same creation operation; changing arguments with that UUID is a
conflict. `--wait 0` returns a pending receipt immediately; the default waits up
to 30 seconds, and the maximum is 60. `--json` prints the operation receipt,
including its request ID, original `requestedName` (null if omitted), and
pending, succeeded or failed status. The created reference contains the actual
server-issued name. A pending
receipt is not confirmation that the session was created. `--open` requires
interactive stdin and stdout before any creation request is sent.

```bash cli-help="tmux open"
# Attach only to the named session in this exact enrollment and tmux server
dl tmux open ':tmux[aaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbb/work]'
```

```bash cli-help="tmux list"
# Read the last collected metadata; this does not trigger a scan
dl tmux list --host geyang/dev/worker
```

```bash cli-help="tmux resolve"
# Inspect cached resolution without creating or attaching
dl tmux resolve ':tmux[aaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbb/work]' --json
```

A durable reference has the form
`:tmux[ENROLLMENT_ID/SERVER_ID/PERCENT_ENCODED_EXACT_NAME]`. Its enrollment is a
24-character lowercase hexadecimal ID and its server is a 16-character lowercase
hexadecimal ID issued by the enrolled host. The name is percent encoded once.
Do not infer the server from a numeric tmux row ID, machine name, default socket,
or a browser terminal. The directive contains no private socket path.

`open` requires an interactive terminal and fresh authorization. It attaches
only to the exact name in the referenced server; a missing, stale, inaccessible
or unsupported reference never creates a session and never falls back to a
plain shell. Press **Ctrl-]** to detach. A replacement with the same name in the
same server scope is the same named destination. Renaming a session does not
redirect its old name through a reused numeric tmux ID. These references identify
live terminals; `:session[ID]` identifies a separately saved agent conversation.
Ephemeral browser shells do not receive durable tmux references.

The command palette uses `/tmux new work --host geyang/dev/worker`. In notes and
chat, `:tmux[new work --host geyang/dev/worker]` is an explicit creation action;
rendering or previewing it does not execute it. Activating it requests a new
session. `:tmux[...enrollment/server/name...]` instead opens an existing named
reference. The shared actions are `new`, `open`, `list` and `resolve`.

Action arguments support single or double quote grouping and backslash escapes;
there is no shell expansion, variable substitution, command substitution, pipe or
redirect execution. For example, `new "work-item" --host geyang/dev/worker`
requests the literal name `work-item`. Quoting does not expand the allowed new-name
character set; existing reference names retain their exact percent-encoded text. Unknown or repeated options and ambiguous
host selections fail explicitly. CLI output and retry flags (`--json`, `--wait`,
`--request-id`, `--open`) are CLI options, not directive action arguments.

```bash cli-help="hosts tmux new"
dl hosts tmux new work --host geyang/dev/worker
```

```bash cli-help="hosts tmux open"
dl hosts tmux open ':tmux[aaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbb/work]'
```

```bash cli-help="hosts tmux list"
dl hosts tmux list --host geyang/dev/worker
```

```bash cli-help="hosts tmux resolve"
dl hosts tmux resolve ':tmux[aaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbb/work]' --json
```

### TypeScript API

For integrations, `createClient` exposes the same metadata and creation contract:

```typescript
import { createClient, parseTmuxReference } from '@dreamlake/dreamlake-cli/api';
const dl = createClient({ remote: 'https://api.dreamlake.ai', token });
const enrollment = 'aaaaaaaaaaaaaaaaaaaaaaaa';
const requestId = crypto.randomUUID(); // Persist before the write; reuse on retry.
const result = await dl.tmux.create(enrollment, { requestId, name: 'work' });
const operation = await dl.tmux.operation(enrollment, requestId);
const reference = parseTmuxReference(':tmux[aaaaaaaaaaaaaaaaaaaaaaaa/bbbbbbbbbbbbbbbb/work]');
const resolved = await dl.tmux.resolve(reference);
const inventory = await dl.tmux.list('geyang', hostId, enrollment);
```

Creation calls `POST /terminal-references/:enrollment/tmux/sessions` with
`{ requestId, name? }`. Operation reads use
`GET /terminal-references/:enrollment/tmux/operations/:requestId`. Resolution uses
`GET /terminal-references/:enrollment/tmux/:server?name=EXACT_NAME`. Listing uses
the existing enrolled-host `multiplexer-sessions` metadata endpoint. A pending
creation returns HTTP 202. A completed operation read returns HTTP 200 with
`succeeded` or `failed`; an existing name reports `failed` with `name_exists`.
Reusing a request UUID with changed arguments returns HTTP 409. All metadata
and operation reads are read-only; listing and resolution never enqueue a
daemon scan.

`tmux.attachTicket(namespace, reference, { cols, rows })` requires a separately
configured gateway transport with its allowed `Origin` header. It sends only a
`tmux-reference` launch with exact enrollment, server and name. The gateway
reauthorizes and resolves the owned server privately before attachment. It
cannot launch a shell or create a missing session. The SDK does not read local
login credentials or allocate a local terminal.

<a id="persistent-tmux-shells" />

### Compatibility: persistent SSH tmux shells

**CLI 0.116.0+.** `dl tmux HOST` creates or attaches to the remote tmux session `dl-session`.
`dl hosts tmux HOST` is the same command. Linux/macOS, local OpenSSH, an interactive
terminal on stdin and stdout, and remote tmux are required. The host is always
explicit; `dl-session` is a tmux name, not a default machine or saved agent session.

```bash cli-help="tmux"
# Explicit create-only operation
dl tmux new work --host geyang/dev/worker
# Read cached session metadata
dl tmux list --host geyang/dev/worker
# Compatibility: create or return to dl-session on this host
dl tmux geyang/dev/worker
# A separate named terminal; --sess and --session are interchangeable
dl tmux geyang/dev/worker --sess work
```

```bash cli-help="hosts tmux"
dl hosts tmux new work --host geyang/dev/worker
# Compatibility: create or attach
dl hosts tmux geyang/dev/worker --session work
```

Detach with **Ctrl-B, then D**, and run the same command to reconnect. Creation
and attachment use tmux's atomic `new-session -A` operation. Names match exactly,
including when another name starts with the same text. The command neither
injects input into an existing pane nor detaches other viewers. Names contain
1–64 letters, digits, underscores or hyphens.

Host selection, `--namespace`, `--enrollment`, `--duration` and `--timeout` use the
same authenticated, host-key-pinned SSH relay as `dl ssh`. tmux is looked up in
the enrolled account's login PATH. If it is missing, the command exits 127 and
explains how to install it or open a plain shell with `dl ssh HOST`.

Each connection ends after 30 minutes without keyboard input (see
[Keyboard-idle disconnect](#keyboard-idle-disconnect)), or at a fixed `--duration`. Reconnecting
requires fresh authorization; it does not replay input. Detaching or losing the
connection leaves tmux running, but reboot survival is not provided. When a user
systemd manager is available, newly started tmux servers use a separate scope.
Existing servers keep their original lifecycle; without a separate scope, a Nymph
service restart may also stop the tmux server. This does not change or resume a
saved Codex/Claude conversation; use `dl sessions` for those identities.

## Upgrade nymph on enrolled hosts

`dl hosts upgrade` installs an exact Nymph release on enrolled hosts and
restarts each host's Nymph service exactly once. `dl hosts rollback`
restores the binary that the last upgrade replaced. Both run the enrollment
bootstrap on the host through the same Nymph relay as `dl exec`, so the
host needs a ready SSH enrollment (web terminal), Python 3, and the service that
`hosts enroll` installed. No inbound SSH port or saved SSH credential is used.

```bash cli-help="hosts upgrade"
dl hosts upgrade geyang/dev/worker --nymph-version 0.1.32 --dry-run
dl hosts upgrade geyang/dev/worker --nymph-version 0.1.32
dl hosts upgrade 'geyang/lab/*' --nymph-version 0.1.32 --concurrency 4 --max-failures 2
dl hosts upgrade --all --namespace geyang --nymph-version 0.1.32 --json
```

```bash cli-help="hosts rollback"
dl hosts rollback geyang/dev/worker
dl hosts rollback geyang/dev/worker --upgrade-id 20261029-001 --json
```

Select hosts by host ID, `namespace/group/host[/user]` or a quoted `namespace/group/*`,
or every host in one namespace with `--all`. A host selected more than once is
processed once. Hosts without a verified online enrollment are reported as
`skipped` and not contacted. `--nymph-version` must be an exact release
(`0.1.32` or `v0.1.32`); fleet upgrades never use `latest`.

`--dry-run` connects to each host read-only and reports its installed version,
the planned step (`upgrade`, `restart`, `current` or `blocked:restart_pending`),
any pending restart, whether a rollback is available, and leftover jobs that a
real run would remove. It changes nothing.

### What happens on each host

1. On macOS, removes the leftover restart job from the October 2026 fleet
   upgrade, using the same rule as `self-update`: only a submitted
   `ai.dreamlake.refresh.*` launchd job that runs this user's
   `~/.local/share/dreamlake/fleet-upgrades/<id>/restart.py`.
2. Refuses to start while an earlier restart is still due (`restart_pending`).
   The CLI then verifies that earlier restart first and, if it verified, applies
   the requested action once; it never stacks a second pending restart.
3. If the service binary already reports the requested version and the running
   process started from it, reports `current` and does nothing else. If only
   the restart is missing, schedules the restart without downloading.
4. Downloads the release with the official installer
   (`https://dreamlake.ai/dreamlake/nymph/install.sh`, which verifies the
   archive's published SHA-256) into a staging directory, and checks that the
   staged binary reports the requested version.
5. Keeps the replaced binary, then swaps the new one into place with an atomic
   rename in the binary's own directory. The binary is the one named by the
   service definition (LaunchAgent `ProgramArguments` or systemd `ExecStart`),
   not whichever `nymph` is first on PATH. A symlinked, package-managed or
   root-owned binary is refused (`nymph_binary_unmanaged`); upgrade it with its
   own installer.
6. Schedules one delayed restart (`--restart-delay`, default 15 seconds) and
   returns. If the restart cannot be scheduled, the previous binary is restored.

Each run writes `~/.local/share/dreamlake/fleet-upgrades/<YYYYMMDD-NNN>/` on the
host: `nymph` (installed binary), `previous-nymph` (replaced binary),
`receipt.json` (versions, SHA-256 digests, service, PIDs and the restart
schedule), `restart.sh`, and after the restart `restart.started`,
`restart.log`, `restart.pid`, `restart.exit` and `verification.json`. One host
lock serializes upgrade, verification and rollback (`upgrade_in_progress`).
Directories are not pruned automatically.

### The one-shot restart

The restart must run after the command that scheduled it has ended: that
command's session is relayed by the Nymph being restarted.

- **macOS:** a plain background process in its own session (`setsid`) that
  sleeps and then runs `launchctl kickstart -k` on the host's agent. It is never
  registered with launchd (no `launchctl submit`, no `KeepAlive`), so nothing
  can start it again, and leaving Nymph's process group means neither the
  session ending nor Nymph's own teardown stops it early. The 2026-10 upgrade
  used `launchctl submit`, whose jobs launchd keeps alive; that job restarted
  Nymph about every 15 seconds for a week.
- **Linux:** a transient systemd user timer, `systemd-run --user --on-active=<delay>
  --collect` with `RemainAfterElapse=no`, running `systemctl --user restart` on
  the host's unit. It runs in the user manager, outside Nymph's cgroup (a child of
  Nymph would be killed by its own restart). The timer fires once, the service
  has no `Restart=`, and systemd unloads both afterwards.

On both systems `restart.sh` first creates `restart.started` with `noclobber`;
any later execution finds the marker and exits without restarting.

### Verification

After the restart delay the CLI reconnects (retrying while the relay comes back,
up to `--verify-timeout`, default 300 seconds) and the host checks that:

- the restart ran exactly once (`restart.log` has one entry) and exited 0;
- the Nymph PID changed, equals the PID recorded right after that restart, and
  stayed the same for `--stable-seconds` (default 15);
- on macOS, launchd counts exactly one new start of the agent; on Linux the
  unit's invocation changed and systemd recorded no automatic restarts;
- the restart helper has finished, and the installed binary has the recorded
  SHA-256 and reports the expected version.

The host result lists PIDs before and after, the restart count, each check and
the names of failed checks. A failed check marks the host `failed`.

### Rollback

`hosts rollback` restores `previous-nymph` from the newest upgrade receipt for
the service binary (or the receipt named by `--upgrade-id`, one host only) and
verifies one restart the same way. It refuses when the installed binary is not
the one that upgrade installed (`rollback_receipt_mismatch`) or the kept binary
no longer matches its recorded digest. Rollback writes its own receipt, so it
can itself be rolled back. Receipts from the ad-hoc 2026-10 upgrade are not used.

### Fleet behavior and results

`--concurrency` (1–16, default 5) bounds hosts processed at once; one host is
never processed twice at the same time. After `--max-failures` failed hosts
(default 5) no new host is started; hosts in progress finish, and the rest are
reported as `not_started`. Each host ends as `upgraded`, `rolled_back`,
`current`, `planned` (dry run), `failed`, `skipped` or `not_started`.

Outcomes are appended as JSON Lines while the run proceeds, to `--record` or
`~/.dreamlake/hosts-upgrades/<run>.jsonl`: one `run` entry, remote-stage `progress` entries, a `scheduled` entry
when a restart is scheduled, one `host` entry per finished host and a final
`summary`. During execution an interactive terminal shows a live paginated table
with remote bootstrap, restart, reconnect and verification status. Use left/right,
Page Up/Page Down or p/n to change pages; q leaves the live view and streams
updates while upgrades continue. Redirected output streams timestamped stage
updates to stderr. `--json` suppresses progress and prints only the final JSON
report to stdout; the JSON Lines record still captures live stages.

The command prints a final table, or the full report with `--json`, and
exits 0 only when every selected host is `upgraded`, `rolled_back`, `current` or
`planned`.

Linux verification checks the running `/proc/<pid>/exe` checksum, not only the
installed file or its modification time. If systemd's effective `ExecStart` uses
a different binary than the enrolled unit file, upgrade fails with
`service_binary_override` before installing or restarting anything. Reconcile
that service override locally, preserving its enrollment config, then retry.

If verification times out, the host may still have restarted correctly; run
`hosts upgrade` again with the same version: a verified or running new binary is
reported as `current`, and a still-due restart is verified rather than repeated.

## Move a private host between namespaces

**CLI 0.102.0+:** requires the matching host-move server.
The move changes the namespace and name prefix while preserving the Host ID,
personal owner, enrollments and machine keys. Organization membership does not
give another member access to the computer, and [connection grants](#share-connection-access)
stop working once the Host leaves the namespace they were made in. Existing execution connections stay
bound to their original owner namespace and remain independently authorized.

Preview first with the exact Host ID from inventory:

```bash cli-help="hosts move"
dl hosts move HOST_ID --namespace alice --to acme --dry-run --json
```

The preview includes `revision`, `previewHash`, destination name, private owner
and dependency blockers. Review the full preview before applying. Apply never
refreshes the preview or invents a request ID:

```bash
dl hosts move HOST_ID --namespace alice --to acme --confirm \
  --request-id laptop-move-001 --expected-revision REVISION \
  --preview-hash PREVIEW_HASH --json
```

Replace the placeholders with the reviewed values. Pending enrollment grants,
name/key collisions, unsupported run dependencies, retained jobs, service-account or provider
bindings, Slurm inventory bindings and managed metrics Sources can block a move.
With the matching retained-session adapter, saved terminal sessions keep their
IDs, original namespaces and links. They become private to their existing owner;
public visibility and organization sharing are removed. The optional `sessions`
preview/receipt field reports `count`, policy
`retain_original_namespace_make_private`, and `accessChanges.public` / `.shared`.
Review those access changes before applying; older clients without this field
remain compatible, and servers without the adapter may block retained sessions.

The optional `runs` preview/receipt field reports `count`, `terminal`, `active`
and policy `retain_original_namespace_acknowledged_runs`. With the matching
adapter, ordinary run history and acknowledged executions retain their original
namespaces, IDs, targets, output, statuses, execution IDs and cancellation intent.
A move does not cancel, restart or relaunch active work. Pending delivery,
private/reporting runs and other unsupported run dependencies remain blockers.

CLI 0.132.0+: when the Host is filed in Projects, the optional
`projectPlacements` preview/receipt field reports `count` and policy `unfile`,
and the human preview adds `Project placements: N will be removed`. The move
removes those filings and their Bindr tags in the same operation; it changes no
host connection grants. The field is absent when the Host is filed nowhere and
from older servers. See [Hosts in Projects](https://cli.dreamlake.ai/projects#hosts-in-projects).

The server preview is authoritative; never detach dependencies or re-enroll a
machine to bypass a blocker. The operation makes no control-plane writes and
does not restart Nymph.

After an uncertain response, retry the exact original source namespace, host,
destination, request ID, expected revision and hash. A historical replay receipt
does not establish the host's current location after a subsequent move. Read
the destination inventory and exact host status back; terminal/metrics readiness
need separate verification.

The public TypeScript API uses the same guarded routes:

```ts
const hosts = createClient(options).hosts('alice')
const preview = await hosts.movePreview(hostId, 'acme')
// Review the preview before applying.
const request = { destinationNamespace: 'acme', requestId: 'laptop-move-001',
  expectedRevision: preview.revision, previewHash: preview.previewHash }
const receipt = await hosts.move(hostId, request)
```

Switching the built-in agent with `/su NAMESPACE` is a separate session-scope
operation. It changes neither host ownership nor the application's workspace.

## Rename a host without re-enrolling

Use the exact Host ID and current name from inventory. Rename preserves the Host ID,
enrollment, machine keys, saved sessions and running work; it does not restart Nymph.
A username suffix must match the enrolled Unix account. Namespace changes use `hosts move`.

```bash cli-help="hosts rename"
dl hosts rename HOST_ID --name fortyfive/bos14/bos14-ctrl/geyang --expected-name fortyfive/bos14/bos14-ctrl-geyang
```

After an uncertain response, reuse the same Host ID, `--name` and `--expected-name`.
A different current name or a destination collision returns a conflict.

TypeScript: `client.hosts('fortyfive').rename(hostId, { name, expectedName })`.
Python: `client.hosts.rename('fortyfive', host_id, name=name, expected_name=expected_name)`.
HTTP: `POST /namespaces/:slug/hosts/:id/rename` with `{ "name": "...", "expectedName": "..." }`.
Read the new name back and verify SSH independently.

## Share connection access

**CLI 0.128.0+.** The owner of a Host in an
organization namespace can let one named member connect to one enrollment.
**CLI 0.132.0+,** with a server that supports team grants: the owner can instead grant one
enrollment to a team (see [Team grants](#team-grants)).
Organization membership alone grants nothing; personal namespaces have no grants.
Filing a Host in a Project grants nothing either (see
[Hosts in Projects](https://cli.dreamlake.ai/projects#hosts-in-projects)).

A grant shares that enrollment's Unix account. The person connects as that
user, with its files, processes, tmux sessions, agent logins, credentials and
OS permissions on the machine; DreamLake creates no OS user and cannot isolate
them. To give someone their own account, enroll a separate Unix user on the
machine and grant that enrollment.

```bash cli-help="hosts access"
dl hosts access list fortyfive/bos14/bos14-ctrl
dl hosts access grant fortyfive/bos14/bos14-ctrl --enrollment ENROLLMENT_ID --user alice
dl hosts access grant fortyfive/bos14/bos14-ctrl --enrollment ENROLLMENT_ID --team robotics
dl hosts access revoke fortyfive/bos14/bos14-ctrl GRANT_ID
```

```bash cli-help="hosts access list"
dl hosts access list fortyfive/bos14/bos14-ctrl
dl hosts access list HOST_ID --namespace fortyfive --json
```

`list` shows each grant's ID, kind (`user` or `team`), person or team, Unix
account, enrollment, machine and state. A revoked grant stays listed with
`state: "revoked"`, `pendingConnections` and `pendingUntil` while connections
opened through it are not yet confirmed closed and not yet expired.

CLI 0.132.0+: `list` asks the server for every grantee kind
(`?grantees=all`). `--json` keeps person grants in `grants`, adds team grants
in `teamGrants` and the organization's teams in `teams`, and sets
`teamGrantsSupported`. A server without team grants answers person grants
only; the CLI then says the server does not support team grants instead of
"Only you can connect", and `teamGrantsSupported` is `false`. Older clients
that list a Host with team grants get
`host_access_grant_client_upgrade_required` (HTTP 409) rather than an
incomplete list: update the client.

```bash cli-help="hosts access grant"
dl hosts access grant fortyfive/bos14/bos14-ctrl --enrollment ENROLLMENT_ID --user alice
dl hosts access grant HOST_ID --namespace fortyfive --enrollment ENROLLMENT_ID --user @alice --json
dl hosts access grant fortyfive/bos14/bos14-ctrl --enrollment ENROLLMENT_ID --team robotics
```

`grant` needs the exact enrollment ID (from `dl hosts enrollments`) and exactly
one of the member's DreamLake username (`--user`) or a team slug (`--team`,
CLI 0.132.0+); the CLI never picks an enrollment, Unix account, person or team for you. Granting the same person the same enrollment again returns the
existing grant. If a grant or revoke gets no clear answer (the server cannot be
reached, a server error, or an unreadable response), its outcome is unknown and
the CLI does not retry it: check `dl hosts access list` before doing anything
else. Refusals name the reason: `grantee_not_found`,
`grantee_not_member`, `grantee_is_owner`, `host_access_grant_org_only`,
`enrollment_not_found`, `team_not_found`, `invalid_host_access_grant` (also
what a server without team grants answers to `--team`),
`host_access_grant_limit` or `host_not_found` (you do not own that Host).

```bash cli-help="hosts access revoke"
dl hosts access revoke fortyfive/bos14/bos14-ctrl GRANT_ID
dl hosts access revoke HOST_ID GRANT_ID --namespace fortyfive --json
```

Revoking denies new connections at once and closes the person's open
connections through the control plane. The receipt reports
`closedConnections` and `unconfirmedConnections`; any unconfirmed ones also
carry `unconfirmedUntil`, the latest time they end on their own. Revoking takes
a person or team grant ID. A connection whose user still holds another current
grant to the same enrollment (their own person grant, or another team's) stays
open and is counted in `stillAuthorizedConnections` (CLI 0.132.0+; older servers
omit it). While any
close is unconfirmed the command exits 1. Running the same revoke again tries
to close them again; the CLI never does this on its own. Revoking is idempotent.

The grantee runs the ordinary commands: the Host appears in their
`dl hosts list` and `dl hosts status` with only the granted enrollments, and
`dl ssh`, `dl exec` and `dl tmux` connect to it. `hosts list` then adds an
ACCESS column (`owner` or `shared`, also the `{access}` format field) and
`hosts status` adds an `Access: shared` line; both come from the server's
`access.kind: "grant"` marker, and `--json` keeps the backend `access` object.
Management, metrics, checks, saved sessions, moves and grant management stay
with the owner. A grant also stops working without revocation when the person
leaves the organization, the owner loses access, the enrollment is revoked or
the Host moves; open `dl ssh` sessions then end at their own expiry.

### Team grants

**CLI 0.132.0+; requires a server that supports team grants.** A team grant lets every
current direct member of one live team in the Host's organization connect to
one enrollment. Members of parent or child teams are not included. The team's
owners, admins and maintainers decide who that is: adding an organization
member to the team lets them connect, and every member connects as the same
Unix account, with its files, processes and credentials. An archived team's
grant lets no one connect until the team is restored.

Team grants never apply to the team's [guests](https://cli.dreamlake.ai/teams#guests). Connecting
through a team grant requires organization membership, and a member whose role
in that team is `GUEST` gets no SSH, web-terminal or host session through any
team grant, even after they join the organization separately. Changing their
team role from `GUEST` to `MEMBER` or higher, which is possible once they are
an organization member, is what lets the team's grants apply to them. Access
they hold another way is unchanged: a direct grant to them, their own hosts, or
a grant through another team where they are not a `GUEST`.

Grant a team only an
enrollment you would grant each of its members.

Access is the union of a person's own grant and the grants of their teams for
that enrollment. Losing one path never closes a connection another current
path still authorizes. When a person leaves or is removed from the team, the
team is deleted, or they leave the organization, new connections through the
team are denied at once and their open team-path connections close: browser
terminals within a few seconds; `dl ssh` sessions when the control plane is
reachable, otherwise at their deadline (30 minutes after opening for a fixed
session, 30 minutes 10 seconds after the last renewal for keyboard-idle), since
renewal is refused once access is gone. Removal does not report close counts.
A grantee's `dl hosts status` names the teams their access comes through.

TypeScript: `client.hosts('fortyfive').accessGrants(hostId)`,
`grantAccess(hostId, { enrollmentId, grantee })` and
`revokeAccess(hostId, grantId)`. CLI 0.132.0+: `allAccessGrants(hostId)` lists
person and team grants (`HostAccessGrantsAll`) and throws
`HostTeamGrantsUnsupportedError` when the server lacks team grants;
`grantAccess(hostId, { enrollmentId, team })` returns `{ teamGrant }`.
Python: `client.hosts.access_grants('fortyfive', host_id)`,
`grant_access('fortyfive', host_id, enrollment_id=..., grantee=...)` and
`revoke_access('fortyfive', host_id, grant_id)`.
HTTP: `GET`/`POST /namespaces/:slug/hosts/:id/access-grants` with
`{ "enrollmentId": "...", "grantee": "alice" }` or, with team grants,
`{ "enrollmentId": "...", "team": "robotics" }` and `GET …?grantees=all`, and
`DELETE /namespaces/:slug/hosts/:id/access-grants/:grantId`.

These person-to-enrollment grants are separate from
[service account host grants](cli-service-accounts.md), which give a machine
identity `read`/`use` permission on a Host.

## SSH usage and capacity

**CLI 0.103.1 and matching deployed services required.** Host details display used/limit counts for SSH sessions, forwarding tunnels and the shared control-plane namespace total. SSH/exec limit errors retain `session_limit` and describe those counts when supplied by the server; older servers show a generic message. Counts are shared worker/namespace capacity, not your personal quota.

See [SSH capacity and usage](https://docs.dreamlake.ai/lakeshore/hosts/browser-terminal#ssh-capacity-and-usage) for the configuration reference, counting rules, limits, examples, recovery and rollout. See [Nymph permissions and commands](https://docs.dreamlake.ai/lakeshore/hosts/nymph-permissions) before changing local policy or proposing live configuration. There is no new `dl ssh --limit` flag or remote config setter in this change.
