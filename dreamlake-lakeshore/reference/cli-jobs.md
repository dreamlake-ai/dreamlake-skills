<!-- generated from https://cli.dreamlake.ai/jobs.md at 0.92.0 a5d6dff; do not edit -->

# External job tracking

`dreamlake jobs` tracks work launched by another tool. It requires CLI 0.55.0 or later
and a compatible Jobs API. Availability depends on both deployments; this source
change does not establish production availability. CLI 0.54.1 and earlier do not
include these commands. Registration does not launch
work, discover processes, collect output, or grant runner control. Existing
[`dreamlake run` and `dreamlake runs`](cli-runs.md) remain the managed execution interface.

## Register external work

Find the exact host ID with `dreamlake hosts list --namespace geyang --json`.
`--host` accepts only the lowercase 24-character hexadecimal `Host.id`, not a
host name, enrollment ID, or the illustrative `h_...` IDs in design examples.
The selected host must be owned and accessible in the selected namespace.

```bash cli-help="jobs register"
dreamlake jobs register --namespace geyang --name train-baseline \
  --host 0123456789abcdef01234567 --request-id train-baseline-01
```

Use `--namespace` to select an organization or another authorized namespace;
otherwise the CLI resolves your current user's namespace. Registration requires
`--request-id`. Repeating the same ID, name, host, and namespace returns the same
job with `alreadyRegistered: true`; changing the payload conflicts. Retain this
ID after an uncertain request. Names are trimmed and limited to 200 characters
without control characters. Request IDs allow 1–128 letters, digits, underscores,
dots, colons, and hyphens. Job IDs are also exact lowercase 24-character hex IDs.

## Report an observation

Run these commands only after the external runner has observed the stated
condition. `cancelled` reports cancellation performed elsewhere; it does not stop
a process. A successful report command exits zero even when reporting `failed`.

```bash cli-help="jobs report"
dreamlake jobs report 89abcdef0123456789abcdef --namespace geyang --state running
dreamlake jobs report 89abcdef0123456789abcdef --namespace geyang \
  --state succeeded --exit-code 0
dreamlake jobs report fedcba9876543210fedcba98 --namespace geyang \
  --state failed --exit-code 7 --message 'Training process exited with an error'
```

Each report sends a UTC observation timestamp, defaulting to the time the command
starts. For retryable automation, explicitly set `--reported-at` and reuse the
same timestamp and payload. On failure, the CLI returns the attempted timestamp
so an uncertain write can be retried exactly. The API rejects older observations,
changed payloads at an existing timestamp, and timestamps more than 60 seconds
in the future. Seconds or three fractional digits are accepted, always with `Z`.

```bash
dreamlake jobs report 89abcdef0123456789abcdef --namespace geyang \
  --state running --reported-at 2026-10-12T12:00:00.000Z --json
```

Terminal reports cannot reopen a job or change its terminal state or exit code.
Exit codes are optional signed 32-bit integers for terminal reports: `succeeded`
requires zero when supplied, `failed` requires nonzero, and `cancelled` allows
any value. Messages are explicit text of at most 2000 characters, without NUL.
Omitted optional fields are omitted from the HTTP request, not sent as null.
No program output is automatically captured or indexed.

## Read reported state and age

```bash cli-help="jobs list"
dreamlake jobs list --namespace geyang
dreamlake jobs list --namespace geyang --host 0123456789abcdef01234567 --state running
dreamlake jobs list --namespace geyang --page 2 --page-size 50 --json
```

Lists return one page, with `page`, `pageSize`, `total`, `totalPages`, and `readAt`.
Text output shows the page count and prompts for the next page when present.
`--page` accepts 1–10000; `--page-size` accepts 1–100 and defaults to 50. Host and
state filters remain explicit. Access and namespace failures are errors, never
substituted with an empty list.

```bash cli-help="jobs status"
dreamlake jobs status 89abcdef0123456789abcdef --namespace geyang
dreamlake jobs status 89abcdef0123456789abcdef --namespace geyang --json
```

Text labels the **reported state**, last report age, and freshness. Registration
alone has state `registered`, no report timestamp or age, and execution state
“not yet reported.” An old `running` observation remains reported `running`; the
CLI never infers failure or confirms live execution from age. Terminal states
are also historical observations.

JSON preserves the full API envelope and timestamps: `reportedAt` is the caller's
observation time, `receivedAt` is server receipt time, and `reportAgeSeconds` is
computed by the API from the observation timestamp, rounded down and clamped to
zero. `reportFreshness` is `missing`, `fresh` through 300 seconds, or `stale`.
`processVerified` is always false, even for fresh reports. Registration receipts
also include `alreadyRegistered`. Error JSON includes an error message and safe
API code/status when available; registration/report failures include retry
identity. Missing or inaccessible jobs are reported without claiming which case
applies.

General Jobs logs, cancellation control, submission, waiting, artifacts, and
lifecycle commands are not implemented by this tracking interface. Use existing
managed-run commands only for runs actually submitted through that interface.
