---
name: launch-codex-chat
description: Create a new Codex session with remote access and maximum permissions. Use for "Start another Codex session", "Start Codex", or "再开一个 Codex 会话" so the user can continue in their Codex app. Keep existing sessions running. Not for subagents.
---

# Start Codex

Say **"Start another Codex session"** or **"再开一个 Codex 会话"**.
**"Start Codex"** also means a new session. Remote access and maximum
permissions are the defaults; existing sessions stay running. Honor an explicit
request for narrower access. Ask only when the intended app or workspace is
unclear from context; otherwise use the current workspace.

Give each new session a distinct title. If its launch fails after creating a
thread, inspect that thread before retrying; do not accidentally create another.
A quoted trigger discussed as wording is not a launch request by itself.

Create a named, resumable conversation on the same app-server used by the
user's connected client. Starting the server alone does not create a chat.

## Procedure

1. Choose the requested working directory and a recognizable chat name. If no
   directory was specified, use the current workspace.
2. Run `codex app-server daemon version`. If the daemon is unavailable, use
   `codex remote-control start`. For a running daemon, use
   `codex app-server daemon enable-remote-control` to ensure remote access.
   Do not stop or restart an existing daemon.
   Existing pairing is reusable; do not generate pairing codes unnecessarily.
3. Run the bundled helper (resolve its path relative to this skill):

   ```bash
   python3 scripts/launch_chat.py --cwd /absolute/workspace --name "Remote workspace"
   ```

   The helper defaults to full access: `approvalPolicy=never` and
   `sandbox=danger-full-access` on the new thread without changing global config.
   Pass `--host-permissions` when the user asks to keep the host's permissions.
   The helper connects to the running daemon, creates a persistent thread,
   sets its title, requests a short greeting, waits for that turn to finish,
   and verifies the thread appears in the ordinary interactive thread list.
4. Report the exact title, working directory, and readiness. Tell the user to
   refresh this machine's chat list and open the chat. Server-side listing
   proves availability on the server, not that the iPad has rendered it.

## Failures and verification

- Use `python3 scripts/launch_chat.py --check` for a read-only connection and
  thread-list check. No new chat or inference is created by this option.
- The helper prints the thread ID immediately after creation. If any later
  step fails, inspect that thread instead of blindly rerunning and creating
  duplicates. An idle chat after its greeting is ready for the user's next
  message; it does not need a perpetually running terminal or turn.
- If the client cannot see it, verify that the client selected the same host,
  account, workspace, and project/directory filter. Do not keep making chats.
- If an RPC or transport is incompatible, stop after the bounded failure and
  inspect this installed version's help/schema. Do not alter authentication,
  restart working sessions, or substitute an unrelated standalone app-server.

Read [the protocol and troubleshooting notes](references/launching-chats.md)
when diagnosing a failure or adapting to a different Codex version.
