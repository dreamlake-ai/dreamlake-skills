<!-- generated from https://cli.dreamlake.ai/analytics.md at 0.119.0 4c56b6a; do not edit -->

# Product analytics

Available starting with CLI **0.56.0**. Usage measurement runs without prompts, banners,
or changes to stdout/stderr. It reports registered command names, duration and
exit outcome, never arguments, paths, tokens, command output or error messages.
Delivery is best effort, detached, and limited to authenticated personal sessions.
Help, version, telemetry settings and internal helpers are excluded. Commander
parser errors are excluded; `run` records only its fixed command name.
Commands using explicit URL, remote, token or debug overrides omit the CLI
completion event rather than attributing it to a different saved account.

Disable before running any command:

```bash
DREAMLAKE_TELEMETRY=0 dl list
```

Or save the preference (no network request):

```bash cli-help="telemetry"
dl telemetry disable --quiet
dl telemetry status
dl telemetry enable --quiet
```

`DO_NOT_TRACK=1` also disables telemetry. Environment opt-out overrides saved
preferences. Missing preferences enable measurement; malformed/unreadable
preferences disable it. Settings live in `~/.dreamlake/telemetry.json`.

The CLI sends an opt-out header on DreamLake API requests, including direct
fetch paths to its configured server. Other API clients can send
`X-DreamLake-Telemetry: off` (or `DNT: 1`) themselves. This disables product
analytics for that request, not operational, security or billing records.

Events go to the configured DreamLake API, never directly to PostHog. Server
operators store events in owned PostgreSQL and configure PostHog to sync the
selected event table. PostgreSQL retains the owned history independently.
Each eligible completion is committed to `~/.dreamlake/telemetry-events` before
upload is attempted. The private rotating journal retains delivered and pending
events for up to seven days, 10 MiB or 10,000 records, whichever limit is reached
first. Rotation occurs on eligible invocations and writes, so an idle installation
cleans up when next used. The original UTC event timestamp (milliseconds) and
UUID remain unchanged on every retry; the clock is the client's system clock.

Every completion triggers a best-effort detached upload attempt. Pending events
are also retried on the next eligible invocation; no always-running daemon is
installed. Upload workers have an eight-second network budget and individual
requests at most 1.5 seconds. Network activity never holds the command open;
committing the local record takes local disk I/O time. Acknowledged events stay
in history until rotation. Records are bound to their original API/account and
never replayed under a different account. Opaque credentials replaced with new
ones cannot recover the old account scope; those records expire locally.

`telemetry disable` purges local history. Environment opt-out stops recording
and uploading, and purges history on the next eligible command/helper. Neither
removes events already accepted by the server. Opt-out settings themselves are
persisted before the purge; re-enabling cannot recover purged records.

Unavailable collectors do not change command results. Disk failure, termination
before the local commit and retention eviction can still lose events; these are
product signals, not audit records. On Windows, files are flushed but directory
fsync is unavailable through Node, so power-loss durability of renames depends
on the filesystem. Clients require connectivity only to DreamLake; a local queue
does not guarantee regional reachability.

## HTTP failure context (CLI 0.104.5+)

Failed commands using the shared CLI HTTP transports can include
`last_http_status` and `last_http_error_code`. Only integer statuses 400–599
and bounded machine codes are collected. These are the last observed HTTP
failure, which may have been handled internally; they are not proof of the
command's final cause. Successful commands omit these fields. Direct fetch
paths and other commands with semantic failures inside HTTP 200 still need
separate instrumentation.
No error message, response body, request ID or resource identifier is uploaded.
Deploy the compatible server collector before releasing this CLI change.

Memo move and metadata-transfer commands also record `operation_error_code`
and `operation_outcome` (`failed`, `blocked`, `partial`, or `uncertain`) when
classified by that command. A blocked HTTP 200 preview therefore records its
blocker without inventing an HTTP error status. These optional fields are
validated again by the collector and omitted for successful exits.
