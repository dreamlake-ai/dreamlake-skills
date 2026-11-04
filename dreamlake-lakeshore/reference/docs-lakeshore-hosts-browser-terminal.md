<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/browser-terminal.md at 0.1.113 a89f9340; do not edit -->

# Browser terminal

Compute can open an interactive SSH terminal on a machine you own and have
enrolled. Open **Compute**, select the machine, choose **Terminal**
(`/:namespace/compute?view=terminal`), then **Connect**. The terminal runs as
the enrolled Unix user. Keys stay on the server, and the browser never sends a
host address or a key.

A machine is listed only when its daemon is online, reports native SSH
support, and is bound to your personal namespace enrollment. Organization
namespaces are not supported yet.

## Connection command

The terminal button in the session header (**Connection command**) selects
the program a new session starts with:

| Option | What runs | On disconnect |
|---|---|---|
| **tmux** (default, session `web-ssh`) | `tmux new-session -A -s web-ssh`: attaches to the session, or creates it | tmux keeps running. Reconnect to return to the same windows and processes. |
| **Login shell** | Your account's login shell | The shell ends. Reconnecting starts a new one. |
| **Custom** | One single-line command, run by your account's shell with a terminal | The session ends when the command exits. |

You can change the tmux session name, for example to keep separate `train`
and `debug` sessions. Names use 1–64 letters, digits, hyphens or underscores.
tmux is found through your login shell's `PATH`, so installs that your
login profile adds to `PATH` (such as Homebrew) work. When tmux is not installed, the session prints
`tmux was not found; starting a login shell.` and opens your login shell.

Choose **All machines** to set the default, or **This machine** to override it
for one machine and Unix user. **Use default** removes a machine's override.
Settings are saved in the current browser and apply the next time you connect.
They never change an open session.

