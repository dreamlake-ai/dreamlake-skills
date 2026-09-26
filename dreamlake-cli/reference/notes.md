# Notes

A note is a collaborative Markdown document. People edit it in the browser in
real time; `dreamlake notes` is how a script or an agent reads and edits the
same document from a shell.

CLI 0.26.2 and later default to a read/patch contract carrying exact source,
hashes and opaque write revisions together. It requires the matching Notes v2
server contract. Use `--legacy` explicitly against older servers; upgrading
the CLI alone does not upgrade the server. The compatibility examples below
retain existing body-only reads and ETag behavior. Check the [release notes](release-notes.md)
for publication and verification status.

## Original-snapshot Bash workflow (v2)

Both reads and uploads select `--format inline-dff` (default) or `--format diff`.
`notes diff --since` is an alias for incremental `notes read --since`. Reading
one format does not constrain the upload format. The backend owns strict parsing
and compiles validated edits to native RTC operations; the CLI does not apply
DMP or guess an alignment.

Text stdout contains `note`, `hash`, `revision`, a blank line and exact source.
An incremental response adds `format`, `base`, `unit` and the patch. `--json`
uses `content` for full reads or `base`/`patch` for incremental reads. Diagnostics
go to stderr. The CLI verifies the SHA-256 of full source before emitting it. Patch receipts
carry `note`, `mode` (`merge` or `exact`), the original `baseRevision`, and the
acknowledged `hash`/`revision` on stdout and in JSON.
A malformed or legacy response is an error, never a silent downgrade.

```bash file="terminal"
set -euo pipefail
NOTE_ID=design-doc
# Login first; add --namespace <slug> for an organization's Note.
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md

dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format inline-dff
dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format diff

# This example requires exact base source: Hello world. (no trailing LF).
dreamlake notes patch "$NOTE_ID" --format inline-dff --base-revision "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
REVISION=$(jq -er .revision committed.json)
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
```

The quoted here-document preserves variables, backticks, newlines and Unicode
literally. Choose a delimiter absent as a standalone patch line. Input defaults
to stdin; pipes and `--file -` work. Optional `--file path` or `--diff string`
conflicts with redirected stdin and with each other. Interactive stdin is
refused. Empty input is a no-op patch, not a whole-body deletion. `--dry-run`
prints the proposed request without uploading it.

Uploads require the original saved `--base-revision`. The default patch validates
against that original source, maps edits to its original RTC identities, and
uses ordinary native CRDT synchronization. It sends no `If-Match` header and
does not require the current document to still equal the baseline. Concurrent
edits outside those original identities are preserved by the existing CRDT
merge behavior; there is no fuzzy rebase onto current text.

MERGE is the default. To require the current revision to equal the saved
baseline, add `--exact` to that patch command. EXACT is scoped to this request.
Explicit `--if-match "$BASE"` remains a compatibility alias for EXACT and can
supply the original baseline when `--base-revision` is absent. When both flags are present, their tokens must match. There is
no permanent EXACT document mode. `--force` is unnecessary and refused for
v2 patches. No preflight read silently replaces the original token. After success, read with the
acknowledged revision before advancing a local sidecar or replacing an immutable
base snapshot. Keep local drafts and their original baselines on errors. A
separately fetched diff does not advance a draft baseline. Exit 3 means stale,
4 means RTC unavailable, and 5 means a rejected patch. The CLI does not retry
HTTP patch requests. If an acknowledgment is lost or the outcome is ambiguous,
keep the original draft and baseline, read the resulting state, and reconcile
before resubmitting. Separate HTTP requests do not share an idempotency receipt.

Hash references use `sha256:<hex>`. Time references are passed unchanged to the
server, including timestamps, dates and `"2 hours ago"`; server retention and
timezone rules apply. Unknown bases fail explicitly. Partial/numbered reads
remain available with `--legacy`; they are not v2 source snapshots.

### Concurrent edit walkthrough: MERGE versus EXACT

Use a test Note whose exact source is `Hello world.` with no final newline.
The patch below changes only the original `world` identities. Keep both files;
none of these commands overwrites the baseline or draft after an error.

