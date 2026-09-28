# Reading and changes

Set `NOTE_ID` to an ID or slug from `dreamlake notes list`. Add `--namespace`
when the note belongs to an organization. The shell examples use `jq`.

## Save a snapshot

```bash
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
REVISION=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md
```

`base.md` is exact source, including its final-newline state. Plain `read > file`
also saves metadata and is **not** a source-only export.

| Field | Use it for |
| --- | --- |
| `note` | The resolved note ID |
| `content` | Complete canonical source |
| `hash` | Content identity, `sha256:<hex>`; pass to `--since` |
| `revision` | Opaque write baseline; pass unchanged to `--base-revision` |

A hash describes text. A revision also identifies collaborative state. Identical
text can have different revisions; do not substitute one token for the other.

## Read only what changed

```bash cli-help="notes diff"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
dreamlake notes diff "$NOTE_ID" --since "$HASH" --format diff
```

`notes diff` is an alias for `notes read --since`. Both accept either format:

```bash
dreamlake notes read "$NOTE_ID" --since "$HASH" --format inline-dff
dreamlake notes read "$NOTE_ID" --since "$HASH" --format diff --json > changes.json
jq -jr .patch changes.json > changes.diff
```

`diff` is the default for differential reads. `inline-dff` is an explicit
character-diff option. `diff` shows a unified line diff, normally with
three context lines around changes. Nearby edits share a hunk; distant edits
remain separate. Older servers may generate broader hunks.

Incremental JSON carries `note`, `base`, `hash`, `revision`, `format`, and `patch`.
`base` identifies the source the patch applies to; `hash` and `revision` identify
the resulting snapshot. Text output includes that metadata and the offset unit
before the patch. Extract `.patch` when a consumer needs only patch text.

No text changes means an empty patch, possibly with a newer revision. Apply an
incremental patch only to source matching `base`, then verify the resulting hash.
Inspecting changes does not edit the note or advance an existing draft's original
baseline. Preserve `baseline.json` and `base.md` until that edit is resolved.

Retained time references also work:

```bash
dreamlake notes read "$NOTE_ID" --since "2 hours ago"
```

The server resolves times and retention. Prefer a saved hash for “since my last
read.” There is no hidden last-read state. Unknown or expired references fail;
the CLI does not silently replace them with the latest revision.

## Read one section

```bash cli-help="notes sections"
dreamlake notes sections release-plan
dreamlake notes sections release-plan --json
```

Use the returned heading anchor to read a passage. Partial reads currently use
the explicit compatibility interface:

```bash
dreamlake notes read "$NOTE_ID" --legacy --section outline --numbered
dreamlake notes read "$NOTE_ID" --legacy --start-line 40 --end-line 80
```

Sections include their heading and all subsections, ending at the next heading
of the same or higher level. Duplicate headings receive suffixed anchors;
`preamble` addresses text before the first heading. Lines are 1-based and inclusive.
A partial read is not a complete patch baseline: its validator covers the whole
note, while its source is only a slice. Never upload that slice as the whole body.

## Search passages

```bash
dreamlake notes find "Draft" --note "$NOTE_ID" --json
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive
dreamlake notes grep "deploy" --glob 'spec-*' --limit 20
dreamlake notes toc --note "$NOTE_ID"
```

`search` finds notes; `find` searches one note; `grep` returns locations across
notes as `slug:line:column`. Literal queries are case-insensitive by default;
regex queries are case-sensitive by default. JSON hits include the legacy ETag
and character range. Use the [legacy editing interface](notes-legacy.md) with
those validators, or capture a full current snapshot for a v2 patch.

## Verify a particular revision

```bash
# REVISION came from a read or a successful patch receipt.
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
```

A matching read returns that snapshot. A mismatch exits `3` with no source on
stdout. After a successful patch, a later read conflict means someone changed
the note again; it does not mean your acknowledged patch failed. Inspect a fresh
read and reconcile before making another edit.

