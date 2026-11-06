<!-- generated from https://docs.dreamlake.ai/notes/agent-presence.md at 0.1.124 b7138276; do not edit -->

# Agent presence and activity

## Agreed lifecycle and identity

**Presence is opt-in.** Agents can read and edit using normal authentication and
revision checks without any agent ID, join, heartbeat, or leave. A runner opts in
by supplying a stable session ID. The client generates it (a UUID once per task),
not the server. Names and IDs are self-reported, grant no permissions, and are not
verified audit identity. Two clients under the same authenticated owner can reuse
an ID; random UUIDs prevent accidental collisions, not deliberate impersonation.

Presence means **active in this memo recently**, for both humans and agents. It is
not proof that an agent is continuously watching, reading, or typing. Reuse the
existing RTC awareness channel and header badge; do not add a status row below
the bindr row.

Keep three identities separate:

| Identity | Purpose |
|---|---|
| Agent identity / display name | Identifies the agent; its name is a supplied label, not verified model identity. |
| Task/session ID | Stable across all CLI calls in one task; distinct for concurrent sessions, even for the same agent. |
| Human owner | Derived from authentication, not an agent-supplied owner field; attribution does not imply the owner is present. |

The runner creates the task/session ID once, retains it across tool invocations,
and passes it to every Memos command. Do not generate an ID on every command or
use a shared display name as the session key. Resume the same ID for the same
task; use a new ID for a new or concurrent task. Socket reconnections have their
own transport IDs and must not create a new logical participant.

The current `DREAMLAKE_AGENT_ID` / `X-DreamLake-Agent-Id` field carries this
**task/session ID**, despite its name. It does not yet represent a separate,
persistent agent-account ID. The roster key is scoped by memo, authenticated
owner, and session ID; the display name is never the key.

| Event | Intended behavior |
|---|---|
| First attributed read/edit | Implicitly join and start the recent-presence timeout. |
| Later read/edit with the same session ID | Refresh the existing badge, without adding another participant. |
| Inactivity | Remove the badge after expiry; no cleanup command is required. |
| Explicit leave/unjoin | Remove that session from that memo immediately; do not erase its identity. |
| Interaction after leave or expiry | Implicitly rejoin using the same session ID. |
| Optional explicit join or maintained session | Support clients that need sustained presence; ordinary CLI use does not require it. |

Human clients can send leave on navigation away or memo closure. Abrupt tab close,
crash, or network loss may prevent delivery, so expiry is still required. Agents
have the same optional leave and expiry fallback. A session ID is identity, not a
live lease: storing the ID does not keep a badge alive. Neither a TUI nor a
continuous edit stream is required for recent presence.

Read activity uses the **existing human selection and cursor display**, with the
agent label and participant color. It selects the returned source range; a
full-body read selects the full source, and incremental changes do not claim a
whole-source selection. New read/focus activity replaces the previous selection.
Search does not add a separate seek event. Do not render a second agent-specific
selection style or a tool-call log.

Insertion/replacement text uses a fading highlight only after acknowledgement.
Deletion has no special marker in this iteration. Failed writes and dry runs never
produce success highlights. Selections expire after 8 seconds; completed edit
highlights fade over 5 seconds. Neither heartbeat nor badge renewal extends those
lifetimes. A completed edit may finish fading after its author leaves. Human
cursors retain relative CRDT anchoring; CLI selections are exact-source-hash bound
and disappear on source changes, rather than guessing a new position.

People and agents share participant-color rules, not action-specific colors.
Use an agent icon and agent/owner labels to distinguish them; do not rely on color
alone. Concurrent sessions must remain distinguishable even when names match.

The defaults are a 60-second recent-presence timeout and a 5-second
completed-edit fade. Optional passage activity has an independent 8-second
expiry. These are DreamLake choices, not asserted Google Docs, iMessage, or
Claude Tag timing constants.

## Availability and optional controls

An attributed operation uses the lifecycle above and
implicitly joins or renews the same 60-second presence entry. Anonymous agent
identity is not inferred from ordinary API calls. A separate persistent
agent-account identity is not yet part of the wire contract. Deployment and
client release status must be checked independently of this source documentation.

