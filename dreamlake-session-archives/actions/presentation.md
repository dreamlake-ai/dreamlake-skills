# Manage personal session presentation

Read [personal session presentation](../reference/docs-lakeshore-hosts-native-session-lineage.md#personal-session-presentation)
and use its documented interface. For an SDK-only request, keep that constraint
and report missing SDK support rather than silently switching transports.

1. Resolve the requested namespace and exact authorized session identities.
   Keep source, provider, native session and component boundaries intact;
   deduplicate only through an authoritative association. For a bulk cleanup,
   finish paginated inventory and record excluded or unresolved entries before
   claiming complete coverage.
2. For names, preserve useful existing titles. Derive a concise label from
   verified native title metadata, an explicit delegated task, or an actual
   opening human request. Use only the evidence needed for the label; leave
   encrypted or unknown content unresolved. Do not infer a task from a UUID,
   tool output, or another source's similarly named session.
3. Read current personal preferences and retain their revision and exact
   aliases. Preserve existing personal names during automatic cleanup unless
   the user explicitly requested replacing them. Prepare the intended changes
   separately from unrelated placement or archive preferences.
4. Apply only the requested fields using the documented revision guard. For
   bulk edits, keep a per-identity journal of the original state and confirmed
   result. Pace writes; stop and reconcile unknown outcomes by reading exact
   state. Re-read conflicts instead of blindly overwriting newer changes.
5. Read back the resulting identity and changed fields. Report confirmed,
   preserved, conflicted and unresolved counts separately. Keep Undo tied to
   the returned revision and restore only the fields this action changed.

Treat hiding a row, changing its displayed nesting, and changing its label as
presentation tasks. Do not substitute provider-file edits, ownership changes,
process termination, transcript deletion or upload consent for these requests.
When the user asks for those separate operations, resolve their own supported
capabilities and authorization.
