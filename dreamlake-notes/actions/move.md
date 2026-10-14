# Refile a Note or move a whole Project

Check `dreamlake notes move --help`; CLI 0.44.3 and earlier do not expose it,
and the server must support the endpoint. Standalone Note ownership transfers across namespaces
remain unsupported. Whole-Project moves use the separate workflow below. Never emulate one by copying/deleting a Note,
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


## Whole Project and owned resources

For a request to move a **whole Project with ordinary files and owned Notes,
Artifacts and Envs**, use the
[whole-Project transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer/)
and the CLI Projects guide instead of repeating standalone Note moves.
Mixed Artifact/Env plans require CLI 0.64.0+ or SDK 0.31.0+ and the matching
accepted backend/RTC deployment; CLI 0.63.0 / SDK 0.30.0 accept Note-only plans.
Check installed help, the Project adapter capabilities and `plan.executable`;
unsupported/disabled capability stops the task without copying/deleting content.
Media-file support requires the companion backend expansion; installing a newer
skill does not change the deployed server. Inspect itemized plan blockers for the
affected item and reason. Episode content remains unsupported.

CLI flow is `project move ... --dry-run --out reviewed.json`, review
scope/access/external audiences, then `--confirm --request-file reviewed.json`.
The manifest must include the Project and every owned live Note, Artifact and
Env; do not reduce it to Notes. Foreign resources, Source bindings, Workflow,
Annotation and structural content block everything. No standalone resource
transfer is added. Preserve access
is off by default. External Note Project filings are removed by default, ending
inherited access through those mounts without deleting the moved Notes/data.
Retaining Note filings requires explicit `--preserve-external-filings` and
destination approval of their live audience, independently of direct-access
retention. Artifact/Env outside placements always detach, and their old
namespace-based links cannot be preserved; review the complete preview.
Source owner requests and destination owner explicitly accepts. Keep the exact
request/key on a lost response; use status for a known operation, never rebuild
or clear a claim/lease. See the [Notes contract](../reference/notes.md#whole-project-and-owned-resources-transfer).