```bash
NOTE_ID=your-test-note
dreamlake notes read "$NOTE_ID" --json > original.json
BASE=$(jq -er .revision original.json)
jq -e '.content == "Hello world."' original.json
cat > original.patch <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
# In the browser, prepend "Human: " and wait for that edit to sync.
# Do not replace original.json or BASE with a newer read.
set +e
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" --exact \
  --file original.patch --json > exact.stdout 2> exact.stderr
EXACT_EXIT=$?
set -e
test "$EXACT_EXIT" -eq 3
test ! -s exact.stdout
cat exact.stderr
# EXACT rejected the intervening revision without submitting patch operations.
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" \
  --file original.patch --json > merge-receipt.json
jq '{note, mode, baseRevision, hash, revision}' merge-receipt.json
dreamlake notes read "$NOTE_ID" --json > merged.json
jq -e '.content == "Human: Hello team."' merged.json
```

The successful receipt has `mode: "merge"`, `baseRevision` equal to the saved
`BASE`, and the content `hash` and RTC `revision` observed coherently after the
patch acknowledgment. These do not claim that every peer is synchronized or
that nobody can edit afterward. Text mode prints those same five fields as
labelled lines; `--json` emits one JSON object. Success diagnostics do not mix
with stdout. HTTP 412 produces exit 3, empty stdout, and a stderr explanation
that retains the original baseline and draft. There is no silent downgrade
from EXACT to MERGE and no automatic resubmission.

The server applies MERGE operations to the identities captured by the original
snapshot. The browser's prefix has different identities and is preserved.
Unavailable snapshots and malformed patches are errors; they never select the
latest source automatically. The API/RTC acceptance fixtures verify identity
preservation and zero patch writes on EXACT rejection separately from these
user-facing text checks.

### Successful EXACT and the next MERGE request

Continue from the merged fixture. This separate edit takes a fresh baseline;
if another writer intervenes again, preserve these files and inspect the note
before deciding on another request. EXACT does not silently select MERGE.

```bash
dreamlake notes read "$NOTE_ID" --json > exact-base.json
EXACT_BASE=$(jq -er .revision exact-base.json)
jq -e '.content == "Human: Hello team."' exact-base.json
cat > exact-success.patch <<'PATCH'
@@ chars 18:18 @@
~ {+!+}
PATCH
dreamlake notes patch "$NOTE_ID" --base-revision "$EXACT_BASE" --exact \
  --file exact-success.patch --json > exact-receipt.json
jq '{note, mode, baseRevision, hash, revision}' exact-receipt.json
jq -e --arg base "$EXACT_BASE" '.mode == "exact" and .baseRevision == $base' exact-receipt.json
dreamlake notes read "$NOTE_ID" --json > after-exact.json
jq -e '.content == "Human: Hello team.!"' after-exact.json

# EXACT applies to one request. This separate no-op uses the MERGE default.
NEXT_BASE=$(jq -er .revision after-exact.json)
printf '' | dreamlake notes patch "$NOTE_ID" --base-revision "$NEXT_BASE" \
  --file - --json > next-merge.json
jq -e --arg base "$NEXT_BASE" '.mode == "merge" and .baseRevision == $base and .revision == $base' next-merge.json
```

Successful EXACT has the same five receipt fields as MERGE, with `mode: "exact"`.
Omitting `--json` on a separate request prints the same values as labelled text.
Do not repeat a successful patch simply to request a different output format.

### Recorded fixture output

These exact outputs were replayed through the candidate CLI from an isolated
API + RTC + Mongo fixture (authentication, catalog, and S3 projections mocked).
They are test evidence, not a production or published-package transcript.
The fixture changed `Hello world.` to `Human: Hello team.` and recorded zero
patch writes for the rejected EXACT request.

Text stdout (exit 0; stderr empty):

```text
note: 507f1f77bcf86cd799439099
hash: sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf
revision: rtc:94c1a7696f6bcd27fa880e4b38b3f73cdd3971f28b44edf9018fadf817df0f3f
mode: merge
baseRevision: rtc:9a67f239fc8b862aa557dd10dd6512a7669861287ac8fe262d9c80afebcd18e7
```

