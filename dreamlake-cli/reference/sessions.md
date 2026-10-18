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
Codex state, the requested directory, `codex`, and `tmux` installed. A session
UUID does not move a conversation between computers or users.

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
starts `codex resume` in the requested directory under a deterministic tmux
session, or attaches to that same tmux session if it exists. Repeated opens share
the same process; an existing Codex process started outside this tmux session is
not automatically discovered or adopted.

Press **Ctrl-]** to detach while leaving the remote session running. Ctrl-C goes
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

`start` explicitly starts Codex in detached, managed tmux, keeps an already
running process, or resumes the saved conversation after an owned pane exits.
Unlike `resume --json`, **`start --json` executes**; JSON changes its output only.
Managed `open` and interactive `resume` start or verify the runtime before
requesting an attachment that cannot create another process.
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
operation is `stop`. The saved descriptor and Codex conversation remain, and a
later explicit `start` or `open` can resume them.

Older, unmarked tmux sessions report `legacy`. A live legacy session can still
be attached without replacing it, but cannot be stopped or restarted through
managed lifecycle commands because ownership is unverified. Missing tmux or
Codex is reported as `dependency_missing`; these commands install no packages
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
