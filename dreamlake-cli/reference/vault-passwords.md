# Verify a saved SSH password

**CLI source included in released tag 0.19.1; Python 0.16.0 remains an unpublished candidate.** Fresh installed-client and hosted password acceptance remains required. Saving during enrollment does not prove the password works. This command verifies one explicitly selected binding using a fresh password-only connection; it does not change a password or authorize backend SSH.

```shell
dreamlake vault verify-password --binding-id "$password_binding_id" \
  --ssh 'worker@worker.example' --known-hosts "$HOME/.ssh/known_hosts"
```

```python
result = client.vault.verify_host_password(
    binding_id=password_binding_id,
    ssh={"host": "worker.example", "user": "worker", "port": 22,
         "knownHostsFile": str(known_hosts)},
)
assert result["status"] == "verified"
```

A verified result includes the method, observation time, binding/entry identity and revision, and remote account identity. Explicit password denial returns `status="denied"` and CLI exit 1. Wrong host keys, network failures, unexpected prompts, alternate authentication and changed binding/entry revisions return a redacted unconfirmed error. No password or password-derived hash appears in output.

The binding must contain an explicit `user@host` matching the supplied target before the client reads or delivers the secret. A stored port must also match; when enrollment omitted the port, the caller supplies it explicitly. Alias-only bindings are rejected by this adapter. Results report `target` and `verificationScope="credential_at_explicit_endpoint"`: this verifies password acceptance at that destination, not a cryptographic assertion that it is the server's `HostId` or enrollment. Trusted SSH host keys remain required.

A denial means authentication was refused; it cannot diagnose an incorrect secret versus account or PAM policy. The [SSH failure message](https://www.rfc-editor.org/rfc/rfc4252.html#section-5.1) does not carry that distinction. Future rotation must verify replacement success again after old-password denial before confirming cleanup.

For a target behind a jump, add `--jump-ssh`, `--jump-identity` and optional `--jump-known-hosts`; Python adds the corresponding `jump` endpoint and its separate `identityFile`. The jump uses its selected key. Verify a jump password separately by addressing that account directly. Password-only multi-hop and keyboard-interactive/MFA are not supported.

A private one-shot askpass channel delivers the saved password to OpenSSH. Arguments, environment values and metadata files contain no password. Parent-client authentication evidence excludes remote forged output and connection reuse; bounded local authentication logs are deleted after each probe. This adapter accepts 1–512 UTF-8 bytes excluding NUL/CR/LF, rejecting unsupported input without trimming it. Generic vault storage remains byte-preserving. Library calls never prompt.

The candidate native binary, npm launcher and Python passed real password success/denial checks for direct jump and target-through-jump use. Disposable users, private loopback SSHD, listener and fixture directory were independently confirmed removed. This source-fixture result is separate from a registry release, hosted KMS or live Nymph enrollment. [Paired guide, exact-source receipt and reusable runners](https://github.com/fortyfive-labs/dreamlake/blob/feat/241-password-probe/docs/vault-passwords.md).

Password rotation remains required work and needs separately verified recovery access plus a pre-mutation reservation; this command does not implement it. [Development plan](https://github.com/dreamlake-ai/dreamlake-workspace/blob/main/docs/pages/dev/plans/host-password-rotation/%2BPage.mdx).

## Password reservation and recovery

**CLI source included in released tag 0.19.1; paired Python candidate remains unpublished.** Requires [backend #370](https://github.com/dreamlake-ai/dreamlake-workspace/pull/370). These low-level commands never change SSH passwords. Use a dedicated non-expiring replacement entry. Private intent/proof files contain metadata only: exact entry references, observed account identity and separately verified recovery-key evidence. The privileged rotation adapter and explicit rollback-resolution API remain required; never fabricate proof to finish an operation.

```shell
dreamlake vault password-rotation reserve --binding-id "$binding_id" \
  --operation-id "$operation_id" --input "$intent_file"
dreamlake vault password-rotation show --operation-id "$operation_id"
# Cancellation is permitted only before mutation starts.
dreamlake vault password-rotation cancel --operation-id "$operation_id"
```

```python
operation = client.vault.reserve_host_password_rotation(
    binding_id=binding_id, operation_id=operation_id, intent=intent,
)
operation = client.vault.host_password_rotation(operation_id)
operation = client.vault.cancel_host_password_rotation(operation_id)
```

`start` and `start_host_password_rotation` durably mark possible mutation before the future privileged adapter runs. `confirm --input proof.json` and `confirm_host_password_rotation(..., proof=proof)` accept exact new/old/new password and recovery-key attestation, then switch only to the pinned live replacement. A lost response requires metadata recovery or exact replay under the same operation ID, never a new ID or automatic SSH retry.

Explicit `read --operation-id ID --slot old` emits the selected recovery string without an added newline; `--to-json` includes its IDs/revision and value. Python `read_host_password_rotation(operation_id, slot="old")` returns the string without printing or prompting. Use `new` for the replacement snapshot. This personal-owner pending recovery read survives original-entry expiry/deletion; ordinary vault reads do not gain that exception. Never place recovered passwords in command arguments or logs.

Pending operations retain encrypted snapshots without TTL. Immutable verified terminal receipts authorize collection after 30 days unless an explicit active recovery reference defers it. Later normal rotation/unbinding does not retain obsolete snapshots forever. A recreated HostId cannot complete an old pending operation. [Full paired API and reusable HTTP test](https://github.com/fortyfive-labs/dreamlake/blob/feat/241-password-reservation/docs/vault-passwords.md#reserve-and-recover-a-password-rotation).

KMS migration retains password recovery snapshots too. These candidate clients display `passwordSnapshotCount`, `totalRetainedRecordCount`, and the supported record schema/kinds, and send schema-2 acknowledgment on migration start/resume. Deploy the compatible backend first. Older clients can inspect status but cannot advance an affected migration; reuse the original operation ID after upgrading.