`--json` stdout (exit 0; stderr empty):

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf",
  "revision": "rtc:94c1a7696f6bcd27fa880e4b38b3f73cdd3971f28b44edf9018fadf817df0f3f",
  "baseRevision": "rtc:9a67f239fc8b862aa557dd10dd6512a7669861287ac8fe262d9c80afebcd18e7",
  "mode": "merge"
}
```

EXACT failure (exit 3; stdout empty; stderr):

```text
✗ the original revision or RTC identities are no longer valid for this request; keep the original baseline and draft, inspect the note before resubmitting ((412) stale)
```

The same fixture returned HTTP 404 with `error: "revision_not_found"` and
`message: "Original RTC baseline is not retained"` for a missing baseline.
A malformed inline patch returned HTTP 422 with `error: "patch_failed"` and
`message: "Expected inline header and one record"`. These are errors, not
instructions to fetch a replacement baseline or downgrade the requested mode.

### Recorded successful EXACT output

A separate run of the isolated API/RTC/Mongo fixture above produced these
receipts, replayed through the candidate CLI. This remains bounded test evidence,
not a published-package or production transcript. Each command exited 0 with
empty stderr. Text and JSON are alternative renderings, not instructions to
submit the same patch twice.

Text stdout for successful EXACT:

```text
note: 507f1f77bcf86cd799439099
hash: sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5
revision: rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484
mode: exact
baseRevision: rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e
```

The same successful EXACT receipt as `--json` stdout:

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5",
  "revision": "rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484",
  "baseRevision": "rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e",
  "mode": "exact"
}
```

