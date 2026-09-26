# Rich content and HTML

Notes store source text. Use the supported Markdown syntax for rich content,
and patch that source through the [normal editing workflow](/notes/editing/).
Saving source and verifying its visible rendering are separate checks.

## Highlights and text color

```markdown
:highlight[Review this sentence]
:highlight[Key finding]{color="#60a5fa"}
:color[Important]{color="red"}
```

`:highlight[...]` adds a background tint; the default is yellow. `:color[...]`
changes the text color. Raw `<span style="...">` is not a substitute: Notes do
not enable arbitrary HTML/CSS styling.

Directive content is plain text, including any Markdown markers. Escape brackets
and backslashes with a backslash. Colors must be quoted supported names or
3-, 4-, 6-, or 8-digit hex values. Invalid colors and unknown attributes remain
literal. Attribute-only forms also work:

```markdown
:highlight{text="Review needed" color="yellow"}
:color{text="Important" color="#ef4444"}
```

Rendering support differs by surface. The app supports these directives; CLI/API
HTML snapshots currently preserve color directives as source text. Check the
[Markdown authoring guide](https://docs.dreamlake.ai/notes/markdown/) for supported
colors, tables, references, and current rendering limits.

## References and placeholders

Keep existing raw note references intact:

```markdown
#note:507f1f77bcf86cd799439011
```

Use an actual accessible note ID, not that example ID. Do not convert references
into guessed URLs or silently replace their source syntax. The authoring guide
is the reference for newer directives and development-preview features.

Short bracket placeholders such as `[ owner name ]` render as placeholders in
the app. Preserve their source when patching surrounding text. Rendered chips,
generated labels, and editor decorations are not replacement document source.

## Read a rendered HTML snapshot

```bash
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --view html > preview.html
```

The CLI writes the complete server-rendered HTML byte-for-byte, with no text
metadata prefix, JSON wrapper, or added newline. It validates the note identity,
source hash, and revision before emitting output. To inspect the acknowledged
result of an edit:

```bash
ACK=$(jq -er .revision receipt.json)
dreamlake notes read "$NOTE_ID" --view html --if-match "$ACK" > verified.html
```

A revision mismatch exits `3` without output. HTML reads require the matching
server contract and CLI 0.26.2+. They cannot be combined with `--json`, `--since`,
`--format`, `--legacy`, `--linger`, or partial/numbered reads.

## Map an element back to source

| Attribute | Meaning |
| --- | --- |
| Root `data-note`, `data-hash`, `data-revision` | Note and snapshot identity |
| Root `data-source-type`, `data-offset-unit`, `data-source` | Canonical source and its encoding/unit contract |
| Element `data-start`, `data-end`, `data-map` | Source range and mapping kind |

Decode the root source attribute exactly once. Offsets count Unicode code points,
not DOM UTF-16 units. Atomic mappings require whole-range edits; generated content
has no editable source range. Use the mapped canonical source and original
revision to prepare a patch. Never upload preview wrappers or metadata as the
note body.

For attaching an HTML file with its own preview URL, see
[Attachments](/notes/attachments/).