CLI 0.27.0+ and Python SDK 0.21.0+ support attributed reads and edits.
CLI 0.29.0+ adds `visit` and `read --linger`; CLI 0.31.0+ adds the read-only
`presence` command and event-driven selections. These require matching server
capabilities; a successful read does not prove presence or event support.
The CLI uses the active login's API; running a locally installed binary does not
select a local server. Use `--remote <url>` to test a specific API or `--debug`
for the local development server.

To check a matching API, use an accessible test memo and the stable task identity
below. Run a read, inspect `notes presence`, then start `read --linger` and stop
it with Ctrl-C to verify automatic session cleanup. Verify patch support
separately on a disposable memo with a merge patch, an exact readback, and a stale
exact request that must fail without changing the source. Do not use an existing
user document as a write-test fixture.

## Read and linger in the foreground

CLI 0.29.0+ adds `notes read --linger` and `notes visit`. They use the deployed Memos v2, presence-roster and
agent-activity endpoints. Python has no corresponding convenience method yet.

Set `DREAMLAKE_AGENT_ID` once to a unique, stable task-session identity (and
optionally `DREAMLAKE_AGENT_NAME`) as described below. `NOTE_ID` must identify a
memo you can access as a member or explicitly shared reader.

```bash
# NOTE_ID and the stable task identity must already be set.
dreamlake memos read "$NOTE_ID" --linger
```

**Use the default text output for people and coding agents.** It shows readable
diffs, participants, and quoted selections. JSON is optional and intended only
for a program that explicitly needs to parse structured events.

The command registers presence automatically, prints the complete source with
its hash/revision and the other current participants, and stays in the foreground.
A separate `visit` is optional. Interrupt with Ctrl-C or SIGTERM to stop and send
leave. No background daemon is spawned. Presence expires after its server lease
if the process is killed or cannot send leave. Use one linger process per
note/task identity; multiple keepers using the same identity share one lease.

Edit delivery is **debounced**: wait until the observed source has been quiet
for `--debounce` (default `2s`), then deliver **one unified diff** from the last
emitted content baseline through the end of the burst. Each newly observed edit
restarts that quiet timer. Continuous editing keeps the diff pending; there is
no forced maximum-wait flush. Stopping before the quiet period ends discards the
pending notification, not any document edits.

All output batches are **throttled** by `--throttle` (default `2s`): no two update
batches are emitted closer together than that interval. Presence and activity
can still be delivered while edits continue; they do not reset the edit quiet
timer. Once a diff is ready it joins the next eligible output batch, so a recent
presence batch can delay it until the throttle expires. The first source snapshot
is immediate. No new batch is emitted merely because a timer elapsed.

Both flags require `--linger` and accept explicit `ms`, `s` or `m` units, including
fractions, from `250ms` through `5m`. Bare numbers, zero, negatives and out-of-range
values are rejected before presence registration. For example:

```bash
# One second of edit quiet; no more than one output batch every two seconds.
dreamlake memos read "$NOTE_ID" --linger --debounce 1s --throttle 2s
# Slower text output for a coding agent or a quieter session.
dreamlake memos read "$NOTE_ID" --linger --debounce 2s --throttle 5s
```

**CLI 0.42.0+:** `--intent "…"` publishes a self-reported purpose with the
session — one short, specific sentence in the agent's own voice, shown to
collaborators in the agent's presence card. It is sent once at join;
heartbeats preserve it, and leave or lease expiry removes it. The flag requires
`--linger` (`notes visit` also accepts it for one-shot presence). The server
trims the text and rejects empty values and more than 280 Unicode code points.

```bash
dreamlake memos read "$NOTE_ID" --linger \
  --intent "I'm reviewing this sequence to make the pacing clearer."
```

**CLI 0.31.0+:** linger subscribes to authenticated
`GET /namespaces/:slug/notes/:noteId/events` (SSE). CLI 0.29.0–0.30.0 used
polling. The event stream requires a matching server; there is no silent
polling fallback.

The server observes the existing RTC connection events and coalesces them to
at most one batch per 250ms. The CLI keeps only the latest selection per browser
connection, emits at most one update per `--throttle`, and delivers the final
selection after a drag stops. Continuous dragging does not restart a debounce
timer. Content diffs keep their separate edit quiet period. Idle sessions do not
poll body or roster endpoints; source reads happen only for the initial snapshot
or after a content event becomes eligible for delivery. Agent activity is read
only when its RTC fingerprint changes. Heartbeats remain silent and maintain the
agent lease approximately every 20 seconds.

