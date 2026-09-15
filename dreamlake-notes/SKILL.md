---
name: dreamlake-notes
description: Read and edit DreamLake notes from Python or the CLI — find text and replace it by name rather than by line number, read part of a long note, search across every note for where a phrase is, and attach files to a note. Use when a task involves reading, editing, searching or attaching files to a DreamLake note, especially while other people have it open.
---

# DreamLake Notes — edit a live document without overwriting anyone

A note is a collaborative Markdown document. People may have it open while you
edit it. Everything here is built so that an edit either lands on exactly the
text you named, or is refused — never applied to the wrong place and never
silently on top of somebody's typing.

Two clients, same behaviour: `dreamlake notes …` and `import dreamlake as dl`.

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

## Reading

```bash
dreamlake notes read "$NOTE"                              # whole body to stdout
dreamlake notes read "$NOTE" --section install            # one section
dreamlake notes read "$NOTE" --start-line 40 --end-line 80 --numbered
dreamlake notes sections "$NOTE"                          # the outline
dreamlake notes toc --note "$NOTE"                        # outline + ranges
```

```python
note = dl.note("<namespace>/design-doc")   # or dl.note("<uuid>")
note.text                                   # whole body
note.read_section("install")
part = note.read_lines(1, 40)               # part.truncated, part.total_lines
```

A **section** is a heading plus everything under it. Anchors are slugs of the
title (`setup`, `setup-2` when they repeat); text above the first heading is
`preamble`.

A ranged read reports the **whole** note's revision, not the range's. Sending a
range back as the body would delete everything outside it — edit with
`replace(line=…)` instead.

## Editing

```bash
dreamlake notes find "Draft" --note "$NOTE"
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note "$NOTE" --dry-run
dreamlake notes insert --text "New line" --line 10 --note "$NOTE"
dreamlake notes delete "obsolete paragraph" --note "$NOTE"
```

```python
doc = dl.note("<uuid>").read()      # a local snapshot; nothing sent yet
doc.find(regex=r"\bTODO\b", flags="i")
doc.replace("$<key>: $<value>", regex=r"(?<key>\w+)=(?<value>\d+)", all=True)
doc.insert("New line", line=10)
print(doc.diff())                   # what would change
doc.save()                          # one conditional write
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

## Finding something across notes

`notes search` says *which* note. `notes grep` says *where*, in a form you can
act on.

```bash
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive --glob 'spec-*'
dreamlake notes grep "Draft" --json        # revision + character range per hit
```

```python
for hit in dl.grep_notes("TODO", namespace="me", context=1):
    print(f"{hit.note_slug}:{hit.line}:{hit.column}  {hit.text}")
```

Output is `slug:line:column`, like `rg`. **Literal and case-insensitive by
default**, so `v1.2` does not also match `v1x2`; `--regex` is explicit.

Each hit carries its revision and `ind`, the character range — enough to go
straight to an edit without re-reading:

```python
hit = dl.grep_notes("Draft", namespace="me").hits[0]
doc = hit.open().read()
doc.replace("Published", ind=hit.ind)
doc.save()
```

## Files on a note

Files inherit the note's permissions, so an attachment on a private note stays
private.

```bash
dreamlake notes files upload ./report.html --note "$NOTE"
dreamlake notes files list --note "$NOTE"
dreamlake notes files cat config.json --note "$NOTE"
dreamlake notes files download report.html --note "$NOTE" -o ./report.html
dreamlake notes files rm old.txt --note "$NOTE"     # trash; restore brings it back
```

```python
note.files.upload("diagram.png", path="assets/diagram.png")
note.files.create("config.json", text='{"enabled": true}\n')
note.files.list("assets/*.png")
note.files.find("assets/diagram.png").download("./local.png")
```

Bytes are streamed both ways and never decoded, so any file survives the round
trip. `cat` **refuses a binary** rather than printing mojibake you might pipe
back into it.

### Looking at one

```bash
dreamlake notes files preview report.html --note "$NOTE" --open
dreamlake notes files preview report.html --note "$NOTE" --share
dreamlake notes files preview report.html --note "$NOTE" --revoke
```

```python
print(note.files.find("report.html").preview_url())
print(note.files.find("report.html").preview_url(share=True))
```

The default link needs the reader signed in and grants nothing by itself.
`--share` opens **without signing in** and does not expire; `--revoke`
withdraws it, and every copy stops working at once.

Uploaded HTML renders in a separate origin, never the dashboard's — a file
somebody attached cannot reach the reader's session. Markdown, SVG, code and
images render too; anything else offers a download.

## Writing while people are in the note

Every write carries the revision it was based on. If someone else wrote first,
yours is refused rather than applied on top:

```bash
REV=$(dreamlake notes read "$NOTE" --json | jq -r .etag)
dreamlake notes write "$NOTE" --file new.md --if-match "$REV"
```

Exit codes worth branching on: **3** stale revision, **4** note busy,
**5** patch did not apply, **6** nothing matched, **7** refused local
overwrite. `--force` skips the check and is the only way to overwrite
deliberately.

## Which addressing to reach for

1. **Exact text** (`query=`) — what you can state reliably; fails loudly.
2. **A section anchor** from `sections` / `toc`.
3. **A line or character range** from a read, TOC or grep hit.
4. **A unified patch** (`notes patch`) for coordinated changes in several
   places at once.

## Two things that look the same and are not

- **`notes search`** matches note titles and bodies and returns notes.
  **`notes grep`** returns positions inside them.
- **`doc.find()`** searches one note you have already loaded, exactly.
  **`grep_notes()`** searches every note you can see, on the server, against
  an index that can lag a few seconds behind a note someone is typing into.

## Setup

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash   # CLI
pip install dreamlake                                   # Python
dreamlake login
```

Both read the same saved login, so signing in once is enough.
