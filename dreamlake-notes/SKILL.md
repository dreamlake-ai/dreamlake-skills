---
name: dreamlake-notes
description: Create, read, edit, search and attach files to DreamLake notes from Python or the CLI — replace text by name rather than by line number, read part of a long note, grep across every note for where a phrase is, and attach files that render in a browser. Use when a task involves any of those, especially while other people have the note open.
---

# DreamLake Notes — edit a live document without overwriting anyone

A note is a collaborative Markdown document. People may have it open while you
edit it. Everything here is built so that an edit either lands on exactly the
text you named, or is refused — never applied to the wrong place and never
silently on top of somebody's typing.

Two clients, same behaviour: `dreamlake notes …` and `import dreamlake as dl`.

## Setup

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash   # CLI
pip install dreamlake                                   # Python
dreamlake login
```

Both read the same saved login, so signing in once is enough.

## The rule that shapes everything

**Name the text, not the line number.** Line numbers move when anyone edits
above them; text does not. And an edit whose query matches twice is
**refused**, not applied to the first match — the failure you cannot see in a
diff is the one worth preventing.

```bash
dreamlake notes replace "Draft" --text "Published" --all --note "$NOTE"
```

```python
doc = dl.note("<uuid>").read()
doc.replace("Published", query="Draft", all=True)
doc.save()
```

Without `--all` / `all=True`, two matches is an error that tells you how many
it found.

## Create and list

```bash
dreamlake notes create "Design Doc"
dreamlake notes create "Design Doc" --file draft.md
dreamlake notes create "Design Doc" --text "# Design Doc"
dreamlake notes create "Design Doc" --public        # default is private

dreamlake notes list
dreamlake notes list --limit 20
dreamlake notes list --shared                        # what others sent you
dreamlake notes list --json
```

```python
note = dl.create_note("<namespace>", "Design Doc", text="# Design Doc\n")
note.id, note.namespace, note.etag

dl.list_notes("<namespace>")
dl.list_notes("<namespace>", limit=20, offset=20)
dl.shared_with_me()
```

Titles may repeat — the slug takes a suffix — so keep `note.id` rather than the
name you passed. The CLI names a note by slug or id; Python takes
`<namespace>/<slug>`, or a bare id.

## Reading

```bash
dreamlake notes read "$NOTE"                              # whole body
dreamlake notes read "$NOTE" --section install            # one section
dreamlake notes read "$NOTE" --start-line 40 --end-line 80 --numbered
dreamlake notes toc --note "$NOTE"                        # outline + ranges
dreamlake notes toc --note "$NOTE" --json
```

```python
note = dl.note("<namespace>/design-doc")
note.text                                   # whole body
note.read_section("install")
part = note.read_lines(1, 40)               # part.truncated, part.total_lines
note.read().toc()
```

A **section** is a heading plus everything under it. Anchors are slugs of the
title (`setup`, `setup-2` when they repeat); text above the first heading is
`preamble`.

`toc` gives each heading an anchor, a **line range** and a **character range**,
so you can go straight to a part without reading the whole note.

A ranged read reports the **whole** note's revision, not the range's. Sending a
range back as the body would delete everything outside it — edit with `replace`
instead.

## Editing

```bash
dreamlake notes grep "Draft" --note "$NOTE"          # where is it, how many
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note "$NOTE" --dry-run
dreamlake notes insert --text "New line" --line 10 --note "$NOTE"
dreamlake notes delete "obsolete paragraph" --note "$NOTE"
```

```python
doc = dl.note("<uuid>").read()      # a local snapshot; nothing sent yet
doc.find(regex=r"\bTODO\b", flags="i")
doc.replace("$<key>: $<value>", regex=r"(?<key>\w+)=(?<value>\d+)", all=True)
doc.insert("New line", line=10)
doc.delete(query="obsolete paragraph")
print(doc.diff())                   # what would change
doc.save()                          # one conditional write
doc.revert()                        # throw the local edits away
```

Patterns are **JavaScript** in both clients: `(?<name>…)`, `$1`, `$<name>`,
`$&`. Expansion is automatic. `--dry-run` shows the result without writing.

Every Python edit is local until `save()`, which sends one patch against the
revision the snapshot was read at. If the note moved meanwhile the save is
**refused** — read again and redo, rather than clobbering.

### HTML

Address an element instead of raw text:

```bash
dreamlake notes select "#contact" --note "$NOTE"
dreamlake notes replace "Contact us" --text "Talk to sales" --selector "#contact" --note "$NOTE"
dreamlake notes insert --text "<li>New</li>" --selector "#list" --position append --note "$NOTE"
```

```python
doc.select("#contact").replace("Talk to sales", query="Contact us")
doc.select("#contact").update(attrs={"href": "/sales"})
doc.select("#list").insert("<li>New</li>", position="append")
```

Only the characters addressed change. Entity spelling, attribute quoting and
whitespace elsewhere survive, so the diff is the edit and nothing else.

## Writing whole parts

When the change is "replace this section" rather than "change this phrase":

```bash
dreamlake notes write "$NOTE" --file whole.md
dreamlake notes write "$NOTE" --section install --file install.md
dreamlake notes append "$NOTE" --text "one more line"
dreamlake notes append "$NOTE" --file more.md
dreamlake notes add-section "$NOTE" --file trouble.md --after install
dreamlake notes rm-section "$NOTE" troubleshooting
```

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

```bash
diff -u before.md after.md | dreamlake notes patch "$NOTE" --file -
dreamlake notes patch "$NOTE" --file change.patch --dry-run
```

```python
note.patch(unified_diff)
note.patch(unified_diff, if_match=doc.etag)
```

## Finding something

```bash
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive --glob 'spec-*'
dreamlake notes grep "Draft" --note "$NOTE"        # one note only
dreamlake notes grep "Draft" --json                # revision + character range
```

```python
for hit in dl.grep_notes("TODO", namespace="<namespace>", context=1):
    print(f"{hit.note_slug}:{hit.line}:{hit.column}  {hit.text}")
