<!-- generated from https://cli.dreamlake.ai/sessions.md at 0.117.0 6ff1564; do not edit -->

# Terminal sessions

CLI **0.74.1 or later** provides `dl sessions`, which shares saved terminal
descriptors with the DreamLake Sessions page. The matching `terminal-sessions`
API and terminal gateway Codex launch support are required. Updating the CLI
does not deploy those server capabilities.

Use **0.74.1 or later** for native and npm installations. Version 0.74.0 omitted
the required WebSocket Origin header in its compiled client and could not attach
to the production terminal gateway. Saved descriptors from 0.74.0 remain usable.

A descriptor binds the selected target, host enrollment, Unix user, working
directory, and exact Codex session UUID. It contains no credentials or transcript.
The remote host must already have that conversation under the selected user's
Codex state, the requested directory, and `codex` installed. Persistent terminals
use `tmux`; CLI **0.81.0+** with a matching gateway can connect directly when
tmux is unavailable. A session
UUID does not move a conversation between computers or users.

## Registration and visibility (0.82.0+)

With the matching API release, **all newly registered sessions default to public**:
UI creation, API creation, CLI creation, metadata-only imports and machine sync.
Public uses DreamLake PUBLIC read semantics: anyone can read session metadata and
an uploaded, redacted conversation. It does not grant terminal execution, resource
editing, or access to linked private Notes/artifacts. Private and team sessions
retain their existing access rules. Existing records without a visibility field
remain private/team; synchronization never resets an existing sharing choice.

Use `--visibility private` when creating/registering/syncing new sessions. This
option affects new records only. To change an existing session explicitly:

```bash cli-help="sessions visibility"
dl sessions visibility <saved-id> --namespace <personal-namespace> --visibility private
```

Register a native Codex/Claude UUID without a host, gateway, or terminal process:

```bash cli-help="sessions register"
dl sessions register --provider codex --session <native-uuid> --cwd /absolute/repository --json
# Explicit private override for a new registration:
dl sessions register --provider claude --session <native-uuid> --cwd /absolute/repository --visibility private --json
# From inside a Claude Code session: register it, print the saved ID and the control send recipe,
# and write an env file other shells can source so their note/artifact writes link to it:
dl sessions register --provider claude --session "${CLAUDE_SESSION_ID:-$CLAUDE_CODE_SESSION_ID}" --cwd "$PWD" --visibility private --write-env "$HOME/.dreamlake/sessions/current.env"
```