Next: [Editing with patches](notes-editing.md) or
[Live collaboration](notes-collaboration.md).

### Focused and historical reads

`read` returns the current snapshot. Use `--at REVISION` for a retained snapshot;
`--since HASH` remains a unified line-diff read. Snapshot selectors are mutually
exclusive, and cannot combine with `--since` or `--linger`:

```bash
# NOTE_ID identifies an accessible note; copy REVISION from its read receipt.
dreamlake notes read "$NOTE_ID"
dreamlake notes read "$NOTE_ID" --at "$REVISION" --toc
dreamlake notes read "$NOTE_ID" --at "$REVISION" --section s1.1
dreamlake notes read "$NOTE_ID" --at "$REVISION" --tag s1.1.p1
```

Selectors return mapped HTML. Nested `section` tags have content-derived IDs and
`data-index="s1.1"`; headings use `s1.1.h`. Paragraphs (`p`), lists (`l`),
regular items (`li`) and checklist items (`cli`) share one counter per section:
`s1.p1 → s1.l2 → s1.li3 → s1.cli4 → s1.p5`. Lists consume a number before their
items; nested lists and items follow depth-first reading order. Item paragraph
wrappers do not consume another number. The preamble uses `s0`. Both `ul` and
`ol` use `l`; checklist `li` elements expose `data-checked="true|false"`.
Read IDs from the returned snapshot, including after a server renderer upgrade. `--tag` is an exact element ID; a section ID selects its
entire subtree. IDs are local to one revision. Unknown IDs and missing snapshots
return 404; every read checks current permissions.

`data-char="start:end"` are absolute, zero-based, end-exclusive Unicode code-point
ranges in original source. `data-lines` is one-based and inclusive. A scoped root
contains only the selected `data-source`, with its global `data-source-start` and
`data-source-end` and its own `data-source-hash`. The root's `data-hash` and
`data-revision` still identify the complete document. Subtract `data-source-start`
when slicing local source; keep absolute offsets in the patch. TOCs carry exact
heading source on each heading and empty root source. Never upload a slice or
rendered HTML as the complete note.

```bash
# edit.dff is prepared from the exact source at REVISION.
dreamlake notes patch "$NOTE_ID" --file edit.dff --base-revision "$REVISION" --exact
# NEXT_REVISION comes from that write receipt.
dreamlake notes read "$NOTE_ID" --at "$NEXT_REVISION" --tag s1.1.p1
```

Exact mode refuses concurrent edits with 412; native merge mode remains available
by omitting `--exact`. `--if-match` checks the current revision, while `--at`
retrieves history: do not combine them. Preserve an existing draft's original
baseline even after another read or linger update. Linger continues to emit source
snapshots and line diffs; inspect a streamed revision using a separate pinned read.
Pinned reads do not overwrite live presence with historical offsets.

See the [addressed-read specification](https://docs.dreamlake.ai/dev/notes/addressed-reads/)
for ID generation, ranges, examples, efficiency limits, and the executable
acceptance harness. These addressed read options are available in CLI 0.33.0 and require the matching Notes server support. The linked page provides the detailed ID and range contract.

For Markdown with address hints (CLI 0.33.0), select the annotated view:

```bash
# REVISION is the original read revision; NOTE_ID identifies an accessible note.
dreamlake notes read "$NOTE_ID" --at "$REVISION" --section s1 --view markdown
dreamlake notes read "$NOTE_ID" --at "$REVISION" --tag s1.li3 --view markdown
```

Lists and items use the shared section-local order above; a list or parent item
includes its nested content. CLI 0.34.1 adds list-container hints to Markdown reads.
The CLI inserts comments such as `<!-- s1.li3 chars=11:29 lines=3:4 -->` before
original Markdown blocks. These hints are reading metadata, not article content;
all offsets refer to the original source. Do not write annotated output back.
Default source reads remain unchanged. The annotated view supports snapshot
scopes and `--at`, but cannot combine with `--since`, `--linger`, or `--json`.
HTML-source notes require `--view html`.
