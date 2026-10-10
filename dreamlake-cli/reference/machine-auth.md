# Machine authentication

This feature requires the matching CLI, Nymph and DreamLake server releases.
It is not enabled by upgrading documentation or the public skill alone.

A managed machine has a dedicated namespace service account, an enrollment and
an Ed25519 proof-of-possession identity. It has no human bearer token. DreamLake
checks enrollment, current control-plane keys, account revocation and explicit
resource grants on every machine request. Requests have a 60-second timestamp
window and single-use nonces, bound to the configured deployment audience.

## Inspect and select an identity

```bash cli-help="machine"
dreamlake machine self
dreamlake machine host 0123456789abcdef01234567
dreamlake machine project 0123456789abcdef01234567
```

```bash cli-help="auth identity"
dreamlake auth identity
dreamlake --identity machine profile
dreamlake --identity user profile
```

`~/.config/dreamlake/machine.json` selects the machine by default when present.
`DREAMLAKE_MACHINE_CONFIG` selects another absolute configuration path.
`--identity user|machine` selects one invocation; `DREAMLAKE_IDENTITY=user|machine`
selects a process and its children. Managed background agents set the latter to
`machine`, independently of any interactive command. Identity selection changes
which credentials the process uses; it never grants additional backend authority.
A broken machine configuration fails closed and never falls back to a human token.

`dreamlake login` reuses the existing browser/device flow and writes only personal
`~/.dreamlake` files. `logout` and `auth env use` also affect only personal files.
Use separate Unix accounts for concurrent human users. To inspect personal
access after login, use `dreamlake --identity user profile`. Machine configuration
and keys are not written by login, logout or environment switching.

The initial signed surface supports identity and explicitly granted host/project
metadata reads. Other commands require personal identity and fail with an
identity-selection hint when invoked as a machine. This does not yet provide
machine-authorized upload, Notes or all other human API capabilities.

## Protected configuration

The provisioner writes this non-secret manifest and its key as owned regular files
with mode 0600. Parent directories must be owned by the machine user or root and
not writable by other users. The CLI refuses symlinks for the manifest/key.

```json
{
  "version": 1,
  "remote": "https://api.dreamlake.ai",
  "audience": "operator-configured-deployment-audience",
  "enrollmentId": "0123456789abcdef01234567",
  "keyFile": "/home/ubuntu/.local/state/dreamlake/hosts/host-hash/identity.key"
}
```

The service principal is separate from the Nymph control-plane principal. The
existing backend binds both to one enrollment key, with different signature
domains and deployment audience; neither protocol's signature can be replayed
into the other. Do not copy personal tokens or a shared fleet key into this file.

The CLI reloads the protected key for each request. Nymph's existing key rotation
and overlap deadline remain authoritative. Revoke the service account with
`dreamlake --identity user service-accounts revoke namespace/ACCOUNT_ID`; verify
that `dreamlake machine self` now fails. A pending control-plane revocation must
be retried and is not proof of remote shutdown. Offline identity inspection is
not authentication success: machine profile requires an authenticated API reply.

## Recovery and rollback

For 401/403 inspect clock synchronization, enrollment binding, account status,
key expiry and grants. For unavailable replies inspect the control-plane link.
Do not print keys, HTTP headers, tokens or raw server errors in diagnostic logs.
Repair ownership/configuration through the provisioning channel, then restart
Nymph to rerun its idempotent required setup hooks. Keep the machine in setup
until CLI authentication, authorized host access and both installed skills pass.

Deploy server schema/index prerequisites and Nymph required-setup support before
enabling managed CLI bootstrap. Pin CLI version and checksums in server config.
Roll back by disabling new managed launches, retaining failed instances for
inspection, and restoring the previous pinned artifacts. Revoked identities
remain revoked; rollback must not restore their authority. Existing personal
logins and installed custom skills survive this procedure.
