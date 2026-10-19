# Terminal sessions

CLI **0.74.1 or later** provides `dreamlake sessions`, which shares saved terminal
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
dreamlake sessions visibility <saved-id> --namespace <personal-namespace> --visibility private
```

Register a native Codex/Claude UUID without a host, gateway, or terminal process:

```bash cli-help="sessions register"
dreamlake sessions register --provider codex --session <native-uuid> --cwd /absolute/repository --json
# Explicit private override for a new registration:
dreamlake sessions register --provider claude --session <native-uuid> --cwd /absolute/repository --visibility private --json
```

This returns a **saved descriptor ID**, distinct from the native UUID. Registration
is idempotent for the personal owner/provider/native ID. It reuses an unambiguous
existing registration; conflicting saved identities require explicit selection.
A metadata-only session has `archiveOnly: true`, null `launch`, and no host
binding. It can be linked and read but cannot open a terminal. A later verified
host registration with the same owner/provider/UUID and exact cwd can bind the
same descriptor, preserving privacy and resource links.

CLI 0.82.0+ automatically registers metadata after an acknowledged Note/artifact
content write when `CODEX_THREAD_ID` or `CLAUDE_SESSION_ID` supplies an exact native
UUID. Set `DREAMLAKE_SESSION_VISIBILITY=private` for a private new registration,
or `DREAMLAKE_SESSION_AFFILIATION=0` to disable affiliation. Explicit saved context
uses `DREAMLAKE_TERMINAL_SESSION_ID` with `DREAMLAKE_SESSION_NAMESPACE`.
No transcript is uploaded unless an export is explicitly selected.

If the CLI says **Content saved; optional session metadata was not fully recorded**,
do not repeat the content write. Retry `sessions register`, then `sessions link`
using the returned saved ID; retry `upload-conversation` separately if needed.
`terminal_access_denied` from `sessions targets` is an execution/discovery authority
failure, not evidence that the Note save failed. Metadata registration does not
need target discovery. Do not change enrollment credentials to repair attribution.

Conversation upload redacts recognized credential assignments, authorization
headers, common provider tokens, JWTs, private keys and signed URL parameters in
all message roles. The API repeats redaction and sanitizes historical archive
reads, including archives made public later. Pattern detection cannot recognize
every arbitrary secret: review a selected export and remove custom secrets before
publishing. Private reasoning and binary attachments are omitted by native import.

Public session unlock icons appear on hover or keyboard focus. Private sessions
keep an orange lock visible in lists, details and session navigation.

## Claude Code and observed states

Provider-aware clients also list and open Claude Code sessions registered by a
compatible machine collector. Use `--provider claude --session <uuid>` when
saving one explicitly, and `--claude-config-dir <absolute-path>` if it uses a
custom Claude configuration root. `--codex-session` remains the Codex-compatible
UUID option. The default provider is Codex.

```bash
dreamlake sessions create --provider claude --session <uuid> --target <target-id> --cwd /absolute/repository --namespace geyang
```

The descriptor reports the agent tool separately from `modelProvider`. Its
`runState` and `runStateObservedAt` describe the latest machine observation;
stale observations become `unknown`. `running` confirms a matching process,
not active model work. Supported native Codex daemons additionally report
`working`, `waiting`, `idle`, or `error` through metadata-only status reads. Listing does not open terminals or SSH-poll each row.
Use `sessions status` for the selected managed terminal's current lifecycle.
Claude resumes with its existing permissions and login; the CLI adds no bypass.
These additions require matching provider-aware API, gateway and collector releases.

## Link notes and artifacts (0.78.0+)

With the matching resource-session API deployed, a saved session can be linked
to multiple notes and artifacts, including resources in another namespace.
Linking requires resource write access and session read access. Every list checks
both permissions again; sharing a resource does not share its terminal.

```bash cli-help="sessions link"
dreamlake sessions link SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --note NOTE_ID --json
dreamlake sessions link SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --artifact loss-plot --json
```

```bash cli-help="sessions unlink"
dreamlake sessions unlink SESSION_ID --namespace geyang \
  --resource-namespace fortyfive --artifact loss-plot --json
