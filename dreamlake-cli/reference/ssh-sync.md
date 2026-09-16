# Selected SSH import

`dreamlake vault import --ssh` reads a local SSH config and saves selected items through
the existing vault entry API. It does not connect to hosts. The destination server
must have authenticated vault routes and encryption configured; unavailable routes
are reported as failures. No episode or other plaintext upload is used.

```shell
# Discover item IDs and review metadata without reading private keys or calling vault.
dreamlake vault import --ssh -p alice --config /absolute/path/to/config --dry-run

# Open an empty checklist, then review selected destinations before uploading.
dreamlake vault import --ssh -p alice --config /absolute/path/to/config
```

Omitting `--config` uses `~/.ssh/config`. Use arrows to move, Space to toggle,
Enter to review, and Escape or Ctrl-C to cancel. The final upload confirmation
defaults to No. Empty selection or cancellation before upload writes nothing.

Profiles and private-key exports are separate rows. Selecting `profile:dev` keeps
its key-file and jump-host references but does not upload those keys, another
alias, or jump-host credentials. A key row is a candidate file reference, not a
promise that the file is exportable. Only selected key files are read, after
confirmation. Hardware-backed keys remain references.

```shell
# Automation: explicit selections are the upload consent; no prompt opens.
dreamlake vault import --ssh -p alice --config /absolute/path/to/config --json \
  --select profile:dev

# Add the key only when exporting its private contents is intended.
dreamlake vault import --ssh -p alice --config /absolute/path/to/config --json \
  --select profile:dev --select key:dev:1
```

`--select` is repeatable. Non-TTY or `--json` uploads require at least one explicit
selection. `--dry-run` can list all discovered metadata without a selection.
The review goes to stderr; stdout contains one JSON result with no secret values.
Neither a generic `--yes` nor quiet mode authorizes key export.

## Destinations and conflicts

For prefix `alice`, `profile:dev` maps to `alice/ssh/profiles/dev` and `key:dev:1`
maps to `alice/ssh/keys/dev-1`. Key indexes are the one-based `IdentityFile` order
within that concrete Host block. Review them again after editing the config.
The prefix is required; the review shows the server, prefix, item type and exact
vault names. Authentication is pinned for the upload/retry session.

Profiles are string-field maps with schema `dreamlake-ssh-profile-v1`, the alias,
explicit hostname/user/port, optional jump reference, and a JSON string containing
identity-file references. They contain no executable SSH directives. Omitted
user/port remain unspecified; global defaults are not guessed. Keys use the
ordinary vault string type, preserving UTF-8 bytes, CRLF and trailing newlines.
No local key file is written and no suggested filename triggers file export.

An equal active destination is reported as verified, without another write.
A differing destination is a conflict until its revision is explicitly supplied:

```shell
dreamlake vault show -n alice/ssh/profiles/dev
dreamlake vault import --ssh -p alice --config /absolute/path/to/config --json \
  --select profile:dev --if-match profile:dev=3
```

`--if-match` is repeatable and applies only to its selected item. Revisions are
never automatically advanced on retry. A missing revision means create-only.
Source files and unselected vault entries are not deleted or modified.

## Partial results and retries

Each selected item reports `pending`, `success`, `failure`, or `unknown`. Cancel
during upload to stop subsequent entries; an in-flight request is allowed to
settle so its outcome can be reported. Completed writes remain saved. There is
no batch rollback. Non-successful final results exit with status 1.

The interactive retry keeps the same selection and source values. Automation can
use `--retry 1` (maximum 3). Successful entries are not rewritten. Failed requests
keep their original revision guard. Uncertain writes are **only read back**: an
equal destination is verified, while an absent, different or unreadable destination
remains unknown. A transport failure or malformed write acknowledgement does not
prove that nothing was saved.

The backend supports receipts for explicitly identified writes (see [write recovery](vault-write-recovery.md)). This importer does not yet attach those receipts to its source batch and cannot prove
which request produced an equal value, or safely replay an unresolved write.
Retry state is held in the current process, not a durable journal. Preserve the
redacted result and resolve unknown outcomes before starting a new invocation;
a new invocation is a new explicit request. No cross-process idempotency or
backend source-manifest support is claimed. A rejected source file needs a new
review after it is corrected.

## Pass OTP import and code retrieval

Choose one source: `--ssh` or `--pass-otp`. Redacted dry-run previews an explicitly
named store. Selected TOTP upload and owner-only code retrieval are available in CLI
`0.13.0` and Python `0.10.0`, with the deployed DreamLake API. For self-hosted
servers, use a backend with TOTP support. HOTP storage, explicit counter ownership, and retry-safe issuance are published in CLI 0.16.0 / Python 0.13.0, with the matching HOTP backend required; package publication and hosted acceptance remain separate. See [Vault operations](vault-operations.md). Ordinary `--pass` is reserved and rejected.

