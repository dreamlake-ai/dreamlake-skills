<!-- generated from https://cli.dreamlake.ai/auth.md at 0.139.0 9cde214; do not edit -->

# Authentication and namespaces

**CLI and TypeScript 0.139.0+, Python 0.57.0+.** A **profile** saves a login,
its **environment** chooses a deployment, and its **default namespace** chooses
where resource commands operate. Selecting `fortyfive` or `dyna-robotics` does
not change your signed-in account or grant access. The server checks permissions
on every operation.

## Choose a workspace

```bash cli-help="namespace"
dl namespace list
dl namespace use fortyfive
dl namespace status
dl namespace use dyna-robotics
dl namespace reset
```

```bash cli-help="namespace list"
dl namespace list
dl namespace list --json
```

```bash cli-help="namespace use"
dl namespace use fortyfive
dl namespace use dyna-robotics
```

```bash cli-help="namespace status"
dl namespace status
dl namespace status --json
```

```bash cli-help="namespace reset"
dl namespace reset
```

`dl su fortyfive` remains supported. Selection verifies personal or organization
membership before saving. Each named login retains its own default when switched
away and back. `reset` returns to the account's personal namespace. An explicit
`--namespace` or namespace-qualified resource target wins for one invocation.
Commands which require an explicit namespace continue to require one.

A saved namespace is a preference, not proof of current access: revoked access
fails at the resource route. No namespace operation transfers resources or changes
the browser workspace.

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

  Switch workspace: dl namespace use <name>
  Switch login:     dl auth switch <profile>
```

Status returns a failure exit code when authentication is absent, rejected, or
unverifiable. It never presents a locally decoded JWT as verified login. JSON
contains no tokens. Environment overrides are named explicitly; saved-profile
mutations refuse active `DREAMLAKE_API_KEY` or `DREAMLAKE_REMOTE` overrides.
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
retains the saved default. A different account starts with its personal default.

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
await setDefaultNamespace('fortyfive');
switchProfile('personal');
const status = await authenticationStatus();
const profiles = savedProfiles();
const namespaces = await namespaceList();
clearDefaultNamespace();
logoutProfile('personal');
```

`authToken(profile?)` is the explicit secret-returning operation. Token renewal
can be saved with `refreshWithToken(token, profile?)`; use the CLI device flow for interactive login.
The `/auth` module is Node-only and is separate from the explicit HTTP API.

## Python API

```python
from dreamlake.auth import Auth

auth = Auth()
auth.login(token=token, profile="personal", environment="prod")
auth.set_default_namespace("fortyfive")
auth.switch("personal")
status = auth.status()
profiles = auth.profiles()
namespaces = auth.namespaces()
auth.clear_default_namespace()
auth.logout("personal")
```

The Python SDK's implicit namespace resolution follows a saved default only when
its server and credential fingerprint match. Explicit method namespace arguments
win. Personal-identity lookup remains separate. Long-lived clients retain their
captured credentials; create a new client after changing profiles. See the
[Python authentication reference](https://github.com/fortyfive-labs/dreamlake/blob/main/docs/authentication.md) and installed SDK
docstrings for API signatures.