```

```bash cli-help="sessions resources"
dreamlake sessions resources SESSION_ID --namespace geyang --page-size 25 --json
```

`resources` returns bounded pages (maximum 50); continue with its `nextCursor`.
These commands only change or read affiliations. They never open, start or stop
terminals and never modify note or artifact content.

Successful note creation/body/section writes and artifact pushes automatically
link a known session context. Set `DREAMLAKE_TERMINAL_SESSION_ID` and
`DREAMLAKE_SESSION_NAMESPACE` to select an exact saved session. Otherwise the CLI
uses `CODEX_THREAD_ID` or explicitly supplied `CLAUDE_SESSION_ID`, only when one
exact owned registered session matches. Arbitrary `DREAMLAKE_AGENT_ID` presence
labels, similar titles and directories are not native session identities.

Automatic affiliation makes at most one bounded catalog lookup and one
idempotent metadata write, with a three-second combined deadline and no retry.
Repeated successful links are deduplicated briefly within the CLI process.
Ordinary reads and failed content writes add no affiliation requests. Missing or
ambiguous registration produces a warning without changing the content command's
successful result; retry only the link with `sessions link`, not the upload/edit.
Set `DREAMLAKE_SESSION_AFFILIATION=0` to disable automatic affiliation. Historical
resources require exact evidence or an explicit link; they are not assigned by
guessing authorship.

## Select the host

Authenticate with your intended personal account and select the environment.
Machine identity cannot open personal terminal sessions; use `--identity user`
explicitly when a machine identity is configured. Target discovery uses the same
existing enrolled-host terminal access as the web page; it creates no machines,
enrollments, or permissions.

```bash cli-help="sessions"
dreamlake sessions targets --namespace geyang
dreamlake sessions list --namespace geyang
```

```bash cli-help="sessions targets"
dreamlake sessions targets --namespace geyang --json
```

Choose `--target` from the returned inventory. Its exact enrollment is discovered
automatically; no first-target default is used. Optionally pin `--enrollment` from
that same row; the gateway verifies the binding when opening. A target with no enrollment ID cannot
be saved as a session. Re-enrollment does not silently retarget saved sessions.

## Resume from the command line

This is the terminal equivalent of selecting a saved session in the web page:

```bash cli-help="sessions resume"
dreamlake sessions resume 01a13cbc-d4a7-7893-81cc-39696769c454 \
  --namespace geyang --target TARGET_ID \
  --cwd /home/ubuntu/workspace-3
```

It saves or finds the matching descriptor, obtains a short-lived gateway ticket,
and attaches an interactive terminal. On the **selected remote host**, the gateway
negotiates the available runtime. With tmux, it starts `codex resume` in the
requested directory under a deterministic tmux session, or attaches to that same
session if it exists. Repeated persistent opens share the same process; existing
agent processes outside that managed session are not adopted.

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
dreamlake sessions create --namespace geyang \
  --target TARGET_ID \
  --cwd /home/ubuntu/workspace-3 \
  --codex-session 01a13cbc-d4a7-7893-81cc-39696769c454 \
  --name 'Workspace 3' --json
```

`create` never starts a remote process. Save the returned `session.id`; identical
target/enrollment, working directory, and conversation inputs resolve to the
existing descriptor. A successful registration alone is not execution proof.

```bash cli-help="sessions list"
dreamlake sessions list --namespace geyang --json
```

```bash cli-help="sessions show"
dreamlake sessions show SESSION_ID --namespace geyang --json
```

```bash cli-help="sessions open"
dreamlake sessions open SESSION_ID --namespace geyang
```

`list` and `show` read saved metadata, not live process state. The terminal service
rechecks authorization and the enrollment binding when opening. `open` does not
accept `--json` because it is interactive.

## Managed runtime lifecycle (0.75.0+)

The following commands require CLI **0.75.0 or later** and the matching
managed-session gateway. CLI 0.74.3 and earlier do not provide them.

```bash cli-help="sessions status"
dreamlake sessions status SESSION_ID --namespace geyang --json
```

