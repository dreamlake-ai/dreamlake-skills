# Host enrollment

`dreamlake hosts enroll` bootstraps a user-owned nymph over your existing SSH
connection, then waits for the backend to confirm that exact enrollment online.
Provider registration is not required. It requires the new authenticated Hosts
API and a control plane supporting identity-bound grants and signed reconnect;
these changes must be deployed together. `--dry-run` only validates inputs and
does not contact the server or target.

The target needs Python 3, OpenSSL, an accessible systemd user manager, and user
linger enabled for service persistence after logout. Enrollment never uses sudo.
It reuses an installed `nymph`, or downloads the official installer into the
user-local binary directory. `--nymph-version` selects an installer version when
the binary is absent. The target generates and retains its nymph private key;
only its public key and Unix username go to the enrollment API. Short-lived
grants travel to the target over SSH stdin, not process arguments or logs.

Check the target account before enrollment:

```shell
ssh bos14-ctrl 'systemctl --user show-environment >/dev/null && loginctl show-user "$(id -un)" -p Linger --value'
```

If this prints `no`, enable lingering for that account:

```shell
ssh bos14-ctrl 'loginctl enable-linger "$(id -un)"'
```

If local policy denies this operation, ask the host administrator to enable it.
Enrollment checks these prerequisites before creating an identity or requesting
a grant.

Use `--lakeshore-id` when your namespace has multiple control-plane connections.
The command prints a request ID before enrollment. After an interrupted request,
repeat the same inputs with `--request-id <id>`. If the API returns `retryAt`, wait
until that time before starting a new request. JSON errors retain the request ID
and available operation/retry fields.
`--wait-seconds` bounds readiness polling (default 60). A timeout reports
`pending` and exits nonzero; it does not claim enrollment succeeded. Repeat
execution preserves the target identity and reuses the user service. Runner/job
readiness is a separate check from a connected nymph.

