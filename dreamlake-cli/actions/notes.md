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

For edits, retain the correct baseline and use the documented patch contract;
read the acknowledged revision back. `--legacy` uses ETags; v2 patches use an
opaque revision. See [Notes](../reference/notes.md),
[reading](../reference/notes-reading.md), and [editing](../reference/notes-editing.md).

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
PROJECT --dry-run`. Cross-workspace transfers are currently unavailable; blocked
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
[Notes reference](../reference/notes.md#create-and-inspect-project-filing-cli-0444)
for server and adapter gates; missing readiness is unsupported.
