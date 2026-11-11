<!-- generated from https://cli.dreamlake.ai/notes/projects.md at 0.121.1 361dc74; do not edit -->

# Project filing

## Create and inspect project filing (CLI 0.45.1)

A Memo belongs to its namespace, independently of its project affiliations.
Repeat `--project` on creation to file the new Memo in several projects in that
same namespace. Duplicate project slugs collapse. The server authorizes each
project before creation; use its current Write/Admin permission. Project filing
does not grant access to Memo content or make organization Memos team-private.
Organization members retain their existing Memo read/edit baseline.

```bash
dl memos create "Disposable filing check" --namespace acme \
  --project research --project reviews --json
```

Creation sends one request containing the full project list; it never falls back
to creating an unfiled Memo after rejection. If the outcome is uncertain, inspect
the namespace before retrying: creation is not an idempotent transfer. Optional
body writing remains a separate operation after creation.

Inspect an existing Memo's project candidates and current affiliations by its
stable ID, using the Memo's owning namespace:

```bash cli-help="memos projects"
dl memos projects 000000000000000000000001 --namespace acme
```

The JSON contains `bound`, `nodeId`, `canBind`, effective project `role`, and
attached `bindrs`. A candidate list alone does not establish that a Memo exists.
`canBind` is the server's current observation, not authorization
for a later write. This does not read the body, activate an RTC room, or add/remove
filing. These additions require CLI 0.45.1 or later. Existing-note `memos move`
remains a separate draft with writer/ownership leases and executable-preview
gates. Do not substitute a namespace rewrite, copy/delete, or an older generic
mount endpoint for that workflow. Cross-namespace transfer requires the journal,
storage and RTC adapters; missing routes/readiness are unsupported, never success.

## Move a memo into a workspace

This section describes standalone `memos move`, available starting with CLI
0.45.1; CLI 0.45.0 and earlier lack it. Same-namespace Project filing is supported.
`memos move` does not submit recipient-accepted cross-namespace ownership requests.
Use [`memos transfer`](cli-notes-transfers.md#transfer-a-standalone-note) for that workflow. Its own
cross-namespace preview remains blocked.
For a whole Project and all its owned Memos, use
[`project move`](https://cli.dreamlake.ai/projects#move-a-whole-project-and-its-supported-resources)
with an enabled whole-Project server adapter. CLI 0.64.0+ and its matching
backend also include owned Artifact/Env attachments; published 0.63.0 rejects
those mixed plans. Review the full typed manifest, not only Memos. External
filing retention applies only to Memos; Artifact/Env placements outside the
moved Project always detach. That Project path does not replace standalone
`memos transfer`; unsupported Source/Workflow/Annotation attachments still block it.

```bash cli-help="memos move"
# Standalone cross-namespace Memo transfer is unavailable (exit 3).
dl memos move MEMO_ID --to-namespace my-org --project shared-research --dry-run
# Add a project association within the note's CURRENT workspace.
dl memos move MEMO_ID --to-namespace current-workspace --project research --dry-run
# Apply only an executable same-workspace preview.
dl memos move MEMO_ID --to-namespace current-workspace --project research
# Relocate the note to an existing folder of one project (CLI 0.87.0+).
dl memos move MEMO_ID --namespace acme --project research --folder reports/2026 --dry-run
```
`--to-project` and `--to-folder` are the contract spellings of `--project` and
`--folder`; `--ns` asserts the source namespace. A display-name change
(`--name`) is not part of the move contract this CLI can send.

Run under the source namespace owner's login. Same-namespace filing requires
write access to every requested project, preserves other project associations,
and leaves ownership, content, history, attachments, visibility and shares intact.
Repeat `--project` to add several associations. Organization membership still
grants read/edit access to organization memos; filing does not make them private
to one team.

A full memo ID resolves its current namespace automatically. `--namespace`
optionally asserts the source and supplies the scope for slug/title lookup.
`--to-namespace` is the destination. `--json` returns the server receipt, including
`executable` and `blockers`. A blocked preview exits 3. Applying a cross-workspace
destination returns `409 NOTE_TRANSFER_UNAVAILABLE` without mutation. Never
simulate a transfer by copying and deleting the memo.

Dry runs do not reserve destinations; execution rechecks permissions, leases and
conflicts. After a transport failure, resolve the stable ID and inspect its
project associations before resubmitting. The CLI never retries automatically.

## Move a memo to another folder in a project

CLI 0.87.0 and later relocate a Memo's node inside one project's tree with
`memos move --folder`. The workspace and project stay the same; only the
folder changes. Preview first, then apply:

```bash
dl memos move MEMO_ID --namespace acme --project research --folder reports/2026 --dry-run
dl memos move MEMO_ID --namespace acme --project research --folder reports/2026
```

`--folder` is a project-relative path to an existing folder. An empty value
(`--folder ""`) means the project root. The CLI never creates folders: a missing
segment fails with `folder_not_found` and nothing changes. `--namespace` and
exactly one `--project` are required. `--to-namespace`, if given, must name the
same workspace.

The move keeps the node ID, so bindr tags, links, attachments, visibility and
shares are unchanged. A Memo with the same name in the destination fails with
`name_collision` (exit 3); permission refusals report `forbidden`. You need write
access to the project. `--dry-run` prints the current and destination paths
without writing; `--json` emits the same receipt. Confirm the result with
`dl list --episode PROJECT@NAMESPACE`.

To tag a filed Memo with a bindr in the same project, use
`dl update bindr BINDR --project PROJECT@NAMESPACE --add-note MEMO_ID`.
