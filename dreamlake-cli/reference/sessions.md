# Terminal sessions

CLI **0.74.0 or later** provides `dreamlake sessions`, which shares saved terminal
descriptors with the DreamLake Sessions page. The matching `terminal-sessions`
API and terminal gateway Codex launch support are required. Updating the CLI
does not deploy those server capabilities.

A descriptor binds the selected target, host enrollment, Unix user, working
directory, and exact Codex session UUID. It contains no credentials or transcript.
The remote host must already have that conversation under the selected user's
Codex state, the requested directory, `codex`, and `tmux` installed. A session
UUID does not move a conversation between computers or users.

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

## Custom deployments

For the production API, terminal requests use `https://term.dreamlake.ai` with
the allowed origin `https://dreamlake.ai`. A custom API environment requires both
`--gateway` and `--origin` for `targets`, `open`, and interactive `resume`, and
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
