<!-- generated from https://docs.dreamlake.ai/notes/writing.md at 0.1.114 594d5f21; do not edit -->

# Writing and formatting

## Native rich Markdown editor

Notes uses the native rich Markdown editor. The former CodeMirror fallback and
browser experiment switch have been removed, including for browsers that saved
the old fallback preference. Source mode uses Monaco and keeps the same shared
Markdown document.

The native editor keeps canonical Markdown in the same collaborative RTC
document. It supports rich Markdown presentation, formatting and insertion
commands, comments and suggestions, references, folding and section navigation,
Vim mode, audio controls, and collaborator cursors and selections. Notes keep
their existing save, sync, version history, and recovery controls. Switching
between rich presentation and raw Markdown does not change the note source.

In rich presentation, native headings align with the surrounding prose: the
heading marker and its separator whitespace do not add a visual indent. Paragraphs
and lists use consistent spacing, and blank lines retain a visible editing position.
These presentation rules preserve the original Markdown, including heading spaces
and line breaks; raw Markdown keeps the source visible.

### Stable prefixes and structural Backspace

The native rich editor keeps heading (`#`), list (`-`, `1.`),
and quote (`>`) prefixes in a fixed left gutter. Activating a line keeps its body
text in the same position and preserves its wrapping. Nested lists keep a stable
indent at each level, and task items keep a stable checkbox slot.

With a collapsed caret at the start of visible text, **Backspace** converts an
`#`-style (ATX) heading to a paragraph; outdents a nested list or task item one level together
with its subtree; converts a root list or task item to a paragraph; or removes
one quote level. Within text or at a soft wrap, Backspace performs ordinary
character deletion. **Undo** restores the structural edit as one action. Raw
Markdown mode keeps literal deletion behavior. These changes apply only to the
native editor. Underlined (Setext) headings have no leading marker and
retain ordinary deletion behavior.

The native editor does not change the CLI, API, note format, or permissions.

See [Markdown authoring](docs-notes-markdown.md) for named footnotes and LaTeX math.
Only inline citations are superscript; reference entries use normal-sized
`[1]: ` labels on the text baseline, with a space before their content. Uncited
definitions remain visible, including suggestions, without broken return links.
Rendering never rewrites their source.

Use the DreamLake CLI for supported operations. Use Python or TypeScript APIs only when a required operation is unavailable through the CLI or the task explicitly requires SDK integration.

{/* <!-- skill-entrypoint:start --> */}

### Links and Cmd+K

There are three ways to make a link in the rich editor:

- **Paste a URL over selected text.** Select the words and paste an `http` or
  `https` URL to get `[words](url)`. This applies only when the selection is one
  line of plain text that isn't already a link, a URL or code. Any other paste
  is inserted as it is.
- **Type `/link` at the start of a line.** The "/" menu's **Link** command
  inserts `[link text](https://)` with the URL selected, ready to type over.
- **Press Cmd+K** (Ctrl+K on Windows and Linux). This inserts the same link
  around the selected text, with the URL placeholder selected.

In developer mode, Cmd+K means one thing everywhere: it opens the agent's ⌘K
window. This includes the note editor, Vim mode and source mode. The note's text
and selection stay as they were, so Cmd+Enter can still hand the selection to
the agent. Use paste or `/link` for links there. With developer mode off,
Cmd+K in the rich editor inserts a link as before. Source mode (Monaco) has no
link shortcut.

Also in developer mode, **Cmd+Option+K** (Ctrl+Alt+K on Windows and Linux) opens
or closes the agent's ⌘K window from anywhere, with no exceptions: note editors,
source mode, any input, the agent's own input and browser terminals. A browser
terminal otherwise keeps Cmd+K for its shell.

## Placeholders

Use square brackets with whitespace immediately inside both brackets for text
that still needs to be filled in: `[ xxxxx ]`,
`[ owner name ]`, or `[ launch date ]`. Notes show these as blue highlighted inline
boxes with visible brackets and inner spacing: `[ owner name ]`. Hover over
a box to see **placeholder**. This works in the editor, table cells and
read-only view. Keep the brackets until you replace
the placeholder with its final value; the saved Markdown remains plain text. `[text]`, `[ text]`, and `[text ]`
are plain text, not placeholders. Empty brackets and whitespace-only content
are not placeholders.

```markdown
Owner: [ owner name ]
Launch: [ launch date ]
Review #note:6aa9951250d9de84058e8ebb before publishing.
```

References take precedence: Markdown links such as `[guide](docs-notes.md)`,
reference links with a definition (`[guide][docs]` or `[docs]`), images, and
`#note:<full-note-id>` keep their reference behavior. Do not turn a reference
into a placeholder. Task markers (`[ ]` and `[x]`) and brackets inside code
are not placeholders. Escape the opening bracket (`\[literal]`) when you want
ordinary bracketed prose without a highlight.

