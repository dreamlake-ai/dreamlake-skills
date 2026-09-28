# Edit a note

First complete [task identity setup](identity.md); reuse it in every shell call.

Prefer a targeted edit that uses source text and its retained revision. First
check the installed client and inspect the exact passage:

```bash
NOTE_ID=release-plan
dreamlake notes read --help
```

When the CLI supports `--view markdown` and addressed reads, obtain the
revision from a scoped read, edit the canonical source using the absolute
code-point offsets shown in its hints, and submit a v2 patch against that same
revision:

```bash
dreamlake notes read "$NOTE_ID" --view markdown --tag s1.li1
BASE='revision from the scoped read'
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" --exact --file edit.dff
```

Use the item's address and line hints to identify the selected text. Ranges
refer to original source, including list markers and indentation. Apply the
absolute code-point range in `edit.dff`; never patch generated comments or write
the annotated Markdown back as source. For a complete DFF example and escaping rules, read
[editing with patches](../reference/notes-editing.md). Keep the source passage,
revision and patch together. If a target sentence may repeat, check its
occurrence and choose the intended passage; do not edit every match unless
asked. After success, take the resulting revision from the plain-text receipt
and read the changed passage with `--at "$NEXT_REVISION"` to verify it.

If the patch returns 412, preserve the original baseline and proposed patch,
stop, then read current source and reconcile before making another write. Do
not fetch a fresh revision just to retry the same patch. Use JSON only when a
program needs structured receipts. If the installed CLI lacks addressed
Markdown reads, use the explicitly documented [legacy conditional edits](../reference/notes-legacy.md);
never pass a legacy ETag as a v2 revision.