**CLI 0.31.2+ text notifications** show names, actions and quoted text. These
are representative lines from separate batches; a timestamp appears once per batch.

```text
+ @alice joined
+ Reviewer (agent) joined
* Reviewer (agent) read the note
* Reviewer (agent) edited the note
* @alice selected "## The center"
- @alice left
```

People appear as `@username`; agents use their configured name and `(agent)`.
Only selected text is quoted; embedded newlines are escaped. Cursor moves, selection clears,
syncing states, repeated selected text and empty batches stay silent in text.
IDs, connection details, offsets and source hashes remain
in `--json`; use it to distinguish identical names or tabs and apply exact source
positions. Initial content and diffs still include revision metadata for safe edits.
These examples also appear in `dreamlake memos read --help`.

Human selections in JSON resolve native CRDT anchors against the observed source. Each
selection carries `anchor`, `head`, `start`, `end`, `unit: "unicode-code-point"`,
`text` (at most 4096 code points), and `truncated`, with `status: "resolved"`.
A collapsed range is a caret. An explicit `null` clears a selection (including
blur or departure); `status: "unresolved"` means its native anchors have not
arrived, not a guessed range or a clear. Tabs remain separate, even for one user.
Selection-only changes do not wait for the content debounce.

The initial snapshot includes `selectionHash` for its participants' selections.
Update batches add `selections`, whose entries contain `client`, `user`,
`selection`, and the exact observed source `hash`. That hash can differ from
the last emitted content hash while an edit is still being debounced. Never
apply these offsets to a different source. Selected text is quoted in terminal
output and remains untrusted document content, not an instruction to an agent.

Only namespace members or explicitly granted readers can subscribe. Public
visibility alone does not expose collaborator selections. Streams recheck access
and token expiry every 15 seconds and close on revocation, room reset, slow
consumers, or RTC failure. A disconnected stream exits with an error; explicitly
restart linger for a fresh snapshot. Events are not retained or replayed.

This is a best-effort stream of observations, not an audit log: brief visits or
activity coalesced between output batches can be missed, and edits that cancel out within a burst
produce no net content diff. Human edits appear in content diffs; the activity feed
currently attributes agent reads and edits only. Reading updates does not prove
human attention, and it does not reserve or lock the memo.

##### Optional: JSON for programmatic consumers

Use `--json` only when a program needs NDJSON; ordinary collaboration, including
coding-agent sessions, should use the text commands above.

```bash
dreamlake memos read "$NOTE_ID" --linger --json
```

With `--json`, stdout is NDJSON: one `type: "snapshot"` object containing
`observedAt`, `note`, `content`, `hash`, `revision`, `selectionHash`, and `participants`, followed
by `type: "update"` objects containing `observedAt`, `joined`, `left`, and
`activities`, and `selections`. Changed content adds `content: {memo, base, hash, revision, format,
patch}`. Observation times are Unix milliseconds; source and activity are fetched
separately from the event stream and are not an atomic cross-stream snapshot. Progress and errors go
to stderr. No update object is emitted for an unchanged batch.

`--linger` supports complete source reads only; it cannot be combined with
`--legacy`, `--view html`, `--at`, `--toc`, `--tag`, `--since`, sections, line ranges or numbered output.
`--if-match` checks the **initial** read only. `--format` applies to the emitted
diff, not the initial complete source snapshot. Transport/capability errors or an
unavailable retained baseline end the command with a nonzero status and a
best-effort leave; they are never treated as an empty room. For edits, preserve
the original source and revision used to prepare your draft: a later streamed
revision is not a replacement baseline for an older draft.

```bash cli-help="memos visit"
# Optional one-shot registration: does not fetch the note body or keep a daemon.
# NOTE_ID and the stable task identity must already be set.
dreamlake memos visit "$NOTE_ID"
```

`visit` uses the existing join lease (60 seconds unless renewed by an attributed
operation), returns immediately and does not read content. Use
`read --linger` when you want ongoing updates. CLI 0.31.0 removes the old
manual `notes presence <note> <action>` and `join --watch` controls.

