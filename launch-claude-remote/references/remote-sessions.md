# Remote sessions: compatibility and lifecycle

This repository owns the launcher. Anthropic owns the CLI contract:

- [Remote Control](https://code.claude.com/docs/en/remote-control): server flags,
  account requirements, app discovery, and reconnection.
- [Permission modes](https://code.claude.com/docs/en/permission-modes):
  `bypassPermissions`, managed restrictions, and app mode labels.
- [CLI reference](https://code.claude.com/docs/en/cli-reference).

Reviewed against these docs on 2026-10-08. Check installed help rather than
assuming every release has the same flags. The helper deliberately uses server
mode's own `--permission-mode bypassPermissions`; global flags placed before
`remote-control` are not reliably carried into the sessions it creates.
`--spawn session` serves one session, avoiding an unintended multi-session host.
The default pre-created session provides a place to type in the app immediately.

Bypass is Claude's maximum permission mode, not root access or a way around
managed policy. Existing sandbox settings can still constrain execution. Do not
rewrite global settings to loosen them. Bypass mode is not reported to claude.ai,
so the mobile dropdown can show a different label from the local mode.

The helper needs a POSIX host with tmux. Its terminal survives the invoking tool
finishing or an SSH disconnect, but not host shutdown, tmux termination, or a
supervisor that kills all descendants. No boot service is installed. Keep the
computer awake and connected. Registration alone does not prove app visibility
or effective permission behavior after the user changes the mode.

## Inspect and stop

The JSON result provides the exact tmux session and attach command. Inspect with
`tmux capture-pane -p -J -t SESSION -S -1000` or attach interactively. Detach with
Ctrl-b then d. To stop this remote session, attach and press Ctrl-C. A dead pane
is retained for diagnosis; remove only that session with
`tmux kill-session -t SESSION` when finished. Do not use `tmux kill-server`.

The session key depends on directory and title. Repeating the same request
reuses its tmux session; conflicting launch settings are rejected. A different
title explicitly requests a different session. A timeout or failed startup
does not automatically clean up or retry. After stopping, use the upstream
resume commands if preserving the remote conversation matters; creating a fresh
session is not resuming one. This helper does not implement resume.

## Another session in the same folder

Claude Code 2.1.293 refuses a second server-mode process in a folder already
served by `claude remote-control`. For a new conversation in that folder, start
an interactive session with Remote Control in a new tmux session instead:

```bash
tmux new-session -d -s claude-remote-2 -c /absolute/workspace -x 240 -y 50 \
  claude --remote-control "Remote workspace 2" --dangerously-skip-permissions
```

Choose an unused tmux name and a recognizable title. Inspect the pane for any
startup prompts, the active Remote Control indicator, and the new session URL.
Keep the first session running. For narrower permissions, replace the bypass
flag with the user's requested `--permission-mode`. This interactive path was
verified alongside a server-mode session in the same folder.

## Startup gaps

First-time workspace trust, Remote Control consent, and bypass-mode consent can
require terminal interaction. Read the actual pane before responding; the helper
does not automate consent. Login requires the user's own browser/account flow.
Do not copy credentials from unrelated sessions or change authentication methods.
If prompts are already authorized by the launch request, complete them without
asking for redundant permission.

Remote Control help can fail before listing flags if the account is ineligible.
Report that error rather than interpreting it as a missing flag. Account/plan,
organization settings, alternate API providers, and feature-flag configuration
can prevent connection; consult upstream troubleshooting for the installed
version. Avoid printing credential values or publishing terminal scrollback.

The automated tests use a fake Claude executable with real tmux to verify
detachment, literal argument passing, session reuse, timeout, and failure paths.
They do not establish a live Anthropic connection or verify the mobile UI.
