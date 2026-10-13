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

## Fresh-host prerequisites and manual gaps

The helper was audited on 2026-10-12. It launches a chat on a prepared host;
it does not provision a machine, install dependencies, transfer credentials,
pair a new host, synchronize repositories, or start the user's development task.

Before invoking it on a new machine:

- Select the infrastructure repository by its ownership and existing Terraform
  state, not by a matching directory name. A provider-setups recipe can be a
  copy of a separately maintained deployment. Use the owning repository's
  isolated development-machine root and state; preserve existing cluster state.
  Neither launch skill owns Terraform or bootstrapping.
- Install Python 3 and a compatible Codex CLI, then verify the daemon and
  remote-control commands under the actual development user. Install requested
  development tools separately: Git, Node.js/npm, GitHub CLI, Heroku CLI, ngrok,
  zsh, Powerlevel10k, and zsh-autosuggestions are not supplied by this helper.
  Check executable versions, the login-shell PATH, shell plugin loading, and
  service authentication independently; a successful installation is not a login.
- For DreamLake-managed access, retrieve only the needed credentials from
  DreamLake Vault using the authorized bootstrap path. Keep credential values
  out of logs, shell tracing, Terraform variables/state, and cloud user-data.
  Deliver them through a private channel to the intended user's restricted
  credential store. Never substitute another account or copy another host's
  identity as a workaround for registration.
- Check the installed client's authentication status before starting its
  daemon. An OAuth snapshot in Vault is not a permanent login: it can expire,
  require refresh, or be revoked. Use the supported refresh/login flow when
  needed; if human authentication is required, report that specific blocker
  promptly. Remote host registration/pairing is separate from account login.
  A fresh machine may need its own pairing; an existing machine's pairing
  does not establish that this host is connected.
- Fetch the intended repository revisions and create the requested separate
  Git worktrees and coordination directory before selecting `--cwd`. Record
  checkout revisions and any uncommitted changes; this helper only checks that
  the directory exists. Inspect actual startup prompts and complete consent
  already covered by the user's request without asking again. Do not blindly
  send keys or weaken organization controls to clear a prompt.

Report host/bootstrap readiness, account authentication, remote pairing, chat
listing, and app visibility separately. This helper verifies returned full-access
permissions and server-side listing; it does not inspect the connected app.
Its only model input is a greeting that explicitly forbids tools or file changes.
When the user also requested development work, send their task to the recorded
thread through a supported client/API after launch and verify that it started.
Do not describe a completed greeting as evidence that the development task is
running, and do not create a replacement chat merely to deliver that task.

### Service readiness after credential restore

A fresh-host run on 2026-10-12 exposed checks that can pass before the service
is usable. DreamLake's `auth.yml` is a saved multi-environment login cache;
copying it alone left Notes unauthenticated. Run the supported
`dreamlake auth env use <saved-name>` to activate the intended saved login in
the CLI's config/token files, then verify an authorized Note or Vault read.
Use the published `@dreamlake/dreamlake-cli` npm package; `@dreamlake/cli`
returned 404 during this run.

Similarly, a restored npm credential file still produced `npm whoami` HTTP 401.
Treat that as failed registry authentication. `ngrok config check` passed, but
`ngrok start --none` returned `ERR_NGROK_108` because the account's two-agent
limit was already in use. A config check cannot establish account capacity;
report the limit without stopping unrelated agents. Restored Codex login did
work in this run, verified through Remote Control connection, the returned
full-access thread settings, and a separately submitted task starting. Keep
these outcomes separate; one working service does not validate the others.

## Pairing codes and desktop registration

Checked on 2026-10-12 with Codex CLI 0.162.1 and the installed desktop app.
Reuse an existing pairing when available. For a new host whose remote-control
daemon is already running, generate a short-lived code on that host:

```bash
codex remote-control pair --json
```

The response contains `pairingCode`, `manualPairingCode`, `environmentId`, and
`expiresAt`. Give the intended user the manual code and expiry through the
authorized channel; keep live codes out of committed documentation. This command
**creates** a code. No supported CLI command to **redeem** a supplied code and
add that host to the desktop was found in this version. The normal completion
step is the desktop's remote-connections pairing flow.

The installed app's implementation revealed an internal authenticated request:

```text
POST /wham/remote/control/client/pair
Body: {"client_id": "<desktop-client-id>", "manual_pairing_code": "<code>"}
Success field used by the app: environment_id
```

After success, the app refreshes remote-control connections and enables
auto-connect for the returned environment. A command-line integration using
this internal endpoint was tested on 2026-10-12: four hosts were paired to an
existing desktop client, and each grant was verified through the app-server's
client list. This remains an undocumented, version-specific API; there is no
new built-in `codex ... add --code` command.

For an authorized programmatic registration:

1. Resolve the intended desktop's existing enrollment from
   `electron-remote-control-client-enrollments` in
   `~/.codex/.codex-global-state.json`. Match the active account and desktop;
   do not select an arbitrary enrollment when several exist. Reuse that
   client's `clientId`; do not create or copy a device identity.
2. Authenticate to `https://chatgpt.com/backend-api` as the same account. In
   the tested installation, the existing Codex CLI `auth.json` access token
   and account ID worked as `Authorization: Bearer ...` and
   `ChatGPT-Account-Id`. Read credentials in process, without printing them
   or placing them in command arguments. Authentication failure is not proof
   that another account's token or identity should be tried.
3. Initialize the local app-server connection with
   `capabilities: {"experimentalApi": true}`. Check
   `remoteControl/client/list` with the target `environmentId`, following
   `nextCursor` if necessary. Skip pairing if the intended `clientId` is
   already present.
4. Generate a fresh manual code on each missing host under its development
   user. Over SSH, use that user's login-shell PATH when Codex is installed
   under `~/.local/bin`. Check that the returned `environmentId` matches the
   requested host, then POST the code and intended desktop client ID to the
   endpoint above. Keep the code in memory; stop on an authentication or
   authorization rejection rather than retrying alternate identities.
5. Require the returned `environment_id` to match, then verify the intended
   `clientId` appears in `remoteControl/client/list`. Record this readback
   separately from desktop visibility and auto-connect. The app's Connections
   page refreshes the remote inventory; `open 'codex://settings/connections'`
   opens that page on the tested macOS installation. A successful `open`
   command alone does not prove that the host connected or its chats rendered.

Recheck the installed implementation before adapting this procedure. A pairing
code alone is insufficient: redemption also needs authenticated account access
and the intended desktop's registered client identity.

The generated app-server protocol exposes host-side pairing start/status and
client list/revoke methods, but no code-redemption method was found. Its
`environment/add` method registers an exec-server execution environment, not a
desktop remote-control host. Similarly, `codex --remote <websocket-url>` connects
the CLI to an app-server endpoint; it does not add a machine to the desktop.

## Sources

- [Official app-server lifecycle and RPC documentation](https://learn.chatgpt.com/docs/app-server)
- [Remote connections and client visibility](https://learn.chatgpt.com/docs/remote-connections)
- [Official remote-control CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-remote-control)
- [Sandbox and approval settings](https://learn.chatgpt.com/docs/sandboxing)

The machine-specific transport behavior above comes from direct local tests,
not a claim that every official client or Codex version uses this transport.
