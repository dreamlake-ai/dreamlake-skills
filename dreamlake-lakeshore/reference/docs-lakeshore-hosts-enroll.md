<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/enroll.md at 0.1.150 29155024; do not edit -->

# Enroll a host

**Released clients:** no-save SSH enrollment is available in CLI 0.13/Python 0.10 and later. CLI 0.16 (including its npm wrapper)/Python 0.13 support post-enrollment saving; [real hosted staging acceptance](https://github.com/dreamlake-ai/dreamlake-workspace/blob/main/infra/vault/hosted-host-saving-acceptance.md) covers Nymph installation, saving, restored SSH and tracked execution. Client release, backend rollout and each environment's live verification remain separate.

Use CLI **0.21.2**, Python **0.16.2** and Nymph **0.1.8** for the current [testing guide](https://docs.dreamlake.ai/lakeshore/hosts/testing). Existing services are not upgraded by installing a new client; inspect the installed daemon version before testing recovery.

A **host** is a machine that executes or manages work, including a Slurm control node. Nymph maintains its connection independently after SSH bootstrap. Providers are not required to enroll an existing machine. Start with this Linux computer using `--local` (CLI 0.51.0+), or an SSH-accessible host; use [Resource setup](https://docs.dreamlake.ai/lakeshore/providers/resource-setup) only when infrastructure is needed.

## Fabric enrollment and worker runtime

Host enrollment is the **fabric** step: establish machine identity, connectivity
and remote-management capability. A general development machine needs no task
queue or queue mount. The same host can also run a **runtime worker** that serves
a queue; that process and queue association are configured separately. Enrollment
alone does not make the host a queue consumer. See [queues](https://docs.dreamlake.ai/lakeshore/queues) and
[worker lifecycle](https://docs.dreamlake.ai/lakeshore/lifecycle) for the runtime layer.

Host enrollment currently uses an authorized **execution connection** owned by
the same DreamLake namespace as the host name. For `alice/dev/laptop`, select an
`alice`-owned connection; an org-owned `acme` connection applies to authorized
`acme/...` hosts. Select it explicitly with `--lakeshore-id CONNECTION_ID` when
needed. The remote Lakeshore server namespace does not replace this owner scope.

The connection credential must also be authorized to mint enrollment tokens.
An ordinary namespace access token, `legacy` connection type, `authMode: token`
or online status alone does not prove this. Verify delegated enrollment support
and the credential's explicit authority with the administrator of the deployed
service; do not distribute its global admin token. Resolve authorization before
retrying a failed mint, preserving any pending enrollment's connection, namespace
and machine identity. See [connection authorization](https://docs.dreamlake.ai/lakeshore/connect-to-dreamlake).

Do not use a Vault-backed queue mount ID: an online mount still returns HTTP 409
`queue_mount_execution_unsupported`. A cross-owner connection ID can return
`lakeshore_not_found`. See [connection selection](https://docs.dreamlake.ai/lakeshore/connect-to-dreamlake).

### Pending control-plane change: SSH access for the enrolling owner

The proposed owner-SSH enrollment fix is not yet released. On compatible control
planes, a connection with `canEnrollHosts` receives an exact Worker SSH grant
only after its bound enrollment proves possession of the machine's private key.
The grant is committed with Worker registration and bootstrap-token consumption;
the owner does not need a second per-machine administrator approval. This does
not grant access to unrelated workers, enable a locally disabled SSH endpoint,
or bypass DreamLake's Host ownership and local access checks.

Reconnects preserve the same identity and do not restore revoked SSH grants.
A fresh signed enrollment can repair a legacy missing grant; explicitly revoked
access requires explicit reauthorization. Previously issued bootstrap tokens
without issuer provenance retain their old behavior. Existing clients and Nymph
can use the new flow after the control-plane release; client installation alone
does not enable it on an older service.

Until this change is deployed, an online Host or a terminal target can still lack
the connection's SSH grant. Verify an actual owner command such as
`dl exec YOUR_NAMESPACE/dev/my-computer -- uname -a` rather than treating
discovery as a completed SSH handshake. The companion server fix reports a
known SSH authorization refusal as `403 ssh_access_denied` instead of a generic
`502 controlplane_unavailable`.

## Register this computer without SSH

CLI **0.51.0+** supports direct local registration on Linux. Python 3, OpenSSL,
a systemd user manager and user linger are required. No SSH server, loopback
connection or SSH credentials are needed. The identity key stays on this computer;
the backend still authorizes the namespace and verifies the exact enrollment.

```shell
dl hosts enroll -n YOUR_NAMESPACE/dev/my-computer --local \
  --nymph-version v0.1.11 --request-id my-computer-first-enrollment
dl hosts status YOUR_NAMESPACE/dev/my-computer --json
```

Check `nymph --version` if it is already installed: enrollment reuses a binary
on PATH; `--nymph-version` selects the installer version only when missing.
Nymph v0.1.11 was verified with the first numbered guide. Install `uv` for tracked
Python jobs; the generated service includes the standard user-local binary path.
`--local` and SSH/credential-saving options are mutually exclusive. Dry-run is
available with `--dry-run` and makes no changes. Local mode is currently CLI-only;
no Python SDK local-enrollment argument is claimed here.

Continue with [01: register a computer and launch a job](https://github.com/dreamlake-ai/lakeshore-examples/tree/main/01-hello-ssh).
The first guide was verified against production with SSH disabled: direct
registration, exact online status, hello execution and a persisted success receipt
with exit code zero. See the [numbered guide catalog](https://docs.dreamlake.ai/lakeshore/examples) for
infrastructure recipes and Vault recovery.

For separately supported machine start, stop, restart and termination, see
[Host machine power](https://docs.dreamlake.ai/lakeshore/hosts/power). Enrollment alone does not grant a
provider power binding.

## Host network and system inventory

The owner-scoped host list and detail APIs include nullable `network` and
`system` observations on each enrollment, after verifying the exact host,
machine, Unix user, enrollment, and active daemon key. Missing or unverified
inventory remains null. These fields do not change host ownership or grant
execution access.

`network` contains `observedAt` (ISO timestamp) and `addresses`, an array of
`{interface, address, family}` entries. `family` is `IPv4` or `IPv6`. The source is
Nymph's `capabilities.network` snapshot, capped at 128 entries; malformed
addresses and invalid or future timestamps are rejected. Old samples remain
historical observations. `system` includes nullable `os`, `arch`, `cpuModel`,
`cpuCores`, and `nymphVersion` from the daemon's reported version inventory.
Arbitrary capability data and credentials are not returned.

CLI 0.104.3+ shows addresses, hostname, and user in its default host list,
adds system columns with `--wide`, and shows per-interface detail and sample
freshness in `hosts status`. See the [CLI inventory contract](https://cli.dreamlake.ai/host-enrollment#list-and-inspect-hosts)
for rendering and compatibility. Nymph 0.1.35 and earlier do not report network
inventory; upgrading the CLI alone cannot populate those missing observations.
Default listing performs no SSH, DNS resolution, or external public-IP lookup.
The CLI's explicit `--probe` option performs SSH diagnostics when requested.
Interface addresses may be private, VPN, container, or public addresses and do
not establish reachability or reveal a NAT public IP.

## Archive and restore host entries

CLI 0.73.0+ and the matching catalog API support reversible archiving. Archiving
hides the entry from default inventory lists. It does not stop the machine,
revoke credentials or prevent future work. Names, enrollment IDs and retained
job/history links remain reserved and addressable. Permanent entry deletion is
not supported.

```shell
dl hosts list --all --namespace YOUR_NAMESPACE
dl hosts lifecycle HOST_ID --namespace YOUR_NAMESPACE --json
dl hosts archive HOST_ID --namespace YOUR_NAMESPACE --request-id archive-001 --expected-revision 0 --json
dl hosts list --all --archived only --namespace YOUR_NAMESPACE
dl hosts restore HOST_ID --namespace YOUR_NAMESPACE --request-id restore-001 --expected-revision 1 --json
```

Use the exact lowercase Host ID and the revision returned by `hosts lifecycle`;
0 and 1 above illustrate a previously unchanged entry. `--all` includes offline
and unknown connections; `--archived` separately selects catalog visibility.
Exact ID/name status reads remain available for archived hosts.

The owner-scoped API provides `GET /namespaces/:slug/hosts/:hostId/lifecycle`
and `POST /namespaces/:slug/hosts/:hostId/archive` or `/restore`, with
`{requestId, expectedRevision}`. Listing accepts `archived=exclude|include|only`,
defaulting to exclude. Each accepted new request increments the catalog revision,
even for an already archived/restored entry. After an ambiguous failure, retry
the exact original tuple. A reused ID with changed input or a stale revision
returns 409. A replay returns the historical receipt (`replayed:true`); read
lifecycle again for current state. Authorization is checked again on every retry.

## Inspect in Compute

The [Compute dashboard](https://github.com/dreamlake-ai/dreamlake-ai/pull/310) uses `/:namespace/compute` for the host inventory and `/:namespace/compute/hosts/:hostId` for details. It preserves enrollment instructions, Unix-user identity, verified heartbeat status and a link to tracked runs. Search a group with a pattern such as `fortyfive/bos14/*`, or search `offline`. **Enroll host** opens the CLI handoff; copy the command for another host, or use `--local` on the computer being enrolled.

Deployed to production on September 15, 2026 (05:10 UTC September 16). The old `/:namespace/hosts` list and detail links redirect to Compute. Host APIs, CLI commands and these guide URLs retain their existing names. See the [UI review guide](https://docs.dreamlake.ai/lakeshore/hosts/testing#review-the-live-host-ui).

## Move a private host between namespaces

**Compatibility:** host moves require the matching server API and client.
Installing a client or skill does not enable an older server. Check installed
command help and review the server preview before requesting a move. The
Compute move dialog and Python API are independent of native CLI packaging;
consult the CLI release notes for package availability.

A host has both a namespace and a personal owner. Moving it to an organization
namespace changes where it is filed; it retains its `ownerUserId` and remains
private to that user. Organization membership does not give another member
access to that host. Compute displays the server-provided private state with a
lock and **Private** badge. A namespace name or a badge by itself is not an
access grant.

A host move is different from switching the built-in agent's acting namespace.
Use `/su NAMESPACE` to change the current agent conversation's scope, for
example `/su alice` or `/su acme`. This does not move resources, change the
signed-in user, or navigate the rest of the application. See
[the built-in agent harness](https://docs.dreamlake.ai/dev/builtin-agent-harness#acting-namespace).

The move keeps the Host ID, personal owner, enrollment identities and machine
keys. Saved terminal sessions keep their IDs, original namespace, native
conversation identity and Memo links. The operation makes those sessions private
and removes their public or team sharing; the preview reports the count and
access changes before apply. Daemon metadata refresh updates the retained
session record instead of creating a replacement in the new namespace. Past run records keep their IDs, original namespace, target names and stored
logs. Acknowledged ordinary `uv-run` / `uvx` work may continue against its exact
existing execution; the move neither dispatches replacement work nor changes a
pending cancellation intent. Metrics Sources keep their original namespace,
Source ID, history and broker configuration. The group and host portion of the
computer name stay the same; its namespace prefix changes. Existing execution connections remain bound to their original
connection namespace, and access to that connection is checked separately.
The operation does not install or restart Nymph, launch a machine, or broaden
connection permissions.

### Preview and apply

The owner-scoped routes are:

| Operation | Route | Body |
| --- | --- | --- |
| Preview | `POST /namespaces/:slug/hosts/:id/move/preview` | `{destinationNamespace}` |
| Apply | `POST /namespaces/:slug/hosts/:id/move` | `{destinationNamespace, requestId, expectedRevision, previewHash}` |

Use the exact Host ID and source namespace from inventory. A preview returns
the source and destination namespaces, destination name, personal owner,
private visibility, revision, preview hash, blockers and whether the move is
executable. `sessions` reports `count`, the
`retain_original_namespace_make_private` policy and `accessChanges.public` /
`accessChanges.shared` counts. `runs` reports `count`, `terminal`, `active`
and the `retain_original_namespace_acknowledged_runs` policy. These reviewed
policies are recorded in the receipt. Review these before applying. Apply binds that preview to an
explicit request ID and expected revision; a changed resource or request must
not be silently accepted.

### CLI, TypeScript and Python

The matching CLI separates preview from apply. Use values from the actual
preview instead of the illustrative placeholders below:

```shell
dl hosts move HOST_ID --namespace alice --to acme --dry-run --json
dl hosts move HOST_ID --namespace alice --to acme --confirm \
  --request-id laptop-move-001 --expected-revision REVISION \
  --preview-hash PREVIEW_HASH --json
```

The public TypeScript API is exported by `@dreamlake/dreamlake-cli/api`:

```ts
import { createClient } from '@dreamlake/dreamlake-cli/api'

const hosts = createClient({
  remote: 'https://api.dreamlake.ai',
  token: process.env.DREAMLAKE_API_KEY!,
}).hosts('alice')
const preview = await hosts.movePreview(hostId, 'acme')
// Review preview.name, ownerUserId, visibility and blockers before applying.
if (!preview.executable) throw new Error(preview.blockers.join(', '))
const request = {
  destinationNamespace: 'acme',
  requestId: 'laptop-move-001',
  expectedRevision: preview.revision,
  previewHash: preview.previewHash,
}
const receipt = await hosts.move(hostId, request)
```

Python exposes the same guards:

```python
from dreamlake import DreamLakeClient

client = DreamLakeClient()
preview = client.hosts.move_preview('alice', host_id, 'acme')
# Review the full preview before using it for a mutation.
if not preview['executable']:
    raise RuntimeError(preview['blockers'])
request = dict(
    destination_namespace='acme',
    request_id='laptop-move-001',
    expected_revision=preview['revision'],
    preview_hash=preview['previewHash'],
)
receipt = client.hosts.move('alice', host_id, **request)
```

Save the request before submitting if the caller must survive a restart. The
built-in agent's `dreamlake_host_move_preview` and `dreamlake_host_move` tools
use these same routes. The mutation tool additionally requires the host-move or
write-tools capability for that turn; the capability never replaces resource
permissions.

A move requires current authority in both namespaces and ownership of the
exact host. A destination name collision or an unsupported dependency stops
the move. External jobs, service-account grants or bindings, provider bindings
and configured Slurm inventory still need dedicated migration adapters and
currently block the move. Missing execution acknowledgements, private setup or
delivery work, unfinished reporting cleanup, inconsistent metrics configuration
and inconsistent or ambiguous saved-session bindings also block the move. The
preview identifies those dependencies; do not detach or delete them to force admission. Existing enrollments
alone do not require re-enrollment.

After a timeout or ambiguous response, preserve the source namespace, Host ID,
request ID, destination, expected revision and preview hash. Reconcile with the
same request rather than generating a new identity. A replayed receipt records
the original operation; read host status in its current namespace to establish
current state. Verify the destination inventory and exact enrollment status;
verify terminal and metrics separately before claiming they work.

## Repair an existing enrollment

CLI **0.20.1** and Python **0.16.1** configure persistent enrolled services with
`runtime.keep_alive_s = -1`. Re-enrollment regenerates `nymph.toml` and its systemd
user unit. Before repair, privately back up those two files on the target; retain
the original identity key. After repair, verify the generated idle setting, then
restore only required custom sections such as `private_tracked` and any reviewed
service overrides. Reload the user manager and restart the same unit if you edit
it, then wait for a fresh verified host status.

For an unresolved response, reuse the original request ID to reconcile it. A
confirmed `request_expired` receipt requires a new explicit repair operation ID;
a separately intended repair after a known completed enrollment is also a new
operation. If the server reports `enrollment_busy`, wait until its `retryAt`
window instead of issuing more operation IDs. Keep the same host name, SSH
profile, Unix user and identity key: the existing host/enrollment is reused,
and changing the identity is rejected. Keep the new ID for reconciliation:

**CLI**

```shell
dl hosts enroll -n fortyfive/bos14/bos14-ctrl \
  --ssh bos14-ctrl --request-id bos14-idle-repair-001 \
  --no-save-credentials
dl hosts status fortyfive/bos14/bos14-ctrl
```

**Python**

```python
from dreamlake import DreamLakeClient

client = DreamLakeClient()
result = client.hosts.enroll(
    "fortyfive/bos14/bos14-ctrl",
    ssh="bos14-ctrl",
    request_id="bos14-idle-repair-001",
    save_credentials=False,
)
host = client.hosts.status("fortyfive/bos14/bos14-ctrl")
```

See the [patch release and owned-host idle validation](https://docs.dreamlake.ai/dev/notes/host-enrollment)
for evidence and the distinction between service restart and machine reboot.

## Enroll and inspect

The target needs Python 3, OpenSSL, a systemd user manager with linger enabled by its administrator, and control-plane connectivity. Bootstrap reuses installed nymph or invokes the official installer; it does not install uv. Authenticate your client, verify SSH access, then enroll:

**CLI**

```shell
ssh bos14-ctrl true
dl hosts enroll -p fortyfive/bos14 -n bos14-ctrl \
  --ssh bos14-ctrl --request-id bos14-first-enrollment
dl hosts status fortyfive/bos14/bos14-ctrl
dl hosts status 'fortyfive/bos14/*'
```

**Python**

```python
from dreamlake import DreamLakeClient
client = DreamLakeClient()
result = client.hosts.enroll(
    name="bos14-ctrl", prefix="fortyfive/bos14", ssh="bos14-ctrl",
    request_id="bos14-first-enrollment", wait_seconds=60,
)
host = client.hosts.status("fortyfive/bos14/bos14-ctrl")
group = client.hosts.status("fortyfive/bos14/*")
```

Preferred names are `<namespace>/<group>/<host-name>/<unix-user>`, for example `fortyfive/bos14/bos14-ctrl/geyang`. The final component must match the enrolled Unix account. Legacy `<namespace>/<group>/<host-name>` names remain valid. `-p fortyfive/bos14 -n bos14-ctrl` and `-n fortyfive/bos14/bos14-ctrl` identify the same host; conflicting prefixes fail. Keep the machine name (`bos14-ctrl`), and use `bos14-node-000` for another host. Wildcards inspect existing hosts only. A namespace prefix grants no authorization.

The API checks namespace access before target identity creation. Nymph's private key stays on the target; a short-lived grant binds its public key to host, Unix user, and enrollment. The initial implementation reserves the name to its owner and rejects another identity. Adding a second Unix user to the same host requires a future explicit linking workflow; names alone cannot authorize it.

## SSH, passwords, and jump hosts

`--ssh` accepts an SSH-config alias, `user@host`, or a quoted argument vector without a repeated `ssh` executable. Existing local SSH configuration remains useful:

```ssh-config
Host bos14-ctrl
  HostName bos14-ctrl.internal
  User geyang
  Port 2222
  ProxyJump ge@bastion.example.com
  IdentityFile ~/.ssh/id_ed25519
```

```shell
dl hosts enroll -p fortyfive/bos14 -n bos14-ctrl \
  --ssh '-J ge@bastion.example.com
    -p 2222
    -i /path/to/id_ed25519
    geyang@bos14-ctrl.internal'
```

Multiline strings preserve argument boundaries without shell expansion. There must be one destination and no appended remote command. Agent forwarding is not required. Never put passwords or private-key contents in arguments or JSON. Verify password access with `ssh geyang@bos14-ctrl.internal`; CLI terminal/password and separate jump-host prompt behavior still need real acceptance. Python always uses noninteractive SSH and fails if a password or passphrase prompt is needed.

## Configuration and dry-run

Save this as `bos14-host.json`. Identity-file paths refer to local bootstrap credentials, not uploaded key contents.

```json
{
  "name": "fortyfive/bos14/bos14-ctrl",
  "ssh": {
    "host": "bos14-ctrl.internal",
    "user": "geyang",
    "port": 2222,
    "identityFile": "/path/to/id_ed25519",
    "jumpHost": "ge@bastion.example.com",
    "options": { "ServerAliveInterval": "30" }
  }
}
```

**CLI**

```shell
dl hosts enroll --config ./bos14-host.json --dry-run --json
```

**Python**

```python
plan = client.hosts.plan(config="bos14-host.json")
preview = client.hosts.enroll(config="bos14-host.json", dry_run=True)
```

Explicit name/prefix fields override configuration fields; SSH replaces the whole SSH object. Unknown fields, invalid ports, unsupported options, and conflicts fail before effects. Dry-run returns `status: "validated"`, `enrolled: false`, and `authorizationVerified: false`; it contacts no server/host and reads no key. Direct-on-target enrollment without SSH is not implemented.

## Readiness, retry, and credentials

`online` means the backend verified a fresh active worker and matching bound identity; it does not prove runner readiness or successful execution. Timeout can return `pending`. Results include stable host/enrollment IDs and operation/request IDs, never bootstrap grants. Reuse the same request ID to reconcile an uncertain write; changed payloads conflict. Exact/group status uses the caller's access. Python raises sanitized exceptions rather than prompting or exiting.

Repeated enrollment and signed restart passed against real services with local transport/supervision adapters. Still verify actual Linux supervision, reboot recovery, and a workload on the intended host. Installation or a heartbeat alone is insufficient.

Credential saving happens after enrollment in native CLI 0.15/Python 0.12 with a compatible backend. Interactive consent defaults to `[y/N]`; `--save-credentials` consents, `--no-save-credentials` declines, and `--quiet` only suppresses progress. Password prompts are masked; Python accepts explicit `HostCredential` inputs and never prompts. Target and jump credentials are selected separately. Saving failure leaves the successful enrollment intact and does not authorize backend SSH delegation. Use CLI 0.16 or later for npm-wrapper password descriptors; the 0.15 wrapper dropped descriptors above 2. See [Managing host credentials](https://docs.dreamlake.ai/lakeshore/hosts/credentials) for status and the paired acceptance examples.

## Live infrastructure is a separate delivery state

The September 12 bos14 demonstration had a signed Slurm heartbeat directly to `dev-api.lakeshore.dreamlake.ai:443` with trusted TLS and no laptop tunnel. Operator SSH still needs VPN. That recorded deployment required a fresh token after process restart; merged reconnect code does not prove it was upgraded. Production `api.lakeshore.dreamlake.ai` was verified as a separate fresh TLS-protected instance with zero workers. Neither observation establishes production host-API rollout or workload execution.

## Related documentation

- **[Python host API](https://github.com/fortyfive-labs/dreamlake/blob/main/docs/hosts.md)** — Actual methods, errors, pagination, and noninteractive behavior.
- **[Host credentials](https://docs.dreamlake.ai/lakeshore/hosts/credentials)** — Vault operations and the optional enrollment-saving boundary.
- **[Resource setup](https://docs.dreamlake.ai/lakeshore/providers/resource-setup)** — EC2/EKS Terraform examples; existing hosts need no provisioning.
- **[Python follow-up plan](https://docs.dreamlake.ai/dev/plans/hosts-python-api)** — Remaining parity and acceptance work.
- **[Provider plan](https://docs.dreamlake.ai/dev/plans/providers)** — Separate Slurm/Kubernetes registration, provisioning, and workload acceptance.

## Rename an enrolled host

Rename the catalog address in place with `dl hosts rename HOST_ID --name NEW_NAME --expected-name CURRENT_NAME`.
The same namespace, owner, Host ID, enrollment, machine keys and saved sessions are preserved.
After an uncertain response, retry those exact inputs. Read status back under the new name,
then verify SSH. See the [CLI rename reference](https://cli.dreamlake.ai/host-enrollment#rename-a-host-without-re-enrolling)
for the HTTP, TypeScript and Python APIs.

## SSH capacity and local permission boundaries

For usage counts, namespace-versus-worker limits, complete SSH configuration options, validation and mixed-version rollout, see [SSH capacity and usage](docs-lakeshore-hosts-browser-terminal.md#ssh-capacity-and-usage). Verify the guide’s component version requirements and deployed versions before use.

The [Nymph permissions and commands record](docs-lakeshore-hosts-nymph-permissions.md) distinguishes local policy, authenticated commands, read-only inspection, startup-only configuration, existing lifecycle exceptions and the requirements for a future dynamic-configuration feature. Capacity is not authority: increasing a quota must not enable SSH, upload data or bypass local execution denial.
