# Work with Notes

Before the first live read or edit, follow [task identity setup](../reference/notes-collaboration.md#one-identity-per-task).
Set both `DREAMLAKE_AGENT_ID` and `DREAMLAKE_AGENT_NAME`, reuse their values across
independent shell calls, and check the roster after the first intended live read.
Without the ID, edits can save without agent presence or fading highlights.
Do not replay saved edits to test attribution; roster verification does not prove
browser highlights. Respect an explicit request for unattributed work.

Use the CLI for normal note tasks and choose a focused read for targeted work:

```bash
dreamlake notes list
dreamlake notes toc --note NOTE_ID
dreamlake notes read NOTE_ID --legacy --section setup
```

Before editing, retain a normal `notes read NOTE_ID` source snapshot with its
opaque revision and content hash; do not use `--json` for this baseline. Prepare
the patch from that exact source, excluding the read's metadata header, and pass
the original revision unchanged as `--base-revision`. Never fabricate, decode,
or substitute a content hash or legacy ETag for that revision. Read the successful
receipt's acknowledged revision back with `notes read NOTE_ID --at ACK_REVISION`
and inspect the intended change. On conflict, retain the baseline and draft,
review concurrent changes, then reconcile; never use `--force` or merely swap in
a fresh baseline to make an old patch pass. `--legacy` uses a separate ETag
contract. See [Notes](../reference/notes.md),
[reading](../reference/notes-reading.md), and [editing](../reference/notes-editing.md).

When creating or changing technical implementation or availability claims, add
or update one concise version line for the affected section. Record the exact
relevant versions actually tested (for example, DreamLake CLI and Nymph) and the
backend source revision when known; distinguish an inspected source revision
from a tested or deployed revision. Label claims as proposed, source-only,
verified production, or unknown according to the evidence. A merged PR or a
published package alone does not verify production behavior. Mark unavailable
version or deployment evidence unknown rather than guessing. Keep software
versions separate from the Note's opaque editing revision, and omit irrelevant
components and repeated per-line labels.

For image URLs to embed in Markdown or HTML, use [inline image upload](media.md).
Use `notes files upload` for attachments that inherit the note's permissions.

For Markdown agent markup, element bodies are literal Markdown, including `<`,
`&`, backslashes and Unicode. Do not HTML-render or DOM-parse these bodies; use
canonical source metadata for machines. Keep a single source range and the
original revision. For literal edits without inline-DFF delimiter escaping,
generate a unified diff from baseline and edited files; see
[editing with patches](../reference/notes-editing.md#literal-text-without-inline-dff-escaping).

For durable checkpoints, use `note tag NOTE_ID LABEL` on the
same Note, then `note hist NOTE_ID` / `note read NOTE_ID --version VERSION_ID` to inspect them.
These commands require CLI 0.44.1 or later: check installed `--help` first.
Retain a reviewed full read's content hash with `--hash`; a stale hash or
`409 note_changed` requires review, never a blind retry or a copied Note.
See [saved versions](../reference/notes-versions.md) for pagination, ancestry,
JSON receipts and uncertain-result recovery.

CLI 0.44.2 removes the old `notes version` command group; use the forms above.

For an older retained snapshot missing from history, follow
[recover a retained snapshot](https://docs.dreamlake.ai/notes#recover-a-retained-snapshot).
First preserve a full source baseline (exact bytes, revision and content hash)
for the same stable Note ID and namespace, and preserve the old source with its
provenance separately. REST hashes use raw SHA-256 digests, not the opaque
revision or the CLI's `sha256:` prefix. `tag` saves current content only: historical
revision saves and checkpoint/journal reads require the documented REST fallback.
Keep `hist` and version readback CLI-first when installed help supports them.
Check CLI and server capabilities independently; an older server's unsupported
route or `409` is not empty history and must not lead to a live-body overwrite.
An unknown create result requires paginating `hist` via `nextCursor`/`--before`
and reading candidate versions by ID to compare exact text, hash and operation
metadata before retrying. Tags are not idempotency keys; stop if the outcome
remains ambiguous. Verify the saved version's exact revision, text, hash and
`sourceObservedAt`, plus the unchanged live baseline. Older servers may ignore
`revision`; HTTP 201 or a matching hash alone is not proof of recovery.
See [saved versions](../reference/notes-versions.md#recover-a-retained-snapshot).

For project filing and ownership-transfer previews, check `dreamlake notes move
--help` first: this command requires CLI 0.45.1; it is absent in CLI 0.45.0 and
earlier. Preview with `notes move NOTE_ID --to-namespace WORKSPACE --project
PROJECT --dry-run`. Standalone `notes move` across namespaces is unavailable; blocked
previews exit 3 and must not be repeated as execution requests. Filing inside
the note's current workspace can execute under its owner's login when
`executable` is true and the user authorized it. Organization notes remain
readable/editable by all current members. Do not simulate a transfer by copying
and deleting the note. See [moving a note](../reference/notes.md#move-a-note-into-a-workspace).

Project filing is separate from ownership. The CLI 0.45.1 additions
`notes create --project SLUG` (repeatable) and `notes projects ID --namespace NS`
cover new-note filing and current filing inspection. Check installed help first:
0.44.3 and earlier lack them. Never emulate an existing-note move through copy/delete,
namespace updates or an older generic mount API. Consult the
[Notes reference](../reference/notes.md#create-and-inspect-project-filing-cli-0451)
for server and adapter gates; missing readiness is unsupported.

Use the matching CLI/server streaming workflow in [Projects](../reference/projects.md).
New `project move` requests stream by default, preserving eligible access and
external filings. Older installed clients may require explicit `--stream`; verify
help and server capabilities independently. Never fall back to a fixed manifest.
Use `project move PROJECT --namespace SOURCE --to DESTINATION --dry-run --out
review.json`, inspect resource/access blockers, then `--confirm --request-file
review.json`. Keep the exact policy/key after a lost response. Unsupported
resources or audiences stop the whole request without removing access or copying
content. Stable IDs, Note RTC bindings and history remain in place.

Source namespace owner requests; destination owner accepts. Project ADMIN alone
cannot transfer. `--accept-if-owner` is explicit and requires current destination
owner authority. Use known-operation status/progress for recovery; never clear
claims, replace keys, or emulate the move by per-Note copy/delete. Existing legacy
saved reviews keep exact replay and existing operations keep decisions/recovery,
but new legacy admission is retired. Standalone Note ownership transfer remains
unsupported; same-workspace Note filing is separate.

CLI 0.48.2 adds attachment journal recovery; CLI 0.48.1 does not include it.
It requires a separately verified journal-enabled API. Check
`notes files write --help`, `cp --help` and `status --help` before using it.
Optional `--idempotency-key` applies only to known-byte text
write/copy, never raw `files upload` or media. Preserve the original operation
ID/request/key/namespace; use `files status OP --note NOTE`, then explicit
`reconcile` to recover original staged bytes without reupload. `cancel` may only
stop an admitted operation before write authorization; uncertain or write-started
work is not safe to delete/resend. Current authority and original actor are
required. See [attachments](../reference/notes-attachments.md#recover-an-attachment-operation-cli-0482).
<!-- Session affiliation requires CLI 0.78.0+ and the matching API. -->

When a task produces or edits a Note, preserve its exact session context.
CLI 0.78.0+ automatically links successful note writes when `CODEX_THREAD_ID`,
explicit `CLAUDE_SESSION_ID`, or the pair `DREAMLAKE_TERMINAL_SESSION_ID` /
`DREAMLAKE_SESSION_NAMESPACE` resolves one owned registered session. Presence
labels are not proof of a native session. If auto-link warns, the note write
still succeeded: use `sessions link SESSION_ID --namespace SESSION_NAMESPACE
--resource-namespace NOTE_NAMESPACE --note NOTE_ID --json` to retry only the link.
Do not repeat a successful edit or guess historical links by title. Read-only
work does not add affiliations; linking never opens a terminal.


CLI 0.79.0+ can also upload a selected conversation export. With user opt-in, set
`DREAMLAKE_CONVERSATION_FILE` to the exact native Codex/Claude export before the
write. No file setting means metadata only. Missing, mismatched or unavailable
archives do not fail the content write; retry only `sessions upload-conversation
SESSION_ID --namespace SESSION_NAMESPACE --file EXPORT --json`. See
[session archives](../reference/sessions.md#optional-conversation-upload-0790)
for identity, size and access limits. An archive is readable history, not a
portable native resume state. Never collect unrelated conversations or secrets.


CLI 0.82.0+ with the matching API registers a missing native session as metadata
only after a successful content write. New sessions default public; set
`DREAMLAKE_SESSION_VISIBILITY=private` for a private new record. Existing privacy
is preserved. If metadata fails, never replay the Note write: run `sessions
register --provider codex --session <native-uuid> --cwd /original/directory`, then
link the returned saved ID. No target discovery, enrollment repair or terminal
start is needed. Conversation upload remains explicit; review custom secrets
before publication even though client and server redact recognized credentials.
