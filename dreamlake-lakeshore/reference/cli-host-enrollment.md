<!-- generated from https://cli.dreamlake.ai/host-enrollment.md at 0.89.0 f14de9c; do not edit -->

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

In CLI 0.76.0 and later, bare `dreamlake hosts` defaults to `hosts list`,
and accepts the same list options directly. `dreamlake hosts -h` shows both
listing options and host commands; `dreamlake hosts list -h` shows only listing
help. See [collection defaults](https://cli.dreamlake.ai/command-reference#collection-defaults-and-help).
Earlier releases require explicit `list`.

CLI 0.73.0 adds active-only listing and `--all`. Earlier versions list all
connection states without that flag.

`hosts list` reads every page of your hosts in one namespace, across all groups,
and shows only active hosts with at least one verified online enrollment. Use
`--all` to include offline hosts and hosts with unknown connection state.
Omit `--namespace` to use the signed-in personal namespace, or select another authorized namespace explicitly. `--group` accepts a single group name.

```bash cli-help="hosts list"
dreamlake hosts list
dreamlake hosts list --namespace geyang --group workstations
dreamlake hosts list --json
dreamlake hosts list --all
```

Text lists show host ID, full name, catalog state, and verified connection state.
An older backend without catalog metadata shows catalog state as unknown. JSON returns
`namespace`, optional `group`, `hosts` (the original host/enrollment records), and
`total` (the number of distinct hosts shown after filtering). A failed page fails
the command; it does not emit a successful partial listing. Pagination reads a live inventory,
not an atomic snapshot; hosts added or removed during the read can change results.

Inspect a full name or the 24-character host ID returned by the API. An ID uses
the personal namespace unless `--namespace` is supplied; a full name already
contains its namespace, and a conflicting flag is rejected.

```bash cli-help="hosts status"
dreamlake hosts status geyang/workstations/worker
dreamlake hosts status HOST_ID --namespace geyang --json
dreamlake hosts status 'geyang/workstations/*' --page 2 --page-size 100 --json
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
dreamlake hosts list --namespace geyang --all --archived include
dreamlake hosts list --namespace geyang --all --archived only
```

`--all` controls connection state; `--archived` controls catalog visibility.
Use both flags to include offline archived hosts. Permanent entry deletion is
not supported.

Read the catalog revision before submitting a change. Lifecycle commands require
one exact lowercase 24-character Host ID, not a name or wildcard. Use the revision
returned by the read; `0` below illustrates a record with no prior catalog changes.

```bash cli-help="hosts lifecycle"
dreamlake hosts lifecycle HOST_ID --namespace geyang --json
```

```bash cli-help="hosts archive"
dreamlake hosts archive HOST_ID --namespace geyang --request-id archive-example-1 --expected-revision 0 --json
```

```bash cli-help="hosts restore"
dreamlake hosts restore HOST_ID --namespace geyang --request-id restore-example-1 --expected-revision 1 --json
```

Every accepted new request increments the revision, including archiving an
already archived record or restoring an active record. The original archive
timestamp is retained by repeated archive actions. Restore clears that timestamp.
All responses state `executionAffected:false` and `retirementSupported:false`.

Retain the request ID, Host ID, namespace, action and expected revision. After an
ambiguous transport failure, repeat that exact request; the CLI never retries or
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
dreamlake hosts enrollments geyang/workstations/worker
dreamlake hosts enrollments HOST_ID --namespace geyang --json
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
dreamlake hosts metrics geyang/workstations/worker --enrollment ENROLLMENT_ID
dreamlake hosts metrics HOST_ID --namespace geyang --enrollment ENROLLMENT_ID --resolution 60 --json
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
dreamlake hosts check geyang/workstations/worker --enrollment ENROLLMENT_ID --action ssh
dreamlake hosts check HOST_ID --namespace geyang --enrollment ENROLLMENT_ID --action tracked-run --json
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

## Enrollment

`dreamlake hosts enroll` bootstraps a user-owned nymph on this computer with
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

The command prints a request ID before enrollment. After an interrupted request,
repeat the same inputs with `--request-id <id>`. If the API returns `retryAt`, wait
until that time before starting a new request. JSON errors retain the request ID
and available operation/retry fields.
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
dreamlake hosts enroll --local --name geyang/dev/my-mac --web-terminal
# Enroll without browser shell access.
dreamlake hosts enroll --local --name geyang/dev/my-mac --no-web-terminal
```

## Output format

Enrollment prints a readable summary by default, including the host name,
verified connection state, and recovery identifiers. Errors also use readable
text. Use `--json` for a structured success, pending, validation, or error receipt;
JSON mode suppresses the introductory request-ID progress line. `--quiet`
suppresses progress only and does not select JSON or hide the final receipt.
These output changes require CLI 0.52.1.

```bash cli-help="hosts enroll"
# Human-readable output (default).
dreamlake hosts enroll --local --name geyang/dev/my-mac
# Structured output for scripts.
dreamlake hosts enroll --local --name geyang/dev/my-mac --json
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
dreamlake hosts enroll -n geyang/lab/current-computer --local --dry-run
dreamlake hosts enroll -n geyang/lab/current-computer --local \
  --request-id current-computer-001
dreamlake hosts status geyang/lab/current-computer --json
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
dreamlake run --target geyang/lab/current-computer --include hello.py \
  --request-id local-hello-001 --timeout-seconds 60 --uv-run python hello.py
```

The command waits for the result and displays its output. Registration alone
does not prove job execution readiness; use the completed run as the check.

## macOS prerequisites and service lifecycle

Use CLI 0.52.0 or newer. Install Python 3, `uv` and OpenSSL 3 using your chosen
package manager if they are absent. For Homebrew:

```shell
brew install python uv openssl@3
dreamlake hosts enroll --local --name YOUR_NAMESPACE/dev/my-mac \
  --nymph-version v0.1.11
dreamlake hosts status YOUR_NAMESPACE/dev/my-mac --json
```

Starting with CLI 0.71.0, a version such as `0.1.26` is normalized to the published
`v0.1.26` installer tag; already prefixed tags and `latest` are preserved.

An existing Nymph binary on PATH is reused; `--nymph-version` selects the
installer version only when Nymph is missing. Check an existing daemon's version
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
dreamlake hosts enroll -p fortyfive/bos14 -n bos14-ctrl --ssh bos14-ctrl
dreamlake hosts status fortyfive/bos14/bos14-ctrl --json
dreamlake hosts status 'fortyfive/bos14/*' --json
```

For configuration-only validation:

```shell
dreamlake hosts enroll -p fortyfive/bos14 -n bos14-ctrl \
  --ssh bos14-ctrl --dry-run

# Equivalent full name, with structured output:
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl \
  --ssh '-i "/Users/ge/My Keys/key" \
    -J ge@bastion.example.com \
    -p 2222 geyang@bos14-ctrl.internal' --dry-run --json
```

Names have exactly three components: namespace/group/host. A matching explicit
prefix and embedded prefix are accepted; conflicting prefixes and wildcards are
rejected. Each component is 1–64 letters, digits, underscores or hyphens and starts
with a letter or digit. A namespace in a name does not grant access to it.
The control-plane namespace comes from the selected connection and can differ
from the DreamLake namespace.

## JSON input

```shell
dreamlake hosts enroll --config ./bos14-host.json --dry-run --json
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
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
  --save-credentials --target-password ge/bos14/login

# Explicit, separate target and jump-key exports.
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh '-J jump bos14-ctrl' \
  --save-credentials --target-key ge/bos14/key=/secure/target-key \
  --jump-key jump=ge/jump/key=/secure/jump-key

# Automation: exact UTF-8 bytes from a protected file/pipe, never argv secrets.
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
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
dreamlake vault bind --host-id HOST_ID --enrollment-id ENROLLMENT_ID \
  --entry-id ENTRY_ID --entry-revision 1 --role target --endpoint bos14-ctrl \
  --kind password
dreamlake vault bindings --host-id HOST_ID --enrollment-id ENROLLMENT_ID
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
clients do not expose these commands; check `dreamlake --version` and command help.

`hosts create` uses the existing provider launch flow and requires automatic
Nymph enrollment. Choose an existing provider and a full host name in its
namespace. One host is created per request (`--count 1`); a stable request ID
allows the same request to recover its instance after an interrupted response.
Provider configuration, launch layers, credentials and bootstrap prerequisites
are the same as for `providers instances launch`.

```bash cli-help="hosts create"
dreamlake hosts create geyang/PROVIDER_ID --host-name geyang/dev/worker \
  --layer development --request-id create-worker-01
```

A launch receipt does not prove enrollment or SSH readiness. By default, the
shared launch flow waits for enrollment and web terminal setup; pending setup
returns a receipt with recovery instructions. `--no-web-terminal` disables that
terminal setup and its wait, so inspect enrollment separately.

Inspect the provider binding and cloud-observed power state before choosing a
power operation. Use the exact enrollment ID reported by this command.

```bash cli-help="hosts power"
dreamlake hosts power geyang/dev/worker
dreamlake hosts power HOST_ID --namespace geyang --json
```

Power commands apply to the machine, not just the Nymph process. They require a
verified AWS EC2 provider launch binding with its configured launch server.
Kubernetes and other provider kinds, and manually enrolled laptops or servers,
are unsupported by the Host power API.
Names, online status and matching tags cannot establish a cloud-instance binding.
Start, stop, restart and terminate preserve the Host catalog record and do not
revoke enrollment credentials. `restart` uses the provider's reboot operation.

```bash cli-help="hosts start"
dreamlake hosts start geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id start-worker-01
```

```bash cli-help="hosts stop"
dreamlake hosts stop geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id stop-worker-01
```

```bash cli-help="hosts restart"
dreamlake hosts restart geyang/dev/worker --enrollment ENROLLMENT_ID \
  --request-id restart-worker-01
```

```bash cli-help="hosts terminate"
dreamlake hosts terminate geyang/dev/worker --enrollment ENROLLMENT_ID \
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
dreamlake ssh geyang/dev/worker
dreamlake ssh HOST_ID --namespace geyang --enrollment ENROLLMENT_ID
```

```bash cli-help="hosts ssh"
dreamlake hosts ssh geyang/dev/worker --duration 1800
```

Select an exact host by ID or full name. `--enrollment` disambiguates multiple
eligible enrollments on one host; the client refuses ambiguous selection rather
than guessing. Session lifetime is 120–1800 seconds (`--duration`, default 1800).
The 120-second minimum avoids a legacy control-plane deadline mismatch for
60-second delegations. Use `--timeout` for shorter attached commands.

```bash cli-help="exec"
dreamlake exec geyang/dev/worker -- uname -a
dreamlake exec geyang/dev/worker --timeout 30 -- sh -c 'printf "%s\n" "$HOME"'
```

```bash cli-help="hosts exec"
dreamlake hosts exec geyang/dev/worker -- python3 -c 'print("hello")'
```

Place the remote command after `--`. Arguments are passed literally; invoke
`sh -c` explicitly when shell expansion or pipelines are wanted. Output streams
to local stdout/stderr and the command returns the remote exit status. SSH
transport failures return the native SSH error status. `--timeout` closes the
session and returns 124; it does not guarantee termination of detached remote
processes. SSH session cleanup removes temporary local keys and closes the
session. File copy and forwarding remain outside these commands.
