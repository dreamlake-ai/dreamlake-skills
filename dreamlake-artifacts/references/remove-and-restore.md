# Remove And Restore

## Delete, restore & permanent purge

```bash
dreamlake artifact delete <id> [--namespace NS] [-y]      # soft delete → Trash
dreamlake artifact restore <id> [--namespace NS]          # undo a soft delete
dreamlake artifact delete <id> --permanent [-y]           # purge — IRREVERSIBLE
```

`delete` **soft-deletes** the artifact: it moves to the dashboard's **Trash** (a tab in
the owner's gallery), its content stops resolving for non-members, and any live
`?share=` link is invalidated. Prompts for confirmation unless `-y`/`--yes`. Member-only.
**Restorable** three ways: `dreamlake artifact restore <id>`, the Restore button in the
Trash, or re-pushing the same `--id`.

`delete --permanent` (v0.4.14+) **permanently erases** the artifact — all versions, the
stored content in S3, and the catalog entry. It works on live or already-trashed
artifacts, uses a stronger confirmation prompt, and **cannot be undone** — never pass
`-y` with `--permanent` unless the user has explicitly confirmed they want the artifact
gone forever. The dashboard equivalent is **Delete forever** inside the Trash.
