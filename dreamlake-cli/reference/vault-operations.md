# Vault operations

**CLI 0.16.0 and Python 0.13.0 are published.** These
operations require the matching Vault backend. Check the
[Vault runtime note](https://docs.dreamlake.ai/dev/notes/vault-runtime/) for hosted
availability; a local build or package release is not deployment evidence.

## HOTP: take ownership explicitly

Import selected registrations as inactive by default. Stop other generators
before explicitly activating DreamLake as the counter owner. For pass-otp, the
stored counter is the last generated counter; activation normalizes it to the
next unused value without writing back to pass. Initial activation supports SHA1
with at least a 128-bit seed; unsupported algorithms remain inactive.

```shell
dreamlake vault import --pass-otp -p alice/otp \
  --store /absolute/password-store --select login
dreamlake vault otp -n alice/otp/login \
  --activate --counter-owner dreamlake --if-match 1

# Alternatively, take ownership during a new import.
dreamlake vault import --pass-otp -p alice/otp \
  --store /absolute/password-store --select another-login --hotp-owner dreamlake
```

```python
client.vault.import_entries(
    source="pass-otp", prefix="alice/otp", store="/absolute/password-store",
    select=["login"],
)
client.vault.activate_otp("alice/otp/login", counter_owner="dreamlake", if_match=1)
```

Each new issuance needs a new private request-file path. After a timeout, process
restart, or uncertain response, reuse the **same file**, never a fresh one.
Its immutable account/origin/entry/revision/request metadata contains no seed,
code, counter or token. Both file and directory must support durable `fsync` on
POSIX; failures send no issuance request. Avoid shared or externally modified
request directories. Hardware/filesystems that ignore fsync cannot promise durability.

```shell
mkdir -m 700 -p "$HOME/.dreamlake/hotp-requests"
dreamlake vault otp -n alice/otp/login \
  --request-file "$HOME/.dreamlake/hotp-requests/login-request-001.json"
# Reuse this exact invocation to recover an uncertain response.
```

```python
code = client.vault.otp(
    "alice/otp/login", request_file="/private/requests/login-request-001.json"
)
```

Receipts are encrypted and recoverable for 24 hours. This is a recovery deadline,
not HOTP code expiry. Missing/expired receipts leave an ambiguous outcome; the
original tuple cannot advance the counter again. Scoped retrieval keys cannot
generate codes. General entry replacement cannot roll an HOTP counter back.

## Metadata pages

**Starting with CLI 0.43.1:** when both stdin and stdout are terminals,
`vault list` opens a searchable, selectable metadata list. Use Up/Down to move,
Space to toggle entries, `/` to filter by name, Enter to return selected metadata,
and Escape or Ctrl-C to cancel. With no checkmarks, Enter selects the focused row.
Filtering preserves selections. No secret values are retrieved.

Pipes and redirected output retain JSON. `--to-json` explicitly requests JSON
even in a terminal. `--tree` remains the separate prefix-policy browser.

```bash cli-help="vault list"
# Interactive on a terminal; JSON when piped or redirected.
dreamlake vault list -p alice
# Always emit metadata JSON.
dreamlake vault list -p alice --to-json
```

```shell
dreamlake vault -p alice/remote list
dreamlake vault -p alice/remote list --limit 50
dreamlake vault -p alice/remote list --limit 50 --cursor "$cursor"
dreamlake vault -p alice/remote list --include-deleted
```

```python
entries = client.vault.list(prefix="alice/remote")
page = client.vault.list_page(prefix="alice/remote", limit=50)
if page["nextCursor"] is not None:
    page = client.vault.list_page(prefix="alice/remote", limit=50, cursor=page["nextCursor"])
```

Default listings return all metadata by following 100-entry pages. Explicit pages
allow 1–200 entries and return `nextCursor`, or null at completion. Keep account,
prefix and retired filter unchanged. Traversal follows binary name order and is
not a snapshot: new earlier names require a fresh listing; deleted names can
vanish. No list operation reveals payloads. Legacy unpaged HTTP remains unbounded
until all consumers migrate.

## Release a host reference

Use exact metadata from the saved binding. Unbinding works after host deletion,
but preserve the binding receipt first. It does not revoke a remote key/password,
delete an active secret, or bypass retired-entry retention.

```shell
dreamlake vault unbind --binding-id "$binding_id" \
  --entry-id "$entry_id" --entry-revision 1
```

```python
client.vault.unbind_host_credential(
    binding_id=binding_id, entry_id=entry_id, entry_revision=1,
)
```

## Organization/team management preview (not released)

Discover scope IDs with `dreamlake vault scopes`. Put `--scope org:<id>` or `--scope team:<id>` before supported entry or management commands. Personal remains the default; recovery keeps the original actor, scope and request ID, with no fallback on denial.

```shell
dreamlake vault --scope org:<id> capabilities
dreamlake vault --scope org:<id> secret-copy-preview --name org/path --destination-scope team:<id> --destination-name team/path --if-match 1 --request-id copy-001
dreamlake vault --scope org:<id> secret-copy --operation-id <id> --action commit
dreamlake vault --scope org:<id> secret-copy-recover --request-id copy-001
dreamlake vault --scope org:<id> policy
dreamlake vault --scope org:<id> policy --export false --if-match 0 --request-id policy-001
dreamlake vault --scope org:<id> audit
```

Use `--destination-scope personal` for an explicit personal destination. `secret-copy --action status` recovers committed identity; `--action cancel` permanently cancels a pending preview. Metadata never includes secret values. Preview expires after 24 hours, policy updates compare revision, and commits recheck source and destination authority. Export/policy requires org OWNER or direct-team MAINTAINER; ordinary entry CRUD remains member-based.

Copies retain the source and reseal a new destination entry. Source-retiring moves require a complete consumer inventory and remain rejected. Customer-KMS destinations need policy-aware reseal recovery and remain rejected. Shared OTP, KMS administration, keys, host/machine credentials and delivery are unsupported.

## Shared-scope entry retirement (unreleased fix)

Use the immutable scope returned by `vault scopes` for every entry request.
The source correction allows the canonical `vault delete` entry operation in
org/team scopes; CLI 0.44.2 incorrectly rejects it before sending the request.
`delete` means retirement under the server's existing retention policy. There
is no `vault retire` command. Current membership is still checked by the server;
an organization owner does not bypass direct team membership.

```bash cli-help="vault delete"
# Use a disposable entry and its current metadata revision.
dreamlake vault --scope org:000000000000000000000001 delete \
  --name acme/test-entry --if-match 1
```

Scoped entry list/show/get/add/delete/restore and write-status use the same
selected scope. Scope denial never retries against personal Vault. Shared OTP,
KMS/key administration, access keys, host bindings and remote delivery remain
unsupported. Do not remove those restrictions to support runtime consumers.
Use `show` for metadata; `get` explicitly retrieves secret values. An unavailable
capabilities endpoint does not imply that advanced operations are supported.
