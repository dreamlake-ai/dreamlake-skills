# Link Note and Artifact writes to an agent session

CLI 0.78.0+ with the matching API affiliates a successful Note write or Artifact
push with one exact owned registered session, resolved from `CODEX_THREAD_ID`,
an explicit `CLAUDE_SESSION_ID`, or the pair `DREAMLAKE_TERMINAL_SESSION_ID` and
`DREAMLAKE_SESSION_NAMESPACE`. The link is attempted after the catalog
acknowledges the content write. If resolution is ambiguous or the affiliation
service is unavailable, the write still succeeded and the CLI warns. Presence
labels (`DREAMLAKE_AGENT_ID`) are not proof of a native session.

Retry only the link, never the content write:

```bash
dreamlake sessions link SESSION_ID --namespace SESSION_NAMESPACE --resource-namespace NOTE_NAMESPACE --note NOTE_ID --json
dreamlake sessions link SESSION_ID --namespace SESSION_NAMESPACE --resource-namespace ARTIFACT_NAMESPACE --artifact ARTIFACT_ID --json
dreamlake sessions resources SESSION_ID --namespace SESSION_NAMESPACE --json   # readable linked notes and artifacts
```

Do not repush an artifact or replay a successful edit to produce a link, and do
not infer historical authorship or contributors from titles. Read-only work adds
no affiliation; resource sharing and linking never grant terminal access. See
[link notes and artifacts](../reference/cli-sessions.md#link-notes-and-artifacts-0780).

## Register a missing native session (CLI 0.82.0+)

With the matching API, a missing native session is registered as metadata only
after a successful content write; no host discovery, enrollment repair or
terminal start is needed. New sessions default public: set
`DREAMLAKE_SESSION_VISIBILITY=private` before the write for a private new record;
existing privacy is preserved. If that metadata step fails, never replay the
write: run `dreamlake sessions register --provider codex --session <native-uuid>
--cwd /original/directory`, then link the returned saved ID as above. See
[registration and visibility](../reference/cli-sessions.md#registration-and-visibility-0820).

## Upload a conversation export (CLI 0.79.0+, opt-in)

With explicit user opt-in, set `DREAMLAKE_CONVERSATION_FILE` to the exact native
Codex or Claude export before the write, or upload afterwards:

```bash
dreamlake sessions upload-conversation SESSION_ID --namespace SESSION_NAMESPACE --file EXPORT --json
```

No file setting means metadata only. A missing, mismatched or unavailable
archive never fails the content write; retry only the upload. The archive is
readable history under the saved session's permissions, not a portable native
resume state: the original host keeps its native conversation state and an
archive cannot migrate it. Uploads never open a terminal. Review custom secrets
before selecting an export; client and server redact recognised credentials but
not exhaustively, and unrelated conversations must never be collected. A Note's
contributing-session row opens the saved terminal in the panel to the right
without requiring an archive; when the descriptor has no verified host binding
the panel explains it and **Check connection again** reloads the descriptor
without selecting a host. Identity, size and access limits:
[optional conversation upload](../reference/cli-sessions.md#optional-conversation-upload-0790).
