# Terraform state and Vault

Available in CLI 0.49.0+ for personal Vault scope. Use an authoritative remote backend with
locking, encryption, access controls and version history. DreamLake Vault stores
backend references and optional selected snapshots; it is not a Terraform active
state backend. Entry revisions and write receipts do not implement Terraform's
lock, lease or atomic state protocol.

These commands currently require POSIX ownership and permission checks. Windows
file selection is refused until an equivalent ACL check is supported. Selected
reference and state files must be owned, owner-only regular files without links.

Terraform state and saved plans can contain secrets even when values are marked
`sensitive`. JSON output may reveal them. Keep state out of Git, Notes, terminal
logs and automatic indexing. See HashiCorp's [sensitive data guidance]
(https://developer.hashicorp.com/terraform/language/manage-sensitive-data).

## Onboard the remote backend

For the `aws-jump-worker` template, choose an existing approved private S3 bucket,
a dedicated state key, exact owner account and region. Enable encryption,
versioning and `use_lockfile=true`. Use Terraform 1.10 or later. Configure the
operator role for the selected state object and lockfile; instance roles should
not receive state access. Backend bootstrap and migration are separate reviewed
operations. See the official [S3 backend and locking documentation]
(https://developer.hashicorp.com/terraform/language/backend/s3).

Use the normal AWS credential chain, preferably a short-lived session. A Vault
credential reference identifies an entry; it does not fetch credentials, execute
a helper or authorize access. Do not put credential values into backend arguments
or the reference JSON.

```json file="backend-reference.json"
{
  "schema": "dreamlake-terraform-backend-reference-v1",
  "backend": "s3",
  "bucket": "approved-state-bucket",
  "key": "providers/aws-demo/terraform.tfstate",
  "region": "us-east-1",
  "expectedBucketOwner": "123456789012",
  "useLockfile": true,
  "versioning": true,
  "encrypt": true,
  "credentialRef": "alice/aws/operator"
}
```

The reference records your chosen configuration. It does not verify the bucket's
live settings, create infrastructure, initialize Terraform or migrate state. The
reference is distinct from the template's Terraform `backend.json`, whose keys
follow Terraform's backend schema.

```bash file="terminal" cli-help="vault terraform backend"
chmod 600 ./backend-reference.json
dreamlake vault terraform backend --file ./backend-reference.json --name alice/terraform/aws-demo
# Upload only after explicitly selecting the file and destination.
dreamlake vault terraform backend --file ./backend-reference.json --name alice/terraform/aws-demo --apply --request-id aws-demo-backend-001
```

## Explicit snapshot backup

Prepare a consistent state export through the authoritative backend's own
authorized workflow and place it in an owner-only local file. Select that file
explicitly. No command searches for state files or uploads active state
automatically. Preview reads the selected file locally and reports metadata only.

```bash file="terminal" cli-help="vault terraform backup"
dreamlake vault terraform backup --file /private/aws-demo.snapshot.json --prefix alice/terraform/backups
# This is an explicit upload of this selected sensitive file.
dreamlake vault terraform backup --file /private/aws-demo.snapshot.json --prefix alice/terraform/backups --apply --request-id aws-demo-snapshot-001
```

Snapshots use the existing audited Vault entry API and the entry's governing KMS
encryption at rest. This is service-side encryption, not a separate client-side
encryption format. The serialized entry is limited to 64 KiB, including metadata
and base64 overhead, so the selected raw state must be smaller. Large states need
a separately reviewed backup destination; the CLI never splits them or falls
back to plaintext storage.

The selected state must use Terraform format 4 with a UUID lineage, nonnegative
integer serial, and valid outputs/resources containers. The snapshot records
lineage, serial, byte length and SHA-256 integrity metadata.
Content-addressed names distinguish snapshots. Existing conflicting entries are
not overwritten; identical retries use the retained request ID. After a write,
the command reads the entry back and checks its content. Retain metadata receipts,
not state values. An uncertain response requires [write-status reconciliation]
(/vault-write-recovery); it is not evidence that no write occurred.

Verified snapshot evidence is tied to the selected bytes and entry revision.
Vault entries are not WORM storage: an authorized later replacement or deletion
can still occur. Neither a snapshot nor an idempotency receipt acquires a
Terraform lock or replaces backend version history.

## Restore into an isolated file

Select one snapshot entry at its original revision `1`, an explicit current-state comparison
export, and a new local destination. The command checks integrity, lineage and
serial and refuses a foreign lineage, a snapshot older than the supplied current
state, or different bytes with the same serial. That comparison is as current as your selected export; refresh it using
the authoritative backend's workflow before a recovery decision.

```bash file="terminal" cli-help="vault terraform restore"
dreamlake vault terraform restore --name alice/terraform/backups/state-SHA256 --if-match 1 --current-state /private/current.snapshot.json --to /private/recovery/candidate.snapshot.json
# Explicitly write the verified candidate into a new file.
dreamlake vault terraform restore --name alice/terraform/backups/state-SHA256 --if-match 1 --current-state /private/current.snapshot.json --to /private/recovery/candidate.snapshot.json --apply
```

Replace `state-SHA256` with the complete name emitted by backup. Use an existing
owned directory with mode `0700` and a new `*.snapshot.json` filename outside
`.terraform`. Restore
writes an owner-only file and never overwrites an existing path, pushes state,
runs Terraform or updates a backend. Inspect the isolated candidate privately.
Promoting it into active state is a separate explicit recovery operation under
the backend's lock and authorization rules. The CLI does not claim that local
comparison eliminates races with future remote state writes.
