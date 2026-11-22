<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/metrics.md at 0.1.210 4edff8b47; do not edit -->

# Machine metrics

**Implementation in progress; not yet released.** The existing Compute Brief
shows missing readings and an explicitly labeled example. Installing a current
released CLI does not install this collector or connect the page to real metrics.
Local Nymph collection, control-plane storage, backend access and UI rollout
must be verified separately before treating readings as live.

Nymph collects resource readings on the machine, including machines outside AWS.
CloudWatch is not required. Linux readings cover CPU utilization, memory,
filesystem capacity for the worker directory, network rates and block-device
I/O. NVIDIA GPUs additionally report utilization, VRAM, temperature and power
when `nvidia-smi` supports those fields. Missing drivers and unsupported fields
produce missing readings. macOS currently provides filesystem and supported
NVIDIA readings only. This feature does not collect or index process arguments,
program output, tool output or terminal contents.

## Local collection

**Since [Nymph 0.1.34](https://github.com/dreamlake-ai/nymph/releases/tag/v0.1.34):** Nymph collects and reports readings only when the daemon
configuration sets `[metrics] enabled = true`. Configurations that omit the
key stop collecting after upgrading. Nymph does not rewrite configuration
files, and an explicit `enabled = true` keeps collection on. See
[host testing](https://docs.dreamlake.ai/lakeshore/hosts/testing) for the related job output setting.

### Direct Source snapshots (implementation in progress)

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

### Numeric extensions (source contract; rollout pending)

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