Compute actions that type a prepared command (such as the
[Cartpole demo](https://docs.dreamlake.ai/lakeshore/hosts/native-cartpole-demo)) always use a fresh login
shell. Their input never goes into a reattached tmux session.

Custom commands are limited to 4096 bytes on one line. For example,
`tmux new-session -A -s web-ssh -c ~/project` or `htop`. The gateway rejects
newlines and control characters.

## Saved agent sessions

**Provider discovery requirements:** Claude discovery and observed
run states require **Nymph 0.1.31+**, **DreamLake CLI 0.77.0+** for the new CLI
flags, and the matching provider-aware API, gateway and interface. Installing a
client or reading updated documentation does not upgrade those other components.
Compatible machine collectors discover Claude Code sessions across their configured project
roots when session discovery is enabled (see below). The registry contains session UUID, working/config directory, explicit
title, repository, provider and observed runtime metadata; conversation bodies
remain on the machine. Claude resumes with `claude --resume SESSION_UUID` in its saved
working directory and configuration root. Codex UUIDs and saved links remain
compatible. Both use the existing private-by-default/team-sharing controls.

Claude bookmarks are identified by their enrolled machine, Unix user, conversation
UUID and configuration root. Later working-directory observations do not create
another bookmark or move its saved launch directory. `observedCwd` records the
newer metadata while the saved ID, launch directory and tmux binding stay fixed.
Saving the same conversation with another launch directory returns
`terminal_session_launch_cwd_conflict` with its existing saved ID; open that saved
session instead. Existing Codex IDs and launch bindings keep their original rules.

Owner-selected reconciliation of a verified discovery cohort can hide private
automatically named duplicates from lists
while keeping their old saved IDs usable. It preserves human names, team shares
and execution bindings, and copies newer observations to the retained bookmark.
Explicit owner renaming or sharing restores a hidden bookmark to the list.

The agent tool (Codex or Claude Code) is separate from the model provider
(OpenAI, Anthropic, DeepSeek, MiniMax, and others). Provider logos use reported
metadata. An unidentified model provider remains unidentified.

Run state is an observation, not inferred from recent edits. `running` means a
matching process was observed; `working` and `waiting` require explicit runtime
signals. Supported Codex daemons provide these through metadata-only native
status reads, plus `idle` and `error`. `stopped` requires confirmed termination. Observations older than
45 seconds become `unknown`; opening the catalog does not start a session or
SSH-poll every row. Existing managed terminal controls still report their own
current lifecycle and dependency errors.

For Claude, discovery covers the enrolled user's default `~/.claude`, inherited
`CLAUDE_CONFIG_DIR` and explicitly configured `claude_config_dirs`. Same-user
project roots and top-level UUID files are indexed; symlinks and subagent trees
are excluded. Explicit titles, summaries, directories and recognized provider
metadata may be retained. First prompts and conversation/tool content are never
used as display titles or uploaded. Saved custom configuration roots are used
again when resuming that session.

Existing Claude history is indexed gradually without an age cutoff. Each
two-second tick has a bounded directory and byte budget; unchanged acknowledged
metadata is cached across daemon restarts. New/changed files receive priority,
and bounded reconciliation recovers missed filesystem notifications. Large
histories can take time to populate; refresh never starts an unbounded host scan.

Codex native states come only from an already-running same-user app-server
control socket on a supported stable daemon version (0.162.1 or newer). Older,
custom or unavailable daemons remain unknown unless exact process evidence is
available. Discovery does not start a daemon or read transcripts as a fallback.
Known states heartbeat every 30 seconds; API observations expire after 45
seconds. `unknown` is an honest absence of current evidence, not a stopped claim.

Use **Sessions** in the main left sidebar for your saved sessions, including
while browsing an organization. In Notes, the session-library tab at the left of
the chat tab row opens a picker without moving the note editor. Its available
list includes your sessions and sessions shared with a team you belong to. The dedicated `/:namespace/sessions`
page saves a machine, its enrolled Unix user, an absolute working directory and
an agent conversation UUID. Click a saved session to open it immediately in the
browser terminal. A session link selects its saved configuration; visiting or
refreshing the link alone executes no command.

Opening a saved session adds a closable terminal tab. Use **+** in the terminal
tab strip to choose another saved session. Choosing an already-open session
focuses its existing tab. Switching tabs keeps their terminal connections open;
closing a tab detaches that viewer while the agent keeps running on the host.
Refreshing still only selects the saved session in the link; click to reconnect.

With focus on a session row, **Up/Down** moves through visible entries and
scrolls the focused row into view. It does not open or start a terminal. Press
**Enter** to activate the focused entry. Search fields and editors retain their
normal caret behavior.

Use the controls beside search to choose a view of the same saved sessions:

- **Machine** groups sessions by their enrolled machine. Each row keeps its
  machine and Unix user visible.
- **Recent** shows one flat list, newest observed conversation activity first.
  The time comes from the exact Codex conversation's activity metadata on its
  machine. Sessions without that observation show **Activity unknown** at the
  end; their registration time is never substituted.
- **Repo** groups sessions by the actual Git repository resolved on their
  machine. A verified, sanitized remote identity can join the same repository
  across machines. Repositories without a safe remote stay grouped by their
  machine, Unix user and actual Git root. **No Git repository** means the
  directory was checked and is not in a repository; **Repository unknown** means
  the repository has not been observed or could not be resolved. The saved
  working directory alone never becomes a repository group.

Search filters session names, machines, working directories and observed
repository information. Use **×** to clear the query. Choosing machine
suggestions adds removable filters; multiple chosen machines match with OR.
Project and Bindr suggestions navigate to those items and do not imply a
session belongs to them. The **Recent** control is labeled, and group expansion
controls show expand/collapse hints. Switching a view or searching does not
connect to a machine.

**Refresh** reloads saved entries and their observations. **Discover sessions**
explicitly reads the selected enrolled machine's recent Codex metadata and lets
you save discovered sessions. Further pages and partial or unavailable results
remain visible; an incomplete discovery is not a complete machine inventory.
Repository and activity values are timestamped observations, not live process
status. Opening a session does not itself refresh those observations from the
machine. Compatible nymph daemons with session discovery enabled also register
new local sessions automatically, as described below.

When you reopen a session in the same browser tab, its last visible screen can
appear while the terminal connects. This read-only preview is marked as previous
output and is replaced by live terminal output. It is not a connection status or
proof that the remote process is still running. The browser keeps a bounded,
temporary plain-text screen cache for the signed-in account and exact saved
binding. Signing out, changing authentication or losing access clears the
preview. The cache stays in the browser tab; it is not sent to DreamLake or
included in saved session metadata.

For example, select the machine that already owns the conversation, enter
`/home/ubuntu/workspace-3` and `01a13cbc-d4a7-7893-81cc-39696769c454`. Opening runs
`codex resume 01a13cbc-d4a7-7893-81cc-39696769c454 -C /home/ubuntu/workspace-3`
inside a stable tmux session when tmux is available. Reopening that configuration
attaches to the running process. Closing its browser viewer detaches from it.

The machine needs its selected provider (Codex or Claude Code), the saved
conversation and the usual provider login. Authentication and workspace trust
prompts remain interactive. With the matching direct-runtime gateway and client,
an owner opening a session on a machine without tmux uses a **direct foreground
terminal**. No package installation is required. Direct mode may stop on disconnect;
it has no detached process, managed Stop action or shared attachment. Reopening is
an explicit new foreground resume, never an automatic reconnect loop. A host reboot
or exiting the provider ends its process; opening again
resumes the conversation in a new process. Bookmarks persist in DreamLake, while
Codex history and running processes stay on the selected machine and Unix account.
Changing machines does not transfer either one.

Saved sessions require matching product API and terminal gateway deployments
with Codex launch support, plus the Sessions page. CLI **0.74.1 or later** uses
the same saved descriptors through the companion
[`dreamlake sessions` commands](https://cli.dreamlake.ai/sessions).
Updating the CLI does not deploy those server capabilities. Existing terminal
access and connection limits below still apply.

### Share a session with a team

Sessions are private by default. The owner can change **Private** to **Team**
and choose one organization they belong to. The interface names that team;
this setting does not publish the session to the internet or every organization
on the account. Both the owner and teammate must remain active members of the
selected team.

Team access is interactive: teammates can see terminal output and type through
the owner's running session. Share only sessions intended for that team. Note
sharing does not grant session access, and session sharing does not grant note
access. Only the owner can change sharing or use the managed start/stop controls.
A teammate attaches to an existing runtime; if it is absent, the owner must open
it first. Closing any terminal tab disconnects only that viewer.

Changing back to **Private**, losing membership or revoking the machine enrollment
removes access. The gateway rechecks active connections and disconnects viewers
whose access has been revoked. Saved descriptors are resolved on the server;
the shared-session route does not accept arbitrary machines, directories or SSH
commands. Interactive terminal access still acts through the owner's session.

### Managed runtime

The managed lifecycle is available through the Sessions page and CLI **0.75.0
or later**, with the matching deployed terminal gateway. Updating an older CLI
alone does not deploy the gateway capability. Opening a saved session
explicitly starts its runtime if needed and then attaches. Reconnect attaches
only: it never starts a replacement process. Closing a tab still only detaches.
Status is refreshed on explicit actions, not by polling every row or hidden tab.

The gateway exposes authenticated, origin-checked `POST` endpoints at
`/namespaces/:namespace/terminal/sessions/:savedId/status`, `/start` and `/stop`.
Status accepts `{}`. Start accepts `{}` (automatic selection) or
`{ runtime: 'auto' | 'tmux' | 'direct' }`. Automatic selection prefers tmux, including
common user-local and Homebrew installations; otherwise it prepares direct mode
for the owner. An explicit tmux request never silently switches modes. Direct
preparation checks executable, directory and provider config without starting a
process. Stop requires the exact fresh observation's
`{ generation, paneId, panePid }`; it is an explicit process-ending operation,
not a way to close a viewer. No endpoint accepts a command, host address or key.
Each successful response is `{ runtime }` with:

| Field | Meaning |
| --- | --- |
| `sessionId`, `targetId`, `enrollmentId`, `tmuxSession` | Exact saved binding; `tmuxSession` is not an active tmux assertion in direct mode |
| `observedAt` | Timestamp of this machine observation |
| `kind`, `capabilities` | `tmux` or `direct`, with `{ persistent, canStop, canShare }`; all three are false for direct |
| `status` | `ready` (direct preflight only), `absent`, `running`, `exited`, `legacy`, `dependency_missing` or `unavailable` |
| `managed`, `generation` | Verified DreamLake ownership and runtime generation; generation is otherwise `null` |
| `pane` | `{ id, pid, dead, exitStatus }` for an observed pane, otherwise `null` |
| `clients` | Number of attached tmux viewers, or `null` when unknown |
| `dependencies` | `{ tmux, codex }`; `codex: null` means not checked during this action |
| `reason`, `created` | Optional fixed failure reason and whether start created or resumed this runtime |

New managed sessions retain an exited pane so its exit status can be observed.
Start can resume that same owned runtime with a new generation. Concurrent starts
do not duplicate Codex. Stop rechecks owner, generation, pane PID and the single
window/pane constraint atomically; a changed runtime returns `409 runtime_changed`
without retrying or killing the replacement. An already-absent runtime stays absent.

Preexisting unmarked tmux sessions appear as `legacy`. They remain attachable but
are never adopted, restarted or stopped by managed actions. A manual pane or
window change also prevents managed stop. Missing provider prerequisites are
reported explicitly. Status and Stop never start a direct session or install
packages. Direct mode never reports a fabricated pane, generation or running
process: these fields and clients are null, managed and created are false.
No mode changes global tmux settings or stops unrelated sessions.

An attach-only terminal ticket includes top-level `managedSessionId` alongside
the existing exact `targetId`, dimensions and Codex `launch`. The gateway resolves
that saved descriptor again and rejects mismatched machine, user, enrollment,
directory or conversation bindings. Legacy clients without this field keep their
existing launch behavior. Metadata operations use the same pinned SSH and owner
authorization as terminals, recheck authorization after the handshake, and return
no terminal contents, environment or raw shell errors.

A direct ticket adds top-level `runtime: 'direct'` and is owner-only. The gateway
rechecks the exact saved binding and owner access before releasing a one-use
stdin gate to start the provider inside its SSH PTY. It allows one direct viewer
per machine/user/directory/provider/native-session/config binding; another returns
`direct_session_in_use` until the previous SSH channel closes. Active sessions
continue the existing bounded access-renewal checks. Tickets without a runtime
field remain tmux attach-only for compatibility, including CLI `sessions reconnect`.
Use an explicit open/resume to start direct mode again. Direct mode requires the
matching gateway, browser client, or CLI 0.81.0+; updating a client alone does not
update the gateway. The runtime adapter contract leaves room for additional
persistent clients; screen is not implemented yet.

The existing viewer limits count attached connections, not running tmux sessions.
Managed metadata requests are separately bounded to two per account and eight
per gateway. A capacity response means retry the explicit action after an active
request completes; it is not a limit on saved bookmarks or detached processes.

### Discovering machine sessions and registry paging

**Since [Nymph 0.1.34](https://github.com/dreamlake-ai/nymph/releases/tag/v0.1.34):** session discovery is off unless the daemon configuration
sets `[sessions] enabled = true`. Configurations that omit the key stop
discovering sessions after upgrading. Nymph does not rewrite configuration
files, and an explicit `enabled = true` keeps discovery on. See
[host testing](https://docs.dreamlake.ai/lakeshore/hosts/testing) for the related job output setting.

With **nymph 0.1.29 or later**, session discovery enabled and the matching
product API on an enrolled machine, new local Codex
sessions are registered automatically from the local SQLite metadata index.
Nymph checks local index/WAL metadata every two seconds and sends bounded
incremental batches. Newly discovered session titles update as Codex fills them
in. Custom names, older saved names and sharing choices stay unchanged.
It never uploads conversation or terminal contents. Missing or locked indexes and upload failures leave existing
saved entries intact; retries are bounded. The visible session picker refreshes
the saved registry every five seconds without scanning remote machines; refresh
stops while hidden. Visibility follows these intervals and network latency, not
a guaranteed subsecond event.

Use **nymph 0.1.30 or later** for discovery diagnostics. Its service logs show
whether discovery started or was disabled. `enrollment_binding_unconfirmed`
means the daemon could not confirm the enrollment from the signed handshake;
it is not proof that the local session index is empty. Retry diagnostics show
only a reason, optional HTTP status and retry delay, at most once per minute,
plus a corresponding recovery event. They exclude session names, paths,
credentials and conversation contents. Upload backoff can reach five minutes
after repeated API failures; a recovered API does not reset an already-running
daemon's retry timer.

Nymph uses its configured Codex home, then inherited `CODEX_HOME`, then
`~/.codex`. For a custom home, the terminal user environment must use the same
`CODEX_HOME` to resume that conversation; saving metadata does not change the
terminal environment. Older conversations outside the recent seven-day window
can still be saved explicitly.

A session created in a normal local terminal cannot be moved into a browser
terminal. Opening its saved entry uses DreamLake's supported terminal runtime;
it does not capture or take over the original local TTY.

With the Codex native-writer guard deployed, a positive observation of a writable
handle to the exact conversation's local rollout file blocks creating or
restarting a managed process, or launching a new direct process, with
`native_session_active`. Continue in the existing Codex chat rather than retrying
automatically or terminating it to clear the error. An already-running managed
tmux session remains attachable without starting another writer.

This check reads file/process metadata, not conversation contents, and does not
stop the observed process. It applies to Codex only. Missing tools, unsupported
layouts, timeouts and inconclusive observations retain the previous behavior;
the absence of an error does **not** prove there is no other writer. The guard
does not provide an exclusive-writer lock or adopt native app sessions. CLI
0.84.1+ preserves the error and recovery guidance; older clients may show only
HTTP 409. Client updates alone do not deploy the gateway guard.

Older daemons still require explicit discovery and saving. That discovery reads the enrolled user's
default `~/.codex` SQLite index for recent, unarchived root conversations from
the last seven days. It excludes spawned agents and checks that the referenced
rollout is readable and belongs to that user's sessions directory. It never
reads rollout contents or starts Codex. Older conversations can still be saved
explicitly with their UUID and working directory.

`POST /namespaces/:namespace/terminal/discovery` on the terminal gateway accepts
`{ targetId, enrollmentId, cursor? }`. It returns `{ discovery }` with the exact
target and enrollment, `observedAt`, `status`, `candidates`, `nextCursor`,
`lookbackDays: 7`, `scope: "default_codex_home"`, `cached`, `skippedCount`,
`metadataOmittedCount` and `partial`. Each candidate has `codexSessionId`, `cwd`, `name`
and `lastActivityAt`, plus an optional repository/activity metadata observation.
Names prefer the index's saved name, then its title. Only sanitized Git remote
identities leave the machine. `skippedCount` reports unusable directory/rollout
references on that page. `metadataOmittedCount` reports candidates whose complete
Git observation could not fit the bounded read; their activity is still returned,
but the client must not pretend a complete observation was saved. `partial` is
true for non-OK status, another page, skipped candidates or omitted observations.

The gateway reads at most 25 index rows per page, caps output at 64 KiB and
allows at most two concurrent host reads. It uses a 15-second observation cache;
each response still rechecks the current owner and exact target binding. Cursors
are signed, bound to that owner/target and snapshot, and expire after ten minutes.
`python_missing`, `index_missing`, `unsupported_schema` and `unavailable` mean
discovery could not establish a complete inventory; they do not mean there are
zero sessions. No dependency is installed or repaired automatically.

Clients save selected candidates through the existing product API. Optional
`nameIfNew` supplies a newly imported bookmark's title while preserving an
existing user-chosen name. Metadata enrichment uses the guarded PATCH below.
Both actions save metadata only. Partial host failures must stay visible rather
than being reported as a successful complete scan.

`GET /namespaces/:namespace/terminal-sessions` now returns one page with
`sessions`, `hasMore` and `nextCursor`. `pageSize` defaults to 100 and may be
1–100; pass `cursor` for the next page. This is a response page size, not a
bookmark count limit. `sort=created` is the default; `sort=recent` orders known
activity first and leaves missing activity at the bottom. `q` searches saved
metadata; repeated `machineId` values restrict machines. Clients that also
match their displayed machine names can pass repeated `matchMachineId` values
alongside `q`. Change the search or sort by starting a new cursor sequence.

### Observed repository and activity metadata

Saved descriptors can also retain an observation of the actual Git root and
the conversation's last activity on its enrolled machine. A working directory
is not evidence of a Git repository, and bookmark creation is not conversation
activity. Unobserved or unavailable values remain explicitly unknown.

The owner-only `PATCH /namespaces/:namespace/terminal-sessions/:id/metadata`
accepts a complete observation. It preserves the bookmark name, execution binding
and running terminal. Supply `binding` with the observed descriptor's exact
`enrollmentId`, `machineId`, `username`, `cwd` and `codexSessionId`, plus:

| Field | Meaning |
| --- | --- |
| `repositoryStatus` | `git`, `not_repository` or `unavailable` |
| `repositoryRoot` | Actual absolute Git root, or `null` unless status is `git` |
| `repositoryIdentity` | Sanitized `git:host[:port]/path` identity, or `null` |
| `activityStatus` | `available` or `unavailable` |
| `lastActivityAt` | Exact conversation activity in UTC ISO format, or `null` when unavailable |
| `metadataObservedAt` | UTC ISO timestamp of the metadata observation |

Dates use millisecond precision, for example `2026-10-17T10:00:00.000Z`.
Repository identities contain no scheme, username, credentials, query or fragment;
the lowercase host and case-preserved path omit the final `.git` suffix. Path
segments use letters, digits, dots, underscores and hyphens. For a Git repository
without a safe remote identity, send `null`: the API derives a `local:` identity
scoped to the enrollment, machine, Unix user and actual Git root. Matching remote
identities can group repositories across machines; local identities cannot.

The API rechecks enrollment ownership and the exact saved binding. A changed
binding or an observation no newer than the stored one returns `409`; do not
retry an old observation with a fabricated newer timestamp. Explicit unavailable
observations clear the corresponding old values. These are caller-observed
metadata, not a server-side filesystem probe or ongoing synchronization. Never
upload raw Git remotes, terminal output, conversation content or credentials.
This endpoint requires the matching metadata-capable API deployment; older
deployments do not accept it. Existing bookmarks return null metadata until
observed, and saving/opening a bookmark does not automatically inspect a host.

## Limits

- At most two terminals per user and eight per gateway.
- A session closes after five minutes without input, output or resize, and
  always after thirty minutes. tmux and its processes keep running after
  either limit, and reconnecting returns to them.
- Access is checked again every few seconds. Revoking the enrollment or
  signing out closes the session.
- Terminal output goes only to your browser. DreamLake does not record, log or
  index it. Saved Codex sessions can retain the temporary browser-tab preview
  described above; live terminal scrollback is limited to 1000 lines.

## Troubleshooting

- **No terminal-enabled machines**: confirm the daemon is online with SSH
  enabled (`[ssh] enabled=true`) and that the enrollment belongs to your
  personal namespace.
- **Connection takes long or times out**: the gateway waits up to 30 seconds
  for the machine's daemon to start its SSH backend. Retry once. If it keeps
  failing, check the daemon on the machine.
- **Control plane busy**: when the Lakeshore control plane's SSH queue refuses
  the request before granting anything, the session request answers HTTP 503
  `controlplane_busy` with `Retry-After` (seconds), and the gateway retries on
  its own with a new key, within the same 30-second setup. If it still fails,
  try again later. HTTP 502 `controlplane_unavailable` means the outcome is
  unknown; it is never retried automatically.
- **Reconnect shows a different shell**: the connection command is set to
  **Login shell** or **Custom**. Switch to **tmux** to keep work across
  disconnects.
- **Detached processes**: anything you start outside tmux can stop when the
  session ends. Use tmux, or a tracked job, for long-running work.

## Resource affiliations

Saved sessions can be linked to notes and every artifact kind. The relation is
many-to-many metadata; it neither starts a terminal nor grants access. Current
resource and session permissions are checked on every request. Resource moves
keep the internal identity and require the new current namespace; reusable artifact
names do not inherit another catalog record's links. Exact old saved-session IDs
remain usable after listing-only Claude duplicate reconciliation.

- `GET /namespaces/NS/resources/TYPE/ID/sessions` lists readable linked sessions.
- `PUT /namespaces/NS/resources/TYPE/ID/sessions/SAVED_ID` links one exact session.
- `DELETE` on the same path unlinks it. Both writes require
  `{ "sessionNamespaceSlug": "SESSION_OWNER_NAMESPACE" }`.
- `GET /namespaces/SESSION_NS/terminal-sessions/SAVED_ID/resources` lists readable
  resources with `type`, `id`, `namespaceSlug`, `title`, and `canManageLinks`.

`TYPE` is `note` or `artifact`; `ID` is a note ID or an artifact's logical name.
Writes return `{ "linked": true, "sessionId": "SAVED_ID" }` (false for unlink)
and are idempotent. Both list directions return `hasMore` and `nextCursor`, accept
`pageSize` from 1 to 50 (default 25), and perform bounded indexed reads. The linked
session list accepts `q` for name, machine, directory and native UUID. Filtering
uses each bounded link page; an empty page with `hasMore` can have later matches.
No total-count or automatic all-catalog scan runs with the application.

## Search and read uploaded Claude conversations

Production verified 2026-10-19: API `4cf8a2e3`, UI `4243b42`. Owner-scoped
body keyword search, click-to-read history, deep-link reload and narrow-screen
wrapping were verified in the authenticated website. Existing upload limits and
reader authority are unchanged; Nymph and the backup collector are unchanged.

In Sessions, choose **Claude**, then search by a keyword in the session title,
metadata, or uploaded user/assistant messages in conversations you own. Shared
conversations remain searchable by metadata and readable under their existing
permissions; their body text never influences another viewer’s search pagination. Matching happens in the database
before the existing bounded pagination and keeps the selected provider and machine
filters. A session with no uploaded conversation can match metadata only. Tool and
system payloads are excluded from the body-search text. Search text is refreshed
atomically with each explicit conversation upload and cleared when it is deleted;
older uploads must be re-uploaded once to populate it. A verified empty snapshot
contains zero messages and is displayed as empty, not as a missing upload. Catalog responses never
include conversation text. No new search service or index is required.

In the standalone Sessions page, clicking a saved Claude session opens its
**Conversation** view without starting
or attaching to a terminal. Choose **Terminal** explicitly to use the existing
terminal workflow. A missing archive is shown as missing, not an empty conversation.
Reading works independently of host liveness; it does not fetch local transcripts
or trigger an upload. The S3 backup collector remains separate: a backup must be
explicitly imported/uploaded into the conversation API to be readable here.

## Optional conversation archives

The Note activity sidebar lists contributing saved sessions before collapsed related
resources. Affiliations can come from successful CLI content writes or explicit
links; a link is not an independently verified authorship claim. Reading a note
or mentioning another note does not invent a contributing session. Older notes
can have no recorded session history.

CLI 0.79.0+ `sessions upload-conversation` accepts an explicitly selected native
Codex/Claude export; `DREAMLAKE_CONVERSATION_FILE` opts successful Note and artifact
writes into snapshots. Without that setting, uploads carry session metadata only.
See [CLI session archives](https://cli.dreamlake.ai/sessions/#optional-conversation-upload-0790).

An explicit conversation upload stores readable text separately from the saved
terminal descriptor. The archive uses the session's existing reader permissions;
sharing a note never grants access to the archive or terminal. Only the session
owner can replace or delete an archive. Uploads never start a process. Archived
history remains readable when the host is offline or enrollment is revoked,
provided the saved session and account permissions remain valid.

The API at `/namespaces/NS/terminal-sessions/ID/conversation` supports:

- `GET`: current `conversation`, `revision`, and exact `provider` and
  `nativeSessionId`. A missing archive returns null content and revision.
  `?metadata=true` omits stored text and returns only its identity/revision.
- `PUT`: `{ conversation, expectedRevision }`. Supply the last read revision
  (null for first upload). Concurrent replacement returns 409; identical retries
  are idempotent. An archive cannot substitute a different provider or native ID.
- `DELETE`: remove only the uploaded archive, preserving the session and native
  conversation on its host.

Conversation version 1 contains `provider`, `nativeSessionId`, and `messages`
with `role` (`user`, `assistant`, `tool`, or `system`), `text`, and optional ISO
`timestamp`. Maximum 20,000 messages and 8 MiB of JSON; oversized uploads fail
without truncation. Catalog responses never include these bytes. The archive is
a snapshot, not live transcript synchronization or a portable provider resume
file. It does not restore missing native state on another host.

Clicking a saved Codex or Claude row in a Note's **Contributing sessions** opens
its terminal in the panel to the right. It does not open the archive first or
require an upload. Current host, enrollment and session execution authorization
still apply, using the supported persistent or direct terminal runtime. A
metadata-only registration without a verified host binding shows connection
guidance, its native session ID and working directory, and **Open Sessions** for
the owner. Connect the original machine and discover or register that exact
session, then use **Check connection again** to reload its saved descriptor.
Checking never selects a host or uploads conversation content. Read access to a public
session does not grant terminal execution.

Explicit conversation history remains readable as inert text, independently of
the terminal and host liveness. Missing archives do not disable terminal opening
or basic note editing. Session permissions remain separate from note permissions.

## SSH capacity and usage

**Release requirements:** usage reporting requires the coordinated November 4, 2026 control-plane, API, terminal-gateway and UI releases. Local capacity configuration requires **Nymph 0.1.35 or later**; numeric CLI quota errors require **CLI 0.103.1 or later**. Older deployments may still enforce 2 SSH sessions and 8 tunnels per worker, 32 combined per namespace, and local combined capacity of 10. Installing a skill or reading this page does not upgrade existing daemons. Check the actual usage response and installed daemon version; publishing a release does not restart enrolled hosts.

The new defaults are:

| Scope | Default limit | What consumes it |
|---|---:|---|
| Enrolled worker | 20 SSH sessions | Browser terminals, CLI SSH and exec connections through DreamLake |
| Enrolled worker | 8 forwarding tunnels | DreamLake forwarding connections; separate from the SSH-session quota |
| Control-plane namespace | 128 combined sessions | All SSH sessions and tunnels across every worker and user in that namespace |
| Nymph process | 28 combined sessions | Local SSH and tunnel tasks being served by that daemon |

The namespace total is a shared concurrent ceiling, not a per-user allowance, daily budget or lifetime count. Five workers with 20 SSH sessions each use 100 namespace slots, leaving 28 for other SSH sessions or tunnels. Multiple DreamLake workspaces can reference the same control-plane namespace; those connections share its ceiling. Multiple enrolled workers on one physical machine each have a worker quota; physical-machine capacity remains shared.

Pending, ready and active sessions reserve slots. Closed or expired sessions and pending/ready attempts past their connect deadline do not count toward new admission. A saved agent bookmark does not reserve a slot. A detached tmux session does not consume a DreamLake SSH slot after its viewer connection closes, although its processes still consume machine resources. Normal OpenSSH connections outside DreamLake do not consume this counter. OpenSSH's `MaxSessions` is a different setting for channels within a connection.

### Read usage

Open a host's details and select its enrolled Unix user. **SSH sessions**, **Forwarding tunnels**, and **Namespace total** show `used of limit in use`. Counts refresh every five seconds while the panel is mounted and on Refresh. They are observations, not reservations: another connection can claim the remaining slot before Connect is clicked. Offline, unauthorized, incompatible or unverified targets show unavailable rather than a fabricated zero. The panel does not create sessions while counting.

The authenticated API read is:

```text
GET /namespaces/:slug/hosts/:hostId/enrollments/:enrollmentId/ssh-usage
```

It requires namespace execution access and exact private host/enrollment ownership. The control-plane read is `GET /v1/namespaces/:ns/ssh-usage/:workerId`; it requires an admin or an active namespace token with an exact worker SSH grant. Session-delegated credentials cannot use this inventory endpoint. Responses contain counts only, with `Cache-Control: private, no-store`:

```json
{"sessions":{"used":3,"limit":20},"tunnels":{"used":1,"limit":8},"namespace":{"used":17,"limit":128}}
```

The namespace total is aggregate capacity, not disclosure of other hosts, owners or session identities. It may include users other than the current viewer. Admission calculates usage inside its existing fenced transaction; the read endpoint is a non-reserving snapshot and can change between its count queries.

### Configure capacity

The control-plane operator sets these environment variables on **every instance serving the same database**:

| Variable | Default | Valid values | Applies to |
|---|---:|---|---|
| `LAKESHORE_SSH_MAX_SESSIONS_PER_WORKER` | 20 | Integer 1–4096 | Ordinary SSH sessions per worker |
| `LAKESHORE_SSH_MAX_TUNNELS_PER_WORKER` | 8 | Integer 1–32 | Forwarding tunnels per worker |
| `LAKESHORE_SSH_MAX_SESSIONS_PER_NAMESPACE` | 128 | Integer 1–4096 | Combined sessions per namespace |

```sh
export LAKESHORE_SSH_MAX_SESSIONS_PER_WORKER=20
export LAKESHORE_SSH_MAX_TUNNELS_PER_WORKER=8
export LAKESHORE_SSH_MAX_SESSIONS_PER_NAMESPACE=128
```

The tunnel maximum matches the current bounded inventory API. Raising it beyond 32 requires a separate inventory/pagination change. An unset value uses its default. Empty strings, zero, negative values, fractions, whitespace, exponential notation and values above the bound fail startup. Zero does not mean unlimited or disable SSH. These are process-wide settings applied independently to each namespace/worker; they are not per-namespace overrides. No user-facing API changes them. Restart/redeploy the control plane through its existing service manager after changing them. Do not mix instances with different values: the shared transaction fence prevents races but does not reconcile different policies.

On the enrolled machine, the owner configures Nymph's existing TOML file:

```toml
[ssh]
enabled = true
state_dir = "/home/worker/.local/state/dreamlake/ssh"
sshd = "/usr/sbin/sshd"
max_duration_s = 3600
max_sessions = 28
```

Use the existing private state directory and SSH host key for an enrolled service; the example path is not a migration instruction.

| Nymph `[ssh]` option | Default | Meaning |
|---|---|---|
| `enabled` | `false` | Enables the SSH backend only when local `command_execution` also permits it. |
| `state_dir` | Empty | Required private directory for enabled SSH; retains its host key and boot binding. |
| `sshd` | `/usr/sbin/sshd` | Local OpenSSH server executable used by the backend. |
| `max_duration_s` | 3600 | Session lifetime cap, 60–14400 seconds; request and credential expiry can shorten it. Browser/API delegations currently cap requests at 1800 seconds. |
| `max_sessions` | 28 | Combined local SSH/tunnel task capacity, integer 1–4096; validated at configuration load. |

There is no new Nymph environment-variable or CLI-flag override for `max_sessions`. It belongs in the config selected by `--config` or the existing service configuration. Omitted options use defaults; unknown options are rejected. Nymph reads this file at startup, not on every poll. `nymph access --config /absolute/path/to/udf-daemon.toml` inspects the file plus local policy without starting a worker; its `settings.sshEnabled`, `sshMaxSessions` and `sshMaxDurationSeconds` describe that inspected startup configuration, not proof that an already-running daemon has reloaded it.

Keep local combined capacity at least the intended simultaneous SSH plus tunnel count for the worker (28 for the defaults). A deliberately lower local capacity still applies: the control plane does not currently advertise or negotiate this local setting, so its counters are control-plane admission limits, not guaranteed local slots. OS process/file-descriptor limits, memory and OpenSSH remain additional constraints. Do not increase those blindly or use quota changes to broaden grants.

### Roll out or reduce limits

1. Record deployed versions, current effective process settings, host enrollment and existing state directory. Inspect usage and active work before restarts.
2. Deploy the configurable control plane initially with explicit legacy limits when older daemons remain. Pending responses stay bounded to ten sessions for compatibility; subsequent polls deliver additional sessions.
3. Upgrade/configure each target Nymph with the required local capacity, validate its config, and restart through its existing supervisor in an agreed interruption window. A daemon restart can disconnect SSH viewers; capacity configuration is not a live update.
4. Apply the selected limits consistently across control-plane instances, then deploy matching API/gateway and clients. Verify usage, a successful connection/disconnection, a limit refusal with counts, and recovery after a slot is released.
5. Publish docs, refresh the public skill references, release the skill and update the CLI pin through their normal workflows. Track each publication separately.

Reducing a control-plane limit below current use does not terminate existing sessions. Usage can legitimately read `used > limit`; new admissions remain blocked until enough sessions close/expire. Restarting Nymph is different and can interrupt its sessions. Record rollback values and deployment versions; restoring an older Nymph requires removing unsupported new TOML fields first. Do not delete SSH state/host keys to roll back a capacity change.

### Limit errors and recovery

HTTP `429` with `session_limit` means an admission quota was reached. The new response carries validated numeric `usage` fields; clients describe host SSH/tunnel usage and namespace total. Older servers without counts produce a generic limit message. Unknown or malformed upstream fields are not shown as numbers, and arbitrary upstream messages/credentials are never echoed.

Close only a connection/tunnel you intend to release, then refresh and retry. Closing an SSH viewer need not stop the underlying agent or tmux workload. A full namespace can block a host with free local slots. If counts appear stale, allow cleanup/connection deadlines to pass and inspect the lifecycle; do not delete session records to bypass the counter. `503 ssh_busy` / `controlplane_busy` indicates the bounded write queue, not the concurrent-session quota. `daemon_unavailable`, `terminal_not_ready` and permission errors require their own readiness/authorization checks.

For the authority model and proposed live-configuration boundary, see [Nymph permissions and commands](docs-lakeshore-hosts-nymph-permissions.md).