This returns a **saved descriptor ID**, distinct from the native UUID. Registration
is idempotent for the personal owner/provider/native ID: registering the same
provider and UUID again (from another directory, on another day) returns the
existing saved session, never a second one. It reuses an unambiguous existing
registration; conflicting saved identities require explicit selection. Without
`--json` the command prints the saved ID, the recipe that lets a runner message
it (one `control restart --permission … --raise` that records the level — a
registered session has none, and a runner refuses a turn for a session
without one, `--permission` on `send` notwithstanding — then plain
`control send` / `control status`) and, with `--write-env <path>`, the file it wrote:
`export DREAMLAKE_TERMINAL_SESSION_ID='…'` and `export
DREAMLAKE_SESSION_NAMESPACE='…'` (exported, so `source`-ing it hands the pair to
every `dl` process that shell starts), mode 600, the explicit
saved-session context described below. The
[`/dreamlake` Claude Code skill](https://cli.dreamlake.ai/dev/claude-code-skill) wraps exactly this
command.
A metadata-only session has `archiveOnly: true`, null `launch`, and no host
binding. It can be linked and read but cannot open a terminal. A later verified
host registration with the same owner/provider/UUID and exact cwd can bind the
same descriptor, preserving privacy and resource links.

CLI 0.82.0+ automatically registers metadata after an acknowledged Note/artifact
content write when `CODEX_THREAD_ID` or `CLAUDE_SESSION_ID` supplies an exact native
UUID. `CLAUDE_CODE_SESSION_ID`, which Claude Code exports to every command it
runs, is accepted as the Claude fallback, so writes made from inside a Claude
Code session link without any setup; an explicit `CLAUDE_SESSION_ID` wins when
both are set. Set `DREAMLAKE_SESSION_VISIBILITY=private` for a private new registration,
or `DREAMLAKE_SESSION_AFFILIATION=0` to disable affiliation. Explicit saved context
uses `DREAMLAKE_TERMINAL_SESSION_ID` with `DREAMLAKE_SESSION_NAMESPACE`.
No transcript is uploaded unless an export is explicitly selected.

If the CLI says **Content saved; optional session metadata was not fully recorded**,
do not repeat the content write. Retry `sessions register`, then `sessions link`
using the returned saved ID; retry `upload-conversation` separately if needed.
`terminal_access_denied` from `sessions targets` is an execution/discovery authority
failure, not evidence that the Memo save failed. Metadata registration does not
need target discovery. Do not change enrollment credentials to repair attribution.

Conversation upload redacts recognized credential assignments, authorization
headers, common provider tokens, JWTs, private keys and signed URL parameters in
all message roles. The API repeats redaction and sanitizes historical archive
reads, including archives made public later. Pattern detection cannot recognize
every arbitrary secret: review a selected export and remove custom secrets before
publishing. Private reasoning and binary attachments are omitted by native import.

Public session unlock icons appear on hover or keyboard focus. Private sessions
keep an orange lock visible in lists, details and session navigation.

## Start Claude Code or Codex under DreamLake

```bash cli-help="claude"
# Interactive Claude Code, registered private before it starts, acceptEdits (workspace-write):
dl claude
# One headless turn at plan level; everything after the wrapper's flags goes to claude unchanged:
dl claude --permission read-only -p "Summarize the open PRs" --model opus
```

```bash cli-help="codex"
dl codex --permission full-access "Fix the failing test"
```

`dl claude …` mints the native session UUID, registers it
(`sessions register`, idempotent, private by default) **before** Claude Code
starts, writes the env file `~/.dreamlake/sessions/<uuid>.env`, and runs
`claude --session-id <uuid> --permission-mode <mode> …` with
`DREAMLAKE_TERMINAL_SESSION_ID` / `DREAMLAKE_SESSION_NAMESPACE` exported, so
every `dl` call the session makes links to it and the
[hook relay](https://cli.dreamlake.ai/dev/claude-code-hooks) finds it without a lookup. `--permission`
maps `read-only` / `workspace-write` (default) / `full-access` onto `plan` /
`acceptEdits` / `bypassPermissions` (Codex: `--sandbox read-only` /
`workspace-write` / `danger-full-access`). Every provider flag that would make
the process run under something other than the recorded level is refused with
the wrapper flag to use instead: Claude `--session-id`, `--permission-mode`,
`--dangerously-skip-permissions`, `--permission-prompt-tool`,
`--allowedTools` / `--disallowedTools`; Codex `--sandbox` / `-s`,
`--ask-for-approval` / `-a`, `--full-auto`,
`--dangerously-bypass-approvals-and-sandbox` and `-c` / `--config` overrides
of `sandbox_mode`, `approval_policy` or `sandbox_*`. Anything after `--` goes
to the provider literally. The terminal
is handed over untouched; Ctrl-C reaches the provider, not the wrapper. When
the provider exits the wrapper beats `stopped`, uploads the transcript
(`--no-upload` skips it; a failure names the `upload-conversation` command to
retry) and exits with the provider's exit code. Before the launch, stderr
names the saved session and the recipe that lets a runner message it (below).

`dl codex …` cannot register first: Codex has no `--session-id` and
names its thread only in its own rollout file. The wrapper runs
`codex -C <cwd> --sandbox <mode> …`, then adopts the **one** rollout created in
this directory at or after the moment the launch began (a rollout from before
it, however recent, is another session's), registers it, writes its env file
and uploads the transcript; with none it reports `no rollout created`, with
several it names them, and in both cases registers nothing and prints the
`sessions register --provider codex --session <thread-id>` line to run by
hand. Inside the session, `dl` calls link through the
`CODEX_THREAD_ID` Codex sets. Both wrappers start the provider in a clean
environment: an inherited `DREAMLAKE_TERMINAL_SESSION_ID` /
`DREAMLAKE_SESSION_NAMESPACE` pair (a sourced env file, a parent agent
session) and inherited provider identities are dropped, so a child's writes
never link to its parent's session.

Registration records no permission level (the route takes none), and a runner
refuses a turn for a session without one (`permission_level_unknown`) —
`--permission` on `control send` does not help. The recipe both wrappers
print is therefore one `sessions control restart <id> --permission <level>
--raise --namespace <ns>` (a raise from "unrecorded": confirmed on a terminal,
on a runner started with `--max-human-permission <level>`), which records the
level the wrapper launched with, followed by plain `control send`. The same
recipe is printed by `sessions register`.

## Claude Code and observed states

Provider-aware clients also list and open Claude Code sessions registered by a
compatible machine collector. Use `--provider claude --session <uuid>` when
saving one explicitly, and `--claude-config-dir <absolute-path>` if it uses a
custom Claude configuration root. `--codex-session` remains the Codex-compatible
UUID option. The default provider is Codex.

```bash
dl sessions create --provider claude --session <uuid> --target <target-id> --cwd /absolute/repository --namespace geyang
```

The descriptor reports the agent tool separately from `modelProvider`. Its
`runState` and `runStateObservedAt` describe the latest machine observation;
stale observations become `unknown`. `running` confirms a matching process,
not active model work. Supported native Codex daemons additionally report
`working`, `waiting`, `idle`, or `error` through metadata-only status reads. Listing does not open terminals or SSH-poll each row.
Use `sessions status` for the selected managed terminal's current lifecycle.
Claude resumes with its existing permissions and login; the CLI adds no bypass.
These additions require matching provider-aware API, gateway and collector releases.

## Link memos and artifacts (0.78.0+)

With the matching resource-session API deployed, a saved session can be linked
to multiple memos and artifacts, including resources in another namespace.
Linking requires resource write access and session read access. Every list checks
both permissions again; sharing a resource does not share its terminal.

```bash cli-help="sessions link"
dl sessions link SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --note MEMO_ID --json
dl sessions link SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --artifact loss-plot --json
```

```bash cli-help="sessions unlink"
dl sessions unlink SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --artifact loss-plot --json
```

```bash cli-help="sessions resources"
dl sessions resources SESSION_ID --namespace geyang --page-size 25 --json
```

`resources` returns bounded pages (maximum 50); continue with its `nextCursor`.
These commands only change or read affiliations. They never open, start or stop
terminals and never modify memo or artifact content.

Memo creation and confirmed body/section changes are attributed by the Memo server,
using the same optional identity as [Memo presence](https://cli.dreamlake.ai/notes/collaboration).
`DREAMLAKE_TERMINAL_SESSION_ID` selects an exact owned saved session; native
`CODEX_THREAD_ID`, `CLAUDE_SESSION_ID` or `CLAUDE_CODE_SESSION_ID` supplies a typed
session identity. Explicit `DREAMLAKE_SESSION_ID` plus
`DREAMLAKE_SESSION_PROVIDER=codex|claude` is also supported. Ambiguous native
identities are not guessed. New attribution-only records start private, with no
launch target or transcript upload. Existing session visibility is preserved.

Use `dl memos contributors NOTE --json` to distinguish server-observed
`created`/`edited` evidence from a manually linked session (`contribution: null`).
No-op and failed edits, reads and presence announcements do not become contributions.
The new CLI does not issue a second Memo link request after content writes.

Artifact pushes retain the client-side registration/link path: at most one lookup
and one idempotent metadata write, a three-second combined deadline and no retry.
Missing or ambiguous registration warns without changing the successful content
result. Retry only metadata operations, never the content write.
`DREAMLAKE_SESSION_AFFILIATION=0` disables automatic attribution and affiliation.
Historical resources require exact evidence or an explicit link; they are not
assigned by guessing authorship.

## Select the host

Authenticate with your intended personal account and select the environment.
Machine identity cannot open personal terminal sessions; use `--identity user`
explicitly when a machine identity is configured. Target discovery uses the same
existing enrolled-host terminal access as the web page; it creates no machines,
enrollments, or permissions.

```bash cli-help="sessions"
dl sessions targets --namespace geyang
dl sessions list --namespace geyang
```

```bash cli-help="sessions targets"
dl sessions targets --namespace geyang --json
```

Choose `--target` from the returned inventory. Its exact enrollment is discovered
automatically; no first-target default is used. Optionally pin `--enrollment` from
that same row; the gateway verifies the binding when opening. A target with no enrollment ID cannot
be saved as a session. Re-enrollment does not silently retarget saved sessions.

## Resume from the command line

This is the terminal equivalent of selecting a saved session in the web page:

```bash cli-help="sessions resume"
dl sessions resume 01a13cbc-d4a7-7893-81cc-39696769c454 \
  --namespace geyang --target TARGET_ID \
  --cwd /home/ubuntu/workspace-3
```

It saves or finds the matching descriptor, obtains a short-lived gateway ticket,
and attaches an interactive terminal. On the **selected remote host**, the gateway
negotiates the available runtime. With tmux, it starts `codex resume` in the
requested directory under a deterministic tmux session, or attaches to that same
session if it exists. Repeated persistent opens share the same process; existing
agent processes outside that managed session are not adopted.

A gateway with the Codex native-writer guard refuses a **new** managed or direct
process when it positively observes a writable handle to that exact conversation's
local rollout file. CLI **0.84.1+** preserves the `native_session_active` error and
recovery guidance; older clients may show only HTTP 409. Continue in the existing
Codex chat. If a managed terminal is already running, `sessions reconnect` attaches
without creating another process. Do not retry automatically or terminate the
original chat to clear the error.

This guard is Codex-only and reads file/process metadata, not conversation content.
It does not block attachment to an existing managed tmux session. Missing,
unsupported or inconclusive observations retain the previous behavior; the absence
of an error does **not** prove there is no other writer. The guard does not adopt
native app sessions or provide a global exclusive-writer lock.

With CLI **0.81.0+** and a compatible gateway, a host without tmux uses a direct
foreground connection for the session owner. The CLI reports this before
connecting. The process starts only when the authorized terminal ticket is
consumed, and **disconnecting may end it**. Use `sessions open` explicitly to
resume again; `reconnect` never starts a replacement. Direct mode has no detached
start, managed stop, or team viewer attachment. Only one direct connection can
use a saved session at a time; close it before opening another. It installs no
packages.
Only tmux and direct mode are currently supported; screen is not an adapter yet.

With tmux, press **Ctrl-]** to detach while leaving the remote session running. Ctrl-C goes
to the remote program. Terminal resizing is forwarded. Exiting Codex ends its
remote process; closing the connection keeps a running tmux session available.
If access expires or the connection breaks, run `sessions open` with the same
saved ID. There is no automatic retry or process restart in the CLI client.

Interactive `resume` and `open` require stdin and stdout to be terminals. A pipe
or redirected invocation fails before writing a descriptor or requesting a
ticket. `resume --json` explicitly **saves only** and reports `executed: false`.

## Save and reopen

```bash cli-help="sessions create"
dl sessions create --namespace geyang \
  --target TARGET_ID \
  --cwd /home/ubuntu/workspace-3 \
  --codex-session 01a13cbc-d4a7-7893-81cc-39696769c454 \
  --name 'Workspace 3' --json
```

`create` never starts a remote process. Save the returned `session.id`; identical
target/enrollment, working directory, and conversation inputs resolve to the
existing descriptor. A successful registration alone is not execution proof.

```bash cli-help="sessions list"
dl sessions list --namespace geyang --json
```

```bash cli-help="sessions show"
dl sessions show SESSION_ID --namespace geyang --json
```

```bash cli-help="sessions open"
dl sessions open SESSION_ID --namespace geyang
```

`list` and `show` read saved metadata, not live process state. The terminal service
rechecks authorization and the enrollment binding when opening. `open` does not
accept `--json` because it is interactive.

## Managed runtime lifecycle (0.75.0+)

The following commands require CLI **0.75.0 or later** and the matching
managed-session gateway. CLI 0.74.3 and earlier do not provide them.

```bash cli-help="sessions status"
dl sessions status SESSION_ID --namespace geyang --json
```

`status` reads the saved descriptor first (`/terminal-sessions/:id/metadata`)
and prints what the session itself last reported: its **live state**
(`running`, `waiting-for-user`, … from its hooks or runner, see
[live state](https://cli.dreamlake.ai/sessions/control#live-state-and-subagent-events)), the current
tool and prompt head, the recorded permission level (and the level the runner
last ran under when they differ), its runner, and the Nymph `runState`. A
session registered without a host (`sessions register`, a runner start)
answers from that alone, instead of the 503 / 409 the gateway used to return
for it. For a gateway-saved descriptor (one with a target) `status` then also
performs the bounded observation on the exact enrolled host — tmux runtime,
pane identity, viewer count, dependencies — without starting Codex or reading
terminal contents; a gateway that cannot answer is reported inline as
`Runtime: unavailable (…)` (`runtimeError` in JSON) and the command still
succeeds. `list` and `show` remain saved metadata only. A status response is a
timestamped observation; `sessions watch` is the continuous view.

```bash cli-help="sessions start"
dl sessions start SESSION_ID --namespace geyang --json
```

When tmux is available, `start` explicitly starts the agent in detached, managed
tmux, keeps an already
running process, or resumes the saved conversation after an owned pane exits.
Unlike `resume --json`, **`start --json` can execute** a persistent process; JSON
does not suppress that action. With CLI 0.81.0+ and direct-mode gateway support,
a missing tmux instead returns `kind: direct`, `status: ready`, and
`executed: false`. This is a dependency preflight, not a running process. Use
`open` to connect and launch it. Managed tmux attachment cannot create another
process; an authorized direct ticket starts its foreground process on connection.
If Codex exits immediately, `start` reports its observed state and exits nonzero;
`open` declines the attachment. Use `status` to inspect the retained pane state.

```bash cli-help="sessions reconnect"
dl sessions reconnect SESSION_ID --namespace geyang
```

`reconnect` requires a terminal and attaches only to an existing live runtime.
It fails if that runtime has ended; it never starts or restarts Codex. Ctrl-]
detaches while keeping the process running. If a start or stop request loses
its response, inspect `status` before retrying.

```bash cli-help="sessions stop"
dl sessions stop SESSION_ID --namespace geyang --yes --json
```

`stop` ends the managed remote program and disconnects all its viewers. It first
reads fresh status and submits the exact generation and pane identity; a changed
runtime is rejected instead of stopping its replacement. An absent runtime is
already stopped. Closing a browser tab or pressing Ctrl-] only detaches; neither
operation is `stop` for tmux. In direct mode, disconnection may end the process
and managed `stop` is unavailable. The saved descriptor and Codex conversation remain, and a
later explicit `start` or `open` can resume them.

Older, unmarked tmux sessions report `legacy`. A live legacy session can still
be attached without replacing it, but cannot be stopped or restarted through
managed lifecycle commands because ownership is unverified. Older gateways report
missing tmux as `dependency_missing`; direct-capable gateways negotiate direct
readiness on `start` instead. Missing agent executables still block opening.
These commands install no packages
and adopt no unrelated process. Unavailable hosts are reported separately from
absent runtimes.

## Discover sessions created directly in Codex (0.75.0+)

Saving a session and discovering one on a machine are separate operations.
`list` reads the registry; it cannot see a conversation that has not been saved.
Use explicit `sync` to discover and register recent conversations without opening
a terminal or sending any input to Codex:

```bash cli-help="sessions sync"
dl sessions sync --namespace geyang --target TARGET_ID --json
dl sessions sync --namespace geyang --all --json
```

Choose exactly one `--target` or `--all`. One invocation reads at most one page
of 25 candidates per selected enrolled machine, with at most two machines in
flight. It queries the selected Unix user's default `~/.codex` SQLite index for
unarchived root conversations updated within seven days. It excludes subagents,
reads no transcripts, and does not recursively scan files. Python 3 must already
exist on the machine; missing Python, missing indexes, unsupported schemas, and
unavailable hosts are reported separately. Custom `CODEX_HOME` directories are
not scanned.

Repeated syncs reuse saved descriptors and preserve existing human names. New
rows receive the discovered title through `nameIfNew`. Actual Git/activity
observations are updated only when collected within the bounded probe; newer
saved observations are preserved. The command reports partial saves if an
operation fails, and never deletes registry rows or installs dependencies.
`sync --json` still performs metadata discovery and registration.
Discovery also reports skipped candidates (for example, missing directories or
rollout files) and omitted Git observations. Activity is available from the index
even when Git probing is omitted, but that candidate's complete registry metadata
remains prior or unknown until a full observation can be saved. Partial results
must not be treated as a complete machine inventory.

For additional results, pass that target's returned `nextCursor` to
`sync --target TARGET_ID --cursor CURSOR`. Discovery cursors expire after ten
minutes and retain the original seven-day snapshot; begin a new explicit sync
to see conversations created since then. Metadata observations may be reused
for fifteen seconds, with authorization checked on every request. Registry
refresh, search, and listing never trigger discovery.

The matching registry supports bounded pagination and saved-metadata filtering:

```bash
dl sessions list --namespace geyang --sort recent --page-size 50 --json
dl sessions list --namespace geyang --sort recent --page-size 50 --cursor CURSOR --json
dl sessions list --namespace geyang --query workspace --machine MACHINE_ID --json
```

Registry and discovery cursors are different. Continue registry pages with the
same filters and sort; recent ordering uses observed activity, not registration
time. These options and `sync` require CLI **0.75.0 or later** and the matching
registry/discovery gateway, and are unavailable in CLI 0.74.3 and earlier.

## Custom deployments

For the production API, terminal requests use `https://term.dreamlake.ai` with
the allowed origin `https://dreamlake.ai`. A custom API environment requires both
`--gateway` and `--origin` for `targets`, `open`, interactive `resume`, and
managed `status`, `start`, `reconnect`, `stop`, or `sync`, and
for `create` or `resume --json` when discovering an omitted enrollment. They
must identify a trusted gateway and its configured allowed web origin. Custom
environment tokens are never sent to the production gateway implicitly.

```bash
dl sessions targets --namespace alice \
  --gateway https://terminal.example.com --origin https://app.example.com
dl sessions open SESSION_ID --namespace alice \
  --gateway https://terminal.example.com --origin https://app.example.com
```

Endpoints must be HTTPS origins; HTTP is accepted only on loopback for local
development. Redirects are refused. Tickets travel in the initial WebSocket
message, never the URL or command output. No local scientific workload, direct
SSH alternative, shell command evaluation, or ambient credential substitution
is used by these commands.

## Optional conversation upload (0.79.0+)

CLI 0.79.0 adds conversation archives to the session affiliations introduced in
0.78.0. The matching conversation API is required.

Select an exact export to upload its readable conversation text:

```bash cli-help="sessions upload-conversation"
dl sessions upload-conversation SESSION_ID --namespace geyang \
  --file /absolute/path/to/conversation.jsonl --json
```

The file can be a native Codex rollout, Claude Code JSONL export, or version 1
DreamLake conversation JSON. Its native session identity must match the saved
session. User/assistant text and tool calls/results are included; binary images,
attachments and private reasoning blocks are not imported. No home-directory
scan or credential/configuration upload occurs. Review the selected file: its
text becomes readable to people who can already read that saved session.

For an opted-in workflow, set `DREAMLAKE_CONVERSATION_FILE` to that exact export
path. Successful memo and artifact writes then affiliate the session and upload
its conversation snapshot. `DREAMLAKE_SESSION_AFFILIATION=0` disables both automatic
operations. Without the file setting, uploads remain metadata-only. This does not
extend auto-affiliation to resource kinds beyond memos and artifacts.

The automatic path retains its combined three-second deadline and no retry;
archive or metadata failures warn while preserving successful content writes.
Retry only `sessions upload-conversation` or `sessions link`, never the original
content upload. Standalone archive uploads have normal bounded API deadlines and
require owner access. Concurrent replacements fail with a revision conflict.

Exports are limited to 32 MiB input and 8 MiB normalized conversation, with at most
20,000 messages. Oversized or mismatched files are rejected without truncation.
A new upload replaces the snapshot; there is no background transcript watcher.
Memo and artifact operations continue normally if metadata is missing or wrong.

The Memo activity panel shows contributing sessions before related resources.
Select a Codex or Claude row to open its saved terminal in the panel to the right.
No conversation upload is required; reading uploaded history is a separate action.
The gateway uses the supported persistent or direct terminal runtime and rechecks
execution authority. If the saved descriptor has no verified host binding, the
terminal panel explains the missing connection; **Check connection again** reloads that
descriptor without selecting a host or uploading content.

An archive remains readable without a live host, but cannot recreate missing
native Codex/Claude state or move a conversation between hosts. Resource links
and transcript text never select a new execution target or grant terminal
permission. Standalone Sessions conversation reading remains available.

## Optional resource activity context (0.79.0+)

Resource activity attribution is separate from managed Terminal sessions. On a
server supporting the resource activity API, CLI reads/edits of Memos, Repo
records and InfraStack state can carry a conversation identity:

```bash
export DREAMLAKE_SESSION_PROVIDER=codex
export DREAMLAKE_SESSION_ID=YOUR_CONVERSATION_ID
export DREAMLAKE_SESSION_NAME="Launch API work"
```

When no explicit ID is supplied, `CODEX_THREAD_ID` supplies Codex context if
present. Missing or malformed optional context is ignored; it cannot block a
memo read or save. Legacy `DREAMLAKE_AGENT_ID` still supplies Memos presence and
agent attribution. Session context does not change permissions or create a
managed terminal session, and it is sent only to supported resource routes.
This capability requires the companion resource activity backend release.

## Command aliases and search (0.114.0+)

`dl sessions`, `dl session`, and `dl sess` are interchangeable. Commands that
accept `--session` also accept `--sess`, including registration, creation,
heartbeat/events, watching, and command filtering or broadcast. The identifier
retains its existing meaning: native UUID for register/create, saved session ID
for watch/control. Aliases do not change permissions or launch behavior.

```bash cli-help="sessions search"
dl sess search "tmux"
dl session search "release" --machine MACHINE_ID --sort recent
dl sess search "release" --search-in title
dl sessions search "RTC" --owner geyang --page-size 25 --json
```

`search "query"` is the explicit form of `list --query "query"`. It accepts the
same namespace, scope, owner/team, machine, sort, archive, and pagination filters.
Continue with the returned `--cursor` and the same query and filters. Searching
never starts, resumes, or attaches to a session and does not scan remote files.
The existing `dl sessions --query "query"` form remains supported.

Use `--search-in title` to search session titles only, or `--search-in all` for
metadata and uploaded conversation text (the default). The TypeScript SDK accepts
`sessions(namespace).list({ q: "release", searchIn: "title" })`; `available()`
accepts the same search fields alongside owner/team filters. Keep `searchIn`
unchanged when continuing with a cursor. Title-only search requires the companion
API release.

List/search and metadata reads preserve the session's provider/native ID and
host/enrollment/machine/user binding. `runStateObservedAt` and
`metadataObservedAt` date the observations; `lastActivityAt` dates activity.
When current state becomes unknown, `lastRunState` preserves the last observation
and `attention` retains `needs_input` or `error` until a newer observation clears
it. CLI text output shows that attention alongside the last observed state;
JSON and the TypeScript SDK retain the fields. These fields do not report the
health of the local collector. Watch backlog and retry diagnostics remain Nymph
log events.

## Codex root binding (0.115.0+)

With CLI/TypeScript **0.115.0+** and the companion API root-binding release,
Codex descriptors may include
`codexHome`, the canonical absolute state directory on the enrolled host. The
TypeScript SDK exposes it on `Session` and accepts it in `terminal(namespace).create()`.
The saved session and its launch descriptor must name the same root; reopening
that session preserves it. The host checks that the root belongs to the enrolled
Unix user. A missing root keeps legacy behavior. It does not select another host
or user, and the CLI does not substitute its local `CODEX_HOME`. Root selection
does not add a CLI flag or change terminal interaction.

## Search scope and access

Session list/search defaults to your personal namespace. Scope never widens
merely because a query has no matches. Explicit examples:

```bash
dl sessions list --query RTC
dl sessions list --owner geyang --query RTC
dl sessions list --team fortyfive --query RTC
dl sessions list --scope available --query RTC
```

`--scope mine` cannot combine with `--owner` or `--team`. Owner is an exact personal
namespace; team is the organization slug/id used by session sharing. A team
filter selects sessions explicitly shared with that organization, not every
member's private conversations. Available scope includes your sessions and
sessions you are currently allowed to read. Metadata and uploaded redacted
human conversation text are searchable; unsynced machine transcripts are not.
The TypeScript `sessions(namespace).available({ owner, team, q })` uses the same
filters. A named person/team grants no access; revoked membership applies on
the next request. Built-in agent chats remain owner-only. Public Codex/Claude
sessions can be read anonymously; current registration defaults new records to
public unless explicitly private. Search does not change that visibility or
grant permission to message or execute a session.

Broad available transcript searches return `terminal_search_scope_too_large` above 64
owner/namespace groups or 256 owner/team policy-check units (at most 768 policy database calls). Narrow the request
with `--owner` or `--team`; the server never silently drops owners. Anonymous
searches without an explicit owner match metadata only. Team slugs accept `@` prefixes.
Historical built-in agent conversations are indexed on their next turn.

The deterministic scope limit returns HTTP 422; narrow the query instead of
retrying it. Listings with no keyword keep their existing pagination and do not
enumerate all owner groups.
