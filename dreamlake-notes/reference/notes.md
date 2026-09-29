# Notes

Read [Markdown authoring](https://docs.dreamlake.ai/notes/markdown/), [Embeds and query arguments](https://docs.dreamlake.ai/notes/embeds/),
[Panels](https://docs.dreamlake.ai/notes/panels/), and [Linked note items](https://docs.dreamlake.ai/notes/linked-items/) for focused guides.
This page retains the complete CLI/API reference and existing section links.

  A note is a collaborative Markdown document. This is how a script — or a
  coding agent working through bash — edits one while people have it open.

See [Panels and agent control](https://docs.dreamlake.ai/notes/panels) for artifact previews, pinned tabs,
and programmable native layouts.

In live preview, an opening H1 with content below it is positioned
above the viewport once, before interaction. Scrolling back to the title keeps it
visible; typing, blur, and idle time do not automatically hide it again. Raw
Markdown, title-only notes, and explicit search or section navigation retain
their existing behavior. Formatting remains enabled while editing. Vim visual
selections remain visible in both rich and raw views. Each connected browser session shares its cursor and selection, including other sessions of the same account. Switching focus keeps the last position visible until that session leaves the Note. Cursor labels size to their names, capped at 20 characters of display width with ellipsis. Remote text updates preserve the
visible text position in the note pane; a new scroll gesture, keystroke, or
selection takes precedence over a pending viewport correction.

History timeline previews return to the current working draft when the pointer
leaves the timeline. An explicitly placed edit marker or selected change range
keeps its historical view open; clicking a version label alone does not pin it.

Use the DreamLake CLI for supported operations. Use Python or TypeScript APIs only when a required operation is unavailable through the CLI or the task explicitly requires SDK integration.

{/* <!-- skill-entrypoint:start --> */}

## Read Notes directly

**For normal reads, run the bare command and inspect its output directly:**

```bash
# Set NOTE_ID to the note ID, slug, or exact title you want to read.
dreamlake notes read "$NOTE_ID"
```

Do not add `--json` or `--view` for ordinary human or agent reads. The default
output includes canonical source, a revision, and a content hash. Retain the
revision and hash with the source when preparing safe edits; agent convenience
is not a reason to switch to JSON.

Use JSON only for an explicitly requested structured integration. The scripted
concurrency examples below demonstrate that compatibility path; they are not
the default reading procedure. Read normal collaboration and selection receipts
directly too.

{/* <!-- skill-entrypoint:end --> */}

## Public catalog reads

`GET /namespaces/:slug/notes` accepts requests without an Authorization header.
Anonymous callers and authenticated nonmembers receive only live public notes;
namespace members retain their existing catalog access. Pagination totals use
the same visibility filter as the rows. A supplied invalid or expired token
returns 401 rather than silently falling back to anonymous access. Anonymous
searches do not activate or flush collaborative rooms. Creating, editing and
sharing notes still require authentication and their existing permissions.

## Browsing in the app

`/<namespace>/profile?tab=notes` and `/<namespace>/notes` reuse the same
Notes catalog. Your own namespace and organizations you belong to show
resources and actions allowed by your permissions. Signed-out visitors and
signed-in visitors to other namespaces see public resources only, without
creation or modification controls. Profile uses an avatar rail; the application
uses resource navigation for the namespace in the URL.

Your own Notes catalog retains Shared with me and recent organization notes. Private Note share links require sign-in under the server's per-person grant rules.

The application sidebar shows the resource owner's avatar and links, including
for anonymous public readers. Your signed-in identity and personal/organization
switcher are separate from that owner. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

The detail header returns anonymous readers to `/<namespace>/profile?tab=notes`
and signed-in readers to `/<namespace>/notes`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.

### Project and bindr associations

Adding a project or bindr from a note changes membership while keeping the
current note, URL, search and panes open. Choose a destination project inside
the association picker. Bindrs belong to that project; identical bindr names in
different projects are separate destinations. A bindr association uses the
existing mounted note node, not a new copy or arbitrary filesystem placement.

Pending operations disable duplicate submissions. A failed bindr addition may
leave a successfully added project association; retry the bindr addition after
reviewing the inline status. Removing an association uses the same context
preservation behavior and retains the last-project guard. Use the separate
**Open project** or **Open bindr** links when you want to navigate.

### Matching passages

Searching the Notes catalog shows up to two distinct matching passages beneath
each result title, with matching words highlighted. Hover or focus a passage to
open a line-based popover, or use **Preview matches** from the keyboard. The
popover shows multiple matching paragraphs with their line breaks and all query
highlights. Repeated excerpts appear once with an occurrence count; expand them
to choose the exact section and occurrence. Selecting a
passage opens the note in the existing pane and selects the matching occurrence
when its current source still agrees with the result. Identical wording at
different source positions remains distinct. A changed source reports **Match
changed** and asks you to choose a current occurrence instead of using stale
offsets. Title-only matches open the note normally.

The current catalog query and list scroll survive opening a passage. Source-only
matches that cannot be mapped safely to rendered Markdown remain visible in the
explicit source excerpt; the interface does not guess a rendered position.

### Resource subviews

Project file and folder details use native draggable sibling view tabs. Files
offer **Preview** and **Details**; folders offer their available **Files**,
**README**, **Visualize** and **Episodes** views. Each tab identifies its resource
and subview. In the project view, selecting another resource reuses the existing
resource tab slots instead of accumulating README/Files pairs for visited folders.
Open note tabs remain in place. Drag a tab to an edge to compare views side by side, or into a panel's
center to group it. Closing a subview leaves its siblings open; **Views** reopens
closed views. Tab switches retain mounted view state. Existing source-browser
URL-owned view controls keep their navigation behavior. ML-Dash run inspectors
use the same native tabs for **Params** and **Log**, while detail pages keep
their existing separate log panel.

## Install

**CLI**

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dreamlake login
```

**Python**

```bash
pip install dreamlake
dreamlake login
```

Both read the same saved login. `pip install dreamlake` installs the Python
SDK; install the standalone CLI using the CLI tab before running
`dreamlake login`. The Python package is not the supported CLI installer.

## Collaboration and sync

People can edit the same note simultaneously. Edits merge through the existing
CRDT; checking sync does not lock the note or wait for other editors to stop.
The status beside the note title describes this tab:

| Status | Meaning |
|---|---|
| **Synced** | This tab matched the server revision and text checksum. |
| **Syncing** | Changes or verification are still in progress. |
| **Out of sync** | Sending is paused; inspect the recovery dropdown. |

A connected socket alone does not prove that text matches. The browser requests
a checksum calculated by the RTC server and compares it only when both hold the
same revision and no local changes are pending. Different revisions, slow
acknowledgements and delayed checks remain **Syncing**; they are not proof of
corruption. New edits invalidate the previous verification.

Typing and selection replacement stay local while the edit is applied, so
intermediate delete/insert events do not reset the cursor. Composition finishes
before an incoming update changes the editor. Updates from other people continue
to merge normally.

### Reconnect and recovery

During a temporary disconnect, the tab keeps pending operations and retries on
reconnect. It replays their original identities only against a compatible server
checkpoint. A proven text mismatch, an update that cannot be applied, or a changed
checkpoint that prevents safe replay pauses sending and retains a local draft.
It does not automatically send that held draft after a refresh.

Open **Out of sync ▾** beside the note title:

1. Choose **Download local draft** to save your text before discarding anything.
2. Choose **Use server version** to discard the held local draft and fetch current
   server content. This does not overwrite the server note.
3. Compare your downloaded draft with the note, then reapply any missing changes
   in the editor.

**Download edit data** saves `note-edit-data.json` with the local editing and sync
state for inspection. It does not send edits, discard the draft or load a server
version. This is diagnostic data, not an automatic restore/import action.

A retained draft normally survives refresh in the same browser tab. Browser
storage can be unavailable; follow the warning to copy or download it before
closing or refreshing. Do not clear browser storage as a recovery shortcut.

Legacy CLI/Python edit helpers retain their conditional revision checks below.
The v2 patch interface uses merge mode by default and opt-in exact mode.
They cannot read or recover an unsent draft held in another browser tab. A fresh
CLI read describes server content, not proof that every open editor matches it.

## Time travel

Click the **Time travel** history icon beside the title to open a near-full-screen,
resizable viewer. Use **Play/Pause**, previous/next step, or the ticked slider to
browse retained versions. Each tick selects one recorded edit; the slider snaps
to those ticks.

The viewer is **view only**. It captures the checkpoint and retained edits when
opened, renders them separately, and does not replace the live editor or publish
changes. Close and reopen it to include newer edits. There is no restore action.

When you step or play through versions, added rendered text briefly glows green.
Removed text appears in red with a strikethrough, fades, then disappears. Colors
compare the view you left with the view you entered: stepping backward reverses
which text appears and disappears. A jump compares the two selected views rather
than replaying every intermediate edit. Formatting-only changes update normally.

Pausing playback freezes an active highlight; resuming continues it. Stepping or
scrubbing cancels the old transition so ghosts never pile up. Faster playback
uses shorter fades. Reduced-motion preferences use static highlights that clear
without fading. Very large comparisons display the version without highlights
to keep navigation responsive. Deleted ghosts are presentation-only, excluded
from accessibility output, selection, and the code-copy action. They never alter
saved text or the live editor. Scroll position stays under your control.

History starts at the retained checkpoint: compaction can remove older versions.
This is not a complete archive, and playback is not a recovery tool for an unsent
local draft. Download a held draft through the sync dropdown instead.

## For coding agents

```bash
git clone https://github.com/dreamlake-ai/dreamlake-skills.git ~/dreamlake-skills
mkdir -p ~/.claude/skills
ln -s ~/dreamlake-skills/dreamlake-notes ~/.claude/skills/
```

`git pull` then updates it. Use `.claude/skills/` for one project.
`dreamlake-cli` in the same repo is the full CLI reference.

The Notes skill's procedure is generated from this guide. Correct examples
here first, then regenerate the docs reference and synchronize the public
skills repository using the [docs-to-skills procedure](https://docs.dreamlake.ai/dev/skills).

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

References take precedence: Markdown links such as `[guide](https://docs.dreamlake.ai/notes/)`,
reference links with a definition (`[guide][docs]` or `[docs]`), images, and
`#note:<full-note-id>` keep their reference behavior. Do not turn a reference
into a placeholder. Task markers (`[ ]` and `[x]`) and brackets inside code
are not placeholders. Escape the opening bracket (`\[literal]`) when you want
ordinary bracketed prose without a highlight.

## Create and list

**CLI**

```bash
dreamlake notes create "Design Doc"
dreamlake notes create "Design Doc" --file draft.md
dreamlake notes create "Design Doc" --text "# Design Doc"
dreamlake notes create "Design Doc" --public        # default is private

dreamlake notes list
dreamlake notes list --limit 20
dreamlake notes list --shared                       # what others sent you
dreamlake notes list --json
```

**Python**

```python
import dreamlake as dl

note = dl.create_note("<namespace>", "Design Doc", text="# Design Doc\n")
note.id, note.namespace, note.etag

dl.list_notes("<namespace>")
dl.list_notes("<namespace>", limit=20, offset=20)
dl.shared_with_me()
```

Titles may repeat — the slug takes a suffix — so keep `note.id` rather than
the name you passed.

## Link to a note in the browser

Use the note's full `id` in browser links:

```text
https://dreamlake.ai/<namespaceSlug>/notes?note=<noteId>
```

Read `namespaceSlug` and `id` from `dreamlake notes create --json` or
`dreamlake notes list --json`. Do not substitute the title or human-readable
slug in this URL: the browser detail route expects the ID, even though the
CLI accepts slugs and titles. Use the returned owner namespace rather than
assuming your personal namespace. The ID is sometimes called the note hash;
it is the `note` query parameter, not a `#` URL fragment.

In the development preview, the path controls the list pane independently of the
active note:

- `/<namespace>/notes` lists notes.
- `/<namespace>/projects` lists projects; `/projects/<project>` opens a project.
- `/<namespace>/bindrs` lists Bindrs; `/bindrs/<bindrId>` opens a Bindr.

Append `?note=<full-note-id>` to any of these paths to open a note. Switching
list context keeps that note open. The note header's contextual list button
hides or restores the list pane. Older note and project links redirect to these
routes. List search includes ordering; default status/category chips are omitted
from the compact panes. Project and Bindr member ordering is applied before
pagination so it covers the entire result set.

Inside another DreamLake note, prefer `:note[<full-note-id>]` (development preview) for a native note
reference. A browser link does not change visibility or grant access to a
private note.

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

See the [Markdown authoring guide](https://docs.dreamlake.ai/notes/markdown/) for formatting examples,
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

### Inline embeds (unreleased)

See [Embeds and query arguments](https://docs.dreamlake.ai/notes/embeds/) for responsive ratios, fixed
sizes, zoom, and the artifact/preview query API. These arguments are unreleased.

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
Both Note and artifact headers show a clickable `#…` badge with the last six ID
characters. Clicking copies the complete bracket reference, including the owner
namespace for artifacts; it does not create a share link or change access.

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

## Suggested edits

Use three tags for reviewable edits stored directly in the note:

```markdown
:insert[new text]{user="geyang"}
:delete[existing text]{user="geyang"}
:replace[existing text]{with="replacement text" user="geyang"}
```

`user` is optional display attribution. `replace` requires `with`; an empty
replacement is allowed. Add optional `reason="Why this change helps"` to explain
a suggestion. Attribute values are JSON strings. Escape literal brackets and
backslashes in the bracket body with a backslash. Insertion-menu choices fill
the signed-in user's name; scripts can supply attribution explicitly.

The bracket form is canonical. The browser also accepts a curly-body alias for
all three kinds; optional named attributes follow in a separate pair of braces:

```markdown
and I:insert[ think this works]
and I:insert{ think this works}
:delete{old text}{reason="No longer needed"}
:replace{old text}{with="new text" user="geyang"}
```

A suggestion can directly follow ordinary text without an intervening space.
Leading and trailing spaces inside its body are preserved when accepted.
Curly bodies support balanced nested braces; escape a literal brace or backslash
with a backslash. Canonical bracket bodies retain their existing bracket escaping.
These aliases apply to suggested edits, not other directive types.

Insertions are underlined and deletions struck through in the note. A replacement
shows both. Inline mode shows these text changes without cards or hover popups.
Switch to Sidebar in a wide pane for **accept · reject** actions. Compact cards
replace the table of contents in its existing column and follow passages visible
in the current viewport. Dense groups scroll inside that column. Hovering or
focusing a card or text anchor highlights the corresponding annotation. Narrow
panes fall back to Inline while retaining the Sidebar preference.

Accept applies the proposed text: insert keeps new text, delete removes old
text, and replace substitutes its `with` value. Reject removes an insertion or
restores the original text of a deletion/replacement. Each decision replaces
only that exact tag in one undoable editor operation and uses the note's normal
collaborative save. If the source changed before the action, it refuses the stale
operation. Note writers can accept/reject; read-only views show the proposal
without write controls. No separate suggestion collection or replies are added.

Incomplete or malformed tags remain literal. Tags inside code, Markdown links,
or comments do not become suggested edits. Supported kinds are intentionally
limited to insert, delete, and replace; use comments for questions or discussion.

## Comments (development preview)

Comments use `:comment[text]` for text stored in the note and
`:comment[cmt_<24 hex digits>]` for a saved comment reference. Both accept optional
`{user="geyang"}` attribution. Braces after a bracket contain metadata only;
there is no `type`, `text`, `ref`, or `userId` field. Attribution is a display
label; the server records the authenticated creator separately. Escape brackets
and backslashes with a backslash. Use `\cmt_...` inside brackets when an ID-shaped
string should be literal text. Code spans and fenced code remain literal.

In the rich editor, typing `:comment{` starts a saved-comment draft. Keep typing
in the note: its side box mirrors the body. The editor supplies a hidden draft
key for retry safety; this key does not create a saved comment object. Closed
drafts first save after 800 ms of inactivity once their body contains at least
two non-whitespace characters, or with any nonempty body when the caret or focus
leaves the comment. Empty and whitespace-only drafts never create objects.
IME composition defers writes. Saving never moves the
caret or replaces active text. Once the caret leaves and the latest body is
acknowledged, source becomes `:comment[cmt_...]{user="..."}` (the optional user
attribute is retained when supplied). Newly typed comment brackets and brace
drafts automatically include the signed-in user's namespace as `user`. Opening
a saved comment edits its object while the reference stays fixed. In Sidebar
view the borderless editor and its Save action share the comment container;
Save waits for the latest save before closing. Comments have no replies; conversations belong in chats.

**Comments → Inline / Sidebar** changes the current view, independently of
storage. Inline comments show the author label and italic text in the author's
collaboration color, with faint brackets around the body. Sidebar comments use
`[…]` anchors and compact bracketed cards. Short comments wrap in full; longer
comments show four lines with **Read more** to expand a scrollable reading view.
**Edit** opens the saved-comment editor separately. The editor grows with its
text up to a bounded height, then scrolls. Cards replace
the table of contents in the same column, follow visible passages, and scroll
within the column when densely packed. Hovering or focusing the anchor or card
highlights its matching annotation. Inline mode has no annotation cards or hover
previews; explicitly opening a saved comment opens its editor beside the clicked
comment, within the visible window, without scrolling the note to the top.
The editor's **Resolve** action saves pending changes before removing that comment
occurrence from the note; **Save** closes the editor without removing it.
Readers without note-edit permission do not see the Resolve action. Narrow panes
fall back to Inline while retaining the Sidebar preference. Read-only readers can open accessible saved comments but
cannot change them. Rendering, loading, and remote text replay never create
comment objects. A brace draft pasted by a script without an editor creation
key remains source text; use the API to create a saved object deliberately.

The same completion menu handles supported tag names after `:`, accessible
resource targets within `[`, and supported attributes within `{`. The `user`
attribute offers people lookup. Free text stays valid; searching does not save
or convert it. Comment bodies are free text: typing inside `:comment[` does not
search saved comments. Existing saved-comment references still render normally.

### Collection API

These endpoints require the matching server version. They are not a CLI release
claim. Paths are relative to the DreamLake API base.

| Method and path | Contract |
|---|---|
| `POST /namespaces/:slug/notes/:noteId/comments` | Body `{body, creationKey, user?}`; authenticated origin-note writer only. Key is 16–128 ASCII letters, digits, `_`, or `-`. |
| `GET /namespaces/:slug/notes/:noteId/comments?q=...` | Up to 30 accessible origin-note comments, newest first; optional body substring search. |
| `GET /namespaces/:slug/comments/:commentId` | Read the object under its original note's permissions. |
| `PATCH /namespaces/:slug/comments/:commentId` | Body `{body, revision}`; compare-and-swap update; stale revision returns 409. |

Returned objects include `id`, `noteId`, `body`, optional `user`, `createdBy`,
`revision`, timestamps and `canEdit`. Bodies are nonempty and at most 20,000
characters. Retrying creation with the same note/key returns the existing object
without overwriting it. A different key deliberately creates a different object.
Reads of public origin notes allow anonymous callers; private origins and deleted
origins do not become visible through a copied reference. Invalid credentials
are rejected, and mutations still require authentication and write permission.

Retain local text on a failed save or revision conflict. Retry uncertain creation
with the same key, and never overwrite a newer object from an older draft.
The editor retains recovery state for the current browser session; the keyed
body remains in the note until acknowledged and collapsed. A changed object
requires reconciliation, with the local draft available to copy. A lost response
can safely be retried. Deleting an anchor does not delete its saved object.

## Name a note

**CLI**

```bash
dreamlake notes read --legacy design-doc                     # slug
dreamlake notes read --legacy 6aa948b3fea6e541282b747e       # id
dreamlake notes read --legacy "Design Doc"                   # exact title

# Every example below uses $NOTE_ID. Set it once — any of the three forms:
NOTE_ID=design-doc
```

**Python**

```python
dl.note("<namespace>/design-doc")
dl.note("6aa948b3fea6e541282b747e")                  # id alone, no namespace
```

A note you may not read answers exactly as one that does not exist.

## Read

### Prefer the smallest relevant read

For a targeted question or edit, read the relevant section or passage instead
of the entire note. Use `toc` or `find` to locate it when needed, then request
that section or line range. Read the whole document when reviewing the whole
document, establishing a required v2 baseline, or recovering a missing or expired
baseline — not on every small edit or verification.

Keep the baseline and its tokens across calls. Once a v2 baseline is available,
use [incremental reads](#keep-incremental-reads-compact) to refresh the cached
source and check edits; inspect only the relevant changed passages. A section
read is not a complete v2 baseline. Do not replace the whole body with a partial
read, or substitute a legacy ETag for an opaque v2 revision.

With the current CLI, `--section`, `--start-line`, `--end-line` and `--numbered`
require `--legacy`. V2 supports complete source and `--since` deltas, not section
snapshots. Prefer the scoped compatibility read for inspection; obtain one full
v2 baseline only when the planned patch workflow needs it and none is cached.

Attributed reads also affect what collaborators see. A full-body read selects
the full source; a scoped read selects its returned passage, and a delta read
does not claim a whole-document selection. Match the requested range to the
work you are doing. Do not issue repeated full reads just to refresh presence;
use a heartbeat for an active session or let recent presence expire.

### Read commands

The existing examples below use the explicit `--legacy` CLI contract (source
`text` and content-hash `etag`). The v2 interface later in this guide uses
`content`, `hash` and an opaque RTC `revision`. Do not mix their tokens.

**CLI**

```bash
dreamlake notes read --legacy "$NOTE_ID"                                    # whole body
dreamlake notes read --legacy "$NOTE_ID" --section install                  # one section
dreamlake notes read --legacy "$NOTE_ID" --start-line 40 --end-line 80
dreamlake notes read --legacy "$NOTE_ID" --start-line 40 --end-line 80 --numbered
dreamlake notes read --legacy --note "$NOTE_ID" --json                      # body + revision
dreamlake notes toc --note "$NOTE_ID"                              # the outline
dreamlake notes toc --note "$NOTE_ID" --json
```

**Python**

```python
note = dl.note("<namespace>/design-doc")
note.text                        # whole body
note.read_section("install")     # one section
part = note.read_lines(1, 40)
part.truncated                   # there is more below
part.total_lines
doc = note.read()
doc.toc()                        # anchor, title, level, line range, ind range
```

A **section** is a heading plus everything under it. Anchors are title slugs
(`setup`, `setup-2` when repeated); text above the first heading is
`preamble`.

`toc` gives each heading an anchor, a **line range** and a **character range** —
enough to edit a part without reading the whole note.

A ranged read reports the **whole** note's revision. Writing a range back as
the body deletes everything outside it — use `replace` instead.

## Edit by what it says

Line numbers move when anyone edits above them; text does not. A query matching
**twice is refused**, not applied to the first match.

The examples below are independent recipes, not a script to run in sequence.
Before each revision-checked edit, read the note and capture its revision
(the CLI recipe uses `jq`):

```bash
REV=$(dreamlake notes read --legacy "$NOTE_ID" --json | jq -er .etag)
```

Inspect the returned body before choosing the edit. After a successful write,
read again before the next edit; do not reuse the old revision or bypass a
conflict with `--force`.

**CLI**

```bash
dreamlake notes find "Draft" --note "$NOTE_ID"
dreamlake notes find --regex '\bTODO\b.*' --flags im --note "$NOTE_ID"

dreamlake notes replace "Draft" --text "Published" --all --note "$NOTE_ID" --if-match "$REV"
dreamlake notes insert --text "New line" --line 10 --note "$NOTE_ID" --if-match "$REV"
dreamlake notes delete "obsolete paragraph" --note "$NOTE_ID"
```

**Python**

```python
doc = dl.note("<uuid>").read()      # local snapshot
doc.find("Draft")
doc.find(regex=r"\bTODO\b.*", flags="im")

updated = doc.replace("Published", query="Draft", all=True)
print(updated)                       # the full new source, not just the part changed
doc.insert("New line", line=10)
doc.delete(query="obsolete paragraph")
print(doc.diff())                    # what would change
doc.save()                           # one conditional write
```

Replacement text is the **first** argument; `query` or `regex` names what to
change. Each edit returns the whole updated source, not just the part it
touched.

Exactly one match is expected. `--all` / `all=True` takes every match;
`--count N` / `count=N` requires exactly N. A failed edit changes nothing.

Python edits are local until `save()`, which writes one patch against the
revision `read()` returned. If the note moved, the save is refused.
`doc.revert()` throws the local edits away.

### Patterns

Regex is explicit — never inferred from the query. JavaScript syntax in both
clients: `(?<name>…)`, `$1`, `$<name>`, `$&`, `$$` for a literal `$`. Capture
expansion is automatic; there is no flag for it.

**CLI**

```bash
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note "$NOTE_ID"
dreamlake notes replace --regex '(?<key>timeout|retries)=(?<value>\d+)' \
  --text '$<key>: $<value>' --all --note "$NOTE_ID" --if-match "$REV" --dry-run
```

**Python**

```python
doc.replace("$1: $2", regex=r"(\w+)=(\d+)", all=True)
doc.replace("$<key>: $<value>", regex=r"(?<key>timeout|retries)=(?<value>\d+)", all=True)
```

`--dry-run` prints the result without writing. Every mutation takes
`--if-match`.

### By line or character range

When the text is awkward to name, address it by position instead. Positions
come from a read or from `toc`.

**CLI**

```bash
dreamlake notes replace --text "Updated line" --line 10 --note "$NOTE_ID" --if-match "$REV"
dreamlake notes replace --text "New block" --line 10:15 --note "$NOTE_ID"
dreamlake notes replace --text "replacement" --ind 120:145 --note "$NOTE_ID"
dreamlake notes insert --text "inserted text" --ind 120 --note "$NOTE_ID"
```

**Python**

```python
doc.replace("Updated line", line=10)
doc.replace("New block", line=(10, 15))
doc.replace("replacement", ind=(120, 145))
doc.insert("inserted text", ind=120)
```

Lines are **1-based and inclusive**. `ind` is **0-based and end-exclusive**,
counted in Unicode code points — so an emoji or a CJK character is one unit,
not two. `toc` returns both.

A line edit keeps the line ending; a character edit adds nothing.

### HTML

Markdown may contain HTML, and a note's body can be an HTML document outright.
When it does, address an **element** rather than raw text — the same sentence
often appears in several places, and a plain query would refuse the edit as
ambiguous.

**CLI**

```bash
dreamlake notes select "#contact" --note "$NOTE_ID"          # where it is, and its text
dreamlake notes replace "Contact us" --text "Talk to sales" --selector "#contact" --note "$NOTE_ID"
dreamlake notes insert --text "<li>New</li>" --selector "#list" --position append --note "$NOTE_ID"
```

**Python**

```python
doc.select("#contact")
doc.select("#contact").replace("Talk to sales", query="Contact us")
doc.select("#contact").update(attrs={"href": "/sales"})
doc.select("#list").insert("<li>New</li>", position="append")
```

A selector must match **exactly one** element; zero or several is an error.
`select` on its own only reports — the element's source range and its decoded
text — and changes nothing.

Only the addressed characters change; entity spelling, attribute quoting and
whitespace elsewhere survive.

## Write whole parts

For replacing a section or the whole body outright, rather than editing text
in place.

**CLI**

```bash
dreamlake notes write "$NOTE_ID" --file whole.md
dreamlake notes write "$NOTE_ID" --section install --file install.md
dreamlake notes append "$NOTE_ID" --text "one more line"
dreamlake notes append "$NOTE_ID" --file more.md
dreamlake notes add-section "$NOTE_ID" --file trouble.md --after install
dreamlake notes rm-section "$NOTE_ID" troubleshooting
```

**Python**

```python
note.write(whole_body)
note.write_section("install", "## Install\n\npip install dreamlake\n")
note.append("\n## Changelog\n\n- shipped\n")
note.insert_section("## Troubleshooting\n\nCheck the logs.\n", after="install")
note.delete_section("troubleshooting")
note.refresh()                   # re-read after someone else wrote
```

Anyone with the note open **sees the change appear** — your edit merges with
what they are typing. Nothing is locked.

### Changes since a read or edit

**Legacy ETag interface:** available alongside v2 in CLI 0.26.2 and Python SDK 0.20.0. Select `--legacy` for these CLI recipes and `legacy=True` for remote Python patches.

The CLI returns the same ref in `read --json` and accepts it via `--since`:

```bash
# Requires jq. Keep the snapshot and ref for a later shell session.
NOTE_ID=design-doc
dreamlake notes read --legacy "$NOTE_ID" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
dreamlake notes diff --legacy "$NOTE_ID" --since "$REV"
dreamlake notes diff --legacy "$NOTE_ID" --since "$REV" --json
# Apply a diff prepared against that saved body:
dreamlake notes patch --legacy "$NOTE_ID" --file change.patch --if-match "$REV" --json
```

`notes diff` requires `--since`; it does not keep a hidden local baseline.
Plain output is the diff on stdout and current ETag on stderr. `--json` also
returns `from` and `to`. The CLI help includes this workflow:
`dreamlake notes diff --legacy --help`, `notes read --help`, and `notes patch --help`.

Reads return `doc.etag`, a quoted SHA-256 hash of the complete note text. Keep
that ref to see changes since your own read or successful edit across sessions:

```python
note = dl.note("<note-id>")
doc = note.read()
ref = doc.etag

print(note.diff(since=ref))          # current text versus that snapshot
print(note.diff())                   # defaults to this handle's last ETag
result = note.patch(my_diff, if_match=ref, legacy=True)
ref = result.etag                   # reference for the successful edit
```

Fetching a diff does not advance the cached revision or write precondition.
Call `read()` or `refresh()` to adopt the latest state. Identical text has the
same hash; the ref identifies content, not an RTC operation index. Unknown refs
return an error, including older refs whose snapshots were never retained.

The HTTP endpoint is `GET /namespaces/:slug/notes/:noteId/diff?since=<etag>`.
It returns `diff`, `from`, `to`, and `etag` (the current ref). Snapshots are
scoped to the note and require current read access. Optional `context` accepts
0–100 lines, default 3. Partial reads return a ref for the complete body.

For local draft changes, use `doc.diff()` for all unsaved changes,
`doc.diff(since="last_edit")` for the latest local operation, and
`doc.patch(unified_diff)` to apply a patch before `doc.save()`.

### Patch

This legacy patch helper validates unified-diff context against current text
and rejects mismatched context. Its optional ETag rejects any intervening
revision. The v2 merge workflow below instead addresses the saved original
native identities and preserves compatible concurrent edits.

**CLI**

```bash
diff -u before.md after.md | dreamlake notes patch --legacy "$NOTE_ID" --file -
dreamlake notes patch --legacy "$NOTE_ID" --file change.patch --dry-run
```

**Python**

```python
note.patch(unified_diff, legacy=True)
note.patch(unified_diff, if_match=doc.etag, legacy=True)
```

## Search

**CLI**

```bash
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive --glob 'spec-*'
dreamlake notes grep "Draft" --json        # revision + character range per hit
```

**Python**

```python
for hit in dl.grep_notes("TODO", namespace="<namespace>", context=1):
    print(f"{hit.note_slug}:{hit.line}:{hit.column}  {hit.text}")
```

Output is `slug:line:column`, like `rg` — which note, and where inside it.
Literal and case-insensitive by default, so `v1.2` does not match `v1x2`.

Each hit carries its revision and `ind`, the character range — enough to edit
without re-reading:

```python
hit = dl.grep_notes("Draft", namespace="<namespace>").hits[0]
doc = hit.open().read()
doc.replace("Published", ind=hit.ind)
doc.save()
```

## Files

Files inherit the note's permissions.

**CLI**

```bash
dreamlake notes files upload ./report.html --note "$NOTE_ID"
dreamlake notes files list --note "$NOTE_ID"
dreamlake notes files list 'assets/*.png' --note "$NOTE_ID"
dreamlake notes files cat config.json --note "$NOTE_ID"
dreamlake notes files write config.json --text '{}' --note "$NOTE_ID"
dreamlake notes files download report.html --note "$NOTE_ID" -o ./report.html
dreamlake notes files mv old.txt new.txt --note "$NOTE_ID"
dreamlake notes files cp a.txt b.txt --note "$NOTE_ID"
dreamlake notes files rm old.txt --note "$NOTE_ID"       # trash
dreamlake notes files list --trashed --note "$NOTE_ID"   # ids of trashed files
dreamlake notes files restore <file-id> --note "$NOTE_ID"
```

**Python**

```python
note.files.upload("diagram.png", path="assets/diagram.png")
note.files.create("config.json", text='{"enabled": true}\n')
note.files.list("assets/*.png")
f = note.files.find("assets/diagram.png")
f.download("./local.png")
f.move("assets/new.png")
f.copy("assets/copy.png")
f = f.trash()                    # each returns the updated file
f = f.restore()
```

Bytes are **streamed** both ways and never decoded, so a file larger than
memory still round-trips intact. `cat` refuses a binary rather than printing
mojibake.

`rm` moves a file to the trash. Restoring takes the file **id**, not its path —
two trashed files can share a path, so the path alone would be ambiguous.
`files list --trashed` prints the ids.

### Look at one

**CLI**

```bash
dreamlake notes files preview report.html --note "$NOTE_ID" --open
dreamlake notes files preview report.html --note "$NOTE_ID" --share
dreamlake notes files preview report.html --note "$NOTE_ID" --revoke
```

**Python**

```python
print(note.files.find("report.html").preview_url())
print(note.files.find("report.html").preview_url(share=True))
note.files.find("report.html").unshare()
```

The default link needs a signed-in reader. `--share` opens without signing in
and does not expire; `--revoke` kills every copy at once.

Uploaded HTML renders in a separate origin, never the dashboard's. Markdown,
SVG, code and images render too; anything else offers a download. A file with
no rendered form is refused rather than linked.

## Legacy revision-checked edit helpers

The legacy whole-body/local-document helpers below carry the revision they were based on. A note that changed in
between is **refused** rather than overwritten:

**CLI**

```bash
REV=$(dreamlake notes read --legacy "$NOTE_ID" --json | jq -r .etag)
dreamlake notes write "$NOTE_ID" --file new.md --if-match "$REV"
```

**Python**

```python
doc = dl.note("<uuid>").read()
doc.replace("Published", query="Draft", all=True)
doc.save()                       # refused if the note moved since read()
```

| Python | CLI exit | Means | Do |
|---|:---:|---|---|
| `NoteChanged` | `3` | It changed since you read it | Re-read, redo. Retrying fails again. |
| `NoteBusy` | `4` | The realtime outcome is unavailable | Preserve the draft and baseline; read and reconcile before resubmitting. |
| `PatchFailed` | `5` | Your diff no longer applies | Re-read, regenerate it. |
| `NoMatch` | `6` | Nothing matched | Widen the query. |
| — | `7` | Refused to overwrite a local file | Pass `--overwrite`. |

`--force` / `force=True` skips the check — deliberately, so overwriting a
colleague is something you typed rather than something that happened.

Verify a write landed by reading it back against the revision it produced:

```python
rev = note.patch(diff, if_match=doc.etag, legacy=True)
check = note.read(if_match=rev.etag)      # refused if anything changed since
```

## Which addressing to reach for

1. **Exact text** (`query=`) — what you can state reliably; ambiguous matches fail.
2. **A section anchor** from `toc` for a heading and its contents.
3. **A line or character range** from a current read, TOC or grep hit.
4. **A unified patch** for coordinated changes in several places at once.

## Next steps

    Every `dreamlake notes` command and flag.

    The endpoints underneath, if you need them directly.

## Notes v2: merge and exact patches

Released September 24, 2026 with CLI 0.26.2, Python SDK 0.20.0 and the Notes API
backed by RTC server 0.5.1. The API retains native baselines and the authority
supplies unlocked baseline observations. Upgrade older clients before using
these examples. Deployment evidence and manual acceptance are tracked in
[the Notes master plan](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).

A v2 source read returns `note`, `hash`, `revision` and `content`. `hash` is
`sha256:` plus the exact UTF-8 source digest. `revision` is an opaque RTC write
baseline; equal text does not imply an equal revision. Keep the original source
and token together until the edit is verified. Never fetch a fresh token merely
to make an old patch pass.

```bash
set -euo pipefail
NOTE_ID=design-doc
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE_HASH=$(jq -er '.hash' baseline.json)
BASE=$(jq -er '.revision' baseline.json)
jq -jr '.content' baseline.json > base.md

dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format inline-dff
dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format diff

# Example requires saved source exactly Hello world. without a final newline.
dreamlake notes patch "$NOTE_ID" --format inline-dff --base-revision "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH

REVISION=$(jq -er '.revision' committed.json)
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
```

Use a quoted heredoc delimiter absent from the patch body. Multiline stdin is
the default; `--file` is optional. Both reads and uploads select `inline-dff` or
`diff` independently. Full reads and incremental reads have self-contained text
metadata by default; JSON is opt-in. `--legacy` selects the previous text/ETag
contract. `notes diff` is the incremental-read alias in the matching CLI.

Inline ranges count Unicode code points, zero-based and end-exclusive. Literal
marker punctuation uses backslash escaping, with `\n`, `\r`, `\t` and `\\`
for controls/backslashes. Unified line patches preserve exact line endings and
`\ No newline at end of file` markers. Invalid patches apply nothing. The default patch sends `{format, patch, baseRevision, mode: "merge"}`
without `If-Match`: the server retrieves the original identity-bearing snapshot
and journal, validates the original source, and compiles the sparse edits into
ordinary native RTC operations. Concurrent changes merge by native character
identity; the server never re-diffs an old target against freshly read text.
The source hash alone cannot identify this baseline. Missing or expired native
baselines fail explicitly and require a new read and a reviewed patch. A room
reset invalidates prior generations even in merge mode.

The default mode is `merge`. Add `--exact --base-revision "$BASE"` to require
the original authoritative revision at commit (`mode: "exact"` in the API). For compatibility, `--if-match`
alone supplies both the original baseline and exact mode; if both flags are
provided they must agree. An explicit API `mode: "merge"` conflicts with
`If-Match` and is rejected. Python uses `base_revision=BASE` with optional
`exact=True`. Patch receipts include `mode` (`merge` or `exact`), the original
`baseRevision`, and the observed resulting `hash` and `revision`. That observation
may already include later concurrent edits. Only exact mode uses the conditional commit
protocol and may return 412 when another writer changed the room. Merge-mode
patches use the existing `crdt`/`ack` protocol. RTC outages produce errors,
never an archive-only replacement.

`--since` accepts a retained hash, ISO timestamp/date, or positive integer
`second(s)`, `minute(s)`, `hour(s)` or `day(s) ago`. Unzoned timestamps and dates
use UTC; relative times resolve once at server request time. Time lookups select
the latest **retained source observation** at or before that instant, not every
browser keystroke or an audit history of all commits. Retention starts when this
interface records snapshots; no earlier history is invented. Unknown or expired
bases return an explicit error. Apply a returned patch only to its exact `base`
source, and verify the resulting hash. A no-op source diff may carry a newer RTC
token; it never advances an existing draft automatically.

The default `diff` read aligns source lines directly, so substantial rewrites do
not consume the character-alignment budget used for merge-safe write patches.
`inline-dff` still requires bounded character alignment. Invalid references
return `400 bad_reference`, missing retained snapshots return `404 revision_not_found`,
diff-generation limits return `422 diff_failed`, and retained-storage or observation
failures return `503 diff_unavailable`. Preserve the original baseline on failure.
A display diff does not guarantee that a later merge patch fits the write limits;
merge remains the default and exact mode remains opt-in.

Native CLI 0.33.0 has a redirected-file input defect: `--file - < edit.dff`
can send an empty patch and receive a successful no-op receipt. Until a release
containing the stdin fix is installed, use `--file edit.dff` and inspect
`--dry-run --json` to verify `payload.patch`. The corrected reader preserves
redirected input and rejects empty patches before sending. This does not change
merge semantics; always verify the requested text in the acknowledged snapshot.

Stop on failure and preserve the patch, working copy and original baseline.
A missing acknowledgement can mean a commit occurred. The backend reconnects
at most once within the same request and resends the identical native message
and operation IDs. The CLI does not automatically retry the HTTP patch. A new
HTTP invocation is an independent operation, with no cross-request idempotency
receipt: read and reconcile the result before resubmitting. Exact readback can itself return a conflict if another writer
has already changed the acknowledged revision.

### Agent presence and activity (opt-in)

#### Agreed lifecycle and identity

**Presence is opt-in.** Agents can read and edit using normal authentication and
revision checks without any agent ID, join, heartbeat, or leave. A runner opts in
by supplying a stable session ID. The client generates it (a UUID once per task),
not the server. Names and IDs are self-reported, grant no permissions, and are not
verified audit identity. Two clients under the same authenticated owner can reuse
an ID; random UUIDs prevent accidental collisions, not deliberate impersonation.

Presence means **active in this note recently**, for both humans and agents. It is
not proof that an agent is continuously watching, reading, or typing. Reuse the
existing RTC awareness channel and header badge; do not add a status row below
the bindr row.

Keep three identities separate:

| Identity | Purpose |
|---|---|
| Agent identity / display name | Identifies the agent; its name is a supplied label, not verified model identity. |
| Task/session ID | Stable across all CLI calls in one task; distinct for concurrent sessions, even for the same agent. |
| Human owner | Derived from authentication, not an agent-supplied owner field; attribution does not imply the owner is present. |

The runner creates the task/session ID once, retains it across tool invocations,
and passes it to every Notes command. Do not generate an ID on every command or
use a shared display name as the session key. Resume the same ID for the same
task; use a new ID for a new or concurrent task. Socket reconnections have their
own transport IDs and must not create a new logical participant.

The current `DREAMLAKE_AGENT_ID` / `X-DreamLake-Agent-Id` field carries this
**task/session ID**, despite its name. It does not yet represent a separate,
persistent agent-account ID. The roster key is scoped by note, authenticated
owner, and session ID; the display name is never the key.

| Event | Intended behavior |
|---|---|
| First attributed read/edit | Implicitly join and start the recent-presence timeout. |
| Later read/edit with the same session ID | Refresh the existing badge, without adding another participant. |
| Inactivity | Remove the badge after expiry; no cleanup command is required. |
| Explicit leave/unjoin | Remove that session from that note immediately; do not erase its identity. |
| Interaction after leave or expiry | Implicitly rejoin using the same session ID. |
| Optional explicit join or maintained session | Support clients that need sustained presence; ordinary CLI use does not require it. |

Human clients can send leave on navigation away or note closure. Abrupt tab close,
crash, or network loss may prevent delivery, so expiry is still required. Agents
have the same optional leave and expiry fallback. A session ID is identity, not a
live lease: storing the ID does not keep a badge alive. Neither a TUI nor a
continuous edit stream is required for recent presence.

Read activity uses the **existing human selection and cursor display**, with the
agent label and participant color. It selects the returned source range; a
full-body read selects the full source, and incremental changes do not claim a
whole-source selection. New read/focus activity replaces the previous selection.
Search does not add a separate seek event. Do not render a second agent-specific
selection style or a tool-call log.

Insertion/replacement text uses a fading highlight only after acknowledgement.
Deletion has no special marker in this iteration. Failed writes and dry runs never
produce success highlights. Selections expire after 8 seconds; completed edit
highlights fade over 5 seconds. Neither heartbeat nor badge renewal extends those
lifetimes. A completed edit may finish fading after its author leaves. Human
cursors retain relative CRDT anchoring; CLI selections are exact-source-hash bound
and disappear on source changes, rather than guessing a new position.

People and agents share participant-color rules, not action-specific colors.
Use an agent icon and agent/owner labels to distinguish them; do not rely on color
alone. Concurrent sessions must remain distinguishable even when names match.

The defaults are a 60-second recent-presence timeout and a 5-second
completed-edit fade. Optional passage activity has an independent 8-second
expiry. These are DreamLake choices, not asserted Google Docs, iMessage, or
Claude Tag timing constants.

#### Availability and optional controls

An attributed operation uses the lifecycle above and
implicitly joins or renews the same 60-second presence entry. Anonymous agent
identity is not inferred from ordinary API calls. A separate persistent
agent-account identity is not yet part of the wire contract. Deployment and
client release status must be checked independently of this source documentation.

CLI 0.27.0+ and Python SDK 0.21.0+ support attributed reads and edits.
CLI 0.29.0+ adds `visit` and `read --linger`; CLI 0.31.0+ adds the read-only
`presence` command and event-driven selections. These require matching server
capabilities; a successful read does not prove presence or event support.
The CLI uses the active login's API; running a locally installed binary does not
select a local server. Use `--remote <url>` to test a specific API or `--debug`
for the local development server.

To check a matching API, use an accessible test note and the stable task identity
below. Run a read, inspect `notes presence`, then start `read --linger` and stop
it with Ctrl-C to verify automatic session cleanup. Verify patch support
separately on a disposable note with a merge patch, an exact readback, and a stale
exact request that must fail without changing the source. Do not use an existing
user document as a write-test fixture.

#### Read and linger in the foreground

CLI 0.29.0+ adds `notes read --linger` and `notes visit`. They use the deployed Notes v2, presence-roster and
agent-activity endpoints. Python has no corresponding convenience method yet.

Set `DREAMLAKE_AGENT_ID` once to a unique, stable task-session identity (and
optionally `DREAMLAKE_AGENT_NAME`) as described below. `NOTE_ID` must identify a
note you can access as a member or explicitly shared reader.

```bash
# NOTE_ID and the stable task identity must already be set.
dreamlake notes read "$NOTE_ID" --linger
```

**Use the default text output for people and coding agents.** It shows readable
diffs, participants, and quoted selections. JSON is optional and intended only
for a program that explicitly needs to parse structured events.

The command registers presence automatically, prints the complete source with
its hash/revision and the other current participants, and stays in the foreground.
A separate `visit` is optional. Interrupt with Ctrl-C or SIGTERM to stop and send
leave. No background daemon is spawned. Presence expires after its server lease
if the process is killed or cannot send leave. Use one linger process per
note/task identity; multiple keepers using the same identity share one lease.

Edit delivery is **debounced**: wait until the observed source has been quiet
for `--debounce` (default `2s`), then deliver **one unified diff** from the last
emitted content baseline through the end of the burst. Each newly observed edit
restarts that quiet timer. Continuous editing keeps the diff pending; there is
no forced maximum-wait flush. Stopping before the quiet period ends discards the
pending notification, not any document edits.

All output batches are **throttled** by `--throttle` (default `2s`): no two update
batches are emitted closer together than that interval. Presence and activity
can still be delivered while edits continue; they do not reset the edit quiet
timer. Once a diff is ready it joins the next eligible output batch, so a recent
presence batch can delay it until the throttle expires. The first source snapshot
is immediate. No new batch is emitted merely because a timer elapsed.

Both flags require `--linger` and accept explicit `ms`, `s` or `m` units, including
fractions, from `250ms` through `5m`. Bare numbers, zero, negatives and out-of-range
values are rejected before presence registration. For example:

```bash
# One second of edit quiet; no more than one output batch every two seconds.
dreamlake notes read "$NOTE_ID" --linger --debounce 1s --throttle 2s
# Slower text output for a coding agent or a quieter session.
dreamlake notes read "$NOTE_ID" --linger --debounce 2s --throttle 5s
```

**CLI 0.31.0+:** linger subscribes to authenticated
`GET /namespaces/:slug/notes/:noteId/events` (SSE). CLI 0.29.0–0.30.0 used
polling. The event stream requires a matching server; there is no silent
polling fallback.

The server observes the existing RTC connection events and coalesces them to
at most one batch per 250ms. The CLI keeps only the latest selection per browser
connection, emits at most one update per `--throttle`, and delivers the final
selection after a drag stops. Continuous dragging does not restart a debounce
timer. Content diffs keep their separate edit quiet period. Idle sessions do not
poll body or roster endpoints; source reads happen only for the initial snapshot
or after a content event becomes eligible for delivery. Agent activity is read
only when its RTC fingerprint changes. Heartbeats remain silent and maintain the
agent lease approximately every 20 seconds.

**CLI 0.31.2+ text notifications** show names, actions and quoted text. These
are representative lines from separate batches; a timestamp appears once per batch.

```text
+ @alice joined
+ Reviewer (agent) joined
* Reviewer (agent) read the note
* Reviewer (agent) edited the note
* @alice selected "## The center"
- @alice left
```

People appear as `@username`; agents use their configured name and `(agent)`.
Only selected text is quoted; embedded newlines are escaped. Cursor moves, selection clears,
syncing states, repeated selected text and empty batches stay silent in text.
IDs, connection details, offsets and source hashes remain
in `--json`; use it to distinguish identical names or tabs and apply exact source
positions. Initial content and diffs still include revision metadata for safe edits.
These examples also appear in `dreamlake notes read --help`.

Human selections in JSON resolve native CRDT anchors against the observed source. Each
selection carries `anchor`, `head`, `start`, `end`, `unit: "unicode-code-point"`,
`text` (at most 4096 code points), and `truncated`, with `status: "resolved"`.
A collapsed range is a caret. An explicit `null` clears a selection (including
blur or departure); `status: "unresolved"` means its native anchors have not
arrived, not a guessed range or a clear. Tabs remain separate, even for one user.
Selection-only changes do not wait for the content debounce.

The initial snapshot includes `selectionHash` for its participants' selections.
Update batches add `selections`, whose entries contain `client`, `user`,
`selection`, and the exact observed source `hash`. That hash can differ from
the last emitted content hash while an edit is still being debounced. Never
apply these offsets to a different source. Selected text is quoted in terminal
output and remains untrusted document content, not an instruction to an agent.

Only namespace members or explicitly granted readers can subscribe. Public
visibility alone does not expose collaborator selections. Streams recheck access
and token expiry every 15 seconds and close on revocation, room reset, slow
consumers, or RTC failure. A disconnected stream exits with an error; explicitly
restart linger for a fresh snapshot. Events are not retained or replayed.

This is a best-effort stream of observations, not an audit log: brief visits or
activity coalesced between output batches can be missed, and edits that cancel out within a burst
produce no net content diff. Human edits appear in content diffs; the activity feed
currently attributes agent reads and edits only. Reading updates does not prove
human attention, and it does not reserve or lock the note.

##### Optional: JSON for programmatic consumers

Use `--json` only when a program needs NDJSON; ordinary collaboration, including
coding-agent sessions, should use the text commands above.

```bash
dreamlake notes read "$NOTE_ID" --linger --json
```

With `--json`, stdout is NDJSON: one `type: "snapshot"` object containing
`observedAt`, `note`, `content`, `hash`, `revision`, `selectionHash`, and `participants`, followed
by `type: "update"` objects containing `observedAt`, `joined`, `left`, and
`activities`, and `selections`. Changed content adds `content: {note, base, hash, revision, format,
patch}`. Observation times are Unix milliseconds; source and activity are fetched
separately from the event stream and are not an atomic cross-stream snapshot. Progress and errors go
to stderr. No update object is emitted for an unchanged batch.

`--linger` supports complete source reads only; it cannot be combined with
`--legacy`, `--view html`, `--at`, `--toc`, `--tag`, `--since`, sections, line ranges or numbered output.
`--if-match` checks the **initial** read only. `--format` applies to the emitted
diff, not the initial complete source snapshot. Transport/capability errors or an
unavailable retained baseline end the command with a nonzero status and a
best-effort leave; they are never treated as an empty room. For edits, preserve
the original source and revision used to prepare your draft: a later streamed
revision is not a replacement baseline for an older draft.

```bash cli-help="notes visit"
# Optional one-shot registration: does not fetch the note body or keep a daemon.
# NOTE_ID and the stable task identity must already be set.
dreamlake notes visit "$NOTE_ID"
```

`visit` uses the existing join lease (60 seconds unless renewed by an attributed
operation), returns immediately and does not read content. Use
`read --linger` when you want ongoing updates. CLI 0.31.0 removes the old
manual `notes presence <note> <action>` and `join --watch` controls.

`read --linger` manages joining, heartbeats, and leaving automatically. Stop it
with Ctrl-C when finished; one-shot reads and `visit` expire naturally. There is
no manual lifecycle sequence to run alongside it. Never start an untracked
helper that outlives the task.

##### Read who is present

In CLI 0.31.0+, `presence` reads the current roster without joining or refreshing
your session. It does not require an agent ID. Text is the default:

```bash cli-help="notes presence"
dreamlake notes presence "$NOTE_ID"
```

Add `--json` only for a program consuming the roster. There are no direct
`notes join`, `notes heartbeat`, or `notes leave` commands. Use `visit`,
`read --linger`, and Ctrl-C for participation.

##### Low-level HTTP lease protocol

SDK integrations and linger use the HTTP protocol below internally. It is not
a manual CLI workflow.

API: `POST /namespaces/:slug/notes/:noteId/presence` accepts
`{action, hash?, ranges?: [{start,end}]}`, bearer authentication,
`X-DreamLake-Agent-Id`, and optional `X-DreamLake-Agent-Name`.
Actions are `join`, `heartbeat`, `read`, `edit`, `seek`, `clear`, `leave`.
Response is `{state}` or `{state:null}` after leave. Only authenticated members or
explicitly shared readers may publish; `edit` also requires write permission.
Public visibility alone does not grant presence access. Controls do not mutate
document content or revision. Owner metadata comes from authenticated lookup.

#### Read who is present (HTTP API)

`GET /namespaces/:slug/notes/:noteId/presence` returns the current RTC awareness
roster, including humans and agents. Use bearer authentication as a namespace
member or explicitly shared reader. Public visibility alone is insufficient.
Agent identity headers are not required, and the observer does not publish
presence, renew an agent lease, or edit the note.

Successful reads default to `text/plain; charset=utf-8` (also available with
`?format=text`):

```text
Observed at: 2026-09-26T08:00:00.000Z
- human: "Ge" (id: "ge"; client: "browser-session-123")
- agent: "Codex" (id: "agent:owner-id:agent-id"; client: "note-agent-session-456"); owner: "Ge" (id: "owner-id"); expiresAt: 1790409660000
```

An empty text roster says `No participants present.` after the observation time.
Client-declared strings are quoted and escaped to keep each connection on one
line. Use `?format=json` for structured output; other format values return
400 `invalid_format`. Error responses remain JSON for either format.

The opt-in JSON response is `{participants, observedAt}`. `observedAt` is Unix time in
milliseconds. Each participant has `client` (connection ID) and `user` with
`id`, `name`, and `kind` (`human` or `agent`), plus optional `color` and `avatar`.
Agents can include `user.owner` and their lease's `expiresAt`. Expired agent
leases and internal observer connections are excluded. Multiple browser tabs
remain separate entries. To identify other agents, compare `user.id` against
`agent:<authenticated-owner-id>:<agent-id>`; the caller is not automatically
excluded. Human identities without a kind field are normalized to `human`.
These are client-declared display identities, not verified authorization claims.

An inactive note returns an empty roster. An active room whose connection fails
or times out returns 503 `presence_unavailable`, not an empty roster. Responses
are not cached. This requires a server with the GET endpoint and an RTC server
supporting awareness rosters; a 404 can also mean the caller lacks access.
There is no CLI or Python convenience method for roster reads yet. Using any
HTTP client, send an authenticated GET to the path above. The roster is an
observation of presence, not a lock or a guarantee that another editor is idle;
continue to use the normal conditional-write contract.

Explicit ranges require the exact source SHA-256 and zero-based, end-exclusive
Unicode code point offsets. Stale or out-of-bounds locations are refused. A
collapsed seek is a caret, not a claim that text was read. Source changes invalidate
hash-bound markers. Deletion-only edits do not invent insertion ranges.
Errors include missing identity/invalid input (400), denied access (404), stale
range (409), expired heartbeat (410), and unavailable relay (503).

Identity values accept 1–128 ASCII letters, digits, dots, colons, underscores and
hyphens; names accept at most 64 printable ASCII characters. CLI 0.27.0+ and
Python SDK 0.21.0+ attach identity headers to Notes body/section/diff operations
when the environment variables below are set. `visit` and `read --linger` require
CLI 0.29.0+ and an active collaborative room; read-only `presence` requires
CLI 0.31.0+. The old manual action commands were removed in 0.31.0.
Updating a skill does not update a binary or deploy a server. Python has no
presence convenience method yet; use the HTTP contract when available.
The authorized agent-activity feed retains operation observations, not an online
roster. Observation failures must not turn an acknowledged edit into an apparent
failed edit. Live source-range decorations currently require the collaborative
editor; read-only views do not run an RTC client.

#### Identity, names and photos

Use a readable agent prefix plus a UUID as the task ID, for example
`codex:7b52e4d1-3ac9-4d88-b2a6-61f03c927ea5`. Generate it once per task and reuse
it across reads, edits and linger sessions. Concurrent tasks need different IDs;
a display name such as `Codex` does not distinguish their sessions. The CLI sends
`DREAMLAKE_AGENT_ID` as `X-DreamLake-Agent-Id` and `DREAMLAKE_AGENT_NAME` as
`X-DreamLake-Agent-Name`. No separate identity-registration request is required.

| Display field | Humans | Agents |
| --- | --- | --- |
| Presence identity | User namespace slug | `agent:<authenticated-owner-id>:<task-id>` |
| Display name | Profile name from `/auth/me`, falling back to namespace slug | `DREAMLAKE_AGENT_NAME`, falling back to `AI agent` |
| Header avatar | Profile photo, or initials when absent | Bot icon |
| Tooltip | Name and presence | Agent name, owner name, activity and task/session ID |

The server derives an agent's owner from authentication and looks up the owner's
profile name/photo; an agent cannot assign an owner through these headers. The
owner's photo is carried in metadata but is not currently rendered as the agent's
header avatar. Owner attribution does not mean that the owner is present.

The header deduplicates connections by identity: multiple browser tabs show one
human avatar, while unique agent task IDs show separate agent avatars. It shows
up to four avatars plus an overflow chip. Colors are derived from identity.
The HTTP roster still returns one entry per connection. Browser awareness names
and photos are display metadata, not an authorization source.

#### Agentic usage pattern: one identity, normal commands

For agent-driven Notes work, set both identity variables before the first live
read or edit, unless the user explicitly requests unattributed work. This is a
workflow prerequisite for attribution, not a requirement for saving content.
Without `DREAMLAKE_AGENT_ID`, an edit can save successfully while producing no
agent presence or attributed fading edit highlight. `DREAMLAKE_AGENT_NAME`
provides the readable label.

Initialize once in the runner's task environment. For separate shell tool calls,
the runner must inject the same saved values each time; an export in one shell
does not propagate into later independent shells. No explicit join is required.

```bash
export DREAMLAKE_AGENT_ID="${DREAMLAKE_AGENT_ID:-codex:$(python3 -c 'import uuid; print(uuid.uuid4())')}"
export DREAMLAKE_AGENT_NAME="${DREAMLAKE_AGENT_NAME:-Codex}"
NOTE_ID="<full-note-id>"
```

Run ordinary commands with that identity. An attributed `read` automatically
registers or refreshes presence; a preceding `visit` is never required. Reading
without agent identity does not invent or register an agent session. Retain the generated ID in the task context and inject that same literal value into each later shell; rerunning the UUID fallback in a new shell would create a different session.

After the first intended live read, verify attribution with
`dreamlake notes presence "$NOTE_ID"` (CLI 0.31.0+). This only inspects the roster;
it does not register an agent. Check the task ID and display name, not merely
another session named Codex. If absent, check the environment passed to the
actual read/edit process before diagnosing a UI regression. Do not repeat a
successful edit to trigger its highlight. Presence expires about 60 seconds
after the last activity; completed edit highlights fade over 5 seconds and
require an exact matching live document revision. A roster entry verifies
presence only: report a highlight as visually verified only after observing it
in the collaborative editor.

| Command | Reads content | Presence lifetime |
| --- | --- | --- |
| `notes read "$NOTE_ID"` | Once | Registers/refreshes presence, then the lease expires naturally |
| `notes read "$NOTE_ID" --linger` | Initial source and ongoing updates | Registers automatically and maintains presence until stopped |
| `notes visit "$NOTE_ID"` | No | Registers once, returns immediately, then the lease expires naturally |

The last two commands require CLI 0.29.0+. A normal
read does not mean the agent remains actively reading between commands.

```bash
dreamlake notes read "$NOTE_ID" --json > baseline.json
dreamlake notes find lighthouse --note "$NOTE_ID" --json
# Draft a reviewed patch against baseline.json, using the patch workflow below.
# Retain its revision, apply the patch, and read back the acknowledged revision.
```

The conditional patch and exact-readback examples elsewhere in this guide remain
required; presence does not relax concurrency checks. Do not retry an old patch
with a newly fetched revision merely to force it through.

When finished, stop `read --linger` with Ctrl-C; it sends leave automatically.
One-shot operations expire naturally. Keep the same session ID between commands,
and remove the task identity from the runner's environment when the task ends.
Lease expiry handles abrupt exits without requiring remembered cleanup.

### Keep incremental reads compact

For an agent following a note, reuse the saved full `read --json` baseline;
obtain one only if none is available. Then use `read --since "$BASE_HASH"` for
subsequent checks instead of repeatedly downloading the full document. For
one-off passage inspection, use the scoped reads above without fetching a full
baseline. Differential reads default to unified line diffs.
Use `--format inline-dff` explicitly when character edits are useful.
On servers with localized unified-diff generation, this returns changed
lines with up to three unchanged context lines on each side; nearby changes
share a hunk and distant changes use separate hunks. Older servers may still
return a whole-document replacement; a docs or skill update alone does not
change server output.

Both formats preserve exact source, including CRLF and a missing final newline.
An unchanged source returns an empty `patch`, possibly with a newer RTC
`revision`. Keep `base`, `hash`, and `revision` with the response. Apply the patch
only to the saved source matching `base`, verify its resulting hash, and never
replace an existing draft's original revision just to make it pass. Unknown or
expired bases remain errors. Use `--json` and extract `.patch` when a consumer
needs patch text alone; normal text output includes metadata.

#### Verify edits without rereading the whole note

After a successful v2 patch, verify the acknowledged revision with a delta from
your saved baseline. This uses the existing `baseline.json` from the pre-edit
read and `receipt.json` from the successful patch; `NOTE_ID` is the same note
used for both operations, as set in [Name a note](#name-a-note).

```bash
BASE_HASH=$(jq -er .hash baseline.json)
ACK_REVISION=$(jq -er .revision receipt.json)
dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" \
  --if-match "$ACK_REVISION" --json > verified-delta.json
```

Check that the returned `base` matches the cached source hash and its `hash`
matches the receipt. Apply the returned patch to that cached source, verify the
resulting hash, and inspect the intended changes. Preserve unrelated changes
when the write used merge mode. Save the reconstructed source and returned
revision as the next baseline only after verification succeeds.

An empty delta from the receipt's hash checks for changes after the write; it
does not by itself verify the edited text. A stale `--if-match` fails rather than
silently accepting a newer revision: retain the receipt and original baseline,
then inspect an incremental read without that condition to reconcile later
edits. Do not retry the write using a newly fetched revision merely to force it
through. If the cached source or retained base is unavailable, take a new full
snapshot explicitly; do not claim exact verification of an expired revision.

The full-read examples below remain useful as standalone demonstrations and
recovery checks. They are not a requirement to reread the entire note after
every targeted edit.

### Reproduce a concurrent merge and an exact conflict

Use a new private fixture with the compatible releases, an authenticated CLI,
`jq`, and Python `dreamlake` configured for the same account/namespace. These
examples deliberately issue an exact request first, inspect its rejection, and
then make a separate, explicit merge request. There is no automatic downgrade.

**CLI**

```bash
set -euo pipefail
dreamlake notes create "Merge/exact example" --text 'Hello world.' --json > fixture.json
NOTE_ID=$(jq -er '.id' fixture.json)
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er '.revision' baseline.json)
jq -jr '.content' baseline.json > original.md
cat > agent.patch <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH

# Simulate a second participant inserting a prefix after the agent's read.
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" --json > human.json <<'PATCH'
@@ chars 0:0 @@
~ {+Human: +}
PATCH

# Expected conflict: stdout stays empty; stderr explains the failure; exit is 3.
set +e
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" --exact \
  --file agent.patch --json > exact.stdout 2> exact.stderr
STATUS=$?
set -e
test "$STATUS" -eq 3
test ! -s exact.stdout
cat exact.stderr

# A separate explicit choice to merge the ORIGINAL patch and identities.
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" \
  --file agent.patch --json > merged.json
jq '{note, mode, baseRevision, hash, revision}' merged.json
dreamlake notes read "$NOTE_ID" --json > observed.json
jq -er '.content == "Human: Hello team."' observed.json
```

**Python**

```python
import json
import os
from pathlib import Path
import dreamlake as dl
from dreamlake import NoteChanged

note = dl.create_note(os.environ["NAMESPACE"], "Merge/exact example",
                      text="Hello world.")
baseline = note.read_snapshot()
patch = "@@ chars 0:12 @@\n~ Hello [-world-]{+team+}.\n"
Path("baseline.json").write_text(json.dumps(baseline.to_dict(), indent=2), encoding="utf-8")
Path("original.md").write_text(baseline.content, encoding="utf-8")
Path("agent.patch").write_text(patch, encoding="utf-8")

# A separate native edit arrives after this baseline.
note.patch("@@ chars 0:0 @@\n~ {+Human: +}\n",
           base_revision=baseline.revision)
try:
    note.patch(patch, base_revision=baseline.revision, exact=True)
except NoteChanged:
    print("Exact request rejected; original files retained.")
else:
    raise AssertionError("Expected a stale exact request")

# Explicitly choose merge; never do this automatically inside the except block.
receipt = note.patch(patch, base_revision=baseline.revision)
print(receipt.mode)           # merge
print(receipt.base_revision)  # the ORIGINAL opaque token
print(receipt.hash)           # observed resulting source hash
print(receipt.revision)       # observed resulting RTC revision
print(json.dumps(receipt.to_dict(), indent=2))
assert note.read_snapshot().content == "Human: Hello team."
```

### Complete an exact edit and return to merge mode

Continue with the fixture above, now containing `Human: Hello team.`. Read a
fresh baseline before making this new edit. Exact mode applies only to its
individual request; the following empty patch uses the default merge mode.

**CLI**

```bash
dreamlake notes read "$NOTE_ID" --json > exact-baseline.json
EXACT_BASE=$(jq -er '.revision' exact-baseline.json)
cat > exact.patch <<'PATCH'
@@ chars 18:18 @@
~ {+!+}
PATCH
dreamlake notes patch "$NOTE_ID" --base-revision "$EXACT_BASE" --exact \
  --file exact.patch --json > exact-success.json
jq '{note, mode, baseRevision, hash, revision}' exact-success.json

dreamlake notes read "$NOTE_ID" --json > after-exact.json
NEXT_BASE=$(jq -er '.revision' after-exact.json)
printf '' | dreamlake notes patch "$NOTE_ID" --base-revision "$NEXT_BASE" \
  --json > merge-after-exact.json
jq -er '.mode == "merge"' merge-after-exact.json
```

**Python**

```python
exact_baseline = note.read_snapshot()
exact_patch = "@@ chars 18:18 @@\n~ {+!+}\n"
Path("exact-baseline.json").write_text(
    json.dumps(exact_baseline.to_dict(), indent=2), encoding="utf-8")
Path("exact.patch").write_text(exact_patch, encoding="utf-8")
exact_receipt = note.patch(exact_patch, base_revision=exact_baseline.revision,
                           exact=True)
print(exact_receipt.mode)  # exact
print(json.dumps(exact_receipt.to_dict(), indent=2))
after_exact = note.read_snapshot()
assert after_exact.content == "Human: Hello team.!"
merge_receipt = note.patch("", base_revision=after_exact.revision)
assert merge_receipt.mode == "merge"
assert merge_receipt.hash == after_exact.hash
assert merge_receipt.revision == after_exact.revision
```

If another writer changes the exact baseline first, stop on the conflict and
retain these files. The examples do not retry the HTTP request or switch modes
after a failure. The successful follow-up merge above is a separate no-op
request with its own saved baseline.

Successful exact output captured from the matching isolated API fixture with
the candidate CLI (exit 0, empty stderr; these are fixture tokens):

```text
note: 507f1f77bcf86cd799439099
hash: sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5
revision: rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484
mode: exact
baseRevision: rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e
```

With `--json`, the same exact receipt is:

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5",
  "revision": "rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484",
  "baseRevision": "rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e",
  "mode": "exact"
}
```

Python's captured `PatchReceipt` attributes match that JSON:

```text
mode: exact
base_revision: rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e
hash: sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5
revision: rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484
```

The following empty patch defaults back to merge and returns this actual CLI
text receipt (exit 0, empty stderr). Python reports `.mode == "merge"`, and
`.to_dict()` returns the same fields with `baseRevision` in JSON:

```text
note: 507f1f77bcf86cd799439099
hash: sha256:2b8c0f5475f23494272f3800abb11a7680b3360bc2e927763c10aec9cf4398f5
revision: rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484
mode: merge
baseRevision: rtc:63834c3821f7b76779815f3a670449268711811e69f86f6b208fb52236713484
```

The local API/RTC/Mongo fixture verifies `Hello world.` → `Human: Hello team.`:
the unrelated prefix survives, original native identities address the replaced
word, and the exact rejection appends zero operation batches. The matching
source hashes observed in that fixture are:

```json
{
  "originalHash": "sha256:aa3ec16e6acc809d8b2818662276256abfd2f1b441cb51574933f3d4bd115d11",
  "mergedHash": "sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf"
}
```

Candidate CLI output captured by replaying that isolated API fixture (exit 0,
empty stderr; these IDs are fixture values, not production):

```text
note: 507f1f77bcf86cd799439099
hash: sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf
revision: rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e
mode: merge
baseRevision: rtc:870fa6d8ca75e1ae8c89b0e4abf08fd8a2c222c99ac698227f25c94b8f5b41e7
```

With `--json`, the corresponding stdout is:

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf",
  "revision": "rtc:71371be6e3227abca241161ebb7d8d65e2d851b8872b5a5d51ce7ec80369d95e",
  "baseRevision": "rtc:870fa6d8ca75e1ae8c89b0e4abf08fd8a2c222c99ac698227f25c94b8f5b41e7",
  "mode": "merge"
}
```

The exact conflict replay exits 3 with empty stdout and this stderr:

```text
✗ the original revision or RTC identities are no longer valid for this request; keep the original baseline and draft, inspect the note before resubmitting ((412) stale)
```

Opaque note/revision values vary. A successful JSON receipt contains exactly
`note`, `mode`, `baseRevision`, `hash`, and `revision`; normal CLI text prints
those metadata fields. Python exposes the corresponding attributes, with
`base_revision` in Python and `baseRevision` in `to_dict()`.
These describe a coherent authoritative observation after persistence was
acknowledged. They do not mean every peer has synchronized or that the document
will remain unchanged. Another edit can arrive before the verification read;
`read --if-match "$REVISION"` / `read_snapshot(if_match=receipt.revision)` makes
that verification exact rather than silently accepting a newer state.

The fixture observed these HTTP errors (no success receipt on failure):

```json
{"error":"stale","message":"The RTC baseline changed"}
{"error":"revision_not_found","message":"Original RTC baseline is not retained"}
{"error":"patch_failed","message":"Expected inline header and one record"}
```

They correspond to exact conflict **412** (CLI exit **3**, Python `NoteChanged`),
missing original identity baseline **404** (CLI exit **1**, Python `NoteNotFound`),
and malformed patch **422** (CLI exit **5**, Python `PatchFailed`). CLI failures
leave stdout empty and explain the failure on stderr, without replacing local files.
A destructive room reset or history rewrite can expire native identities even
when the retained baseline envelope still exists; merge then returns **412**
(`stale`, CLI exit **3**, Python `NoteChanged`) without applying the patch.
Ordinary concurrent editing alone does not cause that merge rejection. A missing
retained envelope instead returns **404**; malformed patches return **422**.
The baseline, draft and patch remain the caller's files on all failures. Neither
client retries a failed HTTP patch or silently changes exact mode to merge.
A transport/acknowledgement failure can be ambiguous even when a write persisted:
read, reconcile, and deliberately decide what remains to be submitted.

### HTML snapshot preview

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

### Literal Markdown for agents

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

See the [addressed-read specification](https://docs.dreamlake.ai/dev/notes/addressed-reads/)
for ID generation, ranges, examples, efficiency limits, and the executable
acceptance harness. Use a CLI/server build supporting the addressed-read options.

### Comment targets in HTML reads

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

### Rich tokens in HTML reads

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

### Heading numbering in HTML reads

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

## Select an agent passage by matching text

**CLI 0.32.0+:** `notes select --text` publishes an agent selection; section
selection requires the server update adding `hash` and `range` to section reads.
Older server responses fail explicitly.

```bash
export DREAMLAKE_AGENT_ID="review-session-42"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID="your-note-id"
dreamlake notes select --text "The next step is tested in simulation." --note "$NOTE_ID"
dreamlake notes select --text "simulation" --section next-steps --occurrence 2 --note "$NOTE_ID"
dreamlake notes select --text "simulation" --section next-steps -o -1 --note "$NOTE_ID"
```

Use a stable task identity and your normal authenticated Notes access. The command
matches exact canonical source text, including whitespace and markup. It refuses
missing or ambiguous matches. `-o` aliases `--occurrence`: `1` selects the first
match, `-1` the last, and `-2` the second-last within the chosen scope. Zero and
out-of-range values fail without publishing. Receipts report the resolved
positive 1-based occurrence.
A section match downloads only that section, not the entire document. A whole-note
match reads source internally without printing it. Target resolution suppresses
read highlighting until a unique match is found.

It then sends `POST /namespaces/:slug/notes/:noteId/presence` with
`{action:"seek", hash, ranges:[{start,end}]}`. Ranges are half-open Unicode code-point
offsets in the whole canonical source. Section reads now return an additive `range`
in code points and the whole-source `hash`; legacy `start`/`end` stay UTF-16.
Old servers without section metadata fail explicitly. The server validates current
source and collaboration access. No source write or human-cursor change occurs.

**Plain text is the default for selection commands and agent workflows.** Omit
`--json` in normal tool calls and examples. The receipt confirms server acceptance and returns the quoted matched
text, scope, resolved match number/count, code-point range and separate expiry
times. Multiline excerpts escape newlines. Only an explicit machine integration
should request `--json`; that optional receipt includes exact `text` and
`scope` (`{kind:"note"}` or `{kind:"section",anchor:"next-steps"}`), alongside
`note`, `hash`, `range`, `occurrence`, `matches`, `published`, `selectionExpiresAt`
and `presenceExpiresAt`. It does not return the surrounding section or document. Browser rendering still
requires an active compatible RTC room and editor. Selection activity lasts eight
seconds and presence lasts sixty; a heartbeat renews presence only. Users can
navigate to the agent's selected passage through its location control.

Pass a retained `--hash "$HASH"` (`sha256:…`) to require the same source. If the
source changes before publication, `stale_range` fails without a guessed retry:
read the section again and select its current text. Duplicate/missing matches
publish no selection. Legacy `notes select "#contact" --note "$NOTE_ID"` and
`notes find` remain lookup operations, not explicit visible seek commands.

For address hints while reading Markdown, use `read NOTE --view markdown` with
the addressed-read CLI/server build. It preserves the selected source text and
inserts generated address/character/line comments. List-item targets use
hierarchical `li` IDs, such as `s1.ul2.li3`, including nested items. Containers
use `ul` or `ol`; every numeric suffix shares paragraph reading order. This
reading view is not
canonical source and must not be written back as a complete note.

## Manage existing share links

Available in CLI 0.32.4 and later; check `dreamlake notes share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash
# Find the release plan and inspect its source and current sharing.
dreamlake notes search "release plan"
NOTE="release-plan" # Replace with the id or slug from search.
dreamlake notes read "$NOTE"
dreamlake notes share get "$NOTE"

# Give signed-in recipients read access, then verify the returned link.
dreamlake notes share create "$NOTE" --role read
dreamlake notes share get "$NOTE"

# When link access is no longer needed, revoke it and verify.
dreamlake notes share revoke "$NOTE"
dreamlake notes share get "$NOTE"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes visibility "$NOTE" public
dreamlake notes visibility "$NOTE" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or an eligible Note creator may manage sharing.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and changes the role evaluated on subsequent requests for
everyone admitted through the link. Note IDs resolve their owning namespace automatically.

```bash
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes share revoke "$NOTE" --revoke-accepted
```

Ordinary revocation clears the link and blocks subsequent link-derived access,
including for prior recipients. Their acceptance records remain: enabling
sharing again restores access under the current link role. `--revoke-accepted`
also deletes those records, so recipients must accept a valid link again. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash
NOTE="release-plan" # Your existing note id or slug.
# List acceptance records and stored roles as a readable table.
dreamlake notes share access "$NOTE"
```

```bash
NOTE="release-plan" # Your existing note id or slug.
USER_ID="user-id-from-access-list"
dreamlake notes share remove "$NOTE" "$USER_ID"
```

The access list defaults to a readable table; use `--json` for a structured
integration. It returns stored roles, which may lag behind the live link role.
Use `share get` to inspect the current link role.

Removing an acceptance record does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.

## Saved versions

The version tag in the toolbar opens a compact revision graph. The right sidebar
uses one toolbar toggle for **Comments**, **Table of contents**, and **History**.
Choose **History** (the GitGraph icon) to see the graph there. Contents is the
default; the note remembers your chosen sidebar. **Working Draft** sits directly above its base version, with an edit
count and a GitCommitVertical save icon on that row. A small solid dot marks the draft endpoint; saved-version waypoints are hollow. Choose the icon, enter an optional title/tag
and summary, then save. Notes continues to autosave while you work; metadata
does not appear in the note body. New milestones receive stable numbers such
as `v3`, independent of their titles. Numbers can have gaps after failed saves.

Saved versions show their parent connections, including forks from a shared
base. The save form defaults to your draft's base; choose another **Base version**
to record a different ancestry. This records the relationship without replacing
or merging the live draft. The working draft follows the newest saved version
when history refreshes, including versions saved by another collaborator, so it
stays at the top and its edit count uses the latest checkpoint. This changes
only the history display and default save parent, not the note text or saved ancestry.
Older versions without recorded
parents remain unconnected.

The current edit marker shows its one-based index and total within that version
interval (for example, **Edit 439 of 443**), including when selected from a grouped tick.
Historical previews use the title-row status slot: **e439**, **preview**
for a saved version, or **e430–439** for a selected range. Version tags use a
lowercase **v** and are hidden while an intermediate edit or range is displayed. Hovering the preview label turns it red with a strikethrough;
clicking it returns to the working draft. The chevron opens history. The full preview label remains in the tooltip.
The history dropdown fits its content, capped at the remaining viewport height
with a 16px bottom gap; longer timelines scroll inside it. The sidebar and dropdown
share the editor selection, including resets and selected ranges. The magnifier
appears above the selected marker and displays its own red edit-index line on
hover. Only an explicitly selected edit or range creates a persistent marker.
The lens follows the pointer immediately; document and range previews settle
after a short pause, reusing a bounded cache of recent historical text.

Each small dot represents one retained intermediate edit; all retained edits
are shown. Hover or keyboard-focus a dot to preview its exact text directly in
the main body. The historical preview is read-only and isolated from live sync;
editor controls and saving are disabled while it is displayed. Leaving the dot
restores the prior selection, while clicking the dot keeps that edit selected.
There is no separate edit list. The magnifier's right edge stays fixed against
the timeline panel as the pointer moves horizontally. A larger magnified region spreads nearby dots
apart for selection. Scrolling previews nearby snapshots; clicking version text or activating it
with the keyboard selects that revision. Leaving a transient preview restores
the last selection. **Back to draft** returns to the still-mounted live editor.
The sidebar's **Contents** view follows Dockit's **On this page** format: compact
heading links, monospace subheadings, an accent-colored active heading, and a
curved progress rail. Section chevrons collapse or expand their child headings;
clicking heading text jumps directly to that section. The separate minimap
column is omitted.

Each saved version retains the exact server-confirmed text, author and date,
plus the available collaboration checkpoint and journal. It remains readable
after live history is compacted or a room is recreated. Compacted edits that were
already missing at save time cannot be recovered; partial counts say **retained
edits**. In a saved-version preview, **Compare / link** opens side-by-side
comparison and **Copy version link**. Saving never replaces the current note.
Tags may repeat; the version ID is unique and immutable. Summaries are written
by the person saving the version; automatic AI drafting is not included.

Saved history requires edit access, including accepted write-share access.
A public note or read-only share does not expose earlier text that may have
been removed. Version links do not grant access. If the note changes or is still
syncing while you save, review the current text and retry; no version is created
from a mismatched browser/server state.

### Version API

These authenticated endpoints are scoped to `/namespaces/:slug/notes/:noteId`:

- `POST /versions` accepts `{hash, tag?, summary?, parentId?}`. `hash` is the lowercase
  SHA-256 of the UTF-8 body the user intends to save. The server compares it
  with a coherent current read and returns `409 note_changed` on mismatch.
  Tags are at most 80 characters and summaries at most 2,000 characters.
  A successful `201` returns `id`, `tag`, `summary`, `hash`, `createdAt`,
  `createdBy`, `author`, `number`, and `parentId`. The optional nullable
  `parentId` must identify a version in this note; a missing/foreign parent
  returns `404 parent_not_found`. Omitting it records no parent. RTC-backed
  versions also include `revision`, `clock`, `editCount`, and `historyComplete`.
  The count measures retained content-edit messages, not keystrokes.
- `GET /versions` returns `{versions, nextCursor}` with up to 50 metadata
  entries, newest first. Send `?before=<nextCursor>` for older entries.
- `GET /versions/:versionId` returns the metadata plus `text`.
- `GET /versions/:versionId/history` returns the retained `{snapshot, journal}`
  for read-only replay, with the same editor access requirement. Legacy versions
  return `{snapshot: null, journal: []}`. This is not a content-write endpoint.

The content hash identifies text, not the identity-bearing RTC baseline used
for collaborative patches. Saving a version is a retained snapshot operation,
not a content write. There are no new CLI flags or Python SDK methods for this
surface yet; use the UI or authenticated REST API.
