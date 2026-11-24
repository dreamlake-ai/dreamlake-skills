# Install and authenticate

Install the standalone CLI, then authenticate and select the deployment:

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dl init  # choose Codex or Claude Code and project/global scope
dl login
dl auth env list
```

Use `dl` for new commands. If the command is missing or conflicts with another
program, follow the [installation guide](../reference/cli-installation.md#the-dl-command)
and use the supported `dreamlake` command until resolved. Keep existing package,
configuration, service, and process-management identifiers unchanged.

Built-in deployments keep separate tokens. Check `dl auth env --help` for
switching and custom deployment setup. Do not assume the active environment is
production. See [installation](../reference/cli-installation.md) and
[environments](../reference/cli-environments.md).

For saved accounts, refresh, logout, token retrieval or default namespace work,
check the installed version and open the relevant help first. These procedures
require CLI **0.140.0+**; an updated skill alone does not upgrade the binary.

```bash
dl --version
dl auth --help
dl auth status
dl auth profiles list
dl namespace --help
dl namespace list
```

Use the user's profile and namespace names. Choose the saved login before
selecting its resource scope. For repository work, inspect namespace status from
the working directory and choose local or global scope to match the request:

```bash
dl auth switch work
dl namespace use fortyfive --local
dl auth status
dl namespace status
```

For a global account preference, inspect and use
`dl namespace use dyna-robotics --global`. For automatic scope, omit the scope
flag and inspect the resulting
source path. In scripts and agents, supply the namespace name; leave the
interactive picker to a user in a terminal. To remove a selection, inspect
`dl namespace reset --help` and reset the requested scope. Confirm the resulting
namespace and source with status and a read-only operation from the intended task.
When the user opens a repository that already selects a namespace, use that
configuration within the requested task; do not add an enrollment step or a
separate approval gate for each write. Preserve explicit namespace arguments
the user supplied. If a selection is denied, inspect
membership and the effective identity; do not substitute another account or
namespace to make the operation succeed.

For login, refresh, removal, token export or Git integration, open that action's
help (`dl auth login --help`, `dl auth refresh --help`, `dl auth logout --help`,
`dl auth token --help`, or `dl auth setup-git --help`) and perform only the
requested action. Keep credentials out of status reports, transcripts and saved
notes. Check status after changing saved authentication. Do not infer that a
DreamLake login authenticates GitHub or authorizes changes to Git credentials.

For an SDK-only request, use that SDK's documented profile or namespace API
and check its installed version; do not silently change the CLI's active profile.
For details, follow [authentication](../reference/cli-auth.md),
[repository configuration](../reference/cli-dreamrc.md),
[environments](../reference/cli-environments.md) and the
installed command help. Before using bundled authentication or namespace
reference text, check its recorded source version. If it predates CLI 0.140.0,
do not use its global-only defaults or reset guidance for repository scope;
use installed help and the published docs for the installed version. Reference
pages update only after docs publication and the next reference sync.
Handle resource moves, identity changes or GUI session changes only when
requested. If a command is missing, use the documented upgrade path; do not
invent hidden binding files or substitute unrelated credential changes. For a
requested `.dreamrc` edit, preserve its other fields and comments and verify the
effective source afterward; keep credentials out of repository configuration.

For scripts, use `dl init --agent codex` or
`dl skill install --agent claude --global`. Skills are bundled with the
CLI; updates remind you when installed copies differ. Review local edits before
using `--force`. See [agent skills](../reference/cli-skills.md).

On a managed machine, start with `dl auth identity` and
`dl machine self`. Machine mode supports granted host/project metadata
reads; other APIs require personal identity. `dl login` uses the existing
device flow without altering machine credentials. Explicitly select personal
access with `dl --identity user profile`. Do not copy user tokens into
machine configuration. See [machine authentication](../reference/cli-machine-auth.md).

CLI 0.56.0 and later support quiet product-analytics opt-out with
`dl telemetry disable --quiet` or `DREAMLAKE_TELEMETRY=0`. See
[product analytics](../reference/cli-analytics.md) for scope and limitations.

For CLI 0.86.0+ with Nymph 0.1.32+, interactive device login can offer optional
background-service setup, default No. See the Nymph section in
[environments](../reference/cli-environments.md). `dl nymph` separates service
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