## Inline text color and highlights

Use a color directive to style an inline span in Notes previews, table cells,
and the app’s rendered Markdown:

```markdown
:color[Important]{color="#ef4444"}
:color[Ready]{color="green"}
:highlight[Review needed]
:highlight[Key finding]{color="#60a5fa"}
:color{text="Review needed" color="#f90"}
```

The content is plain text, including any Markdown markers. Escape brackets and
backslashes with a backslash in bracket content. Color values must be quoted:
3, 4, 6 or 8-digit hex colors, or `black`, `silver`, `gray`, `white`, `maroon`,
`red`, `purple`, `fuchsia`, `green`, `lime`, `olive`, `yellow`, `navy`, `blue`,
`teal`, `aqua`, `orange` or `rebeccapurple`. Unknown attributes and invalid colors
remain literal. Code, escaped directives and Markdown links remain literal too.
Selecting a directive in the editor reveals its original editable source;
saved Markdown is unchanged. `:color` changes the foreground; `:highlight` adds
a translucent background tint and keeps the surrounding text color. Omit the
`color` attribute to use yellow: `:highlight[Important]` or
`:highlight{text="Important"}`. Highlights
accept the same colors and plain-text content as color directives, including the
attribute-only form `:highlight{text="Review needed" color="yellow"}`.
Raw HTML and arbitrary CSS styles are not enabled.

See the [Markdown authoring guide](docs-notes-markdown.md) for formatting examples,
color choices, tables and portability. CLI/API HTML snapshots currently keep
color directives as source text.

### Highlight metadata

Attach optional `user` and `comment` strings to a highlight:

```markdown
:highlight[Review needed]{user="geyang" comment="Confirm the delivery date"}
:highlight[Key finding]{color="#60a5fa" user="geyang" comment="Check the source"}
:highlight[重点 🤖]{comment="First line\nSecond line"}
```

Highlight annotations reuse the Notes inline/sidebar comments toggle. Inline
mode shows no annotation cards or hover popups. Click highlighted text in the
editor to reveal its editable source. Sidebar mode shows the handle and comment
in compact cards in the table-of-contents column, with an edit action for writers.
Cards follow the passages visible in the current viewport; a dense group scrolls
inside the column. Narrow panes fall back to inline mode. Read-only sidebar
cards show metadata without edit controls.

`user` is the canonical public user handle, such as `geyang`, not an internal
user ID or a display name. A single leading `@` is accepted; the saved source is
not rewritten. Autocomplete inserts the canonical handle. Compact sidebar cards
show the handle. Legacy display-name values remain literal; the app never guesses
an account from a name. Attribution is self-declared and does not verify authorship
or grant access.

These are plain-text annotations on a highlight, not saved comment threads.
Either field may be omitted; empty strings add no label. Existing plain highlights
and colors keep their behavior. Select the directive in the editor to edit its
source, including metadata. Metadata does not change the highlighted text or
its source offsets, including in table cells and read-only app views.

Attribute values use JSON string escaping: `\"` for a quote, `\\` for a
backslash and `\n` for a newline. HTML in metadata stays text. Unknown or duplicate
attributes and malformed quoting leave the whole directive literal. Use `user`,
not `author`; only `color`, `user` and `comment` are accepted secondary attributes.

Agents should first read the note and retain its revision, then replace the exact
existing directive using `--if-match` and read it back.
For example, set `NOTE_ID` to the target note ID and read its legacy ETag
(the replacement helper uses an ETag, not a v2 `rtc:` revision):

```bash
# NOTE_ID is the ID returned by create/list; this edits an existing highlight.
SNAPSHOT=$(mktemp)
dreamlake notes read --legacy --note "$NOTE_ID" --json > "$SNAPSHOT"
REV=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["etag"])' "$SNAPSHOT")
dreamlake notes replace ':highlight[Review needed]' \
  --text ':highlight[Review needed]{user="geyang" comment="Check the source"}' \
  --note "$NOTE_ID" --if-match "$REV"
dreamlake notes read "$NOTE_ID" --json
rm "$SNAPSHOT"
```

The existing `notes create --text` / `--file` commands also accept this syntax.
There is no dedicated highlight command: these are ordinary Markdown directives,
so matching text with `notes replace` is enough; no line numbers are needed.

Do not overwrite the whole note to update one annotation. CLI/SDK storage already
accepts this Markdown; no new client method or package version is required.
CLI/API HTML snapshots retain rich directives as source text; the app renders them.

### Web preview tags

Open a web page beside a Note with a preview tag:

```markdown
:preview[https://example.com/deck/#slide-3]{title="Slide 3"}
```

