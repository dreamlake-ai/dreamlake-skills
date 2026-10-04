# Cloud configuration in Vault

**CLI 0.43.0.** Cloud configuration import and restore use the existing Vault
API. Dotfile filename metadata requires the server dotfile-validation update.
No provider login is performed.

## Preview and import

```bash cli-help="vault cloud import"
# No --file: list standard candidate paths without opening their contents.
dreamlake vault cloud import --provider aws -p alice/aws/dev
# Explicit selections: preview names, sizes and profile metadata, without upload.
dreamlake vault cloud import --provider aws -p alice/aws/dev \
  --file "$HOME/.aws/config" --file "$HOME/.aws/credentials"
# Repeat the selection with --apply to upload.
dreamlake vault cloud import --provider aws -p alice/aws/dev \
  --file "$HOME/.aws/config" --file "$HOME/.aws/credentials" --apply
dreamlake vault cloud import --provider gcp -p alice/gcp/dev \
  --file /private/config/service-account.json --apply
```

Each file becomes one exact-content string entry with its original basename in
`fileName`. Entry leaves replace dots with dashes and remove leading/trailing
dashes (`.env.local` becomes `env-local`). Name collisions fail before any write.
Use different prefixes for files with the same basename. A multi-profile AWS
file remains one file; the prefix does not select or filter a profile.

AWS preview reports section/profile names, never property values. GCP accepts
service-account, authorized-user ADC and external-account credential JSON and
reports only credential type and project identifiers. `--provider other` accepts
selected UTF-8 text files without interpreting them. Files must be nonempty,
owned by the current user, not group/other writable, regular and not symlinks or
hard links. The JSON-encoded string must fit Vault's 64 KiB limit. BOM, line
endings and trailing whitespace are preserved. No references, credential
processes, URLs or neighboring files are followed.

Discovery follows the standard locations and overrides documented by
[AWS](https://docs.aws.amazon.com/sdkref/latest/guide/file-location.html) and
[Google](https://cloud.google.com/docs/authentication/application-default-credentials).
Discovery does not search SSO caches or gcloud databases. Upload always requires
explicit `--file` selection and `--apply`.

Existing entries are never silently replaced. For one explicitly selected file,
use `--if-match REVISION`. Each upload prints a nonsecret request ID before the
write; `--request-id ID` permits an exact single-file retry after reconciling
`dreamlake vault write-status --request-id ID`. Changed contents/options require
a new ID. A failed batch may have partially completed: inspect the per-entry
statuses. Readback verifies exact content; no hashes or secret values are printed.

## Restore

**Starting with CLI 0.43.1**, home-relative restore destinations use the receiving machine's home directory. Shell-expanded
`"$HOME/.aws/config"` works as usual; the CLI also expands a literal
`'~/.aws/config'`, `'$HOME/.aws/config'`, or `'${HOME}/.aws/config'` itself.
Do not pass the old machine's absolute home path. Home-relative paths cannot
escape the home directory through `..`. Other relative paths remain relative
to the current working directory. File contents remain byte-for-byte unchanged;
absolute paths inside configuration files are not rewritten.

```bash cli-help="vault cloud restore"
# Preview checks metadata and destination without retrieving the secret.
dreamlake vault cloud restore -n alice/aws/dev/credentials \
  --to '~/.aws/credentials'
# Write only after explicit --apply; existing files additionally need --overwrite.
dreamlake vault cloud restore -n alice/aws/dev/credentials \
  --to '~/.aws/credentials' --apply
```

Restore is POSIX-only because it guarantees mode `0600`. Its destination directory
must already exist, be owned by you, and not be group/other writable. A private
temporary file is flushed and published atomically. Symlink destinations,
nonregular files and multiply linked files are refused even with `--overwrite`.
No-overwrite publication uses an atomic exclusive link. Overwrite rechecks the
destination before rename; concurrent modification is refused when detected.
Use a directory under your control. No plaintext is printed or retained in a
separate backup. Restore one named entry at a time; repeat for a related file.

Restoring files does not establish valid cloud access. SSO tokens can expire and
external-account configurations can reference machine-specific resources. This
does not create a DreamLake cloud connection or change environment variables.

## Local validation

The focused `vault-cloud.test.ts` suite covers preview redaction, source safety,
uncertain writes, exact restores and overwrite races. For the actual server,
start its disposable `src/vault/serveTestFixture.ts` harness and run
`node scripts/test-vault-cloud-integration.mjs /path/to/synthetic-fixture.json`
from the CLI repository. The script refuses non-loopback destinations and uses
only synthetic credentials. This establishes local compatibility, not release
or live cloud-provider authentication.