`read --linger` manages joining, heartbeats, and leaving automatically. Stop it
with Ctrl-C when finished; one-shot reads and `visit` expire naturally. There is
no manual lifecycle sequence to run alongside it. Never start an untracked
helper that outlives the task.

##### Read who is present

In CLI 0.31.0+, `presence` reads the current roster without joining or refreshing
your session. It does not require an agent ID. Text is the default:

```bash cli-help="memos presence"
dreamlake memos presence "$NOTE_ID"
```

Add `--json` only for a program consuming the roster. There are no direct
`notes join`, `notes heartbeat`, or `notes leave` commands. Use `visit`,
`read --linger`, and Ctrl-C for participation.

##### Low-level HTTP lease protocol

SDK integrations and linger use the HTTP protocol below internally. It is not
a manual CLI workflow.

API: `POST /namespaces/:slug/notes/:noteId/presence` accepts
`{action, hash?, ranges?: [{start,end}], intent?}`, bearer authentication,
`X-DreamLake-Agent-Id`, and optional `X-DreamLake-Agent-Name`.
Actions are `join`, `heartbeat`, `read`, `edit`, `seek`, `clear`, `leave`.
Response is `{state}` or `{state:null}` after leave. Only authenticated members or
explicitly shared readers may publish; `edit` also requires write permission.
Public visibility alone does not grant presence access. Controls do not mutate
document content or revision. Owner metadata comes from authenticated lookup.

`intent` is the agent's self-reported purpose — one short plain-text sentence in
the agent's own voice, such as "I'm reviewing this sequence to make the pacing
clearer." Omitting the field preserves the current purpose, `{"summary": "…"}`
replaces it, and an explicit `null` clears it, on any action. Summaries are
trimmed; empty strings and more than 280 Unicode code points are rejected with
400 `invalid_presence`. The server stamps `updatedAt`; clients cannot supply
owner attribution or timestamps. Intent lives with the presence lease: leave or
lease expiry removes it, and a later join never resurrects an expired purpose.
`clear` keeps its existing meaning — it clears passage activity, not intent.
Intent is a self-reported claim, not observed activity, progress, or a
permission grant; the roster's authorized readers can see it.

## Read who is present (HTTP API)

`GET /namespaces/:slug/notes/:noteId/presence` returns the current RTC awareness
roster, including humans and agents. Use bearer authentication as a namespace
member or explicitly shared reader. Public visibility alone is insufficient.
Agent identity headers are not required, and the observer does not publish
presence, renew an agent lease, or edit the memo.

Successful reads default to `text/plain; charset=utf-8` (also available with
`?format=text`):

```text
Observed at: 2026-09-26T08:00:00.000Z
- human: "Ge" (id: "ge"; client: "browser-session-123")
- agent: "Codex" (id: "agent:owner-id:agent-id"; client: "note-agent-session-456"); owner: "Ge" (id: "owner-id"); intent: "I'm reviewing this sequence to make the pacing clearer."; expiresAt: 1790409660000
```

An empty text roster says `No participants present.` after the observation time.
Client-declared strings are quoted and escaped to keep each connection on one
line. Use `?format=json` for structured output; other format values return
400 `invalid_format`. Error responses remain JSON for either format.

The opt-in JSON response is `{participants, observedAt}`. `observedAt` is Unix time in
milliseconds. Each participant has `client` (connection ID) and `user` with
`id`, `name`, and `kind` (`human` or `agent`), plus optional `color` and `avatar`.
Agents can include `user.owner`, their lease's `expiresAt`, and `intent`
(`{summary, updatedAt}` — the self-reported purpose last published with
presence). Expired agent leases and internal observer connections are excluded. Multiple browser tabs
remain separate entries. To identify other agents, compare `user.id` against
`agent:<authenticated-owner-id>:<agent-id>`; the caller is not automatically
excluded. Human identities without a kind field are normalized to `human`.
These are client-declared display identities, not verified authorization claims.

An inactive memo returns an empty roster. An active room whose connection fails
or times out returns 503 `presence_unavailable`, not an empty roster. Responses
are not cached. This requires a server with the GET endpoint and an RTC server
supporting awareness rosters; a 404 can also mean the caller lacks access.
There is no CLI or Python convenience method for roster reads yet. Using any
HTTP client, send an authenticated GET to the path above. The roster is an
observation of presence, not a lock or a guarantee that another editor is idle;
continue to use the normal conditional-write contract.