Direct enrollment on the target host is planned but has no implemented command
syntax yet. For the broader workflow, see the upcoming
[host enrollment guide](https://docs.dreamlake.ai/hosts/enroll) in the main
DreamLake docs (not yet deployed). This page is the CLI input reference.

```shell
dreamlake hosts enroll -p fortyfive/bos14 -n bos14-ctrl --ssh bos14-ctrl
dreamlake hosts status fortyfive/bos14/bos14-ctrl --json
dreamlake hosts status 'fortyfive/bos14/*' --json
```

For configuration-only validation:

```shell
dreamlake hosts enroll -p fortyfive/bos14 -n bos14-ctrl \
  --ssh bos14-ctrl --dry-run

# Equivalent full name, with structured output:
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl \
  --ssh '-i "/Users/ge/My Keys/key" \
    -J ge@bastion.example.com \
    -p 2222 geyang@bos14-ctrl.internal' --dry-run --json
```

Names have exactly three components: namespace/group/host. A matching explicit
prefix and embedded prefix are accepted; conflicting prefixes and wildcards are
rejected. Each component is 1–64 letters, digits, underscores or hyphens and starts
with a letter or digit. A namespace in a name does not grant access to it.
The control-plane namespace comes from the selected connection and can differ
from the DreamLake namespace.

## JSON input

```shell
dreamlake hosts enroll --config ./bos14-host.json --dry-run --json
```

```json
{
  "name": "fortyfive/bos14/bos14-ctrl",
  "ssh": {
    "host": "bos14-ctrl.internal",
    "user": "geyang",
    "port": 2222,
    "identityFile": "/Users/ge/.ssh/bos14_ed25519",
    "jumpHost": "ge@bastion.example.com",
    "options": { "ServerAliveInterval": "30" }
  }
}
```

The file may also contain `prefix`. Explicit CLI name/prefix fields override
those file fields, then prefix conflicts are checked. `--ssh` replaces the
entire file SSH object. Unknown fields are rejected. Identity files are local
paths, never embedded key contents. Use either `ssh.user` or `user@host`, not both.
`--json` controls output only.

SSH argument text is tokenized without shell expansion or evaluation; multiline
whitespace, line continuations, and quoted paths are supported. Do not include
`ssh` itself or a remote command. The initial supported flags are `-i`, `-J`,
`-p`, `-o`, `-l`, and `-F`, each followed by a separate value. Supported `-o`
settings are BatchMode, ServerAliveInterval, ServerAliveCountMax, ConnectTimeout,
IdentitiesOnly, StrictHostKeyChecking, and UserKnownHostsFile. Use an existing
SSH config alias for more advanced transport settings. Preview validates syntax,
not whether an identity file exists, an SSH alias resolves, or SSH authentication works.
Passwords are not accepted in arguments or JSON. Future interactive enrollment
should let OpenSSH prompt for target/jump-host passwords locally; the preview
does not attempt authentication and does not require agent forwarding.

Group status accepts `--page` (1–100000) and `--page-size` (1–100). Exact host
lookup starts at the first page and follows matching pages automatically.

Host status is read from the backend; enrollment succeeds only when the returned
enrollment ID reports online. Infrastructure provisioning and workload execution
remain separate from this operation.

## Save selected credentials after enrollment

**Available in CLI 0.15.0; hosted acceptance pending.** Requires the matching host-binding backend. enrollment succeeds
independently of saving. After confirmed enrollment, an interactive command asks
whether to save selected credentials for your other devices, defaulting to N.
`--save-credentials` gives consent; `--no-save-credentials` declines. `--quiet`
only suppresses progress. JSON/noninteractive calls never prompt automatically.

```shell
# Re-enter the target password securely after enrollment (masked prompt).
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
  --save-credentials --target-password ge/bos14/login

# Explicit, separate target and jump-key exports.
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh '-J jump bos14-ctrl' \
  --save-credentials --target-key ge/bos14/key=/secure/target-key \
  --jump-key jump=ge/jump/key=/secure/jump-key

# Automation: exact UTF-8 bytes from a protected file/pipe, never argv secrets.
dreamlake hosts enroll -n fortyfive/bos14/bos14-ctrl --ssh bos14-ctrl \
  --save-credentials --target-password ge/bos14/login \
  --password-fd ge/bos14/login=3 --json 3</secure/target-password
```

Selecting a target never selects its jump credentials or other keys. Personal
vault paths are independent of the host namespace. Missing selection on an
interactive save opens source selection; automation must supply it explicitly.
Only selected private regular files are read; encrypted key files retain their
original bytes and still require their existing passphrase on use.

Saving does not authorize backend SSH. Do not put passwords/private keys in
configuration JSON. OpenSSH password input cannot be recovered: saving requires
secure re-entry. Cancellation/failure retains successful enrollment and writes;
requested incomplete saving exits nonzero with separate `credentials` outcomes.

An `unknown` entry write includes a stable request ID for `vault write-status`.
A `saved_unbound` result includes exact `binding` metadata for retry without SSH
or secret rereads:

```shell
dreamlake vault bind --host-id HOST_ID --enrollment-id ENROLLMENT_ID \
  --entry-id ENTRY_ID --entry-revision 1 --role target --endpoint bos14-ctrl \
  --kind password
dreamlake vault bindings --host-id HOST_ID --enrollment-id ENROLLMENT_ID
```

Binding management is account-only, idempotent for identical references and
rejects replacement with a different entry/revision. Host setup, remote key
rotation/revocation and explicit binding release are separate follow-up work.

## Cross-component integration check

The repository includes a repeatable check against an isolated local Hosts API,
control plane, persistent databases, and a compiled nymph binary:

```shell
pnpm build
node scripts/test-hosts-integration.mjs \
  /path/to/protected-test-environment.json /path/to/nymph
```

The protected JSON supplies `remote`, `namespace`, `token`, `outsiderToken`, and
`lakeshoreId`; use test-only credentials and a loopback server. The test launches
the actual CLI and nymph subprocesses, verifies online status, stable explicit
request replay, consumed-token and token-absent reconnect, and forbidden access
before target mutation. It uses local SSH/service adapters, so this is not a
live-network SSH or actual-systemd test. Real target access and runner execution
need their own acceptance checks. Test processes are stopped and temporary
identity files removed afterward.

## Paired Python API

Python 0.12.0 is the paired released SDK. Its library never prompts;
application code may collect a password explicitly before enrollment:

```python
from getpass import getpass
from dreamlake import DreamLakeClient
from dreamlake.host_credentials import HostCredential

client = DreamLakeClient()
result = client.hosts.enroll(
    "fortyfive/bos14/bos14-ctrl", ssh="-J jump bos14-ctrl",
    request_id="bos14-save-001", save_credentials=True,
    credentials=[
        HostCredential("target", "bos14-ctrl", "ge/bos14/login", "password",
                       password=getpass("Password to save: ")),
        HostCredential("jump", "jump", "ge/jump/key", "private_key",
                       key_file="/secure/jump-key"),
    ],
)
# Inspect redacted outcomes even when enrollment succeeded.
print(result["credentials"])
with client.http() as http:
    from dreamlake.vault import Vault
    vault = Vault(http)
    for item in result["credentials"]["entries"]:
        if item["status"] == "unknown":
            receipt = vault.write_status(request_id=item["requestId"])
        elif item["status"] == "saved_unbound":
            binding = vault.bind_host_credential(**item["binding"])
```

A missing receipt does not prove failure. Interrupting a Python entry write
retains `unknown`; interruption after saving retains `saved_unbound` and its
binding arguments. Neither recovery operation rereads a secret or reconnects SSH.

Enrolled hosts use a persistent user service with `runtime.keep_alive_s = -1`, so an idle host remains available instead of exiting after five minutes. Re-enrolling the same host with the fixed client updates the generated configuration. Nymph’s default idle policy for other launch modes is unchanged. This fix is unreleased; deployed hosts require the updated client and reconfiguration.

Re-enrollment regenerates the service configuration. Restore reviewed custom settings, including `private_tracked`, after re-enrollment and verify a fresh signed capability poll before private submission. Re-enrollment does not preserve custom configuration.