A subsequent empty patch without `--exact` selected MERGE again, preserving the
successful EXACT revision and hash:

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5",
  "revision": "rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484",
  "baseRevision": "rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484",
  "mode": "merge"
}
```

### Complete mapped HTML through Bash

```bash
NOTE_ID=design-doc
dreamlake notes read "$NOTE_ID" --view html > design-doc.preview.html
# committed.json is the successful patch response from the workflow above.
REVISION=$(jq -er .revision committed.json)
dreamlake notes read "$NOTE_ID" --view html --if-match "$REVISION" > verified.preview.html
```

`--view html` returns the complete server-rendered HTML, byte-for-byte, with no
CLI metadata prefix, JSON wrapper or added newline. The root `data-note`,
`data-hash`, `data-revision`, `data-source-type`, `data-offset-unit` and
`data-source` attributes carry the snapshot contract; element `data-start`,
`data-end` and `data-map` attributes carry source mappings. Decode the root's
source attribute exactly once to recover canonical source. Offsets count Unicode
code points, not DOM UTF-16 units. Atomic mappings require whole-range edits;
generated content has no editable source range. Never upload preview wrappers
or metadata as canonical Note content.

The CLI checks the root Note identity, canonical-source SHA-256 and write token
before writing any stdout. `--if-match` is sent to the server and verified again
against the response's embedded revision. A mismatch exits 3 without output.
HTML reads are full snapshots: `--since`, `--format`, `--json`, `--legacy`,
section/line slicing and numbered output cannot be combined with this view.
`--view source` explicitly selects the default canonical-source interface.
HTML reads are available in CLI 0.26.2 and later and the matching Notes HTML server
contract. Check the [release notes](release-notes.md) for publication and
verification status; an installed CLI alone does not establish server support.

### Agent presence and activity (development preview)

#### Agreed lifecycle and identity

**Presence is opt-in.** Agents can read and edit using normal authentication and
revision checks without any agent ID, join, heartbeat, or leave. A runner opts in
by supplying a stable session ID. The client generates it (a UUID once per task),
not the server. Names and IDs are self-reported, grant no permissions, and are not
verified audit identity. Two clients under the same authenticated owner can reuse
an ID; random UUIDs prevent accidental collisions, not deliberate impersonation.

Presence means **active in this note recently**, for both humans and agents. It is
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
and passes it to every Notes command. Do not generate an ID on every command or
use a shared display name as the session key. Resume the same ID for the same
task; use a new ID for a new or concurrent task. Socket reconnections have their
own transport IDs and must not create a new logical participant.

The current `DREAMLAKE_AGENT_ID` / `X-DreamLake-Agent-Id` field carries this
**task/session ID**, despite its name. It does not yet represent a separate,
persistent agent-account ID. The roster key is scoped by note, authenticated
owner, and session ID; the display name is never the key.

| Event | Intended behavior |
|---|---|
| First attributed read/edit | Implicitly join and start the recent-presence timeout. |
| Later read/edit with the same session ID | Refresh the existing badge, without adding another participant. |
| Inactivity | Remove the badge after expiry; no cleanup command is required. |
| Explicit leave/unjoin | Remove that session from that note immediately; do not erase its identity. |
| Interaction after leave or expiry | Implicitly rejoin using the same session ID. |
| Optional explicit join or maintained session | Support clients that need sustained presence; ordinary CLI use does not require it. |

Human clients can send leave on navigation away or note closure. Abrupt tab close,
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

The proposed defaults are a 60-second recent-presence timeout and a 5-second
completed-edit fade. Optional passage activity has an independent 8-second
expiry. These are DreamLake choices, not asserted Google Docs, iMessage, or
Claude Tag timing constants.

#### Current preview limitations and optional controls

The local implementation uses the lifecycle above: an attributed operation
implicitly joins or renews the same 60-second presence entry. Anonymous agent
identity is not inferred from ordinary API calls. A separate persistent
agent-account identity is not yet part of the wire contract. Deployment and
client release status must be checked independently of this source documentation.

The matching unreleased CLI/server exposes these optional controls:

```bash cli-help="notes presence"
# NOTE_ID and the stable task identity must already be set.
dreamlake notes presence "$NOTE_ID" join
dreamlake notes presence "$NOTE_ID" heartbeat
dreamlake notes presence "$NOTE_ID" clear
dreamlake notes presence "$NOTE_ID" leave
# Alternative: a blocking foreground helper; stop it when the task ends.
dreamlake notes presence "$NOTE_ID" join --watch
```

`join --watch` heartbeats every 20 seconds and leaves when interrupted. It is
optional, not the standard recipe. `clear` clears activity without leaving;
`leave` removes presence. A heartbeat does not create a missing session or revive
an expired one (410); join or a normal attributed interaction can establish
presence again. Never start an untracked helper that outlives the task.

API: `POST /namespaces/:slug/notes/:noteId/presence` accepts
`{action, hash?, ranges?: [{start,end}]}`, bearer authentication,
`X-DreamLake-Agent-Id`, and optional `X-DreamLake-Agent-Name`.
Actions are `join`, `heartbeat`, `read`, `edit`, `seek`, `clear`, `leave`.
Response is `{state}` or `{state:null}` after leave. Only authenticated members or
explicitly shared readers may publish; `edit` also requires write permission.
Public visibility alone does not grant presence access. Controls do not mutate
document content or revision. Owner metadata comes from authenticated lookup.

Explicit ranges require the exact source SHA-256 and zero-based, end-exclusive
Unicode code point offsets. Stale or out-of-bounds locations are refused. A
collapsed seek is a caret, not a claim that text was read. Source changes invalidate
hash-bound markers. Deletion-only edits do not invent insertion ranges.
Errors include missing identity/invalid input (400), denied access (404), stale
range (409), expired heartbeat (410), and unavailable relay (503).

Identity values accept 1–128 ASCII letters, digits, dots, colons, underscores and
hyphens; names accept at most 64 printable ASCII characters. CLI 0.27.0+ and
Python SDK 0.21.0+ attach identity headers to Notes body/section/diff operations
when the environment variables below are set. Explicit presence commands require
the matching unreleased source and server, and an active collaborative room.
Updating a skill does not update a binary or deploy a server. Python has no
presence convenience method yet; use the HTTP contract when available.
The authorized agent-activity feed retains operation observations, not an online
roster. Observation failures must not turn an acknowledged edit into an apparent
failed edit. Live source-range decorations currently require the collaborative
editor; this preview does not add a read-only RTC client.

#### Agentic usage pattern: one identity, normal commands

For agents that opt into presence, initialize once in the runner's task environment. For separate shell tool calls,
the runner must inject the same saved values each time; an export in one shell
does not propagate into later independent shells. No explicit join is required.

```bash
export DREAMLAKE_AGENT_ID="codex:$(python3 -c 'import uuid; print(uuid.uuid4())')"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID="<full-note-id>"
```

Run ordinary commands with that identity. Reading establishes/refreshes presence;
it does not mean the agent remains actively reading between commands.

```bash
dreamlake notes read "$NOTE_ID" --json > baseline.json
dreamlake notes find lighthouse --note "$NOTE_ID" --json
# Draft a reviewed patch against baseline.json, using the patch workflow below.
# Retain its revision, apply the patch, and read back the acknowledged revision.
```

The conditional patch and exact-readback examples elsewhere in this guide remain
required; presence does not relax concurrency checks. Do not retry an old patch
with a newly fetched revision merely to force it through.

When finished, optionally call `dreamlake notes presence "$NOTE_ID" leave` on a
matching preview installation. Otherwise let presence expire. Do not forget the
session ID between commands, and do not require the agent to remember cleanup for
correctness. Stop any optional watch helper and remove the task identity from the
runner's environment when the task ends.

### Keep incremental reads compact

For an agent following a note, save one full `read --json` baseline, then use
`read --since "$BASE_HASH"` for subsequent checks. The default `inline-dff`
returns only character edits and is the preferred compact response for agents.
Use `--format diff` when line context or a standard unified patch is useful.
On servers with localized unified-diff generation, this returns changed
lines with up to three unchanged context lines on each side; nearby changes
share a hunk and distant changes use separate hunks. Older servers may still
return a whole-document replacement; a docs or skill update alone does not
change server output. The default inline format already avoids that expansion.

Both formats preserve exact source, including CRLF and a missing final newline.
An unchanged source returns an empty `patch`, possibly with a newer RTC
`revision`. Keep `base`, `hash`, and `revision` with the response. Apply the patch
only to the saved source matching `base`, verify its resulting hash, and never
replace an existing draft's original revision just to make it pass. Unknown or
expired bases remain errors. Use `--json` and extract `.patch` when a consumer
needs patch text alone; normal text output includes metadata.

## Browser sync and recovery

The browser's **Synced**, **Syncing**, and **Out of sync** indicator checks the
editor against the collaboration server. **Syncing** includes normal pending
edits and reconnects; simultaneous editing remains supported.

If a browser holds a draft after a mismatch, open **Out of sync ▾**, download
the local draft, then choose **Use server version** when you are ready to
discard that browser draft. The CLI reads the server version. It cannot read,
clear, or recover a draft held in another browser tab. Do not force-write an
old export to resolve the warning; compare it with a fresh read and make a
revision-checked edit.

The browser also offers view-only time travel: play or step through retained
versions without changing the live note. There is no new CLI history or restore
command. See the [Notes guide](https://docs.dreamlake.ai/notes/) for browser
controls and recovery details.

## Finding a note

```bash file="terminal"
dreamlake notes list
dreamlake notes list --shared        # shared with you, from other namespaces
dreamlake notes search deploy
```

### Which namespace

Notes belong to a namespace, and **the default is your personal one** — not an
organization you belong to. An organization's notes live in its own namespace
and are only reachable by naming it:

```bash file="terminal"
dreamlake notes list                        # your own
dreamlake org list                          # the organizations you belong to
dreamlake notes list --namespace acme       # one of theirs
```

`--namespace` works on every command below. `notes list --shared` is the one
exception that crosses namespaces: it lists what other people shared with you,
wherever it lives.

A note is named by its slug, its title, or its id. All three work wherever
`<note>` appears below.

`search` is current: before querying, it flushes the notes anyone has open in
this namespace, so a sentence a colleague typed seconds ago is findable. You
do not have to wait for anything.

`search` also says **where** in each note it matched:

```
NOTE      SLUG        UPDATED     ID
Runbook   runbook     2026-03-01  507f…

