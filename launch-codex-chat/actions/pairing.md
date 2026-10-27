# Pairing codes and desktop registration

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
