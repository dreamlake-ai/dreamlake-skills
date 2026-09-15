# Mount a queue server

**Unreleased.** These commands are implemented in the development branch. They
require the matching DreamLake server change; an installed release may still
report `unknown command 'queues'`. They have not been released or verified on a
hosted deployment.

1. **Check your DreamLake login.** These commands use the same environment and
   account as your other DreamLake commands. The first version supports personal
   DreamLake namespaces.

   ```bash
   dreamlake env list
   dreamlake profile
   ```

2. **Mount your Lakeshore server.** Use its HTTPS URL and choose a short prefix.
   The command prints the selected DreamLake server and namespace, then asks for
   the namespace on Lakeshore and an access token in a hidden prompt.

   ```bash
   dreamlake queues mount --uri "$LAKESHORE_URL" --prefix lab
   ```

   Paste a **Lakeshore access token**, created by your Lakeshore administrator.
   The server admin token is for creating access tokens; do not paste it here.
   DreamLake verifies the access token and stores it in your DreamLake Vault.
   The CLI does not read an admin token or reuse a saved Lakeshore CLI login.

   Your DreamLake namespace and Lakeshore namespace are separate. For example,
   `--namespace geyang --lakeshore-namespace default` stores the mount in
   DreamLake's `geyang` and accesses Lakeshore's `default`. Neither is inferred
   from the other.

3. **Look inside the server.** `lab` identifies your mount. Queue names appear as
   `lab/training`, for example; the prefix does not rename the remote queue.

   ```bash
   dreamlake queues inspect lab
   dreamlake queues list lab
   dreamlake queues jobs lab
   dreamlake queues workers lab
   ```

`inspect` performs a live connection check. The other commands read current
collections through DreamLake; the Lakeshore access token stays on the
DreamLake server. DreamLake controls who can use the mount, while the
Lakeshore token determines what that server permits. A prefix is a name, not
an authorization boundary.

For scripts, provide both namespaces explicitly and read a token from stdin:

```bash
cat /path/to/lakeshore-access-token | dreamlake queues mount \
  --uri "$LAKESHORE_URL" --prefix lab \
  --namespace geyang --lakeshore-namespace default --token-stdin --json
```

The file must contain an **access token**, not the server admin token.

To list registrations, replace an expired or revoked access token, or remove a
mount:

```bash
dreamlake queues mounts
dreamlake queues token lab
dreamlake queues unmount lab
```

`token` prompts for a replacement token; it also accepts `--token-stdin`.
`unmount` removes the DreamLake registration. It leaves the server running,
retains its Vault entry, and does not revoke the remote token. Replacing a token
also retains the old Vault entry. Revoke unused tokens on Lakeshore separately.

All commands support `--namespace ` and `--json`.
`mounts` supports `--page` and `--page-size`; `jobs` supports `--limit` and
`--offset`.

This first slice registers a server and reads its collections. Job submission
and changes to queues or workers are separate work. For direct Python queue
usage, see the [dreamlake-lakeshore Python SDK](https://docs.dreamlake.ai/lakeshore/python-sdk).