runbook
  deploy  …Run `pnpm run deploy` to ship…
```

Go straight to that section — `notes read runbook --section deploy` — instead
of reading the whole note to find it. The most specific section is listed
first.

`search` matches **titles and bodies**, case-insensitively, by substring — so a
phrase inside a note finds it, and so does a fragment of an identifier like
`LAKE_REMOTE`. Chinese and other non-spaced scripts match the same way.

A note last written before bodies were indexed matches on its title only,
until someone edits it or an administrator runs the one-off backfill.

## Creating

```bash file="terminal"
dreamlake notes create "Design Doc"
dreamlake notes create "Design Doc" --file draft.md
dreamlake notes create "Public Notes" --text '# Hello\n' --public
```

Titles may repeat; the slug gets a suffix to stay unique, so the command
prints the slug and id it actually made rather than the title you asked for.

## Reading

```bash file="terminal"
dreamlake notes read --legacy design-doc                 # the whole body, to stdout
dreamlake notes read --legacy design-doc > local.md      # …which means this works
dreamlake notes sections design-doc             # the outline
dreamlake notes read --legacy design-doc --section install
```

`sections` lists what you can address:

```
ANCHOR    LEVEL  TITLE        CHARS
title     1      Design Doc     820
install   2        Install      412
macos     3          macOS      180
usage     2        Usage        228
```

A **section** is a heading plus everything under it, up to the next heading of
the same or a higher level — so `install` contains `macos`. The anchor is a
slug of the title, with a numeric suffix when titles repeat (`setup`,
`setup-2`). Text before the first heading is addressed as `preamble`.

For a long note, read a range of lines:

```bash file="terminal"
dreamlake notes read --legacy design-doc --start-line 40 --end-line 80
dreamlake notes read --legacy design-doc --start-line 40 --end-line 80 --numbered
```

A partial read says so on stderr, so a redirected body stays a body. The
revision it reports is the **whole** note's — writing a range back as the body
would delete everything outside it.

## Writing

```bash file="terminal"
# one section
dreamlake notes write design-doc --section install --file install.md

