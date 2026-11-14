# Edit a memo

First complete [task identity setup](identity.md); reuse it in every shell call.

Use this workflow for every requested body edit, including a small correction,
appending a reference, or updating a prompt. Named before/after checkpoints and
presence intent are part of the edit workflow; do not wait for a separate request
to make the work visible. A read-only review creates no checkpoints.

Inspect installed
`dl memos revise --help` first. Review a complete source snapshot, prepare the
proposed text, then use the guarded revision path when available:

```bash
dl memos read "$MEMO_ID" --json > baseline.json
# Review the source; prepare proposed.md without changing baseline.json.
dl memos revise "$MEMO_ID" --baseline baseline.json --file proposed.md \
  --intent "Clarify the evaluation criteria." --label evaluation-criteria \
  --receipt revision-receipt.json
```

Completion requires the concrete intent, immutable before/after version IDs and
acknowledged source readback, not just a successful patch or an opaque revision.
Use the receipt to report completed and incomplete stages separately. A no-op
needs no duplicate checkpoints. Preserve namespace and the same task identity.

Preserve human-authored wording and propose pending native redlines. Use direct
replacement only when the current instruction authorizes it; a review request
is not permission to rewrite. Honor existing authorization without asking
repeatedly. Retain native resource directives and use the
[reference action](references.md) for the correct representation.

The command's safeguards and receipt recovery are documented in
[reviewed revisions](../reference/cli-notes-editing.md).
For a targeted patch or when `revise` is unavailable, use the steps below plus
[versions](versions.md): save and verify
a reviewed baseline before editing, generate native suggestions with installed
`memos suggest-diff --help`, then save and verify the result with meaningful
labels/summaries and immutable IDs. Publish concrete edit intent using installed
`memos visit --help` (or the supported lingering read) before editing. Identity,
presence intent, version summary and session linkage serve different purposes.
Never invent an edit flag or repeat an accepted body edit to recover metadata.

The lower-level patch example below is only the content-write step, not a shortcut
around that workflow. With built-in tools or an explicitly requested SDK, use the
same sequence through documented available presence/version operations; do not
silently switch interfaces or invent unsupported methods. If a required operation
is unavailable or fails, preserve the proposal and explain the incomplete stage.
After an accepted body write, recover metadata only; never replay the body.

Prefer a targeted edit that uses source text and its retained revision. First
check the installed client, then retain the complete structured snapshot and
extract its source and original revision as documented in
[editing with patches](../reference/cli-notes-editing.md):

```bash
MEMO_ID=release-plan
dl memos read --help
dl memos read "$MEMO_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > baseline.md
```

Keep both files unchanged while preparing the patch. This is a program parsing
the snapshot; ordinary inspection can use the smallest addressed read.

When the CLI supports `--view markdown` and addressed reads, inspect the retained
snapshot, edit the canonical source using the absolute code-point offsets shown
in its hints, and submit a v2 patch against that original revision:

```bash
dl memos read "$MEMO_ID" --at "$BASE" --view markdown --tag s1.ul2.li3
dl memos patch "$MEMO_ID" --base-revision "$BASE" --exact --file edit.dff
```

Use the item's address and line hints to identify the selected text. Ranges
refer to original source, including list markers and indentation. Apply the
absolute code-point range in `edit.dff`; never patch generated comments or write
the annotated Markdown back as source. For a complete DFF example and escaping rules, read
[editing with patches](../reference/cli-notes-editing.md). Keep the source passage,
revision and patch together. Never treat mapped output or a JSON envelope as source. Pass the opaque revision unchanged: never fabricate,
decode, or replace it with the content hash or a legacy ETag. If a target sentence may repeat, check its
occurrence and choose the intended passage; do not edit every match unless
asked. After success, retain the resulting revision from the receipt
and read the changed passage with `--at "$NEXT_REVISION"` to verify it.

If the patch returns 412, preserve the original baseline and proposed patch,
stop, then read current source and reconcile before making another write. Do
not use `--force` or fetch a fresh revision just to make the old patch pass.
Use JSON only when a program needs structured receipts. If the installed CLI lacks addressed
Markdown reads, use the explicitly documented [legacy conditional edits](../reference/cli-notes-legacy.md);
never pass a legacy ETag as a v2 revision.

## Markdown source

For footnotes, math and other authoring syntax, consult the bundled
[Markdown authoring reference](../reference/docs-notes-markdown.md). Preserve named
`[^key]` citations and `[^key]:` definitions in source; rendered numbers and
baseline labels are presentation only. Uncited definitions and their suggestions
must not be discarded. Use `\(...\)` for inline math and `\[...\]` for display
math, not `\{`. Retain the normal revision guard and acknowledged readback.

## Versions and availability

When changing technical implementation or availability claims, add or update one
concise version line for the affected section. Record exact relevant versions
actually tested (for example, DreamLake CLI and Nymph) and the backend source
revision when known; distinguish inspected source from tested or deployed code.
Label claims as proposed, source-only, verified production, or unknown according
to the evidence. A merged PR or published package alone does not verify production
behavior. Mark missing version or deployment evidence unknown; never guess.
Software versions are separate from the Memo's opaque editing revision. Omit
irrelevant components and repeated per-line labels.

## Literal agent markup

For Markdown memos on the literal-markdown contract, HTML-like wrappers provide
IDs and ranges; their contents are **verbatim Markdown**, including list markers,
checkboxes and comment directives. Use one `data-char` range for that source;
do not invent inner/outer ranges. Keep `<`, `&`, backslashes and Unicode literal.
Do not add escapes and do not remove escapes already in the saved Markdown.
This is for agents, not browsers: do not render it or DOM-parse its body.
Use `--view markdown` for ordinary reads; machine integrations decode canonical
source metadata once and use its address index. Preserve the original revision.

For punctuation-heavy changes, generate a unified diff from the unchanged
baseline file and an edited copy, then submit it with `patch --format diff
--base-revision "$BASE"`. This avoids manually escaping inline-DFF delimiters.
A literal read does not change the patch format's syntax. See
[editing with patches](../reference/cli-notes-editing.md#literal-text-without-inline-dff-escaping).
