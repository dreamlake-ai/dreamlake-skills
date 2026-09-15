# Vault write recovery

Available in CLI `0.13.0` and Python `0.10.0` with the deployed DreamLake API.
For self-hosted servers, use a backend with write-operation receipts. See the
[release evidence](https://docs.dreamlake.ai/dev/notes/vault-runtime/) and
[Vault tracker](https://github.com/dreamlake-ai/dreamlake-workspace/issues/241).

`PUT /v1/vault/entry` accepts an optional `Idempotency-Key` containing 1–128
ASCII letters, digits, `_` or `-`. Keep this non-secret ID before submission.
Requests without it retain legacy create-only/`If-Match` behavior. Updated CLI
and Python `add` generate an ID when omitted; an explicit ID survives caller
restarts. The CLI prints the ID to stderr before sending; Python returns it in
metadata or on `VaultWriteError.request_id` without logging. Both clients require
the updated receipt-capable server. An older server may commit but omit the
receipt; clients report an unknown outcome instead of assuming safe recovery.
Write receipts cover only entry creation and replacement.

After submission, a timeout or HTTP error leaves the logical operation outcome
unknown: a rejected retry can follow an earlier committed write. The CLI always
prints reconciliation guidance. Python separates `outcome="unknown"` from
`attempt_outcome` (`"rejected"` for 4xx other than 408, otherwise `"unknown"`).
Only a matching authenticated committed receipt establishes commitment. Missing,
expired or unavailable status is not proof of failure.

A successful identified write returns `{entry, operation, replayed}`.
`GET /v1/vault/write-operations/:requestId` returns `{operation}` only to the
current authenticated owner. Scoped keys cannot query it. A receipt has
`requestId`, `state: "committed"`, original entry metadata, `committedAt` and
`retainUntil`; it never reveals values, tenant IDs, ciphertext or fingerprints.
An absent/expired receipt is 404 and does **not** prove the write failed. Status
needs Mongo and account authentication but no KMS decryption.

The same normalized body and `If-Match` with the same ID replays the original
metadata, even after a newer write or retirement. It never restores an old value.
Changed content or revision returns 409 `IDEMPOTENCY_CONFLICT`; a competing ID
with a stale revision returns 409 `REVISION_CONFLICT`. Field-map key order and
normalized paths/timestamps do not affect identity; omitted expiry and explicit
null remain different requests. Review the current entry before making a new
intentional update with a new ID.

Mongo transactions commit the entry CAS and receipt together. A per-tenant guard
serializes identified writers; the unique tenant/request index prevents duplicate
receipts. A receipt contains a keyed HMAC of the normalized request. Its random
key is encrypted through the entry's governing KMS, bound to tenant and request
ID. There is no plaintext digest oracle and no second encrypted copy of the
entry secret. Replays need KMS; status does not. Provider/database diagnostics
remain fixed, redacted errors.

Receipts expire after 30 days via a native Mongo TTL index. Protection is only
promised inside that window; after expiry, do not blindly reuse the ID or assume
absence means failure. TTL deletion is asynchronous; an expired retained receipt
rejects retry with 409 `WRITE_RECOVERY_EXPIRED`. Entry retirement/purge does not
remove a still-valid receipt. Backups follow the operator's separate retention
policy.

```shell
# Secure producer supplies stdin; the request ID is not a credential.
secure-secret-producer | dreamlake vault add -p alice -n service --stdin --request-id service-write-001
# After an uncertain response, inspect metadata without providing the secret:
dreamlake vault write-status --request-id service-write-001
# If retry is needed within retention, repeat the identical input/options/ID.
# A new replacement uses a new ID and the revision from vault show:
secure-secret-producer | dreamlake vault add -p alice -n service --stdin --if-match 1 --request-id service-write-002
```

```python
from dreamlake.vault import VaultWriteError
request_id = "service-write-001"  # persist only this non-secret operation ID
try:
    result = client.vault.add("service", secret, prefix="alice", request_id=request_id)
except VaultWriteError as error:
    # error.request_id is safe to retain; error.status describes this attempt.
    # error.outcome stays "unknown" until a matching committed receipt is found.
    receipt = client.vault.write_status(request_id=error.request_id)
    # A missing/unavailable receipt leaves the outcome unknown.

# New intentional replacement after reviewing current metadata:
client.vault.add("service", replacement_secret, prefix="alice",
                 if_match=1, request_id="service-write-002")
```

Local verification: `src/vault/writeRecovery.e2e.test.ts` runs real JWT/HTTP,
Mongo replica-set transactions and authenticated encryption, including a proxy
that drops the committed response, races, rollback and tenant denial. The Python
repository's `scripts/test_vault_write_recovery_integration.py` drives the actual
CLI and Python clients against `serveTestFixture.ts`, losing both responses.
