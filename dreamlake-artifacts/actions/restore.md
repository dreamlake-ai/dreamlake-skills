# Remove and restore

```bash
dreamlake artifact delete <id> [--namespace <slug>] [-y]     # soft delete → Trash
dreamlake artifact restore <id> [--namespace <slug>]         # undo a soft delete
dreamlake artifact delete <id> --permanent [-y]              # purge — IRREVERSIBLE
```

Options: [Listing, deleting, restoring](reference/cli-artifacts.md#listing-deleting-restoring)
or `dreamlake artifact delete --help`.

## Soft delete

`delete` moves the artifact to the dashboard's **Trash** (a tab in the
owner's gallery): its content stops resolving for non-members and any live
`?share=` link is invalidated. It prompts for confirmation unless `-y`/`--yes`
and is member-only. A soft delete keeps external mount grants.

**Restorable three ways**: `dreamlake artifact restore <id>`, the Restore
button in the Trash, or re-pushing the same `--id`.

## Project placements

On a server that includes the dreamlake-workspace #1343 fix (not yet
released; older servers leave project placements in place), both `delete`
and `delete --permanent` also remove the artifact from **every project** it
was filed in, together with its Bindr tags there. A restored artifact comes
back **unfiled** — add it to the project again if the user wants it there.
Before deleting an artifact that is filed in projects, tell the user it will
leave them. A new artifact with the same name can be filed where the old one
was.

## Permanent purge

`delete --permanent` (v0.4.14+) **permanently erases** the artifact — all
versions, the stored content in S3, and the catalog entry — and revokes
external mount grants. It works on live or already-trashed artifacts, uses a
stronger confirmation prompt, and **cannot be undone**. Never pass `-y` with
`--permanent` unless the user has explicitly confirmed they want the artifact
gone forever. The dashboard equivalent is **Delete forever** inside the
Trash. Source: [Delete it (safely)](reference/docs-artifacts.md#delete-it-safely).

An owned artifact moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
