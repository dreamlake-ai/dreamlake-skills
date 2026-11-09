<!-- generated from https://docs.dreamlake.ai/notes/cli-editing.md at 0.1.134 4bbe54f7; do not edit -->

# Read, edit and search from the CLI

## Name a memo

**CLI**

```bash
dl memos read --legacy design-doc                     # slug
dl memos read --legacy 6aa948b3fea6e541282b747e       # id
dl memos read --legacy "Design Doc"                   # exact title

# Every example below uses $NOTE_ID. Set it once — any of the three forms:
NOTE_ID=design-doc
```

**Python**

```python
dl.memo("<namespace>/design-doc")
dl.memo("6aa948b3fea6e541282b747e")                  # id alone, no namespace
```

A memo you may not read answers exactly as one that does not exist.

## Read Memos directly

**For normal reads, run the bare command and inspect its output directly:**

```bash
# Set NOTE_ID to the note ID, slug, or exact title you want to read.
dl memos read "$NOTE_ID"
```

The default is an annotated reading view. Use the smallest relevant read for
inspection; do not write generated address hints back into the Memo. For an
editing baseline, retain the complete structured snapshot and its opaque revision:

```bash
dl memos read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > baseline.md
```

Keep both files unchanged while preparing a patch. `--view source` exports exact
source bytes without metadata; it alone does not retain the revision required
for a guarded edit. See the current [CLI read contract](https://cli.dreamlake.ai/notes/reading).

### Python SDK read

Python SDK **0.41.0+** exposes the canonical `memos` facade. With the SDK
installed and the intended account logged in, retain one complete snapshot:

```python
import dreamlake as dl

memo = dl.memos("<full-memo-id>")
snapshot = memo.read(view="source")
print(snapshot.content)
# Retain snapshot.revision and snapshot.hash with this original source.
changes = memo.diff(since=snapshot.revision)
print(changes.patch)
```

The facade's `diff(since=...)` accepts a retained RTC revision or prior read
result, reads that retained source and verifies the resulting net diff. It does
not identify the human editor or advance a write baseline. Missing retained
source is an error, not an empty diff. With Python 0.43.0+ and matching server
support, `memo.presence(selections=True)` observes human selections; inspect its
availability fields before interpreting an empty roster. See
[agent presence](docs-notes-agent-presence.md#source-bound-human-selections).

Use the actual full ID returned by DreamLake. `dl.notes` remains an alias for
the facade. The lower-level `dl.memo`/`dl.note` interfaces below remain available;
their `read_snapshot` and hash-based `diff` contract differs from the facade's
revision-based `diff`. Do not interchange those inputs. SDK configuration and
login are documented in the [Python SDK guide](https://py.dreamlake.ai/memos).

{/* <!-- skill-entrypoint:end --> */}

## Read

### Prefer the smallest relevant read

For a targeted question or edit, read the relevant section or passage instead
of the entire memo. Use `toc` or `find` to locate it when needed, then request
that section or line range. Read the whole document when reviewing the whole
document, establishing a required v2 baseline, or recovering a missing or expired
baseline — not on every small edit or verification.

Keep the baseline and its tokens across calls. Once a v2 baseline is available,
use [incremental reads](docs-notes-v2.md#keep-incremental-reads-compact) to refresh the cached
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
dl memos read --legacy "$NOTE_ID"                                    # whole body
dl memos read --legacy "$NOTE_ID" --section install                  # one section
dl memos read --legacy "$NOTE_ID" --start-line 40 --end-line 80
dl memos read --legacy "$NOTE_ID" --start-line 40 --end-line 80 --numbered
dl memos read --legacy --note "$NOTE_ID" --json                      # body + revision
dl memos toc --note "$NOTE_ID"                              # the outline
dl memos toc --note "$NOTE_ID" --json
```

**Python**

```python
note = dl.memo("<namespace>/design-doc")
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
enough to edit a part without reading the whole memo.

A ranged read reports the **whole** memo's revision. Writing a range back as
the body deletes everything outside it — use `replace` instead.

## Edit by what it says

Line numbers move when anyone edits above them; text does not. A query matching
**twice is refused**, not applied to the first match.

The examples below are independent recipes, not a script to run in sequence.
Before each revision-checked edit, read the memo and capture its revision
(the CLI recipe uses `jq`):

```bash
REV=$(dl memos read --legacy "$NOTE_ID" --json | jq -er .etag)
```

Inspect the returned body before choosing the edit. After a successful write,
read again before the next edit; do not reuse the old revision or bypass a
conflict with `--force`.

**CLI**

```bash
dl memos find "Draft" --note "$NOTE_ID"
dl memos find --regex '\bTODO\b.*' --flags im --note "$NOTE_ID"

dl memos replace "Draft" --text "Published" --all --note "$NOTE_ID" --if-match "$REV"
dl memos insert --text "New line" --line 10 --note "$NOTE_ID" --if-match "$REV"
dl memos delete "obsolete paragraph" --note "$NOTE_ID"
```

**Python**

```python
doc = dl.memo("<uuid>").read()      # local snapshot
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
revision `read()` returned. If the memo moved, the save is refused.
`doc.revert()` throws the local edits away.

### Patterns

Regex is explicit — never inferred from the query. JavaScript syntax in both
clients: `(?<name>…)`, `$1`, `$<name>`, `$&`, `$$` for a literal `$`. Capture
expansion is automatic; there is no flag for it.

**CLI**

```bash
dl memos replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note "$NOTE_ID"
dl memos replace --regex '(?<key>timeout|retries)=(?<value>\d+)' \
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
dl memos replace --text "Updated line" --line 10 --note "$NOTE_ID" --if-match "$REV"
dl memos replace --text "New block" --line 10:15 --note "$NOTE_ID"
dl memos replace --text "replacement" --ind 120:145 --note "$NOTE_ID"
dl memos insert --text "inserted text" --ind 120 --note "$NOTE_ID"
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

Markdown may contain HTML, and a memo's body can be an HTML document outright.
When it does, address an **element** rather than raw text — the same sentence
often appears in several places, and a plain query would refuse the edit as
ambiguous.

**CLI**

```bash
dl memos select "#contact" --note "$NOTE_ID"          # where it is, and its text
dl memos replace "Contact us" --text "Talk to sales" --selector "#contact" --note "$NOTE_ID"
dl memos insert --text "<li>New</li>" --selector "#list" --position append --note "$NOTE_ID"
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

Whole-body target writes plan changes against an original source; section
replacement remains a separate compatibility operation.

**Release status — October 12, 2026:** CLI 0.61.0 is publicly published: all nine
npm records, downloaded Linux integrity/version, fresh npm installation and native
skill packaging are verified. The public binary passed concurrent-gap preservation,
strict input and exact-write checks; disposable Memos were removed.
Python SDK 0.28.0 is publicly published: wheel/sdist bytes
match the retained release workflow, and a fresh public installation passed
actual API verified-read/diff/Doc-cache acceptance on a disposable Memo, then
removed it. Live docs and public skill propagation are separate release checks.

**CLI**

```bash
# CLI 0.61.0: retain the original source used to prepare whole.md.
dl memos read "$NOTE_ID" --json > whole-baseline.json
WHOLE_BASE=$(jq -er '.revision' whole-baseline.json)
jq -jr .content whole-baseline.json > whole.md
# Edit whole.md while keeping whole-baseline.json unchanged.
dl memos write "$NOTE_ID" --file whole.md --base-revision "$WHOLE_BASE" --json > whole-ack.json
WHOLE_ACK=$(jq -er '.revision' whole-ack.json)
dl memos read "$NOTE_ID" --at "$WHOLE_ACK"
# Section write remains on its explicit compatibility API.
dl memos write "$NOTE_ID" --section install --file install.md
# Append uses original-revision patches in CLI 0.59.0 and later. Requires jq.
dl memos read "$NOTE_ID" --json > append-baseline.json
BASE=$(jq -er '.revision' append-baseline.json)
dl memos append "$NOTE_ID" --text "one more line" --base-revision "$BASE" --json > append-ack.json
ACK=$(jq -er '.revision' append-ack.json)
dl memos read "$NOTE_ID" --at "$ACK"
# For a file, use --file more.md with the same saved original baseline.
dl memos add-section "$NOTE_ID" --file trouble.md --after install
dl memos rm-section "$NOTE_ID" troubleshooting
```

**Python**

```python
# Python SDK 0.27.0 and later: plan disjoint edits on this original source.
whole_baseline = note.read_snapshot()
write_receipt = note.write(whole_body, at=whole_baseline)
acknowledged = note.read_snapshot(at=write_receipt.revision)
note.write_section("install", "## Install\n\npip install dreamlake\n")
# Python SDK 0.26.0 and later: retain the original collaborative snapshot.
baseline = note.read_snapshot()
receipt = note.append("\n## Changelog\n\n- shipped\n", at=baseline)
acknowledged = note.read_snapshot(at=receipt.revision)
note.insert_section("## Troubleshooting\n\nCheck the logs.\n", after="install")
note.delete_section("troubleshooting")
note.refresh()                   # re-read after someone else wrote
```

Anyone with the memo open **sees an accepted change appear**. Modern append
merges against the original collaborative identities, preserving unrelated
concurrent edits. Add CLI `--exact` or Python `exact=True` to require that the
original revision is still current. A stale exact request requires review;
never replace its baseline with a fresh revision merely to make it pass.

Since server `06fbbe65` (production, 2026-10-27), merge mode refuses, with
HTTP 412 `stale` and no write, any patch that overlaps a change made after its
baseline, including text appended at the same end of the memo. Python reports
this as `NoteChanged`. Disjoint edits still merge. The
CLI's bundled `notes-editing` reference ("Overlapping concurrent changes")
gives the exact rule and recovery.

Python's default append returns a `PatchReceipt`; CLI `--json` returns its
revision and hash. Read back that acknowledged revision before claiming the
intended result. If a write outcome is unknown, reconcile it before resubmitting.
Explicit CLI `--legacy` / `--force` and Python `legacy=True` / `force=True`
retain the older append compatibility path; Python returns a string there.

CLI 0.61.0 whole-body write derives bounded exact disjoint code-point changes
from one hash-verified original snapshot, preserving unchanged identities even
within a paragraph. Retain `--base-revision` when a target was prepared earlier;
omitting it reads one current snapshot and cannot establish an old file's origin.
Modern file/stdin input rejects malformed UTF-8 before transport and preserves
literal BOM, Unicode and line endings. Merge no-ops send no write; an unchanged
`--exact` target sends an empty PATCH so a stale original revision still rejects.
Alignment or patch limits fail before submission without a coarse rewrite.
Explicit `--legacy`, `--force`, or `--if-match` keep the prior body path and cannot
mix with modern baseline/exact flags. `--section` also rejects those modern flags.
Keep the original target/baseline after an unknown acknowledgment; never replay
or silently refresh the baseline. Without `--json`, dry-run stdout is the target
body; JSON dry-run also reports the planned payload. Neither predicts merged
concurrent source.

Python SDK 0.27.0 also defaults whole-body `note.read()` drafts, `note.write()`
and `doc.save()` to original-revision edits. Unchanged source spans preserve
their collaborative identities, including within one paragraph. A draft keeps
its own original snapshot even if other operations use the same Memo object.
After saving, it adopts the acknowledged merged source for the next edit.
If that readback fails after an acknowledged write, preserve the receipt and
draft and reconcile before another save; do not replay the write.

SDK 0.27.0 also fixes native append escaping for tabs. Older native append
clients can reject tab-containing edits; upgrading preserves the saved baseline.
Explicit Python `legacy=True`, `force=True` or `write(if_match=...)` retain
compatibility behavior. A compatibility save keeps subsequent saves in the
ETag domain until a new modern draft is read.

CLI whole-body writes through 0.60.0, Python whole-body writes through 0.26.0,
and section writes/insertion/deletion still use the ETag compatibility interface.
They can reject an intervening content change. Section client migration and
Runbook attachment remain pending; no legacy command or server route is retired here.

### Changes since a read or edit

**Legacy ETag interface:** available alongside v2 in CLI 0.26.2 and Python SDK 0.20.0. Select `--legacy` for these CLI recipes and `legacy=True` for remote Python patches.

The CLI returns the same ref in `read --json` and accepts it via `--since`:

```bash
# Requires jq. Keep the snapshot and ref for a later shell session.
NOTE_ID=design-doc
dl memos read --legacy "$NOTE_ID" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
dl memos diff --legacy "$NOTE_ID" --since "$REV"
dl memos diff --legacy "$NOTE_ID" --since "$REV" --json
# Apply a diff prepared against that saved body:
dl memos patch --legacy "$NOTE_ID" --file change.patch --if-match "$REV" --json
```

`notes diff` requires `--since`; it does not keep a hidden local baseline.
Plain output is the diff on stdout and current ETag on stderr. `--json` also
returns `from` and `to`. The CLI help includes this workflow:
`dl memos diff --legacy --help`, `notes read --help`, and `notes patch --help`.

Reads return `doc.etag`, a quoted SHA-256 hash of the complete memo text. Keep
that ref to see changes since your own read or successful edit across sessions:

```python
note = dl.memo("<note-id>")
doc = note.read(legacy=True)
ref = doc.etag

print(note.diff(since=ref, legacy=True))  # explicit compatibility diff
print(note.diff(legacy=True))             # this handle's cached ETag
result = note.patch(my_diff, if_match=ref, legacy=True)
ref = result.etag                   # reference for the successful edit
```

Fetching a diff does not advance the cached revision or write precondition.
Call `read(legacy=True)` or `refresh(legacy=True)` to adopt the latest
compatibility state. Identical text has the same hash; the ref identifies content, not an RTC operation index. Unknown refs
return an error, including older refs whose snapshots were never retained.

The HTTP endpoint is `GET /namespaces/:slug/notes/:noteId/diff?since=<etag>`.
It returns `diff`, `from`, `to`, and `etag` (the current ref). Snapshots are
scoped to the memo and require current read access. Optional `context` accepts
0–100 lines, default 3. Partial reads return a ref for the complete body.

For local draft changes, use `doc.diff()` for all unsaved changes,
`doc.diff(since="last_edit")` for the latest local operation, and
`doc.patch(unified_diff)` to apply a patch before `doc.save()`.

### Verified full reads and remote diffs (SDK 0.28.0+)

Default `note.refresh()`, cache-miss `note.text` / `note.get_text()`, and
`note.read()` use verified complete v2 source. Returned Memo identity, content
hash and RTC revision must agree; malformed responses or redirects reject without
adopting source. Refresh updates the Memo cache, never an existing Doc's saved
original snapshot. `read_snapshot()` remains an independent verified read;
`at` selects retained source, while `if_match` checks the current RTC revision.
They cannot combine. An ETag is not an RTC revision and must not be supplied here.

```python
note.refresh()                 # verified complete source, not a partial range
source = note.text             # cached source; refresh explicitly for newer text
original = note.read_snapshot()
remote_diff = note.diff(since=original.hash)  # string, not a write receipt
# Retain original.revision separately for a later original-revision edit.
```

Default `note.diff()` returns a unified source-diff string and uses this handle's
cached content hash when `since` is omitted. `since` accepts `sha256:<hex>`, quoted
ETag-shaped SHA-256, or bare SHA-256; RTC revisions are rejected. The v2 diff's
Note/base/format/receipt metadata and acknowledged retained source hash are
validated. Inspection does not adopt returned source or advance any cache/draft
baseline; a display diff is not a write precondition or proof of peer convergence.

Explicit `refresh(legacy=True)`, `get_text(legacy=True)` and `diff(legacy=True)`
retain compatibility behavior. `diff(context=N)` with `N != 3` deliberately
selects the existing compatibility endpoint before transport; context is an
integer from 0 through 100. Default context 3 uses v2, with no fallback after a
failure. Section/line reads remain partial compatibility views and cannot serve
as complete modern write baselines. Existing Doc-local `diff()` and `patch()`
continue to operate on the local draft rather than this remote diff endpoint.

### Patch

This legacy patch helper validates unified-diff context against current text
and rejects mismatched context. Its optional ETag rejects any intervening
revision. The v2 merge workflow below instead addresses the saved original
native identities and preserves compatible concurrent edits.

**CLI**

```bash
diff -u before.md after.md | dl memos patch --legacy "$NOTE_ID" --file -
dl memos patch --legacy "$NOTE_ID" --file change.patch --dry-run
```

**Python**

```python
note.patch(unified_diff, legacy=True)
note.patch(unified_diff, if_match=doc.etag, legacy=True)
```

## Search

**CLI**

```bash
dl memos grep "TODO" -C 2
dl memos grep --regex '\bFIXME\b' --case-sensitive --glob 'spec-*'
dl memos grep "Draft" --json        # revision + character range per hit
```

**Python**

```python
for hit in dl.grep_notes("TODO", namespace="<namespace>", context=1):
    print(f"{hit.note_slug}:{hit.line}:{hit.column}  {hit.text}")
```

Output is `slug:line:column`, like `rg` — which memo, and where inside it.
Literal and case-insensitive by default, so `v1.2` does not match `v1x2`.

Each hit carries its revision and `ind`, the character range — enough to edit
without re-reading:

```python
hit = dl.grep_notes("Draft", namespace="<namespace>").hits[0]
doc = hit.open().read()
doc.replace("Published", ind=hit.ind)
doc.save()
```

## Select an agent passage by matching text

**CLI 0.32.0+:** `notes select --text` publishes an agent selection; section
selection requires the server update adding `hash` and `range` to section reads.
Older server responses fail explicitly.

```bash
export DREAMLAKE_AGENT_ID="review-session-42"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID="your-note-id"
dl memos select --text "The next step is tested in simulation." --note "$NOTE_ID"
dl memos select --text "simulation" --section next-steps --occurrence 2 --note "$NOTE_ID"
dl memos select --text "simulation" --section next-steps -o -1 --note "$NOTE_ID"
```

Use a stable task identity and your normal authenticated Memos access. The command
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
canonical source and must not be written back as a complete memo.

## Proving a patch was not submitted

If preparing the current native body baseline fails before the requested edit
starts, the write API keeps HTTP503/`rtc_unavailable` and adds this current
versioned submission status:

```json
{"error":"rtc_unavailable","mutation":{"apiVersion":1,"started":false,"phase":"baseline_read"}}
```

This proves only that this request did not reach its requested native edit; it
does not claim that other collaborators or internal room initialization changed
nothing. The API logs the request ID, actual preparation stage and the same
marker, without patch/source text or capabilities. Read failures do not carry a
mutation marker. Once native submission begins, an unavailable or lost ACK does
not receive this proof: a503 can still mean that the edit committed.

The CLI recognizes only this exact typed marker and preserves the baseline and
draft. Missing, malformed or unsupported marker versions remain unknown; they
never trigger automatic mutation retry, revision refresh or API downgrade.

## Legacy revision-checked edit helpers

The legacy whole-body/local-document helpers below carry the revision they were based on. A note that changed in
between is **refused** rather than overwritten:

**CLI**

```bash
REV=$(dl memos read --legacy "$NOTE_ID" --json | jq -r .etag)
dl memos write "$NOTE_ID" --file new.md --if-match "$REV"
```

**Python**

```python
doc = dl.memo("<uuid>").read()
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

    Every `dl memos` command and flag.

    The endpoints underneath, if you need them directly.
