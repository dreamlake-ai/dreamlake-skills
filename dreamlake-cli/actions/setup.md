# Install and authenticate

Install the standalone CLI, then authenticate and select the deployment:

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dreamlake init  # choose Codex or Claude Code and project/global scope
dreamlake login
dreamlake auth env list
```

Built-in deployments keep separate tokens. Check `dreamlake auth env --help` for
switching and custom deployment setup. Do not assume the active environment is
production. See [installation](../reference/cli-installation.md) and
[environments](../reference/cli-environments.md).

When the user wants subsequent CLI work in a named namespace, check the installed
command before changing the selection:

```bash
dreamlake --version
dreamlake su --help
dreamlake su <namespace>
```

Use the user's actual namespace name and follow
[namespace selection](../reference/cli-environments.md#select-the-default-cli-namespace).
Confirm the result with a read-only operation from the intended task before
continuing. Preserve explicit namespace arguments the user supplied. For an
SDK-only request, use that SDK's documented namespace argument instead of
changing CLI configuration. Keep this task scoped to the CLI namespace selection;
handle resource moves, identity changes or GUI session changes only when requested.
If the installed command is missing, use the documented upgrade path; do not
substitute credential changes or direct configuration edits.

For scripts, use `dreamlake init --agent codex` or
`dreamlake skill install --agent claude --global`. Skills are bundled with the
CLI; updates remind you when installed copies differ. Review local edits before
using `--force`. See [agent skills](../reference/cli-skills.md).

On a managed machine, start with `dreamlake auth identity` and
`dreamlake machine self`. Machine mode supports granted host/project metadata
reads; other APIs require personal identity. `dreamlake login` uses the existing
device flow without altering machine credentials. Explicitly select personal
access with `dreamlake --identity user profile`. Do not copy user tokens into
machine configuration. See [machine authentication](../reference/cli-machine-auth.md).

CLI 0.56.0 and later support quiet product-analytics opt-out with
`dreamlake telemetry disable --quiet` or `DREAMLAKE_TELEMETRY=0`. See
[product analytics](../reference/cli-analytics.md) for scope and limitations.

For CLI 0.86.0+ with Nymph 0.1.32+, interactive device login can offer optional
background-service setup, default No. See the Nymph section in
[environments](../reference/cli-environments.md). `dreamlake nymph` separates service
configuration, local access policy and runtime observation. Fresh managed setup
denies upload and command execution independently. Configuration edits do not
change access. Grant one permission at a time; only explicit `--yes` bypasses
that permission's default-No confirmation. Restart the exact managed enrollment
to apply policy/config changes and verify runtime separately. Local consent does
not replace server ACLs or manage independent transcript archive collectors.
Do not enroll duplicate daemons, convert legacy access automatically, or assume
a locally saved policy is already enforced by a running older binary.

Use CLI 0.86.1+ for named Nymph enrollments. Version 0.86.0 could ignore a
subcommand enrollment selector and mutate the default profile; upgrade before
grants, revocations, configuration edits or restarts of a named enrollment.
