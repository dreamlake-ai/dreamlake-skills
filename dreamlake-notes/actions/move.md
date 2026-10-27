# File a Note into a Project or change its folder

Check `dreamlake notes move --help` first: the command requires CLI 0.45.1
(absent in 0.45.0 and earlier) and a server that supports the endpoint.
Standalone Note ownership transfer across namespaces is [transfer](transfer.md),
not this command; a whole Project with its Notes is the `projects` action of
`dreamlake-cli`. Never emulate either by copying and deleting a Note, changing
namespace IDs or bypassing the ownership lease. Filing is separate from ownership.

Use the source workspace owner's login and preview the requested scope:

```bash
# An organization destination currently returns blockers and exit status 3.
dreamlake notes move NOTE_ID --to-namespace ORG --project PROJECT --dry-run
# Add a project association within the Note's CURRENT workspace; inspect executable first.
dreamlake notes move NOTE_ID --to-namespace CURRENT_WORKSPACE --project PROJECT --dry-run
# Relocate a filed Note to an existing folder of one project (CLI 0.87.0+).
dreamlake notes move NOTE_ID --namespace NS --project PROJECT --folder PATH --dry-run
```

Only an executable same-workspace preview can be applied, when the user has
authorized that filing, by repeating the command without `--dry-run`. A blocked
preview exits 3 and must not be repeated as an execution request. Repeat
`--project` for more same-workspace associations. Filing requires current write
access to all selected projects and preserves existing associations, identity,
content, history, comments, attachments, visibility and shares. Organization
members retain their Note read/edit baseline; filing does not make an
organization Note team-private.

A full ID resolves the current owner. `--namespace` optionally asserts the source
and supplies its scope for slug or title lookup. A blocked cross-workspace apply
returns `409 NOTE_TRANSFER_UNAVAILABLE` without mutation. A generic tree move
cannot substitute for this workflow. On `NOTE_FILING_RECONCILIATION_REQUIRED`,
keep the original filing and use additive filing only when that matches the
request. Do not blindly retry a conflict or network failure: resolve the stable
ID and inspect its current workspace and project associations before deciding
what remains. See [move a note into a workspace](../reference/cli-notes-projects.md#move-a-note-into-a-workspace),
[moving between workspaces](../reference/docs-notes.md#moving-between-workspaces-development-preview)
and [concurrent writes](../reference/docs-notes.md#metadata-permissions-and-concurrent-writes)
for ownership-busy and lost-authority recovery.

## Folders and bindr tags (CLI 0.87.0+)

The `--folder` target must already exist; bindr tags and access are kept.
Preview with `--dry-run`, then repeat without it. Tag a filed Note with a bindr
through `dreamlake update bindr BINDR --project PROJECT@NS --add-note NOTE_ID`,
not a raw API call. See
[move to another folder](../reference/cli-notes-projects.md#move-a-note-to-another-folder-in-a-project).

## Create filed and inspect filing (CLI 0.45.1+)

`notes create --project SLUG` (repeatable) files a new Note; `notes projects
NOTE_ID --namespace NS` shows its current filing. CLI 0.44.3 and earlier lack
both. Never emulate an existing-note move through copy/delete, namespace updates
or an older generic mount API; missing server or adapter readiness is
unsupported. See [project filing](../reference/cli-notes-projects.md#create-and-inspect-project-filing-cli-0451).

Project grants and what they authorize are the `project-access` action of
`dreamlake-cli`.
