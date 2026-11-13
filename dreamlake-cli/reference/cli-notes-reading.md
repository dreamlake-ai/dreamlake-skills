<!-- generated from https://cli.dreamlake.ai/notes/reading.md at 0.125.0 b8ca5e1; do not edit -->

# Reading and changes

Set `MEMO_ID` to an ID or slug from `dl memos list`. Add `--namespace`
(or its alias `--ns`) when the memo belongs to an organization: the CLI looks an
ID or slug up in that namespace or your configured one. The shell examples use `jq`.

## Save a snapshot

```bash
MEMO_ID=release-plan
dl memos read "$MEMO_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
REVISION=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md
```

`base.md` is exact source, including its final-newline state. Plain `read` prints
the mapped Markdown reading view, generated hints included, and is **not** a
source export; `--json` is the structured snapshot, and `--view source` prints
the exact source bytes only (no header, no added newline), so
`dl memos read "$MEMO_ID" --view source > memo.md` is a byte-exact export.

| Field | Use it for |
| --- | --- |
| `note` | The resolved memo ID |
| `content` | Complete canonical source |
| `hash` | Content identity, `sha256:<hex>`; pass to `--since` |
| `revision` | Opaque write baseline; pass unchanged to `--base-revision` |

A hash describes text. A revision also identifies collaborative state. Identical
text can have different revisions; do not substitute one token for the other.

## Read a saved version

With CLI 0.44.1+, `dl memos read MEMO_ID --version VERSION_ID` reads the
immutable text saved by `memos tag`; `memos hist MEMO_ID` lists its version IDs.
`note` aliases `notes`. Saved reads return version metadata and `text` in JSON,
not a live write baseline, and refuse live/partial/HTML/collaboration options.
See [Saved versions](cli-notes-versions.md). Without `--version`, reads remain live.

## Read only what changed

```bash cli-help="memos diff"
MEMO_ID=release-plan
dl memos read "$MEMO_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
dl memos diff "$MEMO_ID" --since "$HASH" --format diff
```

`memos diff` is an alias for `memos read --since`. Both accept either format:

```bash
dl memos read "$MEMO_ID" --since "$HASH" --format inline-dff
dl memos read "$MEMO_ID" --since "$HASH" --format diff --json > changes.json
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
Inspecting changes does not edit the memo or advance an existing draft's original
baseline. Preserve `baseline.json` and `base.md` until that edit is resolved.

Retained time references also work:

```bash
dl memos read "$MEMO_ID" --since "2 hours ago"
```

The server resolves times and retention. Prefer a saved hash for “since my last
read.” There is no hidden last-read state. Unknown or expired references fail;
the CLI does not silently replace them with the latest revision.

## Read one section

```bash cli-help="memos sections"
dl memos sections release-plan
dl memos sections release-plan --json
```

Use the returned heading anchor to read a passage. Section reads use the
explicit compatibility interface; for a line range use `--lines` (below):

```bash
dl memos read "$MEMO_ID" --legacy --section outline --numbered
```

Sections include their heading and all subsections, ending at the next heading
of the same or higher level. Duplicate headings receive suffixed anchors;
`preamble` addresses text before the first heading. Lines are 1-based and inclusive.
A partial read is not a complete patch baseline: its validator covers the whole
memo, while its source is only a slice. Never upload that slice as the whole body.

## Read a line range

```bash
dl memos read "$MEMO_ID" --lines 40:80
dl memos read "$MEMO_ID" --lines 40:80 --json
```

`--lines a:b` takes two integers, 1-based and inclusive, and prints the exact
source slice with its global address: after `note`, `hash` and `revision` the
text header carries `scope: lines a:b chars s:e` (Unicode code points,
end-exclusive, in the complete source) and `complete: false`, then the slice.
The JSON form is `note`, `hash` (of the complete source), `revision`, `lines`,
`chars`, `scope` (`{"lines": [a, b]}`), the `content` slice, `complete: false`
and `next` (the line after `b`, when the memo has one). It has no whole-note `content`, so a focused read
cannot be mistaken for a complete body: never upload it as the whole memo. The
last line's newline belongs to it; a final newline does not start a line.
Ranges past the end are refused, not clamped. `--lines a:b --view source`
prints only the slice bytes. `--lines` combines with `--at` and `--if-match`, and not with `--legacy`, `--start-line`, `--end-line`,
`--numbered`, `--since`, `--linger` or the mapped views. The conversion from
lines to code points is done by the CLI and by the TypeScript API
(`note.read({ lines: [40, 80] })`), never by hand.

## Search passages

```bash
dl memos find "Draft" --note "$MEMO_ID" --json
dl memos grep "TODO" -C 2
dl memos grep --regex '\bFIXME\b' --case-sensitive
dl memos grep "deploy" --glob 'spec-*' --limit 20
dl memos toc --note "$MEMO_ID"
```

`search` finds memos; `find` searches one memo; `grep` returns locations across
memos as `slug:line:column`. `find` and `toc` read the v2 snapshot: their JSON
carries `note`, `hash`, `revision` and code-point ranges, `--at REVISION` pins a
retained snapshot, and a literal `find` query is case-sensitive unless
`--no-case-sensitive`. `grep` hits still carry legacy ETags and character ranges;
use the [legacy editing interface](cli-notes-legacy.md) with those validators, or
capture a full current snapshot for a v2 patch.

## Verify a particular revision

```bash
# REVISION came from a read or a successful patch receipt.
dl memos read "$MEMO_ID" --if-match "$REVISION" --json > verified.json
```

A matching read returns that snapshot. A mismatch exits `3` with no source on
stdout. After a successful patch, a later read conflict means someone changed
the memo again; it does not mean your acknowledged patch failed. Inspect a fresh
read and reconcile before making another edit.

Next: [Editing with patches](cli-notes-editing.md) or
[Live collaboration](cli-notes-collaboration.md).

### Focused and historical reads

`read` returns the current snapshot. Use `--at REVISION` for a retained snapshot;
`--since HASH` remains a unified line-diff read. Snapshot selectors are mutually
exclusive, and cannot combine with `--since` or `--linger`:

```bash
# MEMO_ID identifies an accessible note; copy REVISION from its read receipt.
dl memos read "$MEMO_ID"
dl memos read "$MEMO_ID" --at "$REVISION" --toc
dl memos read "$MEMO_ID" --at "$REVISION" --section s1.1
dl memos read "$MEMO_ID" --at "$REVISION" --tag s1.1.p1
```

Selectors return mapped HTML. Nested `section` tags have content-derived IDs and
`data-index="s1.1"`; headings use `s1.1.h`. Paragraphs (`p`), unordered lists
(`ul`), ordered lists (`ol`) and all list items (`li`) share one counter per
section, in document reading order. List and item IDs include their containing
list/item path: `s1.p1 → s1.ul2 → s1.ul2.li3 → s1.ul2.li4 → s1.p5`.
A nested ordered list under the fourth element is `s1.ul2.li4.ol5`, and its
next item is `s1.ul2.li4.ol5.li6`. The suffix is the shared section counter,
not an item-local position.

Checklist items use the same `li` prefix and expose `data-checked="false"` or
`data-checked="true"`; ordinary items omit that attribute. Adding, checking or
removing a checkbox does not change the item's prefix or its container's type.
There is no `tl`, `tli` or `cli` type. HTML tags remain `ul`, `ol` and `li`.

Lists consume a number before their items; nested lists and items follow
depth-first reading order. Item paragraph wrappers do not consume another
number. The preamble uses `s0`.
Read IDs from the returned snapshot, including after a server renderer upgrade. `--tag` is an exact element ID; a section ID selects its
entire subtree. IDs are local to one revision. Unknown IDs and missing snapshots
return 404; every read checks current permissions.

### Literal Markdown for agents

With CLI 0.34.4 and a compatible server, `--view html` on a Markdown memo is
an **agent format**: HTML-like tags supply structure and addresses; their
contents are the exact original Markdown. There is one `data-char` source
range, including the construct's syntax. There is no inner/outer split.

```text
<li id="s0.ul1.li2" data-char="0:11">- [ ] Ship
</li>
```

Keep Markdown literal: `- [ ]`, `**bold**`, `:comment[...]`, backslashes,
`<`, `&`, and Unicode remain exactly as saved. Do not add HTML escapes,
Markdown escapes, or Unicode escape sequences to element contents. Do not
strip escapes that are already present in canonical source. No display-text
index conversion is needed: ranges address the source text inside the wrappers.
A parent item's range includes its nested source.

This is not browser HTML. Do not render it or use a DOM parser to recover its
body. CLI 0.34.4 requests `contentFormat=literal-markdown` automatically; direct API clients add that parameter to a v2 HTML read. Existing clients keep the prior rendered contract. The API serves Markdown agent markup as `text/plain` and marks the root
`data-content-format="literal-markdown"`. Generated heading numbers and other
preview decoration are absent. The separate visual preview is unchanged.

Metadata attributes still use transport encoding: decode the root `data-source`
attribute once for an exact machine-readable source slice, and use the trusted
root `data-addresses` index rather than finding tags inside arbitrary Markdown.
CLI `--view markdown` handles this and prints literal source with address hints.
Keep the original revision with the source and verify the acknowledged edit.
Older servers may return rendered HTML; do not assume literal bodies without the
format marker. Canonical HTML memos retain their existing HTML source mapping.

`data-char="start:end"` are absolute, zero-based, end-exclusive Unicode code-point
ranges in original source. `data-lines` is one-based and inclusive. A scoped root
contains only the selected `data-source`, with its global `data-source-start` and
`data-source-end` and its own `data-source-hash`. The root's `data-hash` and
`data-revision` still identify the complete document. Subtract `data-source-start`
when slicing local source; keep absolute offsets in the patch. TOCs carry exact
heading source on each heading and empty root source. Never upload a slice or
rendered HTML as the complete memo.

```bash
# edit.dff is prepared from the exact source at REVISION.
dl memos patch "$MEMO_ID" --file edit.dff --base-revision "$REVISION" --exact
# NEXT_REVISION comes from that write receipt.
dl memos read "$MEMO_ID" --at "$NEXT_REVISION" --tag s1.1.p1
```

Exact mode refuses concurrent edits with 412; native merge mode remains available
by omitting `--exact`. `--if-match` checks the current revision, while `--at`
retrieves history: do not combine them. Preserve an existing draft's original
baseline even after another read or linger update. Linger continues to emit source
snapshots and line diffs; inspect a streamed revision using a separate pinned read.
Pinned reads do not overwrite live presence with historical offsets.

See the [addressed-read specification](https://docs.dreamlake.ai/dev/notes/addressed-reads/)
for ID generation, ranges, examples, efficiency limits, and the executable
acceptance harness. These addressed read options are available in CLI 0.33.0 and require the matching Memos server support. The linked page provides the detailed ID and range contract.

For Markdown with address hints (CLI 0.33.0), select the annotated view:

```bash
# REVISION is the original read revision; MEMO_ID identifies an accessible note.
dl memos read "$MEMO_ID" --at "$REVISION" --section s1 --view markdown
dl memos read "$MEMO_ID" --at "$REVISION" --tag s1.ul2.li3 --view markdown
```

Lists and items use the shared section-local order above; a list or parent item
includes its nested content. CLI 0.34.1 adds list-container hints to Markdown reads.
The CLI inserts comments such as `<!-- s1.ul2.li3 chars=11:29 lines=3:4 -->` before
original Markdown blocks. These hints are reading metadata, not article content;
all offsets refer to the original source. Do not write annotated output back.
The annotated view is the default text output of `memos read`; `--view source`
prints the exact source bytes only, and `--json`, `--since` and `--lines` always
return exact source. The annotated view supports snapshot
scopes and `--at`, but cannot combine with `--since`, `--linger`, or `--json`.
HTML-source memos require `--view html`; a defaulted text read of an
HTML-source memo prints exact source instead.

## Addressed reading view

`dl memos read MEMO_ID` (the text default; `--view markdown` says so
explicitly) uses the shared v2 reading view.
It prints actual line breaks and addressed block hints, automatically draining
pages pinned to the first revision. A failed continuation exits unsuccessfully;
stdout may contain the completed prefix, so consumers must check the exit code.
Generated hints are reading metadata, never an edit baseline. Use `--json` source
reads to retain canonical content and the original opaque edit revision.

TypeScript callers use the facade: `const note = dl.notes(noteId)` opens a
local handle by stable ID; `await note.read()` is the exact snapshot,
`note.read({ view: "mapped", section, address, at })` the reading view and
`note.read({ lines: [40, 80] })` a focused slice. The page-level
`dl.notes.namespace(ns).readView(noteId, { at, start, section, tag, toc, limit })`
remains: follow `next` with the first `revision` until `complete` is true. Offsets address Unicode code points in the reading view.
The 32 KiB page budget measures JSON-escaped text bytes. This contract requires
a backend supporting `view=reading`; older backends fail rather than silently
returning a different representation.