The URL is required; the title is optional. Tags work in the editor, tables and
rendered Markdown. A normal click opens the built-in web preview panel beside
the Note. New targets open as tabs in the existing panel on the right; a right
panel is created only when one is absent. Reopening the exact URL reuses its tab;
different URL fragments retain separate preview tabs. Note references follow the
same rule. References opened from a side Note add tabs in that same side panel,
preserving the current Note and its edits. Modified clicks keep ordinary browser link behavior.
Only absolute HTTP(S) URLs without embedded credentials are accepted. Invalid
syntax, duplicate or unknown attributes, unsafe schemes, code and escaped tags
remain literal text. The saved source is unchanged by rendering.

A target must allow iframe embedding. Its own authentication and framing policy
still apply. A temporary tunnel URL works only while its tunnel and server run.
Browser static rendering retains an inert label before hydration; server CLI
HTML snapshots currently leave preview directives as literal source with the
existing source mapping. They do not load the target or create a panel.

### Embeds

See [Embeds and query arguments](docs-notes-embeds.md) for responsive ratios, fixed
sizes, zoom, and the artifact/preview query API. Inline references stay in the text
flow; `embed` shows a content block; opening a reference shows its standalone
page in the preview/browser.

### Artifact references (development preview)

Use Markdown directive notation for new references:

```markdown
:note[6ab5aaeed3b4339ea2f4c162]
:artifact[geyang/pitch-deck]
:bindr[bindr-id]
:asset-reference[asset-id]{caption="plot"}
:placeholder[owner name]
:chatgpt-content-reference[0]
```

This follows the [remark-directive convention](https://github.com/remarkjs/remark-directive),
a Markdown extension, not core CommonMark. Brackets hold primary content; braces
hold optional named attributes. Resource semantics are DreamLake-specific.
The namespace and artifact ID are both required because artifact IDs are scoped
to their owner; note IDs resolve globally. The Note picker, extraction and copy
reference button now prefer `:note[<full-note-id>]` in the development UI.
Note headers show a clickable `#…` badge with the last six ID characters.
Artifact headers use a copy icon instead of shortened ID text, including in
compact layouts. Either button copies the complete bracket
reference, including the owner namespace for artifacts; it does not create a
share link or change access.

Saved `#note:<full-note-id>`, `#artifact:geyang/pitch-deck`,
`:note{id="note-id"}`, `:artifact{namespace="geyang" id="pitch-deck"}` and all
existing attribute-only rich components remain accepted. Do not bulk-rewrite
stored notes. Bare `:note{ID}` and `:artifact{namespace/id}` are invalid.
Secondary attributes currently include asset `caption`; values are double-quoted
JSON strings. Unknown/duplicate attributes, conflicting primary values, missing
fields and invalid IDs remain literal. Preserve exact source on reads and patches.
Placeholder content can escape brackets and backslashes with a backslash.

References grant no access and never change sharing. Missing/inaccessible resources
remain unavailable. Code, escapes and Markdown links stay literal. Imported ChatGPT
citation forms stay unresolved and retain their original source; never invent a
Note or artifact to replace them. Existing `[ owner name ]` placeholders remain supported.

Click an artifact tag in a Note or a project's Note pane to open the reusable
artifact panel to the right of that note. The note stays open. Clicking another
reference to the same artifact reuses its panel, including references to a different
slide. Panels retain the artifact viewer's preview, version, zoom and authorized
sharing controls, and use the common draggable tabs and close controls.
Control/Command-click keeps the ordinary artifact link behavior. The current
implementation is a development preview until the companion UI is deployed.

The browser resolves titles through authorized artifact metadata. API HTML
previews map each full token atomically and leave it unresolved, without fetching
private metadata or embedding capability URLs. Artifact tags are implemented in
the local development UI/API; production deployment is not yet verified. There
is no artifact insertion picker yet: type/paste the complete token.

### Fragment reference syntax (development preview)

A reference can retain a slide or section target as a URL fragment:

```markdown
:note[6ab5aaeed3b4339ea2f4c162#overview]
:artifact[geyang/pitch-deck#slide-3]
:artifact[geyang/pitch-deck#/3]
```

The optional named form `:note[id]{fragment="overview"}` is also accepted.
Specify the fragment only once. The parser separates it from the resource ID and
preserves the exact raw token, including percent encoding. Malformed fragments
remain literal. Static API HTML maps the complete reference atomically without
fetching metadata or creating capabilities.

Artifact references pass their fragment to the panel's local `dreamlake.route`.
For example, `:artifact[geyang/landing-pages#slide-3]` opens the landing-page copy
at stage 3. Selecting another slide updates the existing iframe without reloading
it or changing the surrounding Note/project URL. Note-section scrolling remains
separate from this artifact behavior. An existing artifact ID or an author-defined hash route must supply
the target; do not infer slide numbering or invent a section.
