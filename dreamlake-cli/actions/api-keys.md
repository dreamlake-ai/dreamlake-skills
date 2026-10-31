# Store a third-party API key in pass and the vault

Checked against CLI 0.88.0. A service API key (Runway, Heroku, OpenRouter, a
GitHub token) is kept in both stores: `pass` is the local GPG-encrypted copy on
the machine where the key was issued; Vault is the account-scoped copy other
machines, hosts and agents retrieve. The user types the key once, into `pass`.
Every other copy is piped from there. The value never goes in a command
argument, shell history, command output, a Note or the transcript. Do not ask
the user to paste it into the conversation.

Name the Vault entry `<owner>/cli/<service>/api-key` and set `--env` to the
variable the service's own tooling reads. Entries saved earlier under
`<owner>/env/<VARIABLE>` keep working; move them when next rotated.

1. Local copy, typed by the user (never by the agent):

   ```bash
   pass insert runway
   ```

2. Vault copy, piped from `pass`. Keep the first line only and strip its
   newline: `--stdin` stores bytes exactly, and a stored newline would later be
   exported inside the variable.

   ```bash
   pass show runway | head -n 1 | tr -d '\n' | dreamlake vault add \
     -p <owner>/cli/runway -n api-key --stdin --env RUNWAYML_API_SECRET
   ```

   To replace an existing entry, read `revision` from
   `dreamlake vault show -n <owner>/cli/runway/api-key` and add
   `--if-match <revision>`. Keep the printed request ID; on a timeout or an
   uncertain response repeat the identical pipe with `--request-id <id>` or
   check `vault write-status`, never a fresh write. Flags:
   [vault add](../reference/cli-command-reference.md#vault-import); recovery:
   [write recovery](../reference/cli-vault-write-recovery.md).

3. Confirm metadata only: `dreamlake vault show -n <owner>/cli/runway/api-key`.
   `show` and `list` print no values.

4. Load the key where a tool needs it. The saved `--env` names the export; an
   `ALIAS=path` selector adds a second name from the same entry:

   ```bash
   eval "$(dreamlake vault get -n <owner>/cli/runway/api-key --to-envs)"
   eval "$(dreamlake vault get -n <owner>/cli/runway/api-key \
     -n RUNWAY_SKILLS_API_SECRET=<owner>/cli/runway/api-key --to-envs)"
   ```

   Keep `vault get` inside `eval "$(…)"` or a `$(…)` assignment; without
   `--to-envs` it prints the raw value. On the machine that holds the store,
   `export RUNWAYML_API_SECRET="$(pass show runway | head -n 1)"` is the
   equivalent from `pass`.

Runway: the official Claude Code plugin `runway-api` (3.0.0,
`claude-plugins-official`) reads `RUNWAYML_API_SECRET` in its Python scripts
and `RUNWAY_SKILLS_API_SECRET` in its `runway-api.mjs` helper. Save the entry
with `--env RUNWAYML_API_SECRET` and export both names with the two-selector
`get` in step 4; it is one entry.

## Exceptions

| Symptom | Cause | Do |
|---|---|---|
| User asks for `dreamlake vault import --pass` | The flag is reserved; ordinary pass import is not implemented and is rejected. Only `--ssh` and `--pass-otp` import | Use the pipe in step 2, one entry per command |
| `Noninteractive add requires --stdin or --stdin-json` | Piped input without `--stdin` | Add `--stdin` |
| Exported variable ends in a newline or the API rejects the key | Entry stored with the trailing newline | Rotate: repeat step 2 with `head -n 1 \| tr -d '\n'` and `--if-match` |
| Export is named `API_KEY` | Entry saved without `--env` | Re-add with `--env <VARIABLE>` and `--if-match`, or use an `ALIAS=path` selector |
| Replace rejected without `--if-match` | The entry exists | Read `revision` from `vault show`; pass `--if-match` |
| Write timed out or returned an error | Outcome unknown; the write may have committed | `vault write-status --request-id <id>`, then retry only the identical input with the same ID |
| `pass show` prompts for GPG | The store's key is locked | The user unlocks it; do not copy the value out by hand |