`status` performs a bounded observation on the exact enrolled host. It reports
the tmux runtime, pane identity, viewer count, and dependencies; it does not
start Codex or read terminal contents. `list` and `show` remain saved metadata
only. A status response is a timestamped observation, not continuous monitoring.

```bash cli-help="sessions start"
dreamlake sessions start SESSION_ID --namespace geyang --json
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
dreamlake sessions reconnect SESSION_ID --namespace geyang
```

`reconnect` requires a terminal and attaches only to an existing live runtime.
It fails if that runtime has ended; it never starts or restarts Codex. Ctrl-]
detaches while keeping the process running. If a start or stop request loses
its response, inspect `status` before retrying.

```bash cli-help="sessions stop"
dreamlake sessions stop SESSION_ID --namespace geyang --yes --json
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
dreamlake sessions sync --namespace geyang --target TARGET_ID --json
dreamlake sessions sync --namespace geyang --all --json
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
dreamlake sessions list --namespace geyang --sort recent --page-size 50 --json
dreamlake sessions list --namespace geyang --sort recent --page-size 50 --cursor CURSOR --json
dreamlake sessions list --namespace geyang --query workspace --machine MACHINE_ID --json
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
dreamlake sessions targets --namespace alice \
  --gateway https://terminal.example.com --origin https://app.example.com
dreamlake sessions open SESSION_ID --namespace alice \
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
dreamlake sessions upload-conversation SESSION_ID --namespace geyang \
  --file /absolute/path/to/conversation.jsonl --json
```

The file can be a native Codex rollout, Claude Code JSONL export, or version 1
DreamLake conversation JSON. Its native session identity must match the saved
session. User/assistant text and tool calls/results are included; binary images,
attachments and private reasoning blocks are not imported. No home-directory
scan or credential/configuration upload occurs. Review the selected file: its
text becomes readable to people who can already read that saved session.

For an opted-in workflow, set `DREAMLAKE_CONVERSATION_FILE` to that exact export
path. Successful note and artifact writes then affiliate the session and upload
its conversation snapshot. `DREAMLAKE_SESSION_AFFILIATION=0` disables both automatic
operations. Without the file setting, uploads remain metadata-only. This does not
extend auto-affiliation to resource kinds beyond notes and artifacts.

The automatic path retains its combined three-second deadline and no retry;
archive or metadata failures warn while preserving successful content writes.
Retry only `sessions upload-conversation` or `sessions link`, never the original
content upload. Standalone archive uploads have normal bounded API deadlines and
require owner access. Concurrent replacements fail with a revision conflict.

Exports are limited to 32 MiB input and 8 MiB normalized conversation, with at most
20,000 messages. Oversized or mismatched files are rejected without truncation.
A new upload replaces the snapshot; there is no background transcript watcher.
Note and artifact operations continue normally if metadata is missing or wrong.

The Note activity panel shows contributing sessions before related resources.
Select one to read its uploaded history, then choose **Continue this conversation
here** to open its saved terminal to the right. The gateway uses the existing
managed tmux integration and rechecks execution authority. An archive remains
readable without a live host, but cannot recreate missing native Codex/Claude
state or move a conversation between hosts. Resource links and transcript text
never select a new execution target or grant terminal permission.

## Optional resource activity context (0.79.0+)

Resource activity attribution is separate from managed Terminal sessions. On a
server supporting the resource activity API, CLI reads/edits of Notes, Repo
records and InfraStack state can carry a conversation identity:

```bash
export DREAMLAKE_SESSION_PROVIDER=codex
export DREAMLAKE_SESSION_ID=YOUR_CONVERSATION_ID
export DREAMLAKE_SESSION_NAME="Launch API work"
```

When no explicit ID is supplied, `CODEX_THREAD_ID` supplies Codex context if
present. Missing or malformed optional context is ignored; it cannot block a
note read or save. Legacy `DREAMLAKE_AGENT_ID` still supplies Notes presence and
agent attribution. Session context does not change permissions or create a
managed terminal session, and it is sent only to supported resource routes.
This capability requires the companion resource activity backend release.
