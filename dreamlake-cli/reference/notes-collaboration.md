# Live collaboration

Use `read --linger` when you want to stay with someone in a note. It registers
your presence, prints the initial source and participants, and streams updates
until you stop it. It requires CLI **0.29.0+** and compatible presence and activity
endpoints, in addition to the Notes read endpoint.

## One identity per task

Generate an ID once, give it a readable name, and reuse both for that task:

```bash
SESSION_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
export DREAMLAKE_AGENT_ID="codex:$SESSION_ID"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --linger
```

Separate tool shells must receive the same saved environment values; an export
in one shell does not persist into the next. Concurrent tasks need different IDs.
The name is a label, not the identity. No separate registration call is needed.

| Command | Content | Presence |
| --- | --- | --- |
| `notes read "$NOTE_ID"` | One snapshot | Attributed reads register/refresh recent presence |
| `notes read "$NOTE_ID" --linger` | Snapshot, then changes | Maintained until the foreground process stops |
| `notes visit "$NOTE_ID"` | None | Registers once and returns |

Ordinary reads and edits work without an agent ID. Presence is opt-in and does
not change permissions or patch checks. Members and explicitly shared readers
can publish presence; public visibility alone does not grant that access.

The server derives your human owner from authentication. The app shows agents
with a bot icon and humans with a profile photo or initials. Agent names are
self-reported labels, not verified model identity. Owner attribution does not
mean the owner is currently present. Recent presence is not proof of attention.

## How updates arrive

```bash
dreamlake notes read "$NOTE_ID" --linger --debounce 1s --throttle 2s
```

The first snapshot is immediate. Then:

- **Debounce** waits for an observed edit pause before emitting one net diff.
  Each new edit restarts the timer. Default: `2s`.
- **Throttle** sets the minimum interval between update batches, including
  participant and activity changes. Default: `2s`.
- Unchanged polls and heartbeats stay silent. Your own presence and activity
  are filtered out. Continuous editing can keep a content diff pending;
  there is no forced maximum-wait flush.

Both timing flags require `--linger`. Use `ms`, `s`, or `m`, between `250ms` and
`5m`; fractions are allowed. Polls are sequential, with a pause of
`min(1s, debounce, throttle)` between completed batches of requests. Network and
polling time add delay. Presence and activity may arrive while edits are pending.

Linger defaults to unified `diff`. Use `--format inline-dff` for character edits.
Changes are computed from the last **emitted** content baseline, so a burst is
not reduced to only its final keystroke. Brief visits or activity can be missed;
this is an observation stream, not an audit log.

## Consume JSON events

```bash
dreamlake notes read "$NOTE_ID" --linger --json
```

Stdout is newline-delimited JSON, with one object per line. Stderr carries
progress and errors.

| Event | Fields |
| --- | --- |
| `snapshot` | `observedAt`, `note`, `content`, `hash`, `revision`, `participants` |
| `update` | `observedAt`, `joined`, `left`, `activities`; optional `content` |
| Update's `content` object | `note`, `base`, `hash`, `revision`, `format`, `patch` |

Times are Unix milliseconds. Source, roster, and activity are fetched separately,
so a batch is not an atomic snapshot of all three. Human edits appear in content
diffs; the activity feed currently attributes agent reads and edits.

Linger accepts full source only. Do not combine it with `--since`, `--legacy`,
HTML, sections, line ranges, or numbered output. `--if-match` checks only the
initial read. Streamed revisions do not replace the original baseline of a
patch you are already preparing.

## Leave or visit briefly

Ctrl-C or SIGTERM stops the foreground process and attempts to leave. It spawns
no daemon. Pending notifications are discarded on stop; document edits remain.
Abrupt termination falls back to lease expiry, normally 60 seconds. Use one
keeper per note/task identity because multiple keepers share the same lease.

```bash cli-help="notes visit"
# Reuse the task's DREAMLAKE_AGENT_ID and DREAMLAKE_AGENT_NAME.
NOTE_ID=release-plan
dreamlake notes visit "$NOTE_ID"
```

For lower-level control (CLI 0.28.0+):

```bash cli-help="notes presence"
# Requires the stable task identity configured above.
NOTE_ID=release-plan
dreamlake notes presence "$NOTE_ID" join
dreamlake notes presence "$NOTE_ID" heartbeat
dreamlake notes presence "$NOTE_ID" clear
dreamlake notes presence "$NOTE_ID" leave
```

`clear` removes activity without leaving. A heartbeat cannot revive an expired
session (HTTP 410); join or interact again. `presence ... join --watch` is a
silent foreground lease keeper, heartbeating every 20 seconds. Prefer linger
when you need updates. Explicit `read`, `edit`, and `seek` presence actions take
`--hash` and `--range start:end`; ranges use exact-source Unicode code points.
These actions report activity, not document mutations.

## If joining fails

A successful read does not prove presence support. Check `dreamlake --version`,
`notes read --help`, the selected server, note access, and your stable identity.
`--remote <url>` selects a specific API; a local binary still uses your configured
remote unless told otherwise. Connection errors and unsupported endpoints end
linger with a nonzero status and a best-effort leave, never a fabricated empty
room. Do not claim to have joined until the command succeeds.

IDs accept 1–128 ASCII letters, digits, dots, colons, underscores, or hyphens;
names accept at most 64 printable ASCII characters. Attributed body operations
require CLI 0.27.0+; explicit controls require 0.28.0+; visit/linger require 0.29.0+.
Each also needs matching server support.

Next: [Editing with patches](/notes/editing/).
