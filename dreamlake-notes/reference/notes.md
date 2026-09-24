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

Inside another DreamLake note, use `#note:<full-note-id>` for a native note
reference. A browser link does not change visibility or grant access to a
private note.

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
`text` and content-hash `etag`). The v2 preview later in this guide uses
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

**Unreleased:** requires the revision-diff server endpoint and matching Python SDK/CLI.

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
result = note.patch(my_diff, if_match=ref)
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

A unified diff carries its own context, so it refuses to apply to a document
that moved rather than taking half of it. Reach for this when one change
touches several places at once.

**CLI**

```bash
diff -u before.md after.md | dreamlake notes patch --legacy "$NOTE_ID" --file -
dreamlake notes patch --legacy "$NOTE_ID" --file change.patch --dry-run
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

## Notes v2 preview: Bash patches

This interface is implemented in draft milestone PRs tracked by
[the Notes master plan](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).
It requires a compatible RTC server with unlocked baseline observations and the matching CLI release;
these docs do not claim it is deployed. Existing installed clients keep their
current interface until upgraded.

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
revision: rtc:94c1a7696f6bcd27fa880e4b38b3f73cdd3971f28b44edf9018fadf817df0f3f
mode: merge
baseRevision: rtc:9a67f239fc8b862aa557dd10dd6512a7669861287ac8fe262d9c80afebcd18e7
```

With `--json`, the corresponding stdout is:

```json
{
  "note": "507f1f77bcf86cd799439099",
  "hash": "sha256:163af32ec4bc25f27e3b9ae68fe85c75e5b4436a769cc82a4050692643ce92cf",
  "revision": "rtc:94c1a7696f6bcd27fa880e4b38b3f73cdd3971f28b44edf9018fadf817df0f3f",
  "baseRevision": "rtc:9a67f239fc8b862aa557dd10dd6512a7669861287ac8fe262d9c80afebcd18e7",
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

They correspond to exact conflict **412**, missing original identity baseline
**404**, and malformed patch **422**. CLI exact conflicts return exit **3**,
empty stdout and explanatory stderr; Python raises `NoteChanged`. The CLI also
reports malformed patches on stderr (exit **5**), without replacing local files.
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

### Rich tokens in the draft HTML read representation

The unreleased v2 HTML renderer recognizes strict Markdown source tokens for
`:placeholder{text="owner"}`, `:asset-reference{id="asset-id" caption="plot"}`,
`:note{id="note-id"}`, `:bindr{id="bindr-id"}` and
`:chatgpt-content-reference{index="0"}`. Attribute values use double quotes;
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

This source capability is tracked in [master #706](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706)
and requires the corresponding server/client releases and deployment before
hosted use. Browser rich components are reviewed separately in
[UI PR #415](https://github.com/dreamlake-ai/dreamlake-ai/pull/415).

### Heading numbering in draft HTML reads

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
interpreted as Markdown front matter. This remains unreleased work tracked in
[master #706](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).
