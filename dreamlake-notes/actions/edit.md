# Edit a note

First complete [task identity setup](identity.md); reuse it in every shell call.

Prefer a targeted edit that uses source text and its retained revision. First
check the installed client and retain a normal source read, including its opaque
revision and content hash. Do not use `--json` for this editing baseline:

```bash
NOTE_ID=release-plan
dreamlake notes read --help
dreamlake notes read "$NOTE_ID" > baseline.txt
BASE=$(sed -n '3s/^revision: //p' baseline.txt)
```

When the CLI supports `--view markdown` and addressed reads, inspect the retained
snapshot, edit the canonical source using the absolute code-point offsets shown
in its hints, and submit a v2 patch against that original revision:

```bash
dreamlake notes read "$NOTE_ID" --at "$BASE" --view markdown --tag s1.ul2.li3
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" --exact --file edit.dff
```

Use the item's address and line hints to identify the selected text. Ranges
refer to original source, including list markers and indentation. Apply the
absolute code-point range in `edit.dff`; never patch generated comments or write
the annotated Markdown back as source. For a complete DFF example and escaping rules, read
[editing with patches](../reference/cli-notes-editing.md). Keep the source passage,
revision and patch together. Exclude the normal read's metadata header from the
source being edited. Pass the opaque revision unchanged: never fabricate,
decode, or replace it with the content hash or a legacy ETag. If a target sentence may repeat, check its
occurrence and choose the intended passage; do not edit every match unless
asked. After success, take the resulting revision from the plain-text receipt
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
Software versions are separate from the Note's opaque editing revision. Omit
irrelevant components and repeated per-line labels.

## Literal agent markup

For Markdown notes on the literal-markdown contract, HTML-like wrappers provide
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