# the whole body
dreamlake notes write design-doc --file whole.md

# inline, or from a pipe
dreamlake notes write design-doc --section install --text '## Install
pip install dreamlake
'
cat install.md | dreamlake notes write design-doc --section install

# add to the end
dreamlake notes append design-doc --text $'\n## Changelog\n- shipped\n'
```

A section is replaced **verbatim, heading included** — which is how you rename
one. Leave the heading out and the section stops being a section.

### Adding and removing sections

```bash file="terminal"
dreamlake notes insert design-doc --after install --text '## Troubleshooting

Check the logs.
'
dreamlake notes insert design-doc --before install --file prereqs.md
dreamlake notes insert design-doc --text '## Licence\n\nMIT\n'   # at the end

dreamlake notes rm-section design-doc troubleshooting
```

`--after` places the new section past that one **and its subsections** —
anything else would drop it inside the section you named. The heading is part
of the text, so you pick the level: a `###` can go under a `##`.

`insert` prints the new outline, because the anchor is only knowable afterwards
— a duplicate title takes the next free suffix.

`rm-section` removes the subtree too. That is what the section is; leaving the
subsections behind would promote them into the previous one.

## Editing by what it says

Naming the text beats counting lines, and is safer: a query that matches twice
is **refused** rather than applied to the first one.

```bash file="terminal"
dreamlake notes find "Draft" --note design-doc
dreamlake notes replace "Draft" --text "Published" --all --note design-doc
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note design-doc --dry-run
dreamlake notes insert --text "New line" --line 10 --note design-doc
dreamlake notes delete "obsolete paragraph" --note design-doc
dreamlake notes toc --note design-doc
```

Patterns are JavaScript: `(?<name>…)`, `$1`, `$<name>`, `$&`. Expansion is
automatic. `--dry-run` prints the result without writing, and every mutation
takes `--if-match`.

For HTML, address an element:

```bash file="terminal"
dreamlake notes select "#contact" --note page
dreamlake notes replace "Contact us" --text "Talk to sales" --selector "#contact" --note page
dreamlake notes insert --text "<li>New</li>" --selector "#list" --position append --note page
dreamlake notes replace --html "<b>done</b>" --selector "#status" --note page
```

Only the characters addressed change — entity spelling and attribute quoting
survive, so the diff is the edit and nothing else.

## Searching across notes

`notes search` finds *which* note; `notes grep` finds *where*, in a form you
can act on.

```bash file="terminal"
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive
dreamlake notes grep "deploy" --glob 'spec-*' --limit 20
dreamlake notes grep "Draft" --json          # etag + character range per hit
```

Output is `slug:line:column`, like `rg`. Literal and case-insensitive by
default, so `v1.2` does not also match `v1x2`. The JSON form carries each
hit's revision and `ind` range — enough to edit exactly what was found.

## Files on a note

Files inherit the note's permissions, so an attachment on a private note stays
private.

```bash file="terminal"
dreamlake notes files upload ./report.html --note design-doc
dreamlake notes files list --note design-doc
dreamlake notes files list 'assets/*.png' --note design-doc --limit 50
dreamlake notes files cat config.json --note design-doc
dreamlake notes files download report.html --note design-doc -o ./report.html
dreamlake notes files mv old.txt new.txt --note design-doc
dreamlake notes files rm old.txt --note design-doc        # trash; restore brings it back
```

Bytes are streamed both ways and never decoded, so any file survives the round
trip. `cat` refuses a binary rather than printing mojibake you might pipe back.

To look at one:

