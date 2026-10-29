<!-- generated from https://cli.dreamlake.ai/analytics.md at 0.94.0 cbe0f3f; do not edit -->

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
DREAMLAKE_TELEMETRY=0 dreamlake list
```

Or save the preference (no network request):

```bash cli-help="telemetry"
dreamlake telemetry disable --quiet
dreamlake telemetry status
dreamlake telemetry enable --quiet
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
