<!-- generated from https://cli.dreamlake.ai/auth.md at 0.149.0 587adf6; do not edit -->

# Authentication and namespaces

**Profiles: CLI and TypeScript 0.139.0+, Python 0.57.0+.**
**Repository namespaces: CLI and Node auth API 0.140.0+, Python 0.58.0+.** A **profile** saves a login,
its **environment** chooses a deployment, and its **default namespace** chooses
where resource commands operate. Selecting `fortyfive` or `dyna-robotics` does
not change your signed-in account or grant access. The server checks permissions
on every operation.

## Remote-managed namespace defaults

**CLI and TypeScript 0.141.0+:** these controls require the matching server policy API.

Enable managed defaults for the current login when an organization manages its
members' upload destination:

```bash cli-help="namespace managed"
dl namespace managed on
dl namespace managed status --json
dl namespace managed off
```

Managed mode checks the remote policy on every implicit namespace resolution.
The order is explicit `--namespace`, remote managed default, repository `.dreamrc`,
global profile default, then personal namespace. When the server reports no policy,
local defaults still apply. An unreachable server, invalid policy, or revoked
membership stops resolution; it never silently falls back to a different upload
destination. Unmanaged mode preserves the existing local behavior.

The opt-in belongs to the verified login profile and API origin, survives profile
switching and verified credential refresh, and does not grant access. The server
validates current membership when reading or using a managed destination.
`namespace use` and `namespace reset` still edit local/global preferences;
`namespace managed off` stops applying the remote policy on this login.

An organization OWNER can set or clear that organization's default for a current
member. These commands change the remote policy; they do not enable managed mode
on the member's computers. Use the member's exact user ID:

```bash cli-help="namespace policy set"
dl namespace policy set fortyfive <user-id> --json
```

```bash cli-help="namespace policy clear"
dl namespace policy clear fortyfive <user-id> --json
```

A policy belonging to another organization cannot be overwritten by this
organization. Clearing a policy restores local fallback for managed clients.
Neither operation moves, copies, hides, or deletes existing sessions.

## Choose a workspace

```bash cli-help="namespace"
dl namespace list
dl namespace use fortyfive --local
dl namespace status
dl namespace use dyna-robotics --global
dl namespace reset --local
```

```bash cli-help="namespace list"
dl namespace list
dl namespace list --json
```

```bash cli-help="namespace use"
dl namespace use
dl namespace use fortyfive --local
dl namespace use dyna-robotics --global
```

```bash cli-help="namespace status"
dl namespace status
dl namespace status --global
dl namespace status --json
```

```bash cli-help="namespace reset"
dl namespace reset --local
dl namespace reset --global
```

`dl namespace use` opens a picker in an interactive terminal. Choose a namespace
and the command writes the selection directly to the selected scope. Scripts and
agents pass the name explicitly; they do not wait for a picker. `dl su fortyfive`
remains supported. Selection verifies personal or organization membership before
saving.