```bash file="terminal"
dreamlake notes files preview report.html --note design-doc --open
dreamlake notes files preview report.html --note design-doc --share
dreamlake notes files preview report.html --note design-doc --revoke
```

The default link needs the reader signed in. `--share` opens without signing
in and does not expire; `--revoke` withdraws it everywhere at once. Uploaded
HTML renders in a separate origin, never the dashboard's.

## Legacy whole-body and section writes while others edit

Every write is a **real-time collaborative edit**. The server joins the note's
collaboration room and applies your change there, so anyone with the note open
watches it appear — and it merges with what they are typing, the same way two
people's edits merge.

That is true of all of them: `write`, `append`, `patch`, `add-section`,
`rm-section`. You do not have to wait for people to leave, and nothing is
locked.

### The precondition is a different thing

Collaboration handles two edits arriving at once. It does not help with an
edit built from a document that has since changed — read a note, spend a
minute deciding, write the whole body back, and you would erase what happened
while you were deciding.

So a write also sends the version it was based on. If the note moved in
between, it is **refused** rather than applied:

| Exit | Means | Do |
|---|---|---|
| `3` | The note changed since you read it | Re-read, redo the edit. Retrying as-is fails again. |
| `4` | The realtime service could not take the write, and people are editing | Transient — wait a few seconds and retry. |
| `5` | Your diff no longer applies | Re-read and regenerate it. |

Exit `4` is an infrastructure signal, not a queue. It means the collaboration
room was unreachable AND somebody is connected — the fallback (writing the
archive) would reset the room and cost them whatever they have not saved, so
the command refuses instead. With the service healthy you will not see it.

```bash file="terminal"
dreamlake notes write design-doc --section install --file new.md
case $? in
  0) echo "done" ;;
  3) echo "someone edited it — re-read and redo" ;;
  4) sleep 30; echo "retrying" ;;
  5) echo "regenerate the diff" ;;
esac
```

### Pinning a version yourself

`read --legacy --json` gives you the content validator, which you can hold across a longer edit:

```bash file="terminal"
ETAG=$(dreamlake notes read --legacy design-doc --json | jq -r .etag)
# …edit…
dreamlake notes write design-doc --file new.md --if-match "$ETAG"
```

### Overwriting on purpose

```bash file="terminal"
dreamlake notes write design-doc --file whole.md --force
```

`--force` is the only way past the check. Overwriting a colleague should be
something you typed, not something that happened.

## Legacy changes since your last read or edit

Legacy revision diffs require the server revision-diff endpoint and CLI 0.25.0
or later on both native and npm channels. In CLI 0.26.2 and later, select this
ETag interface with `--legacy`. Check `dreamlake notes diff --legacy --help`
for command availability.

A read's `etag` is the quoted SHA-256 hash of the complete note. Keep that ref
and pass it as `--since` to compare with the current body, including edits made
by others. References are retained by the server and can be reused across
shell sessions. Partial reads still identify the complete note.

```bash
NOTE=release-plan
dreamlake notes read --legacy "$NOTE" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
dreamlake notes diff --legacy "$NOTE" --since "$REV"
dreamlake notes diff --legacy "$NOTE" --since "$REV" --json > changes.json
```

These shell recipes use `jq`. Plain output writes only the unified diff to
stdout and the current ETag to stderr. `--json` returns `diff`, `from`, `to`,
and `etag` (same as `to`). `--context 0` removes context lines; the default is
3 and the maximum is 100. No changes produce empty stdout and exit 0.

`--since` is required: the CLI does not guess which earlier read you mean or
maintain a hidden per-machine baseline. Keep the quoted ETag intact. Identical
text has the same hash, regardless of RTC operations. Unknown or unretained
refs return an error; refs issued before retention was deployed may be missing.
Fetching a diff does not edit the note. Apply a patch you prepared from the
saved body using `notes patch --legacy --if-match "$REV"`; stale refs are refused.
A successful patch's JSON `etag` is the next ref you can save.

## Legacy unified patching

A unified diff carries its own precondition — the context has to match — so a
document that moved refuses the patch instead of taking half of it.

```bash file="terminal"
dreamlake notes read --legacy design-doc > before.md
cp before.md after.md
# …edit after.md…
diff -u before.md after.md | dreamlake notes patch --legacy design-doc --file -
```

## Permissions

Reading needs read access; writing needs write access. A read-only share link
gives the first and not the second — reads work, writes fail with "read-only
access to this note". A note you cannot read at all reports as not found.