Explicit ranges require the exact source SHA-256 and zero-based, end-exclusive
Unicode code point offsets. Stale or out-of-bounds locations are refused. A
collapsed seek is a caret, not a claim that text was read. Source changes invalidate
hash-bound markers. Deletion-only edits do not invent insertion ranges.
Errors include missing identity/invalid input (400), denied access (404), stale
range (409), expired heartbeat (410), and unavailable relay (503).

Identity values accept 1–128 ASCII letters, digits, dots, colons, underscores and
hyphens; names accept at most 64 printable ASCII characters. CLI 0.27.0+ and
Python SDK 0.21.0+ attach identity headers to Memos body/section/diff operations
when the environment variables below are set. `visit` and `read --linger` require
CLI 0.29.0+ and an active collaborative room; read-only `presence` requires
CLI 0.31.0+. The old manual action commands were removed in 0.31.0.
Updating a skill does not update a binary or deploy a server. Python has no
presence convenience method yet; use the HTTP contract when available.
The authorized agent-activity feed retains operation observations, not an online
roster. Observation failures must not turn an acknowledged edit into an apparent
failed edit. Live source-range decorations currently require the collaborative
editor; read-only views do not run an RTC client.

## Identity, names and photos

Use a readable agent prefix plus a UUID as the task ID, for example
`codex:7b52e4d1-3ac9-4d88-b2a6-61f03c927ea5`. Generate it once per task and reuse
it across reads, edits and linger sessions. Concurrent tasks need different IDs;
a display name such as `Codex` does not distinguish their sessions. The CLI sends
`DREAMLAKE_AGENT_ID` as `X-DreamLake-Agent-Id` and `DREAMLAKE_AGENT_NAME` as
`X-DreamLake-Agent-Name`. No separate identity-registration request is required.

| Display field | Humans | Agents |
| --- | --- | --- |
| Presence identity | User namespace slug | `agent:<authenticated-owner-id>:<task-id>` |
| Display name | Profile name from `/auth/me`, falling back to namespace slug | `DREAMLAKE_AGENT_NAME`, falling back to `AI agent` |
| Header avatar | Profile photo, or initials when absent | Bot icon |
| Tooltip | Name and presence | Agent name, owner name, stated purpose (intent), activity and task/session ID |

The server derives an agent's owner from authentication and looks up the owner's
profile name/photo; an agent cannot assign an owner through these headers. The
owner's photo is carried in metadata but is not currently rendered as the agent's
header avatar. Owner attribution does not mean that the owner is present.

The header deduplicates connections by identity: multiple browser tabs show one
human avatar, while unique agent task IDs show separate agent avatars. It shows
up to four avatars plus an overflow chip. Colors are derived from identity.
The HTTP roster still returns one entry per connection. Browser awareness names
and photos are display metadata, not an authorization source.

## Agentic usage pattern: one identity, normal commands

For agent-driven Memos work, set both identity variables before the first live
read or edit, unless the user explicitly requests unattributed work. This is a
workflow prerequisite for attribution, not a requirement for saving content.
Without `DREAMLAKE_AGENT_ID`, an edit can save successfully while producing no
agent presence or attributed fading edit highlight. `DREAMLAKE_AGENT_NAME`
provides the readable label.

Initialize once in the runner's task environment. For separate shell tool calls,
the runner must inject the same saved values each time; an export in one shell
does not propagate into later independent shells. No explicit join is required.

```bash
export DREAMLAKE_AGENT_ID="${DREAMLAKE_AGENT_ID:-codex:$(python3 -c 'import uuid; print(uuid.uuid4())')}"
export DREAMLAKE_AGENT_NAME="${DREAMLAKE_AGENT_NAME:-Codex}"
NOTE_ID="<full-note-id>"
```

Run ordinary commands with that identity. An attributed `read` automatically
registers or refreshes presence; a preceding `visit` is never required. Reading
without agent identity does not invent or register an agent session. Retain the generated ID in the task context and inject that same literal value into each later shell; rerunning the UUID fallback in a new shell would create a different session.

