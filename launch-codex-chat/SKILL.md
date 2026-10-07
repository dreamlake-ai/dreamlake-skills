---
name: launch-codex-chat
description: Create a normal, persistent Codex chat on an existing local app-server so the user can open and continue it in their connected Codex app, including on an iPad. Use for requests to launch a new chat on this machine; not for delegating work to subagents or merely starting a remote-control daemon.
---

# Launch Codex Chat

Create a named, resumable conversation on the same app-server used by the
user's connected client. Starting the server alone does not create a chat.

## Procedure

1. Choose the requested working directory and a recognizable chat name. If no
   directory was specified, use the current workspace. Preserve the host's
   permission defaults unless the user requests a different mode.
2. Run `codex app-server daemon version`. If the user requests a chat visible
   through remote control and the daemon is unavailable, use
   `codex remote-control start`. Do not stop or restart an existing daemon.
   Existing pairing is reusable; do not generate pairing codes unnecessarily.
3. Run the bundled helper (resolve its path relative to this skill):

   ```bash
   python3 scripts/launch_chat.py --cwd /absolute/workspace --name "Remote workspace"
   ```

   Add `--full-access` only when authorized. It sets `approvalPolicy=never` and
   `sandbox=danger-full-access` on the new thread without changing global config.
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
