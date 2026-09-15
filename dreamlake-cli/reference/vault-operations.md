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
