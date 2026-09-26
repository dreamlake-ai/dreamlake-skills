# Notes

  A note is a collaborative Markdown document. This is how a script — or a
  coding agent working through bash — edits one while people have it open.

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
and subview. Selecting another resource opens or reuses its views in the detail
region. Drag a tab to an edge to compare views side by side, or into a panel's
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
https://dreamlake.ai/<namespaceSlug>/notes/<noteId>
```

Read `namespaceSlug` and `id` from `dreamlake notes create --json` or
`dreamlake notes list --json`. Do not substitute the title or human-readable
slug in this URL: the browser detail route expects the ID, even though the
CLI accepts slugs and titles. Use the returned owner namespace rather than
assuming your personal namespace. The ID is sometimes called the note hash;
it is a path segment, not a `#` URL fragment.

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

This release accepts and preserves target syntax only. Reference-click target
navigation, scrolling and artifact-frame routing are deferred to the tab/view
workstream. An existing artifact ID or an author-defined hash route must supply
the target; do not infer slide numbering or invent a section.

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
CLI 0.28.0+ adds explicit presence controls. These are separate capabilities:
a successful read does not prove that the server supports the presence endpoint.
The CLI uses the active login's API; running a locally installed binary does not
select a local server. Use `--remote <url>` to test a specific API or `--debug`
for the local development server.

To check a matching API, use an accessible test note and the stable task identity
below. Run a read, then join, heartbeat, clear and leave. Verify patch support
separately on a disposable note with a merge patch, an exact readback, and a stale
exact request that must fail without changing the source. Do not use an existing
user document as a write-test fixture.

#### Read and linger in the foreground

The next CLI release adds `notes read --linger` and `notes visit`; these are not
available in CLI 0.28.0. They use the deployed Notes v2, presence-roster and
agent-activity endpoints. Python has no corresponding convenience method yet.

Set `DREAMLAKE_AGENT_ID` once to a unique, stable task-session identity (and
optionally `DREAMLAKE_AGENT_NAME`) as described below. `NOTE_ID` must identify a
note you can access as a member or explicitly shared reader.

