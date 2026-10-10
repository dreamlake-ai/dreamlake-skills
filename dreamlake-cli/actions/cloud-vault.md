# Import and restore cloud configuration

Requires CLI 0.43.0. Check `dreamlake auth env list` before writing.

1. Preview standard paths with `dreamlake vault cloud import --provider aws -p <owner>/aws/<scope>` (or `gcp`). This does not read their contents.
2. Select each file explicitly with repeated `--file /absolute/path`. Omit `--apply` for a metadata-only output preview; selected files are read locally. Whole AWS files retain every profile. No credential helper or referenced file is executed/read.
3. Add `--apply` only within the user's authorized upload scope. Secrets stay out of arguments and output. Existing entries require a single-file `--if-match <revision>`. Retain emitted request IDs and reconcile uncertain writes before an identical retry.
4. Preview restore with `dreamlake vault cloud restore -n <entry> --to /absolute/destination`. Add `--apply` to write; existing destinations additionally require explicit `--overwrite`. POSIX restore writes 0600 files into an existing owned directory.

GCP supports service-account, authorized-user and external-account JSON. Use `--provider other` for other selected UTF-8 configs. This does not authenticate providers, copy SSO caches or create DreamLake connections. Dotfile metadata requires the matching server fix.

See [complete options and limits](../reference/vault-cloud.md).

## Terraform setup and selected state snapshots

The next CLI release adds `provider create --provider aws-jump-worker`. Follow
the generated `AGENT.md` and `--json` `nextAction` loop: resolve every blocking
input, rerun `create --continue`, then plan using the selected remote backend.
An apply, enrollment or resource lifecycle action requires the user's explicit
scope. Terraform IDs are not enrolled Host/Worker IDs; the jump and worker stay
distinct. See [provider lifecycle](../reference/provider-lifecycle.md).

Prefer an authoritative locked/versioned remote backend. Use `vault terraform
backend` for a selected nonsecret backend/credential reference, `backup --file`
for an explicitly selected state snapshot, and `restore` only into a new isolated
file with an explicit current-state comparison. Preview first; add `--apply`
only for the selected upload or local write. Never scan/upload active state,
publish state in Notes/artifacts, or infer backend support from Vault revisions.
Unknown writes require receipt reconciliation before retry. Large states and
live backend migration are outside this surface; do not substitute a generic
upload or SDK call. See [state limits and recovery](../reference/vault-terraform-state.md).
