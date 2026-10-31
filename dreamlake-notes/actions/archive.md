# Archive or restore notes and folders

Check the installed interfaces before choosing commands:

```bash
dreamlake notes archive --help
dreamlake notes unarchive --help
dreamlake notes list --help
dreamlake folders --help
```

1. Set and reuse the [task identity](identity.md). Resolve a requested note in its owning namespace, or a folder in its
   owning namespace and project. Inspect the candidate and
   preserve its stable ID; do not choose another same-named item.
2. Read the archival contract in the [Notes guide](../reference/docs-notes.md)
   and the installed CLI help. Choose the requested archive or unarchive
   operation. Do not substitute deletion, a version tag, or a metadata edit.
3. Run one operation against the resolved ID. For a note, use `notes archive`
   or `notes unarchive`; for a folder, use `folders archive` or `folders unarchive`.
   Take namespace/project options from the installed help.
4. Read back with archive inclusion enabled and check the returned archive
   state, then compare the normal listing. Verify the requested scope only;
   do not edit content as a way to test archival.
5. Report the item link and verified result. If a request times out or reports
   an unconfirmed result, inspect the same ID before deciding whether to retry.
   Keep denied or conflicted operations visible in the report.

For an explicit SDK integration request, consult the current
[API documentation](https://docs.dreamlake.ai/api/archival) for the requested
language and installed version. Do not invent a client method or a model-tool
name. If the installed interface is missing, report that gap and use the
supported update/install workflow from `dreamlake-cli`; do not emulate archive
by deleting or rewriting the item.