```bash
# NOTE_ID and the stable task identity must already be set.
dreamlake notes read "$NOTE_ID" --linger
# Alternative: newline-delimited JSON for a runner consuming the stream.
dreamlake notes read "$NOTE_ID" --linger --json
```

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
# Slower output for an agent runner; each line is a complete JSON event.
dreamlake notes read "$NOTE_ID" --linger --debounce 2s --throttle 5s --json
```

Polling is sequential, with a pause of `min(1s, debounce, throttle)` between
completed requests. Timing is based on **observed** source changes, so polling
and network latency can add delivery delay; this is not a keystroke-level timer.
Activity from the same agent/operation is coalesced to its latest pending
observation, and arrivals/departures that cancel within a pending batch are
omitted. `--format inline-dff` selects that incremental format instead.
Unchanged batches and heartbeats are silent. Repeated activity observations for
the same agent, operation, source hash and range are suppressed; your own agent
presence and activity are omitted. Multiple browser connections remain distinct.
Names are quoted in text notifications. Heartbeats renew the lease roughly every
20 seconds in addition to the attributed reads.

This is a best-effort stream of observations, not an audit log: brief visits or
activity between polls can be missed, and edits that cancel out within a burst
produce no net content diff. Human edits appear in content diffs; the activity feed
currently attributes agent reads and edits only. Reading updates does not prove
human attention, and it does not reserve or lock the note.

With `--json`, stdout is NDJSON: one `type: "snapshot"` object containing
`observedAt`, `note`, `content`, `hash`, `revision`, and `participants`, followed
by `type: "update"` objects containing `observedAt`, `joined`, `left`, and
`activities`. Changed content adds `content: {note, base, hash, revision, format,
patch}`. Observation times are Unix milliseconds; batch sources are fetched
separately and are not an atomic cross-stream snapshot. Progress and errors go
to stderr. No update object is emitted for an unchanged batch.

`--linger` supports complete source reads only; it cannot be combined with
`--legacy`, `--view html`, `--since`, sections, line ranges or numbered output.
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
operation), returns immediately and does not read content. Legacy
`notes presence ...` controls remain available for compatibility; use
`read --linger` when you want ongoing updates rather than silent keepalive.

CLI 0.28.0+ and the matching server expose these low-level compatibility controls:

```bash cli-help="notes presence"
# NOTE_ID and the stable task identity must already be set.
dreamlake notes presence "$NOTE_ID" join
dreamlake notes presence "$NOTE_ID" heartbeat
dreamlake notes presence "$NOTE_ID" clear
dreamlake notes presence "$NOTE_ID" leave
# Compatibility: a silent foreground lease keeper; prefer read --linger in the next CLI release.
dreamlake notes presence "$NOTE_ID" join --watch
```

`join --watch` does not stream updates; it heartbeats every 20 seconds and leaves when interrupted. It is
optional, not the standard recipe. `clear` clears activity without leaving;
`leave` removes presence. A heartbeat does not create a missing session or revive
an expired one (410); join or a normal attributed interaction can establish
presence again. Never start an untracked helper that outlives the task.

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
when the environment variables below are set. Explicit presence commands require
CLI 0.28.0+ and the matching server, and an active collaborative room.
Updating a skill does not update a binary or deploy a server. Python has no
presence convenience method yet; use the HTTP contract when available.
The authorized agent-activity feed retains operation observations, not an online
roster. Observation failures must not turn an acknowledged edit into an apparent
failed edit. Live source-range decorations currently require the collaborative
editor; read-only views do not run an RTC client.

#### Agentic usage pattern: one identity, normal commands

For agents that opt into presence, initialize once in the runner's task environment. For separate shell tool calls,
the runner must inject the same saved values each time; an export in one shell
does not propagate into later independent shells. No explicit join is required.

```bash
export DREAMLAKE_AGENT_ID="codex:$(python3 -c 'import uuid; print(uuid.uuid4())')"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID="<full-note-id>"
```

Run ordinary commands with that identity. Reading establishes/refreshes presence;
it does not mean the agent remains actively reading between commands.

```bash
dreamlake notes read "$NOTE_ID" --json > baseline.json
dreamlake notes find lighthouse --note "$NOTE_ID" --json
# Draft a reviewed patch against baseline.json, using the patch workflow below.
# Retain its revision, apply the patch, and read back the acknowledged revision.
```

The conditional patch and exact-readback examples elsewhere in this guide remain
required; presence does not relax concurrency checks. Do not retry an old patch
with a newly fetched revision merely to force it through.

When finished, optionally call `dreamlake notes presence "$NOTE_ID" leave` on a
matching installation. Otherwise let presence expire. Do not forget the
session ID between commands, and do not require the agent to remember cleanup for
correctness. Stop any optional watch helper and remove the task identity from the
runner's environment when the task ends.

### Keep incremental reads compact

For an agent following a note, save one full `read --json` baseline, then use
`read --since "$BASE_HASH"` for subsequent checks. The default `inline-dff`
returns only character edits and is the preferred compact response for agents.
Use `--format diff` when line context or a standard unified patch is useful.
On servers with localized unified-diff generation, this returns changed
lines with up to three unchanged context lines on each side; nearby changes
share a hunk and distant changes use separate hunks. Older servers may still
return a whole-document replacement; a docs or skill update alone does not
change server output. The default inline format already avoids that expansion.

Both formats preserve exact source, including CRLF and a missing final newline.
An unchanged source returns an empty `patch`, possibly with a newer RTC
`revision`. Keep `base`, `hash`, and `revision` with the response. Apply the patch
only to the saved source matching `base`, verify its resulting hash, and never
replace an existing draft's original revision just to make it pass. Unknown or
expired bases remain errors. Use `--json` and extract `.patch` when a consumer
needs patch text alone; normal text output includes metadata.

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
`data-start`/`data-end` ranges address that source in Unicode code points;
`data-map` marks linear text, atomic syntax or generated presentation.

Decode the source attribute once to recover canonical source, including original
entity spelling and line endings. Patch that source using the embedded revision;
never upload generated wrappers or mapping attributes. HTML reads are full
snapshots; `--view html --since` is rejected. HTML-looking source is rendered as
HTML, other source as Markdown. Rich or restricted structures may map atomically;
no editable range is guessed from generated text. Scripts, active attributes and
network-loaded media are excluded from this static preview.

### Rich tokens in HTML reads

The v2 HTML renderer recognizes strict Markdown source tokens for
`:placeholder[owner]`, `:asset-reference[asset-id]{caption="plot"}`,
`:note[note-id]`, `:artifact[geyang/pitch-deck]`, `:bindr[bindr-id]` and
`:chatgpt-content-reference[0]` in the development preview, plus every saved legacy form. Attribute values use double quotes;
unknown/duplicate attributes and malformed tokens remain literal source.
Code, escaped punctuation, Markdown links and URL paths keep their ordinary
interpretation. Existing `[ owner ]` placeholders retain blue boxes, visible
brackets, inner spacing and the **placeholder** hover label.

Recognized components carry atomic `data-start`, `data-end` and `data-map`
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
