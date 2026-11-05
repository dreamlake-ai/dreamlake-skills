<!-- generated from https://docs.dreamlake.ai/notes/html-reads.md at 0.1.118 967fe678; do not edit -->

# HTML reads

## HTML snapshot preview

With the compatible v2 server and CLI, `dreamlake notes read "$NOTE_ID" --view html`
returns a complete inert HTML document. Root `data-note`, `data-hash`,
`data-revision`, `data-source-type`, `data-offset-unit` and `data-source`
attributes contain the exact canonical source and its baseline. Element
`data-char="start:end"` ranges address that source in Unicode code points;
`data-map` marks linear text, atomic syntax or generated presentation.

Decode the source attribute once to recover canonical source, including original
entity spelling and line endings. Patch that source using the embedded revision;
never upload generated wrappers or mapping attributes. HTML reads are snapshot
views; `--view html --since` is rejected. HTML-looking source is rendered as
HTML, other source as Markdown. Rich or restricted structures may map atomically;
no editable range is guessed from generated text. Scripts, active attributes and
network-loaded media are excluded from this static preview.

## Literal Markdown for agents

With CLI 0.34.4 and a compatible server, `--view html` on a Markdown note is
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
format marker. Canonical HTML notes retain their existing HTML source mapping.

## Focused and historical reads

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

A list consumes a number before its items; nested lists and items continue
that same counter depth-first. Paragraph wrappers inside list items do not
consume another number. Numbering restarts in each section; content before
the first heading uses `s0`. A list target includes its entire subtree, and an
item target includes its continuation lines and nested lists. Markdown task
markers (`[ ]`, `[x]`, `[X]`) and leading HTML checkbox inputs identify checklist
items. Read IDs from the returned snapshot rather than calculating them. `--tag` is an exact element ID; a section ID selects its
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

See the [addressed-read specification](https://docs.dreamlake.ai/dev/notes/addressed-reads)
for ID generation, ranges, examples, efficiency limits, and the executable
acceptance harness. Use a CLI/server build supporting the addressed-read options.

## Comment targets in HTML reads

Closed comment directives render as individually addressable elements with
`data-rich-kind="comment"`. Their `id` uses `sN.cK` (for example, `s1.c2`),
sharing the section's reading-order counter with paragraphs, lists and items.
Use the returned ID with `--view html --at "$REVISION" --tag s1.c2` to read one
comment's exact canonical directive. The atomic `data-char` and `data-lines`
cover the complete directive, including attribution attributes. These HTML
addresses are revision-local; read them from the snapshot, rather than guessing.

Saved references such as `:comment[cmt_0123456789abcdef01234567]` additionally
carry `data-comment-id="cmt_0123456789abcdef01234567"`. That persistent resource
ID survives moves and edits and can be used with the comment API. Repeated
references to the same saved comment get distinct HTML target IDs but retain
the same `data-comment-id`. Keyed drafts expose `data-comment-key`; inline text
comments have a target address but no invented persistent resource ID.

Static HTML shows source text or the saved reference ID; it does not fetch a
comment's private body. Code examples, escaped directives, malformed comments
and Markdown links remain literal. When normalization prevents an exact range,
the surrounding block remains the edit target instead of a guessed comment range.

## Rich tokens in HTML reads

The v2 HTML renderer recognizes strict Markdown source tokens for
`:placeholder[owner]`, `:asset-reference[asset-id]{caption="plot"}`,
`:note[note-id]`, `:artifact[geyang/pitch-deck]`, `:bindr[bindr-id]` and
`:chatgpt-content-reference[0]` in the development preview, plus every saved legacy form. Attribute values use double quotes;
unknown/duplicate attributes and malformed tokens remain literal source.
Code, escaped punctuation, Markdown links and URL paths keep their ordinary
interpretation. Existing `[ owner ]` placeholders retain blue boxes, visible
brackets, inner spacing and the **placeholder** hover label.

Recognized components carry atomic `data-char` and `data-map`
attributes addressing the complete token in canonical Unicode-code-point
source. The root `data-source` remains exact. When Markdown normalizes a region
so an exact token range cannot be proven, its enclosing block remains atomic;
the renderer never guesses an editable token range.

Static previews show assets, Notes and bindrs as unresolved labels. They perform
no metadata lookup and include no download URL or authorization capability.
Labels come only from source the reader can already read. The interactive
application separately resolves resources through authorized APIs. Imported
ChatGPT citation tags render as unresolved broken-link icons with their original
source in the hover label. Neither form implies that the reference is valid or
accessible. Placeholder CSS is static and hash-authorized by the preview's CSP;
source-provided styles and active HTML remain inert.

This capability is included in the September 24 release. Browser rich
components were delivered separately in
[UI PR #415](https://github.com/dreamlake-ai/dreamlake-ai/pull/415).

## Heading numbering in HTML reads

Markdown Notes can place the following options in an initial YAML front-matter
block. The same policy is used by the editor/outline and the server HTML preview:

```markdown
---
render:
  headings:
    numbering: hierarchical
    startLevel: 2
---
# Design notes

## First
#### Deeper
### Next
## Last
```

The displayed numbers are `1`, `1.1`, `1.2`, `2`. Number only actual ancestors:
skipping a heading level does not insert zero components. A heading above
`startLevel` stays unnumbered and resets the sequence. `numbering` accepts `off`
or `hierarchical` (default `off`); `startLevel` is an integer from 1 through 6
(default 2). ATX and setext headings share the policy; code fences do not count.

Front matter remains part of canonical source, source hashes and patch offsets,
but does not render as body text. Unknown YAML fields survive unchanged. Invalid
supported values or malformed YAML produce a visible diagnostic and default
options; no source rewrite occurs. Unterminated front matter stays literal body
source with a diagnostic.

Numbers are display-only spans marked `data-map="generated"` with no editable
source range. Heading source/anchor behavior stays unchanged. Body and rich-token
source ranges still count from the start of the full document, including front
matter and CRLF. These options apply to Markdown source; canonical HTML is not
interpreted as Markdown front matter. Server HTML reads and the browser
editor/outline support this policy in the September 24 release.