By default, namespace reads use the nearest project [`.dreamrc`](cli-dreamrc.md#repository-namespace)
when it contains `namespace`, then the active profile's global default, then the
signed-in personal namespace. Writes update an existing project `.dreamrc`; when
none exists, they update the global profile default. Use `--local` to create a
repository default, or `--global` to ignore local configuration and manage the
profile default. An existing `.dreamrc` without `namespace` inherits the global
default on reads but remains the target for automatic writes.

```yaml file=".dreamrc"
namespace: fortyfive
```

The local setting is an ordinary YAML field, so opening a repository with this
file selects its namespace. There is no separate enrollment or credential binding
for the file. Credentials stay in the global login store. Namespace edits preserve
other fields and comments; the picker edits this same file. See the
[discovery and scope rules](cli-dreamrc.md#repository-namespace) for nested directories.

`namespace reset --local` removes the local field and restores global fallback.
`namespace reset --global` clears the profile default, without removing a local
selection. With neither flag, reset chooses the same destination as use. Switching
profiles restores that profile's global default; an existing repository namespace
continues to take precedence. Status shows the effective namespace source, selected config file and profile
default separately.

An explicit `--namespace` or namespace-qualified resource target wins for one
invocation. Commands which require an explicit namespace continue to require one.
For ordinary resource commands, put the config selector before the command:
`dl --global hosts list` ignores the repository default. Namespace commands and
`auth status` also accept their scope selector after the command, such as
`dl namespace status --global` or `dl auth status --global`. Existing command
flags retain their own meanings; do not append `--local` or `--global` to a
resource command to select configuration scope.
A saved namespace is a preference, not proof of current access: revoked access
fails at the resource route. No namespace operation transfers resources, changes
your account or changes the browser workspace.

## Save and switch accounts

```bash cli-help="auth"
dl auth login --env prod --profile personal
dl auth status
dl auth profiles
dl auth switch personal
dl namespace use fortyfive
```

```bash cli-help="auth login"
dl auth login --env prod --profile personal
dl auth login --env prod --profile work --no-browser
```

The same deployment can have several named accounts. Names are labels you choose;
use a namespace default when you simply want another workspace under the same
account. Existing `login`, `logout`, `profile`, and `auth env` commands continue
to work. A custom deployment uses `--url` and, when needed, `--auth`.

```bash cli-help="auth profiles"
dl auth profiles
dl auth profiles --json
```

```bash cli-help="auth switch"
dl auth switch personal
dl auth switch --profile work
```

Omitting the profile toggles when exactly one other profile exists, or offers a
terminal picker. Noninteractive ambiguous selection fails with a selection hint.
A switch restores saved credentials locally; `auth status` verifies them online.

```bash cli-help="auth status"
dl auth status
dl auth status --json
```

```text
✓ Signed in

  Profile             personal
  Account             geyang
  Environment         prod
  Server              https://api.dreamlake.ai
  Personal namespace  geyang
  Default namespace   fortyfive
  Namespace source    local
  Config scope        local
  Config file         /workspace/robotics/.dreamrc
  Profile default     dyna-robotics

  Switch workspace: dl namespace use <name>
  Switch login:     dl auth switch <profile>
```

Status returns a failure exit code when authentication is absent, rejected, or
unverifiable. It never presents a locally decoded JWT as verified login. JSON
contains no tokens. Environment overrides are named explicitly; saved-profile
mutations refuse active `DREAMLAKE_API_KEY` or `DREAMLAKE_REMOTE` overrides.
Local namespace writes can use those credentials after verifying membership;
global namespace mutations require the saved connection.
Machine identities use their provisioned machine interface. Existing personal
login/switch/logout commands can still manage the separate human credential store
without changing machine files or selecting user mode. Select `--identity user`
to use those personal credentials, verify their status, or change namespaces.

## Renew or remove credentials

```bash cli-help="auth refresh"
dl auth refresh
dl auth refresh --profile work --no-browser
```

Refresh performs device authorization again; DreamLake does not expose GitHub's
OAuth scope flags. A verified login for the same personal namespace and server
retains the saved global default. A different account starts with its personal
global default. Neither operation rewrites a repository `.dreamrc`.

```bash cli-help="auth logout"
dl auth logout --profile work
```

Logout removes local credentials. Copies of the token elsewhere remain valid
until their server-side expiry or revocation. Removing the active profile selects
another saved login; removing the last login clears the local connection.

```bash cli-help="auth token"
dl auth token --profile personal
```

`auth token` writes only the token and a newline to stdout. Use it only when a
program explicitly needs credentials; do not include its output in reports,
logs, or notes. `auth login --with-token` reads a token from stdin rather than
putting it in shell history or a process argument.

```bash cli-help="auth setup-git"
dl auth setup-git
```

DreamLake tokens authenticate the DreamLake API, not Git remotes. This command
explains that boundary and exits unsuccessfully without changing Git config.
For GitHub repositories use `gh auth setup-git` with GitHub credentials. Vault
credential selection remains a separate explicitly scoped operation.

## TypeScript APIs

Browser/server clients have an explicit, client-local default:

```typescript
import { createClient } from '@dreamlake/dreamlake-cli/api';
const client = createClient({ remote: 'https://api.dreamlake.ai', token });
await client.selectNamespace('fortyfive'); // verifies membership
await client.hosts().list();
await client.hosts('dyna-robotics').list(); // one-call override
await client.auth.status();
await client.auth.namespaces();
```

`createClient({ remote, token, namespace: 'fortyfive' })` sets a caller-supplied
default without a preliminary membership request. Resource routes still enforce
access. Clients never read local CLI files implicitly, and later CLI switches
do not mutate an already-created client.

Node programs can explicitly use the shared local login store:

```typescript
import {
  authenticationStatus, savedProfiles, switchProfile, loginWithToken,
  logoutProfile, namespaceList, setDefaultNamespace, clearDefaultNamespace,
} from '@dreamlake/dreamlake-cli/auth';
await loginWithToken({ profile: 'personal', env: 'prod', token });
await setDefaultNamespace('fortyfive', { scope: 'local', cwd: '/workspace/robotics' });
await setDefaultNamespace('dyna-robotics', { scope: 'global' });
switchProfile('personal');
const status = await authenticationStatus({ cwd: '/workspace/robotics' });
const profiles = savedProfiles();
const namespaces = await namespaceList();
clearDefaultNamespace({ scope: 'local', cwd: '/workspace/robotics' });
logoutProfile('personal');
```

`authToken(profile?)` is the explicit secret-returning operation. Token renewal
can be saved with `refreshWithToken(token, profile?)`; use the CLI device flow for interactive login.
The `/auth` module is Node-only and is separate from the explicit HTTP API.
Namespace operations accept `scope: 'auto' | 'local' | 'global'` (default `auto`)
and `cwd` (default the process working directory). Login, profile switching and
credential storage remain global. In status, `namespaceSource` is `local`,
`global` or `personal`; `profileDefaultNamespace` is the saved global preference
or `null`. `configScope` and `configFile` identify the selected configuration
file. When a local file has no namespace, `configFile` still names that file while
`namespaceSource` describes the inherited global/personal value. `scope: 'global'`
bypasses local configuration, including an invalid project file.

## Python API

```python
from dreamlake.auth import Auth

auth = Auth(cwd="/workspace/robotics")
auth.login(token=token, profile="personal", environment="prod")
auth.set_default_namespace("fortyfive", scope="local")
auth.set_default_namespace("dyna-robotics", scope="global")
auth.switch("personal")
status = auth.status()
profiles = auth.profiles()
namespaces = auth.namespaces()
auth.clear_default_namespace(scope="local")
auth.logout("personal")
```

Python 0.58.0+ resolves an implicit namespace from the repository `.dreamrc`,
then the global preference when its server and credential fingerprint match,
then personal identity. Explicit method namespace arguments win. `Auth` accepts
`scope="auto" | "local" | "global"` and `cwd`; `status`, `namespaces`,
`get_namespace`, `set_default_namespace` and `clear_default_namespace` can
override them per call. `auth.get_namespace()` returns the effective default;
`auth.get_namespace("fortyfive")` explicitly selects that namespace for the
lookup. Status includes `namespaceSource`, `configScope`, `configFile` and
`profileDefaultNamespace` with the same meaning as the Node API. Login, switching
and logout always use the global credential store, including when local YAML is
invalid. Personal-identity lookup remains separate. Long-lived clients retain their
captured credentials; create a new client after changing profiles. See the
[Python authentication reference](https://github.com/fortyfive-labs/dreamlake/blob/main/docs/authentication.md) and installed SDK
docstrings for API signatures.
