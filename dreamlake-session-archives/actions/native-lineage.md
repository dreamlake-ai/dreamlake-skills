# Inspect native session relationships

```sh
nymph --version
nymph session-lineage --help
nymph session-archives --help
```

1. Read the [relationship contract](../reference/docs-lakeshore-hosts-native-session-lineage.md) and establish whether the request is inspection or authorized metadata reconciliation. A parent/child question alone does not authorize collection, archive upload or execution.
2. Resolve the exact authorized Source, provider, local root and native address from existing metadata. Read using the [published protocol](../reference/docs-lakeshore-hosts-native-session-lineage.md#protocol). Preserve source boundaries and unresolved addresses; do not search another account for a missing parent.
3. Report each returned relation using its recorded type and evidence. Distinguish native ancestry from managed session relationships and resource affiliations. Keep missing or unsupported evidence explicit; do not infer parenthood from titles, message links or similar history.
4. If reconciliation is requested, inspect bounded native evidence locally first, then follow [native collection](../reference/docs-lakeshore-hosts-native-session-lineage.md#native-collection) for the exact enrolled and applied source binding. Confirm the deployed capability and running worker prerequisites. Preserve archive policy and active terminal processes; installing a package alone does not establish automatic collection.
5. Read back the exact source and native address. Compare the returned edge identity, type and evidence with the inspected metadata. After an uncertain response, retain the same source and evidence for recovery; do not substitute a new source or upload transcript content.
6. Report separately what was observed locally, recorded in the API, exposed in the UI and enabled for future automatic reconciliation. Distinguish a relationship inventory from a complete session inventory and state any truncation or unsupported provider format.

For an explicitly SDK-only request, use only a documented SDK operation; if none is available, explain the gap and stop before switching to HTTP. Never invent `dl` commands or SDK methods. Provider installation is not proof of archive-body support or runnable terminal access. For absent continuation evidence, retain the unsupported result rather than constructing an edge.
