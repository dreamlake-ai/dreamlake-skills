# Prefix KMS policies

**Published CLI 0.17.0 and Python 0.14.0; requires the matching backend.** Managed KMS is the default and needs no cloud setup for ordinary users. These owner-only commands inspect trusted references configured by an operator; they do not create cloud keys or permissions. Scoped access keys and project membership do not grant policy-management authority.

```shell
dreamlake vault -p alice/research kms show
dreamlake vault -p alice/research kms preview --key research-key
# Persist the account/server, prefix, key reference and request ID before activation.
dreamlake vault -p alice/research kms activate --key research-key --request-id research-kms-001
dreamlake vault kms status research-kms-001
```

```python
client.vault.kms.show(prefix="alice/research")
client.vault.kms.preview(prefix="alice/research", key_ref="research-key")
client.vault.kms.activate(prefix="alice/research", key_ref="research-key", request_id="research-kms-001")
client.vault.kms.status(request_id="research-kms-001")
```

Preview does not reserve a prefix or probe the key. Activation verifies the approved key and commits only if the prefix has no entries (including retired/expired entries), retained write/HOTP receipts, or overlapping ancestor/descendant policy. A parent policy governs its whole subtree; `alice/work` does not govern `alice/workshop`. Output names the governing prefix and key reference without printing key ARNs or credentials.

After an uncertain response, inspect the original request ID and retry the identical prefix/reference/ID. A missing receipt does not prove an in-flight commit failed. Python raises `VaultWriteError` carrying the original `request_id`; it never prompts or generates a replacement ID. Do not switch accounts or servers while reconciling an operation.

The empty-prefix foundation is merged. Populated-prefix migration is merged and published in the paired clients; backend enablement still requires the operator rollout gate. Policy removal, general customer-grant onboarding and mixed-provider routing remain open. Existing ciphertext and receipts retain their original key dependencies; do not delete an old KMS key because new writes use another key. See the [full development plan](https://docs.dreamlake.ai/dev/plans/vault-prefix-kms/) for migration, outage and GCP acceptance tasks.

## Populated-prefix migration

Migration changes the key for future writes, then explicitly re-encrypts retained entry and recovery ciphertext in bounded batches. It preserves logical revisions, HOTP counters and existing request IDs. Keep the original account/server/prefix/key/request ID when a response is uncertain; `status` and another bounded `resume` reconcile committed progress. Libraries never prompt or launch a background loop.

```shell
dreamlake vault -p alice/research kms preview --key research-key
dreamlake vault -p alice/research kms migrate --key research-key --request-id research-move-001
dreamlake vault -p alice/research kms resume research-move-001 --limit 50
dreamlake vault kms status research-move-001
# Repeat resume explicitly until state is completed.
```

```python
client.vault.kms.preview(prefix="alice/research", key_ref="research-key")
client.vault.kms.migrate(prefix="alice/research", key_ref="research-key", request_id="research-move-001")
client.vault.kms.resume(request_id="research-move-001", limit=50, prefix="alice/research")
client.vault.kms.status(request_id="research-move-001")
```

Preview counts include retired entries and retained write/HOTP receipts, even if their source entry was purged. Resume considers at most 1–100 ciphertext rows per call. `managed` selects the operator's default key explicitly; moving back uses a **new** migration ID after the current operation completes. This implementation uses one configured provider. AWS keys stay in the configured region; GCP accepts operator-allowlisted CryptoKey locations, with cross-location live acceptance still unverified. Customer grants, cross-provider routing and live GCP setup remain separate work.

Completion covers the active database. It does not re-encrypt retained backups, revoke SSH access, or authorize old-key deletion. Keep historical keys accessible until actual backup and recovery retention no longer require them. KMS denial pauses progress with no fallback. High same-tenant write contention can return503: reconcile and retry the identical write intent. Migration requires all writing backend instances to support encryption epochs; mixed-version rollout is unsupported. The paired clients are released, and the owned staging AWS fixture passed the acceptance below. Production rollout remains pending.

An explicit `--prefix` on resume is checked by the server against the original migration before any mutation. Omit it for ID-only recovery. Python accepts optional `prefix=`; status also rejects a mismatched explicit prefix.

Operators must enable `DREAMLAKE_VAULT_KMS_MIGRATION_ENABLED=true` only after verifying every backend writer supports epochs. The flag defaults off; disabled servers report migration unavailable and omit its routes.

Staged AWS acceptance with these published clients migrated nine encrypted dependencies to a dedicated key and back, recovered a committed response, verified isolated grant denial without checkpoint progress, and retired the four fixture entries with read404. [Guide and sanitized evidence](https://github.com/dreamlake-ai/lakeshore-examples/pull/31). Production and cross-provider acceptance remain separate.