After the first intended live read, verify attribution with
`dreamlake memos presence "$NOTE_ID"` (CLI 0.31.0+). This only inspects the roster;
it does not register an agent. Check the task ID and display name, not merely
another session named Codex. If absent, check the environment passed to the
actual read/edit process before diagnosing a UI regression. Do not repeat a
successful edit to trigger its highlight. Presence expires about 60 seconds
after the last activity; completed edit highlights fade over 5 seconds and
require an exact matching live document revision. A roster entry verifies
presence only: report a highlight as visually verified only after observing it
in the collaborative editor.

| Command | Reads content | Presence lifetime |
| --- | --- | --- |
| `notes read "$NOTE_ID"` | Once | Registers/refreshes presence, then the lease expires naturally |
| `notes read "$NOTE_ID" --linger` | Initial source and ongoing updates | Registers automatically and maintains presence until stopped |
| `notes visit "$NOTE_ID"` | No | Registers once, returns immediately, then the lease expires naturally |

The last two commands require CLI 0.29.0+. A normal
read does not mean the agent remains actively reading between commands.

```bash
dreamlake memos read "$NOTE_ID" --json > baseline.json
dreamlake memos find lighthouse --note "$NOTE_ID" --json
# Draft a reviewed patch against baseline.json, using the patch workflow below.
# Retain its revision, apply the patch, and read back the acknowledged revision.
```

The conditional patch and exact-readback examples elsewhere in this guide remain
required; presence does not relax concurrency checks. Do not retry an old patch
with a newly fetched revision merely to force it through.

When finished, stop `read --linger` with Ctrl-C; it sends leave automatically.
One-shot operations expire naturally. Keep the same session ID between commands,
and remove the task identity from the runner's environment when the task ends.
Lease expiry handles abrupt exits without requiring remembered cleanup.

## Persistent contributing sessions

Agent presence and durable contribution attribution share the request's optional
session identity. A presence lease expires; a contribution remains attached to
the Memo and the saved session. The server records `created` after successful Memo
creation and `edited` after a native body/section write is acknowledged. A read,
visit, self-reported editing state, failed write, or no-op is not a contribution.
Replayed command receipts do not repeat attribution.

Use an authenticated request with either:

- `X-DreamLake-Terminal-Session-Id`: the exact saved session ID owned by the caller.
- `X-DreamLake-Session-Provider: codex|claude` and `X-DreamLake-Session-Id`: the actual
  native session UUID. A unique owned match is reused; a new identity gets a private
  metadata-only archive, without a launch directory, target or conversation upload.

`X-DreamLake-Agent-Id` and `X-DreamLake-Agent-Name` remain the presence identity and
label. Without an agent ID, valid session context supplies a stable presence ID.
Built-in agents use their existing saved conversation ID. Arbitrary presence
labels and mentions never establish a conversation identity. Set
`X-DreamLake-Session-Affiliation: 0` to suppress durable attribution.

`GET /namespaces/:slug/notes/:noteId/contributors` lists the same authorized,
paginated sessions as the resource-session catalog. It accepts `pageSize` (1–50),
`cursor` and `q`. Responses contain `sessions`, `hasMore` and `nextCursor`. Each
session carries `contribution: {kind, firstAt, lastAt}` for server-observed writes,
or `null` for explicit/legacy links. These are not edit counts or a full audit log.
The reader must independently be allowed to read the Memo and each session.

```bash
# CLI with the matching release; this is read-only and does not join presence.
dreamlake memos contributors "$NOTE_ID" --namespace "$NAMESPACE" --json
```

The built-in agent exposes the same read as a real tool:

```javascript
dreamlake_notes_contributors({ note: noteId, namespace: namespaceSlug })
```

Normal Memo edit tools already carry the conversation identity; no follow-up
"mark contributed" call is needed. Direct browser RTC edits without a session
identity are not attributed to a terminal session. Historical links remain links;
no authorship is inferred from access, similar names or Memo mentions.

Optional attribution has a bounded wait and bounded outstanding work. If it is
unavailable, content saves still succeed; a late record may appear on refresh.
Never replay an accepted content write to repair metadata. Presence expiration,
missing metadata and contribution-list errors do not prevent normal Memo editing.
