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
> now manages MuJoCo environments (see the Envs page). There is no alias —
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
dreamlake login --env dev \
  --url https://dev-api.example.com \
  --bss https://dev-bss.example.com
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
| BSS URL | `DREAMLAKE_BSS_URL` |
| Token | `DREAMLAKE_API_KEY` |
| Web app URL (receipt `open:` links) | `DREAMLAKE_WEB_URL` |

The effective connection lives in two files shared with the Python SDK
(all `chmod 600`):

| File | Contents |
| --- | --- |
| `~/.dreamlake/tokens.json` | the active token (`dreamlake-token` slot) |
| `~/.dreamlake/config.json` | `remote_url`, `bss_url`, cached `namespace`, `device_secret` |

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

Successful `env`, `artifact`, `workflow` and `share` commands print an
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
