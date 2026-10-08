# Creating a chat that a connected client can continue

Verified on Linux with Codex CLI and app-server 0.161.0, on 2026-10-07. The
user confirmed that the created conversation opened and worked on an iPad.
Treat transport details as version-specific and consult installed help and
generated schemas when adapting them.

## What the successful flow did

`codex remote-control start` enabled the machine's remote-control daemon. It
did **not** create a conversation. Shell write/network checks demonstrated
execution permissions, but did not establish that a new chat existed.

`codex app-server daemon version` returned the running daemon's Unix socket
in `socketPath`. On this installation that endpoint accepts a WebSocket HTTP
upgrade over a Unix-domain socket. Plain newline-delimited JSON sent directly
to that socket closed the connection. An attempt through `app-server proxy`
stalled; its cause was not established. Do not describe that observation as a
universal proxy defect. The helper uses the successfully tested WebSocket path.

After the WebSocket handshake, send these JSON-RPC messages in order:

1. `initialize` with truthful `clientInfo`, then `initialized` notification.
2. `thread/start` with `cwd`, `ephemeral: false`, `approvalPolicy: "never"`,
   and `sandbox: "danger-full-access"`. These are this launcher's defaults.
   `--host-permissions` omits the permission overrides when narrower access
   is requested.
3. Record the returned thread ID before any further action.
4. `thread/name/set` with the chosen name and thread ID.
5. `turn/start` with a minimal greeting request and no task to execute. This
   creates real conversation history that the client can continue.
6. Wait for this thread's `turn/completed`; confirm `status: "completed"`.
7. Set the name again to preserve the requested title after the greeting.
8. `thread/list` with `searchTerm` and verify the exact thread ID is returned.

Closing the helper's connection leaves the persistent chat available. The
server can unload an idle thread when subscribers disconnect; the app can
resume it. A completed greeting and an idle status are expected.

## Commands

From the skill directory:

```bash
# Read-only check; neither creates a chat nor invokes a model.
python3 scripts/launch_chat.py --check

# Create a chat with maximum permissions (default).
python3 scripts/launch_chat.py --cwd /absolute/project --name "Project work"

# Keep host permissions when requested.
python3 scripts/launch_chat.py --cwd /absolute/project --name "Project work" --host-permissions
```

The helper requires Python 3 and a running daemon with a local WebSocket Unix
socket. It uses the Python standard library and the installed `codex` binary.
Each RPC has a deadline; the greeting wait defaults to 120 seconds. If the
greeting times out, it may still be running on the server. The helper reports
the created thread ID so the caller can inspect it without creating another.
It does not modify global config, publish network ports, or restart services.

For an unsupported schema, inspect without starting another server:

```bash
codex --version
codex app-server --help
codex app-server generate-json-schema --experimental --out /tmp/codex-chat-schema
```

Do not confuse `--dangerously-bypass-approvals-and-sandbox` on an unrelated CLI
process with permissions for a thread on the connected server. Verify the
actual thread/start response when a permission override was requested.

## Sources

- [Official app-server lifecycle and RPC documentation](https://learn.chatgpt.com/docs/app-server)
- [Remote connections and client visibility](https://learn.chatgpt.com/docs/remote-connections)
- [Sandbox and approval settings](https://learn.chatgpt.com/docs/sandboxing)

The machine-specific transport behavior above comes from direct local tests,
not a claim that every official client or Codex version uses this transport.
