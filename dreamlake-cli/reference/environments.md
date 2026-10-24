# Environments

The CLI can target multiple DreamLake deployments. It ships with two
**built-in** environments — `staging` and `prod` — so you never type their
URLs. Each environment keeps its own token; switching never logs you out of
the other.

## Log into a built-in environment

```bash file="terminal"
dreamlake login --env staging
dreamlake login --env prod
```

`dreamlake login` prints the complete authorization link with the code in its
query parameters. Open that link to authorize without copying the code manually,
including when using `--no-browser` on a remote machine. The code is also shown
as a fallback if prompted.

No `--url` / `--bss` needed — the URLs are baked in. `dreamlake login` with
no `--env` re-authenticates the active environment, and falls back to `prod`
when nothing is logged in yet.

## Switch environments

```bash file="terminal"
dreamlake auth env list           # show logged-in envs (* = active)
dreamlake auth env use prod       # switch — no URLs, no re-login
dreamlake auth env remove staging # forget a saved env
```

> **Note:** These lived at `dreamlake env ...` before v0.6; the top-level `env` command
> is a compatibility alias for `dreamlake scene` (see [Scenes](scenes.md)). For login switching,
> update scripts to `dreamlake auth env ...`.

Every command then targets the active environment — **and so does the
Python SDK**: switching writes the token and server to `~/.dreamlake`,
the same files `dreamlake-py` resolves its connection from. One switch
moves both tools. `dreamlake profile` shows which environment is in
effect (`[env: prod]`).

The `*` in `auth env list` marks the environment your commands will *actually*
hit, not just the last one you selected — if a `DREAMLAKE_*` env var is
overriding the connection, or the files were edited by hand, the star
disappears and a note explains why.

## Custom / self-hosted environments

Define a custom environment once with its URLs, then switch by name forever:

```bash file="terminal"
dreamlake login --env dev --url https://dev-api.example.com
dreamlake auth env use dev
```

> **Warning:** The device-flow auth server must be the one your target API trusts. The
> built-ins set this automatically (staging uses `staging-auth.vuer.ai`,
> prod uses `auth.vuer.ai`). For a custom env on a non-default auth server,
> pass `--auth <url>`. A mismatch fails token exchange with
> `No matching key found in JWKS`.

## Overrides and storage

Resolution order (high → low): **flag → env var → `~/.dreamlake` → prod**.
For one-off commands you can override the active env:

| Setting | Env var |
| --- | --- |
| Server URL | `DREAMLAKE_REMOTE` |
| Token | `DREAMLAKE_API_KEY` |
| Web app URL (receipt `open:` links) | `DREAMLAKE_WEB_URL` |

The effective connection lives in two files shared with the Python SDK
(all `chmod 600`):

| File | Contents |
| --- | --- |
| `~/.dreamlake/tokens.json` | the active token (`dreamlake-token` slot) |
| `~/.dreamlake/config.json` | `remote_url`, cached `namespace`, `device_secret` |

`login` and `auth env use` always rewrite the token and server **together**, so
the pair can never point at different environments.

`~/.dreamlake/auth.yml` additionally caches a token per environment — it
exists only so `auth env use` can switch without a new device-flow login, and
is never consulted to answer "what am I connected to":

```yaml file="auth.yml"
current: prod
envs:
  staging: { server, bss, auth, namespace, token }
  prod:    { server, bss, auth, namespace, token }
```

## Receipt web links

Successful `scene`, `artifact`, `workflow` and `share` commands print an
`open:` URL into the web app. The CLI derives it from the active server
URL. For the known deployments:

| Deployment | API server | Web app |
| --- | --- | --- |
| prod | `api.dreamlake.ai` | `dreamlake.ai` |
| staging | `staging-api.dreamlake.ai` | `staging.dreamlake.ai` |

Any other server maps conservatively: a leading `api.` label is stripped
(`api.example.com` → `example.com`); everything else — localhost, a custom
deployment — is printed unchanged rather than guessed. Set
`DREAMLAKE_WEB_URL` to print a different web origin (a trailing slash is
trimmed); it beats every derivation above.

