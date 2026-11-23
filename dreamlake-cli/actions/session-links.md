# Link resources and agent sessions

CLI 0.78.0+ with the matching API affiliates a successful Memo write or Artifact
push with one exact owned registered session, resolved from `CODEX_THREAD_ID`,
an explicit `CLAUDE_SESSION_ID`, or the pair `DREAMLAKE_TERMINAL_SESSION_ID` and
`DREAMLAKE_SESSION_NAMESPACE`. The link is attempted after the catalog
acknowledges the content write. If resolution is ambiguous or the affiliation
service is unavailable, the write still succeeded and the CLI warns. Presence
labels (`DREAMLAKE_AGENT_ID`) are not proof of a native session.

Retry only the link, never the content write:

```bash
dl sessions link SESSION_ID --namespace SESSION_NAMESPACE --resource-namespace NOTE_NAMESPACE --note NOTE_ID --json
dl sessions link SESSION_ID --namespace SESSION_NAMESPACE --resource-namespace ARTIFACT_NAMESPACE --artifact ARTIFACT_ID --json
dl sessions link SESSION_ID --namespace SESSION_NAMESPACE --resource-namespace ANNOTATION_NAMESPACE --annotation ANNOTATION_NAME --json
dl sessions resources SESSION_ID --namespace SESSION_NAMESPACE --json   # readable linked Memos, Artifacts and Annotations
```

Do not repush an artifact or replay a successful edit to produce a link, and do
not infer historical authorship or contributors from titles. Read-only work adds
no affiliation; resource sharing and linking never grant terminal access. See
[link memos and artifacts](../reference/cli-sessions.md#link-memos-and-artifacts-0780).

## Register a missing native session (CLI 0.82.0+)

With the matching API, a missing native session is registered as metadata only
after a successful content write; no host discovery, enrollment repair or
terminal start is needed. New sessions default public: set
`DREAMLAKE_SESSION_VISIBILITY=private` before the write for a private new record;
existing privacy is preserved. If that metadata step fails, never replay the
write: run `dl sessions register --provider codex --session <native-uuid>
--cwd /original/directory`, then link the returned saved ID as above. See
[registration and visibility](../reference/cli-sessions.md#registration-and-visibility-0820).

## Upload a conversation export (CLI 0.79.0+, opt-in)

With explicit user opt-in, set `DREAMLAKE_CONVERSATION_FILE` to the exact native
Codex or Claude export before the write, or upload afterwards:

```bash
dl sessions upload-conversation SESSION_ID --namespace SESSION_NAMESPACE --file EXPORT --json
```

No file setting means metadata only. A missing, mismatched or unavailable
archive never fails the content write; retry only the upload. The archive is
readable history under the saved session's permissions, not a portable native
resume state: the original host keeps its native conversation state and an
archive cannot migrate it. Uploads never open a terminal. Review custom secrets
before selecting an export; client and server redact recognised credentials but
not exhaustively, and unrelated conversations must never be collected. A Memo's
contributing-session row opens the saved terminal in the panel to the right
without requiring an archive; when the descriptor has no verified host binding
the panel explains it and **Check connection again** reloads the descriptor
without selecting a host. Identity, size and access limits:
[optional conversation upload](../reference/cli-sessions.md#optional-conversation-upload-0790).

## Record relationships and inspect related work

```bash
dl resources --help
dl resources link note MEMO_ID annotation ANNOTATION_CATALOG_ID --json
dl resources relationships note MEMO_ID --json
dl resources history annotation ANNOTATION_CATALOG_ID --json
dl resources sessions annotation ANNOTATION_NAME --namespace ANNOTATION_NAMESPACE --json
```

1. Check the installed command surface and the matching API release. If either
   lacks the operation, report that limitation; do not invent an endpoint or
   create a replacement resource.
2. Resolve both exact resources from current metadata. Follow the
   [identity and permission contract](../reference/cli-sessions.md#resource-relationships-and-history)
   before selecting identifiers. Keep catalog identities separate from
   publication IDs or URL slugs, and distinguish a saved terminal session from
   an attribution context. Never infer identity or authorship from similar titles.
3. Record only the requested relationship or session association. A Memo body
   reference is a separate content edit owned by `dreamlake-memos`; do not
   rewrite content just to populate the relationship panel.
4. Read the relationship or session list back and retain its returned identity.
   Follow returned cursors when more context is needed, including after an empty
   filtered page. Preserve access boundaries when reporting the result.
5. To undo a confirmed association, use `dl resources unlink RELATIONSHIP_ID`
   or `dl sessions unlink` with the original resource options, then read back.
   Never delete content or change sharing as a shortcut.

After an uncertain response, read back before retrying. Repair metadata without
replaying successful content writes. Do not present a manual association or a
partial activity feed as proof of authorship or a complete audit trail. Never
append invented events or import terminal output into activity. For an explicit
TypeScript integration, follow the [SDK operations](../reference/cli-sessions.md#typescript-resource-relationships)
using the same confirmed identities and readback.

## Inspect native parent and agent relationships

For a native ancestry question, first read the [native relationship contract](../reference/docs-lakeshore-hosts-native-session-lineage.md). Resolve the authorized Source and exact native address before reading relationships. Keep resource affiliations separate from native ancestry; an associated Memo does not identify a spawning agent.

Use the documented read interface when HTTP is allowed. For an explicitly SDK-only request, report a missing documented SDK operation instead of inventing one or silently switching transports. Report unresolved parents and unsupported evidence as such; do not turn a read-only question into collection, transcript upload or terminal execution. For authorized metadata reconciliation, follow the [native collection prerequisites](../reference/docs-lakeshore-hosts-native-session-lineage.md#native-collection), preserve the exact applied Source and archive policy, and verify the returned evidence through a readback. Report local inspection, recorded metadata and automatic activation separately.
