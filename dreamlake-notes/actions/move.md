# Preview ownership or add same-workspace filing

Check `dreamlake notes move --help`; CLI 0.44.3 and earlier do not expose it,
and the server must support the endpoint. Cross-workspace ownership transfers
are currently unavailable. Never emulate one by copying/deleting a Note,
changing namespace IDs or bypassing the ownership lease.

Use the source workspace owner's login and first preview the requested scope:

```bash
# An organization destination currently returns blockers and exit status 3.
dreamlake notes move NOTE_ID --to-namespace ORG --project PROJECT --dry-run
# Add a project in the Note's current workspace; inspect executable first.
dreamlake notes move NOTE_ID --to-namespace CURRENT_WORKSPACE --project PROJECT --dry-run
```

Only an executable same-workspace preview can be applied, when the user has
authorized that filing, by repeating the second command without `--dry-run`.
Repeat `--project` for more same-workspace associations. It requires current
write access to all selected projects and preserves existing associations,
identity, content, history, comments, attachments, visibility and shares.
Organization members retain their Note read/edit baseline; project filing does
not make an organization Note team-private.

A full ID resolves the current owner. `--namespace` optionally asserts the source
and supplies its scope for slug/title lookup. A blocked cross-workspace apply
returns `409 NOTE_TRANSFER_UNAVAILABLE` without mutation. A generic tree move
cannot substitute for this workflow. If it reports
`NOTE_FILING_RECONCILIATION_REQUIRED`, keep the original filing and use additive
filing only when that matches the requested operation.

Do not blindly retry a conflict or network failure. Resolve the stable ID and
inspect its current workspace and project associations before deciding what
remains. See the [Notes reference](../reference/notes.md#moving-between-workspaces-development-preview)
for readiness limits and [concurrent writes](../reference/notes.md#metadata-permissions-and-concurrent-writes)
for ownership-busy and lost-authority recovery.
