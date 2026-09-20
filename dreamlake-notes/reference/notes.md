# Notes

  A note is a collaborative Markdown document. This is how a script — or a
  coding agent working through bash — edits one while people have it open.

## Browsing in the app

`/<namespace>/notes` is the signed-in catalog. Your own catalog also shows
Shared with me and a separate section for recent organization notes. Public
Notes open directly at `/<namespace>/notes/<note-id>` without an application
sidebar when signed out. Private note share links require sign-in according to
the server's per-person grant rules.

`/<namespace>/profile?tab=notes` displays public notes, even for the owner.
The namespace Notes list API supports anonymous reads; nonmembers only see
public, non-deleted notes, with matching filtered totals. Supplied invalid tokens
are rejected. Anonymous searches use the stored index without flushing RTC rooms.
Private notes and shared-with-me results stay in the signed-in application. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

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

CLI and Python writes continue to use their conditional revision checks below.
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

## Name a note

**CLI**

```bash
dreamlake notes read design-doc                     # slug
dreamlake notes read 6aa948b3fea6e541282b747e       # id
dreamlake notes read "Design Doc"                   # exact title

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

**CLI**

```bash
dreamlake notes read "$NOTE_ID"                                    # whole body
dreamlake notes read "$NOTE_ID" --section install                  # one section
dreamlake notes read "$NOTE_ID" --start-line 40 --end-line 80
dreamlake notes read "$NOTE_ID" --start-line 40 --end-line 80 --numbered
dreamlake notes read --note "$NOTE_ID" --json                      # body + revision
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
REV=$(dreamlake notes read "$NOTE_ID" --json | jq -er .etag)
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

### Patch

A unified diff carries its own context, so it refuses to apply to a document
that moved rather than taking half of it. Reach for this when one change
touches several places at once.

**CLI**

```bash
diff -u before.md after.md | dreamlake notes patch "$NOTE_ID" --file -
dreamlake notes patch "$NOTE_ID" --file change.patch --dry-run
```

**Python**

```python
note.patch(unified_diff)
note.patch(unified_diff, if_match=doc.etag)
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

## Don't overwrite anyone

Every write carries the revision it was based on. A note that changed in
between is **refused** rather than overwritten:

**CLI**

```bash
REV=$(dreamlake notes read "$NOTE_ID" --json | jq -r .etag)
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
| `NoteBusy` | `4` | The realtime service is unavailable | Wait a few seconds, retry. |
| `PatchFailed` | `5` | Your diff no longer applies | Re-read, regenerate it. |
| `NoMatch` | `6` | Nothing matched | Widen the query. |
| — | `7` | Refused to overwrite a local file | Pass `--overwrite`. |

`--force` / `force=True` skips the check — deliberately, so overwriting a
colleague is something you typed rather than something that happened.

Verify a write landed by reading it back against the revision it produced:

```python
rev = note.patch(diff, if_match=doc.etag)
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
