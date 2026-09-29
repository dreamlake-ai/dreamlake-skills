# Read a note

First complete [task identity setup](identity.md); reuse it in every shell call.

Set `NOTE_ID` to an ID or slug from `dreamlake notes list`. Add
`--namespace <slug>` when the note belongs to an organization. Check the
installed CLI before choosing a read contract:

```bash
NOTE_ID=release-plan
dreamlake notes read --help
```

When help lists `--view markdown`, `--toc`, `--section`, `--tag` and `--at`,
use addressable Markdown reads. Start with the outline, then pin any section or
element reads to the revision printed in the first result:

```bash
dreamlake notes read "$NOTE_ID" --view markdown --toc
REVISION='revision from the outline result'
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --section s1.1
# Or target one passage or list item instead of reading the whole section:
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --tag s1.1.p1
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --tag s1.ul2.li3
```

Use the smallest read that answers the question. The Markdown view adds
address, character and line hints as comments before headings, paragraphs,
lists and list items. Read the actual IDs from the snapshot: paragraphs `p`,
unordered lists `ul`, ordered lists `ol` and all items `li` share one counter
per section: `s1.p1 → s1.ul2 → s1.ul2.li3 → s1.ul2.li4 → s1.p5`.
Nested lists extend the parent path, e.g. `s1.ul2.li4.ol5.li6`. A list/item
target includes its subtree. Checkbox state is an item attribute
(`data-checked="true|false"`), not a different ID type. Hints are not saved note text.
Keep the revision with the passage. Do not combine `--at` with `--since` or
`--if-match`, or combine multiple scope selectors. If the installed CLI lacks
these options, use the compatible legacy reads below and do not infer HTML
addresses:

```bash
dreamlake notes toc --note "$NOTE_ID"
dreamlake notes read --legacy "$NOTE_ID" --section setup
dreamlake notes read --legacy "$NOTE_ID" --start-line 40 --end-line 80
```

For a whole-source delta, retain the plain-text read's `hash` and pass it to
`--since`; `hash` and opaque write `revision` are different tokens. Use
`--json` only when a program needs parsed fields. See [reading and changes](../reference/notes-reading.md)
and [the full Notes guide](../reference/notes.md).

For comment targeting in HTML reads, use the emitted `sN.cK` ID with `--tag` and
the same revision. Saved comments also expose persistent `data-comment-id`;
HTML target IDs are revision-local. See [comment targets](../reference/notes.md#comment-targets-in-html-reads).

## Literal agent markup

For Markdown notes on the literal-markdown contract, HTML-like wrappers provide
IDs and ranges; their contents are **verbatim Markdown**, including list markers,
checkboxes and comment directives. Use one `data-char` range for that source;
do not invent inner/outer ranges. Keep `<`, `&`, backslashes and Unicode literal.
Do not add escapes and do not remove escapes already in the saved Markdown.
This is for agents, not browsers: do not render it or DOM-parse its body.
Use `--view markdown` for ordinary reads; machine integrations decode canonical
source metadata once and use its address index. Preserve the original revision.
