# Add or remove one asset remotely

```bash
dreamlake library add <ns>/<name> ./my-mug --title "Blue mug" --category household
dreamlake library add <ns>/<name> ./my-mug --replace   # update an existing id in place
dreamlake library rm <ns>/<name> my-mug old-chair      # server reclaims their files
```

No full local copy needed — these edit the remote library directly. Flags
(`--id --title --description --category --tags --license --attribution`,
`--replace`, `--json`): `dreamlake library add --help` and
[Add or remove one asset](../reference/docs-libraries.md#add-or-remove-one-asset).

## Rules

- `add` discovers the one directory (or loose file) exactly like push,
  including multi-file splat layouts, with metadata from flags; an existing
  id is an error unless `--replace`. Bytes the library already holds
  (shared meshes, unchanged files under `--replace`) are not re-uploaded.
- `rm` transfers nothing — the server reclaims every file no remaining
  asset references — and refuses to empty a library (delete the library
  instead).
- Concurrent edits converge through the same revision compare-and-swap as
  push. A later full `push` from a directory that predates these edits
  trips the drift guard if it would delete assets ([publish](publish.md)):
  pull to merge first.
- Deleting an asset = `library rm <ns>/<name> <id>` (no local copy needed),
  or delete its directory locally and push — either way the server
  reconciles storage to the manifest (check with `--dry-run` first).