> **Note:** The automatic `staging-api.dreamlake.ai` → `staging.dreamlake.ai` mapping
> is introduced in CLI 0.37.1. On 0.37.0 and earlier, staging receipts print
> the API host instead — set `DREAMLAKE_WEB_URL=https://staging.dreamlake.ai`
> there; the override works in every released CLI.

`dreamlake logout` removes the active environment's token and activates
the next saved one (or clears the connection if none is left).

> **Note:** State previously lived at `~/.config/dreamlake`. The first run of a newer
> CLI moves it into `~/.dreamlake` automatically — logins survive, nothing
> to redo.

## Optional Nymph setup after login

The login consent and local overview require CLI **0.86.0 or newer** and the
companion Nymph **0.1.32 or newer**. These are source requirements; do not treat
an older installed release as supporting this flow.

After successful interactive device login, the CLI offers an optional background
service with a default **No** response:

```text
Enable Nymph background service?
Supports uploads, command execution and other tools; access permissions are managed separately. [y/N]
```

Enter, No and cancellation leave service and access settings unchanged. Token
login, noninteractive stdin/stdout and CI do not prompt. Use `login --no-nymph`
to skip the offer. Existing local instances are shown for review; login does not
register a second daemon or automatically migrate a legacy installation. Setup
failure does not undo successful authentication.

```bash cli-help="nymph"
dreamlake nymph
dreamlake nymph --json
```

The overview keeps three things separate:

| Area | Authority |
| --- | --- |
| Configuration | The local `nymph.toml`: pacing and runtime settings |
| Access | A separate private `access.json`, bound to the control plane, namespace and machine |
| Runtime | Read-only local instance observations; missing observations remain unknown |

Fresh managed setup defaults both automatic upload and command execution access
to **denied**. Enabling the service does not grant either permission. Enrollment
still requires an authorized Lakeshore connection; this command does not create
a control plane or copy your personal login token into Nymph. A Nymph binary
without the separate-policy interface is refused before enrollment grants are
requested. Configure or upgrade Nymph first when that prerequisite is missing.

```bash cli-help="nymph setup"
dreamlake nymph setup --name alice/computers/laptop --lakeshore-id CONNECTION_ID
```

Configuration is managed independently of access:

```bash cli-help="nymph config"
dreamlake nymph config --name alice/computers/laptop
```

```bash cli-help="nymph config set"
dreamlake nymph config set --name alice/computers/laptop --poll-seconds 30 --max-invocations 4
```

Use CLI **0.86.1+** when selecting a named enrollment. It honors `--name` on
parent or final commands and rejects conflicting selections before any mutation.
CLI 0.86.0 could silently use the default profile for subcommand operations even
when a name was provided; upgrade before managing multiple enrollments.

Configuration edits validate with the installed Nymph parser before committing.
They do not change `access.json`. Select a managed enrollment by its full name
when the automatic `namespace/computers/hostname` name does not apply.

```bash cli-help="nymph access show"
dreamlake nymph access show --name alice/computers/laptop
```

```bash cli-help="nymph access grant"
dreamlake nymph access grant upload --name alice/computers/laptop
dreamlake nymph access grant command-execution --name alice/computers/laptop
```

Each grant has its own default-No confirmation. For automation, `--yes` explicitly
approves only that one permission. Revoke independently:

```bash cli-help="nymph access revoke"
dreamlake nymph access revoke upload --name alice/computers/laptop
dreamlake nymph access revoke command-execution --name alice/computers/laptop
```

Changes are saved locally and take effect after restarting that enrollment;
configuration inspection is not evidence of a running process applying them.

```bash cli-help="nymph restart"
dreamlake nymph restart --name alice/computers/laptop
```

The daemon fails closed on missing, malformed, foreign-scope or non-private managed
policies. Upload access controls Nymph's automatic session metadata, compute metrics
and experiment reporting; it does not enable a transcript archive by itself.
Command access covers remote jobs, exec, setup scripts, SSH and remote updates,
including their requested outputs. Server-side authorization is additionally
required: local consent cannot grant access to another account or bypass an API
ACL. Already-running commands finish under the prior startup snapshot until the
restart/drain completes.

Independent transcript archive services retain their own configuration and
credentials. The overview labels that boundary; changing Nymph consent does not
silently alter an existing archive collector. Legacy installations with no managed
access file retain their current behavior and are displayed as **unmanaged /
unknown**, not as newly consented or denied.