## Command summary

| Command | Does |
|---|---|
| `notes create <name>` | Make a note, optionally with a body |
| `notes list [--shared]` | Notes in the namespace, or shared with you |
| `notes search <query>` | Match note titles and bodies |
| `notes sections <note>` | The outline, with anchors |
| `notes read <note> [--view source\|html] [--since <ref>] [--format <format>]` | Exact source or selected patch with hash/revision metadata |
| `notes read <note> --legacy [--section <anchor>]` | Previous body-only or section output |
| `notes write <note> [--section <anchor>]` | Replace body or section |
| `notes insert <note> [--before\|--after]` | Add a section |
| `notes rm-section <note> <anchor>` | Remove a section and its subtree |
| `notes patch <note> --base-revision <revision> [--exact] [--format <format>]` | Upload a patch against its original snapshot; EXACT is opt-in |
| `notes append <note>` | Add to the end |
| `notes find <query> --note` | Where the text is, in one note |
| `notes grep <query>` | Where it is, across every note you can see |
| `notes toc --note` | Outline with line and character ranges |
| `notes replace <query> --text` | Replace by text, regex, line or selector |
| `notes insert --text` | Insert at a line, offset or element |
| `notes delete <query> --note` | Remove what a query matches |
| `notes select <css> --note` | One HTML element and its text |
| `notes files upload/download` | Attach a file, or fetch it back |
| `notes files list/mv/cp/rm/restore` | Manage what is attached |
| `notes files preview [--share]` | A link that renders the file |

Every one of them takes `--namespace`, `--json`, and the usual connection flags.
V2 `patch` requires an original `--base-revision`; `--exact` opts in to EXACT
for that request. Explicit `--if-match` also selects EXACT and can supply the
baseline when used alone. It rejects
`--force`; legacy mutation commands retain their previous flags.

## Command-help recipes

These examples are also shipped in each command's `--help`. Log in first.
Replace `release-plan` with a note you can access. Shell recipes using `jq`
require it locally. Each edit example captures the revision before the edit;
an unavailable original snapshot requires a fresh read and a reviewed edit.
A concurrent edit alone does not require rebasing an merge patch.

```bash cli-help="notes list"
dreamlake notes list --limit 10
dreamlake notes list --shared --json
dreamlake notes list --namespace acme
```

```bash cli-help="notes search"
dreamlake notes search "release plan"
dreamlake notes search deploy --namespace acme --json
```

```bash cli-help="notes create"
dreamlake notes create "Release plan" --text "Draft checklist"
printf '# Release plan\n' | dreamlake notes create "Release plan" --file - --json
```

```bash cli-help="notes read"
dreamlake notes read release-plan
dreamlake notes read release-plan --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
BASE=$(jq -er .revision baseline.json)
dreamlake notes read release-plan --since "$BASE_HASH" --format inline-dff
dreamlake notes read release-plan --view html --if-match "$BASE" > release-plan.preview.html
# Partial reads use the explicit compatibility interface.
dreamlake notes read release-plan --legacy --start-line 1 --end-line 20 --numbered
```

```bash cli-help="notes write"
NOTE=release-plan
dreamlake notes read --legacy "$NOTE" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
jq -r .text note-snapshot.json > note.md
# Edit note.md after reading the snapshot, then preview and apply.
dreamlake notes write "$NOTE" --file note.md --if-match "$REV" --dry-run
dreamlake notes write "$NOTE" --file note.md --if-match "$REV" --json
```

```bash cli-help="notes diff"
dreamlake notes read release-plan --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
dreamlake notes diff release-plan --since "$BASE_HASH" --format diff
# Keep the original baseline.json while preparing an edit.
```

```bash cli-help="notes patch"
# Requires the exact saved base: Hello world. (no trailing newline).
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
dreamlake notes patch "$NOTE_ID" --format inline-dff --base-revision "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
REVISION=$(jq -er .revision committed.json)
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json
# For a separate patch, select EXACT for this request only:
# dreamlake notes patch "$NOTE_ID" --file draft.diff --base-revision "$BASE" --exact
```

```bash cli-help="notes sections"
dreamlake notes sections release-plan
dreamlake notes sections release-plan --json
```

```bash cli-help="notes files list"
dreamlake notes files list --note release-plan
dreamlake notes files list --note release-plan --json
```
