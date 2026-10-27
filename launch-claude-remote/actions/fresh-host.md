# Fresh-host prerequisites and manual gaps

The helper was audited on 2026-10-12. It starts or inspects one Remote Control
terminal; it does not provision a machine, bootstrap tools, authenticate an
account, synchronize repositories, or send a development task.

- Infrastructure belongs in the repository that owns the deployed Terraform
  state. Verify ownership rather than assuming a provider-setups recipe is the
  canonical deployment. Use a separate development-machine root/state and keep
  existing infrastructure intact; this launch skill does not implement either.
- Install Python 3, tmux, and a compatible Claude Code under the development
  user. Separately verify requested Git, Node.js/npm, GitHub CLI, Heroku CLI,
  ngrok, zsh, Powerlevel10k, and zsh-autosuggestions. Check the login-shell PATH
  and shell plugin loading as well as executable versions. The helper's `--check`
  verifies Claude flags and tmux availability, not these other tools or logins.
- Use the authorized DreamLake Vault bootstrap path for DreamLake-managed
  credentials. Deliver only needed values privately to the intended user's
  restricted credential store; never include them in logs, shell tracing,
  Terraform variables/state, or cloud user-data. A saved OAuth snapshot can
  expire or require refresh. Verify the eligible subscription login on this
  host and use the supported refresh/login flow if needed. API-key availability
  does not establish Remote Control eligibility. Report any required human
  authentication promptly; do not copy unrelated sessions' authentication files.
- Prepare the requested repository revisions, separate Git worktrees, and
  coordination directory before launch. The helper verifies only that `--cwd`
  exists. Launch as the intended development user and inspect first-run prompts;
  the user's explicit full-permission request covers ordinary trust and bypass
  consent, but the helper does not answer it. Do not send blind keystrokes or
  edit internal consent files. A fresh host's registration is separate from
  login, and another host's session URL does not register this one.

Readiness has distinct stages: dependencies installed, account authenticated,
Remote Control registered, app-visible session, and development task started.
The helper returns `registered` when a live pane contains a session URL; this
does not verify the app or infer that a task is running. It has no prompt/task
argument and sends no development task. After registration, deliver the user's
authorized task to that session through a supported interactive client and
verify it starts. Keep the existing tmux session alive during the handoff; no
reboot recovery or boot service is installed by this helper.

## Service readiness after credential restore

In a fresh-host run on 2026-10-12, `claude auth status` reported `loggedIn: true`
and a team subscription after OAuth restore, but email/organization details
were absent. The helper's Remote Control check then failed with
`Unable to determine organization` and requested `claude auth login`. A saved
token or positive login status alone does not prove Remote Control readiness.
Follow that supported login flow; do not patch private `.claude.json` account
or organization fields to bypass the failure.

Check development services independently. DreamLake's `auth.yml` is a saved
multi-environment cache: copying it alone left Notes unauthenticated. Activate
the intended saved login with `dreamlake auth env use <saved-name>`, then verify
an authorized Note or Vault read. Its published npm package is
`@dreamlake/dreamlake-cli`; `@dreamlake/cli` returned 404 during this run.
Restored npm credentials still yielded `npm whoami` HTTP 401, and a passing
`ngrok config check` was followed by `ERR_NGROK_108` on `ngrok start --none`
because the account's two-agent limit was occupied. Report the actual service
failure; do not equate files or config validation with authentication/capacity,
and do not stop unrelated ngrok agents to make room.