```

Output is `slug:line:column`, like `rg` — which note, and where inside it.
**Literal and case-insensitive by default**, so `v1.2` does not also match
`v1x2`; `--regex` is explicit.

Each hit carries its revision and `ind`, the character range — enough to go
straight to an edit without re-reading:

```python
hit = dl.grep_notes("Draft", namespace="<namespace>").hits[0]
doc = hit.open().read()
doc.replace("Published", ind=hit.ind)
doc.save()
```

`doc.find()` is the local counterpart: it searches a snapshot you already hold,
with no network call, and is what you want mid-edit.

## Files on a note

Files inherit the note's permissions, so an attachment on a private note stays
private.

```bash
dreamlake notes files upload ./report.html --note "$NOTE"
dreamlake notes files write config.json --text '{}' --note "$NOTE"
dreamlake notes files list --note "$NOTE"
dreamlake notes files list 'assets/*.png' --note "$NOTE"
dreamlake notes files cat config.json --note "$NOTE"
dreamlake notes files download report.html --note "$NOTE" -o ./report.html
dreamlake notes files mv old.txt new.txt --note "$NOTE"
dreamlake notes files cp a.txt b.txt --note "$NOTE"
dreamlake notes files rm old.txt --note "$NOTE"        # trash
dreamlake notes files list --trashed --note "$NOTE"    # ids of trashed files
dreamlake notes files restore <file-id> --note "$NOTE"
```

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
memory still round-trips intact — a 100 MB upload costs single-digit MB of
resident memory. `cat` **refuses a binary** rather than printing mojibake you
might pipe back in.

Restoring takes the file **id**, not its path: two trashed files can share a
path, so the path alone would be ambiguous. `files list --trashed` prints ids.

### Looking at one

```bash
dreamlake notes files preview report.html --note "$NOTE" --open
dreamlake notes files preview report.html --note "$NOTE" --share
dreamlake notes files preview report.html --note "$NOTE" --revoke
```

```python
print(note.files.find("report.html").preview_url())
print(note.files.find("report.html").preview_url(share=True))
note.files.find("report.html").unshare()
```

The default link needs the reader signed in and grants nothing by itself.
`--share` opens **without signing in** and does not expire; `--revoke`
withdraws it, and every copy stops working at once.

Uploaded HTML renders in a separate origin, never the dashboard's — a file
somebody attached cannot reach the reader's session. Markdown, SVG, code and
images render too; anything else offers a download. A file with no rendered
form is refused rather than linked.

## Writing while people are in the note

Every write carries the revision it was based on. If someone else wrote first,
yours is refused rather than applied on top:

```bash
REV=$(dreamlake notes read "$NOTE" --json | jq -r .etag)
dreamlake notes write "$NOTE" --file new.md --if-match "$REV"
```

Exit codes worth branching on: **3** stale revision (`NoteChanged`), **4** note
busy (`NoteBusy`), **5** patch did not apply (`PatchFailed`), **6** nothing
matched (`NoMatch`), **7** refused to overwrite a local file. `--force` /
`force=True` skips the check and is the only way to overwrite deliberately.

Verify a write landed by reading it back against the revision it produced:

```python
rev = note.patch(diff, if_match=doc.etag)
check = note.read(if_match=rev.etag)      # refused if anything changed since
```

## Which addressing to reach for

1. **Exact text** (`query=`) — what you can state reliably; fails loudly.
2. **A section anchor** from `toc`.
3. **A line or character range** from a read, TOC or grep hit.
4. **A unified patch** for coordinated changes in several places at once.
