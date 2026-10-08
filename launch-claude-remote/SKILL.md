---
name: launch-claude-remote
description: Create a new Claude session with remote access and maximum permissions. Use for "Start another Claude session", "Start Claude", or "再开一个 Claude 会话" so the user can continue in their Claude app. Keep existing sessions running. Not for cloud tasks or ordinary Claude chats.
---

# Start Claude

Say **"Start another Claude session"** or **"再开一个 Claude 会话"**.
**"Start Claude"** also means a new session. Remote access and maximum
permissions are the defaults; existing sessions stay running. Honor an explicit
request for narrower access. Ask only when the intended app or workspace is
unclear from context; otherwise use the current workspace.

For each new-session request, choose a fresh title and terminal name. Reuse
those identifiers only when retrying that same launch, not for a request to
start another session. A quoted trigger discussed as wording is not a launch
request by itself.

Create a named Remote Control session using the host's existing Claude login.
This skill defaults to `bypassPermissions`, as requested by its full-access
purpose. Honor a user's narrower permission choice. No global settings change.

## Launch

1. Choose the requested directory and recognizable title; default to the current
   workspace. The host needs Python 3, tmux, and Claude Code with Remote Control.
   Run the helper's `--check` to verify the installed CLI supports its flags.
   Remote Control requires an eligible claude.ai subscription login, using the
   same account as the app; API-key-only authentication does not work.
2. Resolve the helper relative to this skill and run:

   ```bash
   python3 scripts/launch_remote.py --cwd /absolute/workspace --name "Remote workspace"
   ```

   It starts `claude remote-control --name … --spawn session --permission-mode
   bypassPermissions` in detached tmux, waits up to 45 seconds for a session URL,
   and returns JSON with readiness, URL, working directory, and attach command.
   For narrower access pass `--permission-mode default`, `acceptEdits`, or `plan`.
   Maximum permissions means Claude's bypass mode; OS permissions, managed
   restrictions, and separately configured sandboxing still apply.
3. If startup needs login, workspace trust, or the one-time Remote Control or
   bypass acknowledgement, inspect the exact prompt in the reported tmux pane.
   Complete ordinary consent already covered by the user's request; ask only for
   missing authentication or a genuinely new decision. Never blindly send keys
   or edit Claude's internal consent/authentication files. Re-run the same helper
   arguments afterward: it inspects the existing session instead of duplicating it.
4. Report the title, URL, directory, requested permission mode, and actual
   readiness. The session should appear automatically under **Code** in the same
   account's Claude app or at `claude.ai/code`. A local URL is registration
   evidence, not proof the app rendered it. Keep the host and tmux process alive.

## Recovery

- For another session in a folder already served by `claude remote-control`,
  use the [interactive launch](references/remote-sessions.md#another-session-in-the-same-folder).
  Keep the existing session running.
- A timeout leaves the session intact and returns an attach command. Inspect it;
  do not repeatedly create sessions or restart unrelated Claude processes.
- A dead process is a failure even if its scrollback contains a URL. Inspect the
  retained pane before stopping that exact tmux session and launching again.
- `--check` only probes dependencies, version, and Remote Control help; it creates
  no session. Help itself can fail when the account is ineligible or signed out.
- The app's permission label may not display bypass mode. Do not change to a
  narrower mode from the app and assume the launch permissions remain active.
- A blocked bypass mode, unsupported CLI, or disabled Remote Control is a
  reported limitation, not a reason to change organization controls or silently
  launch with different permissions.

Read [compatibility and lifecycle notes](references/remote-sessions.md) for
startup failures, session cleanup, and the authoritative upstream references.