```shell
dreamlake vault import --pass-otp -p alice --dry-run \
  --store /absolute/path/to/password-store --gpg-home /absolute/path/to/gnupg
```

The dry-run result contains metadata and `uploaded: false`; decryption failures and
invalid OTP records cause a nonzero exit. Source selection is mutually exclusive,
and source-specific options cannot be mixed. Prefix placement works before
`vault`, after `vault`, or after `import`; conflicting prefixes fail.

Existing `vault ssh sync` and `vault pass sync --otp` commands remain compatibility
aliases. Prefer `vault import --ssh` and `vault import --pass-otp` in new scripts.
Import is a selected, one-way operation: it does not delete source entries or
perform tracked reconciliation. The word `sync` is reserved for that future
capability rather than a promise made by the compatibility aliases.

## Supported sources

Discovery parses text without running OpenSSH, commands, plugins or config
conditions. `Include` is reported and not followed. `Match`, global defaults,
wildcard inheritance and blocks containing wildcard/negated patterns are not
resolved. Unsupported directives are omitted with line-number warnings, including
`ProxyCommand`, `LocalCommand` and host-key-checking overrides. The result is an
explicit-fields profile, not a fully evaluated OpenSSH configuration.

Concrete aliases must start with a letter/digit and contain only letters, digits,
underscores or hyphens, up to 128 characters. Duplicate aliases (including case
variants), dotted aliases and unsafe aliases are excluded with warnings; they
are never silently renamed. Simplify the selected config explicitly if necessary.
Quoted values, comments, CRLF and `Keyword=value` are supported. Ambiguous escaped
syntax or unsupported connection-field values exclude the affected profile.

Only absolute and `~/` key paths can offer export rows. Relative, tokenized,
wildcard, environment-expanded and `none` identity paths stay references.
Private-key files must be owned by the current user with no group/other permission
bits, and use a supported PEM/OpenSSH private-key envelope. Config files must not
be group/other writable. Both must be regular files, at most 64 KiB, valid UTF-8
without NULs, with no symlink components or hard links. File identity and changes
are checked while reading; serialized vault values must also fit 64 KiB.

Implementation tracking: [SSH sync #241](https://github.com/dreamlake-ai/dreamlake-workspace/issues/241)
and [master #247](https://github.com/dreamlake-ai/dreamlake-workspace/issues/247).
CLI `0.13.0` and Python `0.10.0` passed production import and TOTP checks; see the
[release evidence](https://docs.dreamlake.ai/dev/notes/vault-runtime/).
After importing credentials, verify the intended host login separately.

```shell
# Create only the selected login.gpg registration under alice/otp/login.
dreamlake vault import --pass-otp -p alice/otp --store /canonical/test-store --select login
# Explicitly reveal a code; never put it in logs or command arguments.
dreamlake vault otp -p alice/otp -n login
dreamlake vault otp -p alice/otp -n login --to-json
```

```python
result = client.vault.import_entries(source="pass-otp", prefix="alice/otp",
                                    store="/canonical/test-store", select=["login"])
code = client.vault.otp("login", prefix="alice/otp")
code_json = client.vault.otp("login", prefix="alice/otp", to_json=True)
```

Selection is mandatory, even on a TTY; interactive upload additionally asks
`[y/N]`. `--json` is noninteractive, and explicit `--select` consents to those
paths only. Python never prompts. Pass paths omit `.gpg` and use canonical
slash-separated names. GPG uses batch/no-tty/pinentry-error. Apply decrypts only
selected files and excludes adjacent password lines. HOTP registrations default to inactive; explicit `--hotp-owner dreamlake` opts into counter ownership. It validates
the entire batch and rechecks encrypted source bytes before upload. There is no
persisted preview plan; apply validates a fresh selection each time.

OTP import creates entries only. Conflicts stop the batch; OTP does not
accept SSH `--if-match` or `--retry` options. Successful earlier writes are
retained. An `unknown` result means a write may have committed; inspect `show`
and securely compare with explicit `get` before deciding what to do. Never
blindly repeat an unknown import. Identified-write recovery exists separately; import batch outcomes still require explicit reconciliation.

For TOTP, `otp --to-json` returns only `code` and `validUntil`; without it, output is the
code. The server clock determines the code, and entry expiry may shorten its
validity. Scoped keys cannot generate codes. Explicit `vault get` instead
reveals the registration JSON string, including its seed. The target login
service enforces one-time acceptance. HOTP requires explicit authority and a durable `--request-file`; it advances only on an explicit issuance request and replays that request after uncertain responses. The legacy pass sync command
continues to provide preview only.
