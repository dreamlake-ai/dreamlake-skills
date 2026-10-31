<!-- generated from https://cli.dreamlake.ai/vault-api-keys.md at 0.97.2 1633dd9; do not edit -->

# Third-party API keys in pass and Vault

Checked against CLI 0.88.0. A third-party API key (Runway, Heroku, OpenRouter,
a GitHub token) lives in two places. The local `pass` store is the GPG-encrypted
copy on the machine where the key was issued. Vault is the account-scoped copy
that other machines, hosts and agents retrieve. Both hold the same bytes. The
key is typed once, into `pass`; every other copy is piped from there. It never
appears in a command argument, in shell history, in command output, in a Note
or in an agent transcript.

## Naming

| Store | Name | Example |
| --- | --- | --- |
| `pass` | `<service>`; the first line is the secret, later lines are notes | `runway` |
| Vault entry | `<owner>/cli/<service>/api-key` | `alice/cli/runway/api-key` |
| Vault `--env` | the variable the service's own tooling reads | `RUNWAYML_API_SECRET` |

`<owner>/cli/<service>/…` groups every key that a CLI, SDK or agent plugin
reads under one prefix, so `dreamlake vault list -p alice/cli` audits all of
them and one prefix policy can cover them. Use a different leaf when a service
issues more than one kind of credential (`alice/cli/gh/github-token`). Entries
saved earlier under `<owner>/env/<VARIABLE>` keep working; move them to the
convention when they are next rotated.

`--env` is saved metadata, not a second copy of the secret: `vault get
--to-envs` uses it as the exported variable name. Without it the export is the
last path segment uppercased (`API_KEY`), which no tool reads.

## Store the key

```shell
# 1. Local copy. pass prompts for the value; it is not on the command line.
pass insert runway

# 2. Vault copy, piped from pass. --stdin stores the bytes exactly as received,
#    so keep the first line only and drop its newline.
pass show runway | head -n 1 | tr -d '\n' | dreamlake vault add \
  -p alice/cli/runway -n api-key --stdin --env RUNWAYML_API_SECRET

# 3. Confirm metadata. show never prints the value.
dreamlake vault show -n alice/cli/runway/api-key
```

`vault add` takes the value only from stdin or from a masked prompt; there is
no value flag. `--stdin` is exact: a trailing newline would be stored and later
exported inside the variable, which is why the pipe strips it.

The write prints metadata and a request ID and no secret. Keep the ID. After a
timeout or an uncertain response, repeat the identical pipe with
`--request-id <id>`, or look the write up with
`dreamlake vault write-status --request-id <id>`; see
[Vault write recovery](cli-vault-write-recovery.md).

## Rotate the key

Rotate the local copy first, then replace the Vault entry against its current
revision. `vault add` replaces an existing entry only with `--if-match`.

```shell
pass insert -f runway
dreamlake vault show -n alice/cli/runway/api-key        # read "revision"
pass show runway | head -n 1 | tr -d '\n' | dreamlake vault add \
  -p alice/cli/runway -n api-key --stdin --env RUNWAYML_API_SECRET --if-match 1
```

## Load the key

```shell
# The saved --env names the variable: export RUNWAYML_API_SECRET='…'
eval "$(dreamlake vault get -n alice/cli/runway/api-key --to-envs)"

# The same value under a second name, in the same call. An ALIAS=path selector
# sets the exported name for that selector only.
eval "$(dreamlake vault get \
  -n alice/cli/runway/api-key \
  -n RUNWAY_SKILLS_API_SECRET=alice/cli/runway/api-key --to-envs)"

# From pass, on the machine that holds the store. $(…) drops the newline.
export RUNWAYML_API_SECRET="$(pass show runway | head -n 1)"
```

Keep `vault get` inside `eval "$(…)"` or a `$(…)` assignment. Without
`--to-envs` it prints the raw value to stdout, which belongs in a pipe or an
assignment and never in a terminal, a log or an agent transcript.
`--env-prefix <prefix>` prepends a string to every exported name when a tool
expects namespaced variables.

### Runway

The official Claude Code plugin `runway-api` (3.0.0, `claude-plugins-official`)
reads the key from two variables: its Python scripts read `RUNWAYML_API_SECRET`
and its `runway-api.mjs` helper reads `RUNWAY_SKILLS_API_SECRET`. Save the
entry with `--env RUNWAYML_API_SECRET` and export both names with the
two-selector `get` above. The variables hold the same key; there is one entry.

## `vault import --pass` is reserved

`dreamlake vault import` lists a `--pass` flag, but it is reserved: ordinary
pass entry import is not implemented and the command rejects it. Only `--ssh`
and `--pass-otp` import. The pipe above is the supported path from `pass` to
Vault for an API key, one entry per command. The two stores are kept in step by
hand: after `pass insert -f`, repeat the pipe with `--if-match`.

## Rules

- The value is never a command argument. `vault add` has none; do not wrap it
  in a helper or an alias that takes one.
- Metadata is safe to print (`vault show`, `vault list`, write receipts);
  values are not (`vault get`, `pass show`).
- One entry per key, named `<owner>/cli/<service>/api-key`, with `--env` set
  to the variable the tool reads. Add a second name at retrieval time with an
  `ALIAS=path` selector, not with a second entry.
- Keep the request ID until the write is confirmed; it contains no secret.
