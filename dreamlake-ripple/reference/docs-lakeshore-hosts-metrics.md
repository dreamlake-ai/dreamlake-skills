<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/metrics.md at 0.1.214 98a81329b; do not edit -->

# Machine metrics

Machine readings are live. Nymph 0.1.9 through 0.1.33 collect resource
readings by default, and 0.1.34 and later collect only when configured to
(see [Local collection](#local-collection)). DreamLake serves those readings
through the Lakeshore control plane. **Compute → host → Brief → Resources**
shows the recorded readings with the time of the last sample, or "No telemetry
received" when there are none; it never shows example data. The standalone
[Ripple collector](#ripple-collector) is a separately released CPU and memory
collector; its section states which version each feature needs.

Nymph collects resource readings on the machine, including machines outside AWS.
CloudWatch is not required. Linux readings cover CPU utilization, memory,
filesystem capacity for the worker directory, network rates and block-device
I/O. NVIDIA GPUs additionally report utilization, VRAM, temperature and power
when `nvidia-smi` supports those fields. Missing drivers and unsupported fields
produce missing readings. macOS currently provides filesystem and supported
NVIDIA readings only. This feature does not collect or index process arguments,
program output, tool output or terminal contents.

## Where readings come from

Each enrollment has one source of readings, chosen on every read in this
order:

1. A metrics Source configured for the enrollment
   ([Direct Source snapshots](#direct-source-snapshots-operator-configured)).
   The response has `mode: "source"`.
2. Otherwise, Ripple, if the DreamLake operator has enabled the enrollment
   for Ripple ([Ripple collector](#ripple-collector)). Ripple provides CPU and
   memory only: `cpu_percent`, `memory_total_bytes` and `memory_used_bytes`.
3. Otherwise, the readings Nymph reports to the Lakeshore control plane.

A read uses only that source. If the source is unavailable the request fails
(see [Read through DreamLake](#read-through-dreamlake)); it does not fall back
to another source, and readings from different sources are never combined.

## Local collection

**Since [Nymph 0.1.34](https://github.com/dreamlake-ai/nymph/releases/tag/v0.1.34):** Nymph collects and reports readings only when the daemon
configuration sets `[metrics] enabled = true`. Configurations that omit the
key stop collecting after upgrading. Nymph does not rewrite configuration
files, and an explicit `enabled = true` keeps collection on. See
[host testing](https://docs.dreamlake.ai/lakeshore/hosts/testing) for the related job output setting.

### Direct Source snapshots (operator-configured)

An owner can enable a managed metrics Source for an enrollment with
`POST /namespaces/:slug/hosts/:hostId/enrollments/:enrollmentId/metrics/source`
(an empty JSON object and an `Idempotency-Key`). The matching GET reports
`unconfigured`, `pending`, or `ready`; retry the POST after a pending result.
Configuration uses the existing Source permissions and storage. A scoped broker
credential stays on the control plane; Nymph receives only short-lived upload
URLs for its enrollment's fixed snapshot path.

Nymph uploads the complete bounded history directly to object storage. SHA256,
byte length, content type and snapshot identity are signed. Conditional writes
prevent overlapping uploads from replacing a newer snapshot. A failed upload
leaves the previous snapshot readable. The backend checks object metadata to
confirm completion without fetching the readings or writing datapoints to Mongo.

`POST .../metrics/source/read-capability` returns a short-lived GET capability;
the dashboard fetches the snapshot directly from storage. A missing object means
the first upload is still pending. Revocation blocks new capabilities; issued
capabilities remain valid until expiry (uploads two minutes, reads five minutes).
Changing a binding uses a new object prefix so old upload URLs cannot change the
new binding. This does not add a metrics ingestion service or a new storage tier.

For an existing owned enrollment, using the same authenticated API origin as
the dashboard:

```shell
curl --fail-with-body -X POST \
  "$DREAMLAKE_API_URL/namespaces/$NAMESPACE/hosts/$HOST_ID/enrollments/$ENROLLMENT_ID/metrics/source" \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: enable-machine-metrics' \
  --data '{}'
```

This requires the compatible Nymph, Lakeshore control plane and DreamLake
backend releases. The operator pins `LAKESHORE_METRICS_BROKER_ORIGIN` on the
existing control plane to the DreamLake API's HTTPS origin. The managed Source
uses its existing bucket configuration; no new host, bucket or paid service is
provisioned. Configure the bucket's existing CORS policy to allow the dashboard
to GET snapshots; never make the bucket public. The scoped broker credential
is created and encrypted by the existing control-plane secret store during
setup and never returned to the browser or daemon.

The source implementation samples every 10 seconds in a separate background
task. CPU and I/O rates need two readings. Counter resets and gaps longer than
30 seconds invalidate rates until a new baseline is available. GPU probes have
a two-second deadline and bounded output. Collection and persistence failures
do not interrupt workload execution.

```toml
[metrics]
enabled = true
# Optional: defaults beside identity.key_file, with a .metrics.json extension
history_file = "/var/lib/dreamlake/machine.metrics.json"

[introspect]
enabled = true
```

With a binary built from the matching source:

```shell
nymph metrics --once
nymph metrics
curl http://127.0.0.1:9876/metrics
```

`--once` reads the current host without starting/registering a worker or writing
history. The other commands read the running daemon's loopback API. Do not expose
that unauthenticated endpoint on the network.

## Ripple collector

Ripple is a small standalone CPU and memory collector. It can print local
readings with no DreamLake account, or report an enrolled host to DreamLake
once the DreamLake operator has enabled that host for Ripple.

| | Linux | macOS (since v0.4.0) |
| --- | --- | --- |
| Architectures | `amd64`, `arm64` | Apple silicon (`arm64`), Intel (`amd64`); macOS 12 or later |
| Default install location | `/usr/local/bin` (uses `sudo` only if not writable) | `~/.local/bin` (created if missing; no `sudo`) |
| Service | systemd system service, run as root | per-user launchd agent, run as yourself, never as root |
| Reads | `/proc` | Mach host and VM statistics |

Releases are published at
`https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple`:
`install.sh` at the root, `latest/<file>` (moves forward with each release)
and `vX.Y.Z/<file>` (immutable). Each version holds one
`ripple-<os>-<arch>.tar.gz` per platform, `install.sh`, `setup-systemd.sh`,
`setup-launchd.sh` (v0.4.0+), a `.sha256` file beside each, `SHA256SUMS`,
`VERSION` and `manifest.json`.

### Install the binary

```shell
RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
RIPPLE_VERSION=v0.4.0

curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version "$RIPPLE_VERSION"
# Linux without sudo: install into a directory you own (it must exist)
mkdir -p "$HOME/.local/bin"
curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version "$RIPPLE_VERSION" --dest "$HOME/.local/bin"
```

`install.sh` detects the OS and architecture (on Apple silicon it installs
`arm64` even from a Rosetta shell), checks the archive's SHA-256 against its
`.sha256` file before extracting, and refuses a binary that does not report
the requested version. It replaces an existing binary by an atomic rename;
a running service keeps the old binary until it restarts. The `.sha256` file
comes from the same origin as the archive, so it detects corruption, not
tampering: for authenticity, take the hash from that version's `SHA256SUMS`
through a separate channel and pass `--sha256 <hash>`.

The Apple silicon binary is ad-hoc signed by the linker; the Intel binary is
unsigned. Neither is Developer ID signed or notarized. Install them with
`install.sh`, which runs them as downloaded. Do not download the archive
through a browser and do not remove its quarantine attribute or override
Gatekeeper to run it.

### Local readings

No account, token or endpoint is involved, and nothing is sent:

```shell
ripple once                         # one set of samples, labeled host_id="local"
ripple once --machine-id=my-laptop  # choose the label
ripple help                         # commands; `ripple <command> -h` lists flags
```

On macOS use `~/.local/bin/ripple` if that directory is not on your `PATH`.
`ripple once` prints Prometheus text: `lakeshore_host_cpu_usage_ratio`,
`lakeshore_host_memory_total_bytes` and
`lakeshore_host_memory_available_bytes`.

### What the readings mean

CPU is the share of non-idle time between two readings. On Linux, available
memory is the kernel's `MemAvailable`. On macOS it is an **estimate**: free
pages (which already include speculative pages; they are not added again),
plus file-backed and purgeable pages, times the page size. Wired, compressed
and other app memory are not counted, so total minus available approximates
Activity Monitor's "Memory Used". Ripple measures the kernel it runs on: in
a container on a Mac (for example Docker Desktop) it reports Docker's Linux
virtual machine, not the Mac.

### Report an enrolled host to DreamLake

Reporting is enabled per enrollment by the DreamLake operator; there is no
self-service token. Ask the operator for:

- the enrollment's machine ID (`host-…`); samples labeled with any other ID
  are refused;
- a machine token issued for that machine ID. It can only submit samples for
  that enrollment; it cannot read metrics or call any other API, and a user
  sign-in token cannot submit samples.

Save the token in a file only you can read (mode `0600`), without putting it
on a command line, then check the configuration. `check` validates the
flags, the token file and access to the counters and sends nothing:

```shell
MACHINE_ID=host-…                            # from the operator
TOKEN_FILE=/root/ripple-token                # Linux service; on macOS e.g. "$HOME/ripple-token"
(umask 077; cat > "$TOKEN_FILE")           # paste the token, then Ctrl-D

ripple check --delivery-mode=staged \
  --url=https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
  --machine-id="$MACHINE_ID" --token-file="$TOKEN_FILE"
```

The endpoint answers `401` without a valid machine token, `202` while
samples are only staged and `204` once every submitted sample is in the
hourly archive; the collector keeps its local spool (up to 7 days) until
then. Samples older than 8 days are refused. Readings appear through the
same [read endpoint](#read-through-dreamlake) and history windows, as
`cpu_percent`, `memory_total_bytes` and `memory_used_bytes` (total minus
available at the same sample time).

### Run as a systemd service (Linux)

As root on the machine to be measured, with the binary in `/usr/local/bin`:

```shell
curl -fsSLO "$RIPPLE_BASE/$RIPPLE_VERSION/setup-systemd.sh"
curl -fsSL "$RIPPLE_BASE/$RIPPLE_VERSION/setup-systemd.sh.sha256" | sha256sum -c -

bash setup-systemd.sh --machine-id "$MACHINE_ID" \
  --url https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
  --token-file /root/ripple-token --delivery-mode staged --dry-run
# review the plan, then run the same command without --dry-run

systemctl status ripple.service
journalctl -u ripple.service
ripple status --spool-dir=/var/lib/lakeshore-host-metrics   # spool backlog
```

`--token-file` must be an absolute path to a root-owned regular file with
mode `0600` or `0400`. `--dry-run` prints the files it would write and
changes nothing; it does not check the token file's owner or mode, so the
real run can still refuse. `--no-start` enables the service without starting
it; `--help` lists every option. The script creates the no-login system user
`lakeshore-host-metrics`, copies the token to
`/etc/lakeshore-host-metrics/token` (owned by that user, mode `0400`),
writes `/etc/lakeshore-host-metrics/config.env` and
`/etc/systemd/system/ripple.service`, keeps its spool in
`/var/lib/lakeshore-host-metrics`, and runs `ripple check` as the service
user before enabling and restarting the service. It refuses before writing
anything if a target was not written by it, if an unrelated account or
state directory with the same name exists, or if the token is not
root-owned with mode `0600` or `0400`. The unit runs without capabilities,
under `ProtectSystem=strict`, with `MemoryMax=64M`, at lower CPU and I/O
priority than the host's own services.

To upgrade, rerun `install.sh` and then `setup-systemd.sh`. To rotate the
token, rerun `setup-systemd.sh` with the new token file.

### Run as a launchd agent (macOS)

As yourself (not root) on the Mac to be measured, with the binary in
`~/.local/bin`:

```shell
curl -fsSLO "$RIPPLE_BASE/$RIPPLE_VERSION/setup-launchd.sh"
curl -fsSLO "$RIPPLE_BASE/$RIPPLE_VERSION/setup-launchd.sh.sha256"
shasum -a 256 -c setup-launchd.sh.sha256

bash setup-launchd.sh --machine-id "$MACHINE_ID" \
  --url https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
  --token-file "$HOME/ripple-token" --delivery-mode staged --dry-run
# review the plan, then run the same command without --dry-run

launchctl print "gui/$(id -u)/ai.dreamlake.ripple" | grep state
ripple status --spool-dir "$HOME/Library/Application Support/ripple/spool"
```

`--token-file` must be an absolute path to a regular file you own with mode
`0600` or `0400`. The script runs `ripple check` before writing anything, so
`--dry-run` already rejects a wrong token file; it prints the agent plist it
would write. `--binary` selects another binary; `--no-start` writes the
agent without loading it (it starts at your next login); `--help` lists every
option. The script writes only:

- `~/Library/LaunchAgents/ai.dreamlake.ripple.plist` (label `ai.dreamlake.ripple`);
- `~/Library/Application Support/ripple/token`, a `0600` copy of the token;
- `~/Library/Application Support/ripple/spool/` (`0700`);
- `~/Library/Logs/ripple/ripple.log`.

A plist it did not write is never overwritten or removed. The agent starts
at login, restarts after a failure, and runs at background priority.
**It runs only while you are logged in**: Ripple provides no system-wide
macOS service, and readings stop while nobody is logged in to that account.

To upgrade, rerun `install.sh`, then
`launchctl kickstart -k "gui/$(id -u)/ai.dreamlake.ripple"`. To rotate the
token, rerun `setup-launchd.sh` with the new token file.

### Automatic updates

Since v0.5.0, opt-in. By default Ripple never updates itself: you pin a
version with `install.sh --version` and upgrade by hand as above. A reporting
host can opt in instead. It then updates only when all of these hold:

- its service was set up with `--auto-update`;
- the Host's owner has set an upgrade target for that enrollment in
  DreamLake (see [Set the upgrade target](#set-the-upgrade-target)). Without
  a target nothing updates, and clearing the target stops further updates;
- the target is a published stable release (`vX.Y.Z`) newer than the running
  version. Ripple never downgrades, never follows `latest/`, and pre-release
  or development builds never update. Publishing a release updates no host
  by itself.

Ripple learns the target only from its own accepted deliveries (staged mode
over `https://`), so opting in adds no requests. Before updating it downloads
that version's `manifest.json` and archive from the release base, checks the
archive's size and SHA-256 against the manifest, and checks that the new
binary reports the target version. It then writes buffered samples to the
spool, replaces its executable by an atomic rename and restarts itself in the
same process. Spooled samples are kept and sent as after any restart. If any
step fails, Ripple keeps running the current version and retries after a
cooldown (5 minutes by default).

The service never runs as root to update itself and never uses `sudo`.
Updating needs an executable the service's own account can replace, so the
setup scripts keep a separate copy for the service:

| | Linux | macOS |
| --- | --- | --- |
| Opt in | as root: `setup-systemd.sh … --delivery-mode staged --auto-update` | as yourself: `setup-launchd.sh … --delivery-mode staged --auto-update` |
| Service runs | `/var/lib/ripple-bin/ripple`, owned by the `lakeshore-host-metrics` account | `~/Library/Application Support/ripple/bin/ripple`, owned by you |
| Unchanged | `/usr/local/bin/ripple` stays root-owned | `~/.local/bin/ripple` |

Use the other flags exactly as in the setup sections above; `--dry-run`
shows the plan first. For a service that is already set up, `--token-file`
can be the service's own copy (`/etc/lakeshore-host-metrics/token` on Linux,
`~/Library/Application Support/ripple/token` on macOS); setup then keeps it
in place. `--auto-update` needs staged delivery, an `https://`
URL and a stable v0.5.0 or later `--binary`. Setup never replaces a newer
service copy (the result of an update) with an older `--binary`, and refuses
a copy of the same version with different bytes. Rerunning
setup without `--auto-update` opts out; the service then runs `--binary`
again and the copy is kept. Versions before v0.5.0 have no updater: install
v0.5.0 with `install.sh --version v0.5.0` and rerun setup with
`--auto-update` once, by hand.

#### Set the upgrade target

The target belongs to one enrollment of one Host. Only the Host's owner, who
still has `lakeshore:use` in the namespace, can read or change it; people
the Host is shared with cannot. It takes effect without any change on the
host, within about 30 seconds:

```shell
TARGET_URL="$DREAMLAKE_API_URL/namespaces/$NAMESPACE/hosts/$HOST_ID/enrollments/$ENROLLMENT_ID/ripple-target"

curl --fail-with-body -H "Authorization: Bearer $DREAMLAKE_TOKEN" "$TARGET_URL"
curl --fail-with-body -X PUT "$TARGET_URL" \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" -H 'Content-Type: application/json' \
  --data '{"targetVersion": "v0.5.0"}'
# clear it: --data '{"targetVersion": null}'
```

Both return `{"enrollmentId", "hostId", "targetVersion", "updatedAt"}`;
`targetVersion` is `null` when no target is set. The value must be a stable
release tag `vX.Y.Z` without leading zeros, at most 32 characters; anything
else, including `latest`, is refused with `400 invalid_target_version`.
`403 forbidden` means you lack `lakeshore:use` in the namespace;
`404 host_not_found` also means you are not the Host's owner, and
`404 enrollment_not_found` that the enrollment is not an active one of this
Host. Setting the current value again changes nothing. DreamLake does
not check that the version is published: set only a version listed on the
release base. Collectors without `--auto-update` ignore the target.

#### Check which binary runs

A changed file or setting does not prove which binary runs. Since v0.5.0,
`ripple status --process` prints the running process as it recorded itself:
PID, version, executable path, the SHA-256 of the running image,
`auto_update`, and after an update `updated_from` and the last attempt's
target and result (plain `ripple status` output is unchanged). Compare it
with the service's process:

```shell
# Linux (root)
ripple status --process --spool-dir=/var/lib/lakeshore-host-metrics
PID=$(systemctl show -p MainPID --value ripple.service)
sha256sum /proc/$PID/exe                 # equals sha256= above
journalctl -u ripple.service | grep -E 'auto-update|starting'
# macOS (as yourself)
ripple status --process --spool-dir "$HOME/Library/Application Support/ripple/spool"
launchctl print "gui/$(id -u)/ai.dreamlake.ripple" | grep -E 'pid|state'
lsof -a -p <pid> -d txt -Fi | head -2   # inode of the running image
stat -f %i "$HOME/Library/Application Support/ripple/bin/ripple"
```

After an update the log shows `auto-update: installed; re-executing`, then
`auto-update complete` and `starting version=… updated_from=…` under the
same PID. Neither the log nor the status record contains the token.

### Stop or remove

Check the spool backlog first: deleting the spool loses samples the API has
not acknowledged yet.

```shell
# Linux (root)
systemctl disable --now ripple.service
# macOS (as yourself)
bash setup-launchd.sh --uninstall
```

`setup-launchd.sh --uninstall` stops the agent and removes its plist; it
keeps `~/Library/Application Support/ripple` (token and spool) and
`~/Library/Logs/ripple` for you to delete. On Linux there is no uninstaller:
the binary, `/etc/systemd/system/ripple.service`,
`/etc/lakeshore-host-metrics/`, `/var/lib/lakeshore-host-metrics/` and the
`lakeshore-host-metrics` user remain. Stopping does not revoke the token;
ask the operator to revoke it when the machine stops reporting.

## Bounded history

| Resolution | Maximum retention |
| --- | --- |
| 10 seconds | 1 hour |
| 1 minute | 24 hours |
| 15 minutes | 7 days |
| 1 hour | 30 days |

Buckets retain averages, peaks, valid-value counts and total sample counts.
Missing buckets remain gaps; missing values are distinct from zero. Coverage
is the valid count relative to expected 10-second samples. Current buckets are
partial. A snapshot is replaced atomically once per minute and on orderly
shutdown; each snapshot is limited to 2 MiB, keeping active and temporary files
together under 5 MiB. Fine history is evicted first when space is tight.
Malformed or oversized saved history is ignored on restart. A crash can lose
the most recent minute. Retention windows are maxima, not guaranteed coverage.

Signed worker heartbeats carry recent idempotent bucket updates. Replayed
updates replace the same bucket without double counting. A long disconnection
can leave gaps in remote fine history; local history remains authoritative.

## Read through DreamLake

The new read-only endpoint is scoped to the authenticated owner, namespace,
host and enrollment. It verifies the worker's exact enrollment binding and an
active matching daemon key before reading the control-plane metrics. Queue-only
mounts do not grant this access. It never executes a command to obtain readings.

```shell
curl --fail --silent --show-error \
  -H "Authorization: Bearer $DREAMLAKE_TOKEN" \
  "$DREAMLAKE_REMOTE/namespaces/$NAMESPACE/hosts/$HOST_ID/enrollments/$ENROLLMENT_ID/metrics?resolution=60"
```

Allowed resolutions are `10`, `60`, `900` and `3600` seconds; the default is `60`.
The response contains `latest`, `tiers` and `stale`. `latest` is null when no
readings exist. All timestamps are Unix seconds. A reading older than 90 seconds
is stale. HTTP 401/403 indicates missing access, 404 a missing owned binding,
409 an unverified worker identity, and 502/503 unavailable upstream readings.
Do not replace an error with zero utilization.

`latest.values` uses unit-bearing keys such as `cpu_percent`,
`memory_used_bytes`, `memory_total_bytes`, `filesystem_used_bytes`, and
`filesystem_total_bytes`. Network series use
`net/<interface>/rx_bytes_per_second` and `tx_bytes_per_second`; block-device
series use `disk/<device>/read_bytes_per_second` and `write_bytes_per_second`.
GPU series use `gpu/<GPU-uuid>/utilization_percent`, `memory_used_bytes`,
`memory_total_bytes`, `temperature_celsius`, and `power_watts`.

### Numeric extensions

New numeric metric names can be collected and retained without a backend
allowlist release. Add `extensions=1` to the metrics URL to return extensions
alongside known resource readings. Existing callers retain their known-resource
response shape. `sensors=1` independently includes the existing Apple CPU
temperature, CPU power and Neural Engine power keys.

Extension names are at most 96 ASCII characters, start with a letter, digit or
underscore, and use letters, digits, `_`, `.`, `:`, `@`, `/` or `-`. Diagnostic,
output, credential and prototype-reserved path segments are excluded. Values
must be finite numbers; extensions may represent negative measurements. Extension
aggregates require finite mean/peak, peak at least mean and integer count from
1 through the bucket's sample count. Invalid extensions are ignored. Known
resource readings retain their existing strict validation, including fields
hidden from a legacy response. Payloads remain capped at two MiB and input/stored
value maps at 256 keys; arbitrary metadata is never returned.

Partial bucket updates preserve existing series that were omitted from the
update. Retransmitted series replace their own aggregates without double counting.
Updates with no usable numeric latest values cannot erase existing readings.
When a bucket reaches its key cap, existing series take precedence over adding
more names. Clients must handle unfamiliar metric names and units before opting
in; extensions do not change scheduling, billing or ownership decisions.

Each tier is an array of `{ timestamp, samples, values }` buckets. Each value is
`{ mean, peak, count }`. Derive memory/filesystem/VRAM percentages from matching
used and total readings. Device-mapper and backing disks are separate series;
adding them double counts I/O. GPU UUIDs identify devices independently of
index order.

These readings are observational. They are not ownership receipts, billing
measurements, scheduler capacity claims or sufficient proof that a machine is
idle. Cost display and idle shutdown remain separate work.
