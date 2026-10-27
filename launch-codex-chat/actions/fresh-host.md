# Fresh-host prerequisites and manual gaps

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

## Service readiness after credential restore

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
