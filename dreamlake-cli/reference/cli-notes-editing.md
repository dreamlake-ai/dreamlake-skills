<!-- generated from https://cli.dreamlake.ai/notes/editing.md at 0.92.0 a5d6dff; do not edit -->

# Editing with patches

A patch describes changes to the source you read. Save that source and its
revision, submit the patch against that original revision, then verify the
acknowledgment. **MERGE is the default; EXACT is an option for one request.**

## Try a complete edit

This creates a new private test note and uses normal text output throughout.
It requires login and write access. The initial source is exactly `Hello world.`
without a trailing newline. Keep the baseline unchanged while preparing the patch.

```bash cli-help="notes patch"
set -euo pipefail
dreamlake notes create "Patch tutorial" --text 'Hello world.' > created.txt
NOTE_ID=$(sed -n 's/^  id //p' created.txt)
dreamlake notes read "$NOTE_ID" > baseline.txt
# Normal reads print note, hash, and revision before the source.
BASE=$(sed -n '3s/^revision: //p' baseline.txt)
dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" > receipt.txt <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
ACK=$(sed -n '3s/^revision: //p' receipt.txt)
dreamlake notes read "$NOTE_ID" --if-match "$ACK"
# Expect Hello team. Inspect the result; do not repeat a successful patch.
```

## Explicit structured integration

Use this alternative only when a structured integration has been requested.
It requires login, write access, and `jq`.
The initial source is exactly `Hello world.` without a trailing newline.

```bash notes-example="inline-roundtrip"
set -euo pipefail
dreamlake notes create "Patch tutorial" \
  --text 'Hello world.' --json > created.json
NOTE_ID=$(jq -er .id created.json)
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md

dreamlake notes patch "$NOTE_ID" --base-revision "$BASE" \
  --json > receipt.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH

ACK=$(jq -er .revision receipt.json)
dreamlake notes read "$NOTE_ID" --if-match "$ACK" \
  --json > verified.json
jq -e '.content == "Hello team."' verified.json
```

A successful receipt contains `note`, `mode`, `baseRevision`, `hash`, and
`revision`. `baseRevision` is the snapshot you submitted; `revision` is the
acknowledged result. The quoted here-document passes patch text literally,
including `$`, backticks, backslashes, and Unicode.

## MERGE and EXACT

| Mode | Command | If someone edits after your read |
| --- | --- | --- |
| MERGE (default) | `patch --base-revision "$BASE"` | Applies to the original collaborative character identities |
| EXACT | `patch --base-revision "$BASE" --exact` | Rejects atomically if the original revision is no longer current |

For example, if a person prepends `Human: ` after you read `Hello world.`, the
patch above can merge to `Human: Hello team.`. The prefix has its own character
identities. EXACT instead rejects the intervening revision with exit `3` and
zero patch writes. MERGE preserves unrelated concurrent edits; it does not
promise that overlapping edits express either author's intended final sentence.

### Overlapping concurrent changes

The DreamLake server checks overlap in MERGE mode since `06fbbe65`, deployed to
production on 2026-10-27. No CLI update is needed. Earlier servers could keep two
replacements of the same word side by side (for example
`browser-overlapCLI-overlap`) with exit `0`.

MERGE refuses the whole patch with exit `3` (HTTP 412 `stale`,
message `merge refused: …`) and writes nothing when a change made after your
read overlaps any hunk. The check compares collaborative character identities,
not text, so an identical word elsewhere in the note never matches. A hunk
overlaps when, since your read:

- a character it replaces or deletes was changed, deleted or replaced, even by
  an identical replacement;
- new text appeared inside its span or directly at either edge, with no
  original character in between;
- the character directly before or after the span was deleted; or
- for a pure insertion, new text was inserted at the same position, or a
  neighbouring character was deleted.

Adjacent edits are treated as overlapping on purpose: replacing `shared` in
`shared baseline` still merges with a concurrent edit to `baseline`, because the
original space between them is unchanged, but not with text typed directly
against `shared`. Two concurrent appends at the end of a note also conflict.
Disjoint hunks continue to merge, and EXACT is unchanged.

The server checks and commits against the same revision, so a change that lands
in between is never written over: the server re-checks the same original intent
at most three times, then refuses with `merge refused: the note kept changing`.
On a refusal, keep your original baseline and draft, read the note, review the
concurrent change and reconcile. Never use `--force` or substitute a newer
baseline for the old patch.

Both modes validate against the retained original snapshot. Missing snapshots,
invalid ranges, and mismatched old text are errors. There is no fuzzy matching
against the latest source and no automatic baseline refresh.

`--if-match "$BASE"` is a compatibility alias for EXACT and can supply the
baseline by itself. If supplied with `--base-revision`, the values must agree.
EXACT never locks the note or changes later requests. V2 patches reject `--force`.

## Patch formats

Choose a format for each upload independently of the format used for reads.

### Inline character edits

The current format name is `inline-dff` (the default). Each hunk has a range
header and one physical `~ ` record:

```text
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
```

Plain text is unchanged; `[-…-]` deletes; `{+…+}` inserts. The old projection
must exactly match the specified source range. Offsets are zero-based,
end-exclusive **Unicode code points**, not UTF-8 bytes or JavaScript UTF-16
indices. All hunks address the same original source and must be ordered and
disjoint. A zero-length range inserts at that boundary.

Inside a record, encode newlines as `\n`, carriage returns as `\r`, tabs as `\t`,
and backslashes as `\\`. Escape literal delimiter characters with a backslash.
Unknown escapes, nested markers, overlaps, and malformed hunks are rejected.
Patch framing uses LF and is not appended to the note.

### Unified line diff

For editing in a local editor, save exact source, edit a copy, then generate a
diff. Start with an accessible `NOTE_ID`; keep both the baseline and draft.

```bash notes-example="unified-roundtrip"
set -euo pipefail
dreamlake notes read "$NOTE_ID" --json > line-baseline.json
BASE=$(jq -er .revision line-baseline.json)
jq -jr .content line-baseline.json > before.md
cp before.md after.md
# Edit after.md in your editor, then continue below.
diff_status=0
diff -u before.md after.md > draft.diff || diff_status=$?
# diff exits 1 when differences exist; values above 1 are errors.
test "$diff_status" -le 1
if [ "$diff_status" -eq 0 ]; then
  echo "No changes; no patch sent."
  exit 0
fi
dreamlake notes patch "$NOTE_ID" --format diff --base-revision "$BASE" \
  --file draft.diff --json > line-receipt.json
ACK=$(jq -er .revision line-receipt.json)
dreamlake notes read "$NOTE_ID" --if-match "$ACK" \
  --json > line-verified.json
```

Only a single-file unified patch is accepted. Preserve context, line counts,
CRLF, and `\ No newline at end of file` markers. File labels do not select the
note. If the files match, stop without sending a patch. Empty patch input is rejected.

## Preview and input

`--dry-run` prints the proposed request without submitting it. It does **not**
ask the server to validate the patch or prove that a later write will succeed.
Input can be a here-document, a pipe, `--file -`, `--file path`, or `--diff string`.
Choose one. Explicit file/string input conflicts with redirected stdin;
interactive stdin is refused. Patches are limited to 8,000,000 UTF-8 bytes.

## Handle a failure

| Exit | Meaning | Next action |
| --- | --- | --- |
| `1` | Invalid options, authentication, transport, missing baseline, or a proven unsubmitted patch | Read the diagnostic; retain your files |
| `3` | Stale EXACT/read precondition, invalid original identities, or a MERGE overlap refusal | Inspect current state and review the edit |
| `4` | RTC acknowledgment unavailable; outcome may be ambiguous | Read resulting state before deciding whether to resubmit |
| `5` | Patch rejected against its original snapshot | Correct the patch using that source |

A current API503 with `error: "rtc_unavailable"` and exactly
`mutation: {apiVersion: 1, started: false, phase: "baseline_read"}` proves that
the requested native edit did not start. The CLI reports **patch not submitted**,
exits1, and leaves the original baseline and draft intact. This does not prove
that other collaborators made no changes. An absent, malformed or unsupported
marker proves nothing: submission remains unknown and exit4 still applies. The
CLI never guesses from the error sentence or downgrades APIs to recover a write.

The CLI does not automatically retry an HTTP patch. Separate requests do not
share an idempotency receipt. If an acknowledgment is lost, keep the original
baseline and draft, inspect the note, and reconcile. Never attach a newer revision
to an old patch merely to make it pass. A later successful read does not by itself
prove whether an earlier ambiguous request committed.

Next: [Live collaboration](cli-notes-collaboration.md). For existing section/text
mutation scripts, see [Legacy commands](cli-notes-legacy.md).

## Native stdin and error diagnostics

Use `--file edit.dff` for a saved patch. Native CLI 0.33.0 can incorrectly read
`--file - < edit.dff` as empty input and receive a successful no-op receipt; this
is an input-transport defect, not a merge conflict. The fix is unreleased. Until
upgrading to a release containing it, pass the file path directly and inspect
`--dry-run --json` to verify `payload.patch` before submission.

The corrected native reader preserves redirected-file and pipe bytes, rejects
empty patch input before sending, and retains UTF-8 and 8 MB limits. Server error
details are printed alongside their error code. A 422 may indicate an alignment
limit as well as an invalid patch; it does not by itself prove a baseline mismatch.
Keep the baseline and draft on any failure. Default merge and opt-in exact mode
are unchanged. Verify the intended edits in the acknowledged `--at` snapshot.

## Literal text without inline-DFF escaping

To avoid hand-writing `\[`, `\-` and other inline-DFF escapes, prepare an edited
copy of the exact canonical baseline and generate a unified diff. Keep Unicode,
`$`, `<`, `&` and backslashes literal in those files. Do not copy generated
address hints into either file. Preserve the baseline's original revision and
line endings. This uses the existing source patch API, not a new semantic edit API.

```bash
# base.md is the exact canonical source read at BASE; edit only edited.md.
cp base.md edited.md
# Apply the intended edit to edited.md with your file-editing tool.
# diff exits 1 when it successfully finds differences; 2 means failure.
DIFF_STATUS=0
diff -u base.md edited.md > edit.diff || DIFF_STATUS=$?
if [ "$DIFF_STATUS" -gt 1 ]; then exit "$DIFF_STATUS"; fi
if [ "$DIFF_STATUS" -eq 1 ]; then
  dreamlake notes patch "$NOTE_ID" --format diff --file edit.diff --base-revision "$BASE"
fi
# Read the resulting receipt revision with --at to verify the exact source.
```

The patcher checks the old source against the retained baseline. Keep any
Markdown escapes needed in the actual saved source; the diff transport does not
require extra escaping of its line contents. Existing merge/exact semantics apply.

## Propose instead of write

To let the note's owner accept or reject each change rather than applying it
directly, render the edit as suggested edits with
[`notes suggest-diff --in-place`](cli-notes-suggest-diff.md#propose-edits-inside-an-existing-note)
and write that body instead.

## Append against the original snapshot (CLI 0.59.0+)

Original-revision append requires CLI 0.59.0 or later and the compatible Notes
v2 API. CLI 0.58.0 and earlier use the retained ETag/body replacement append.
The new append preserves collaborative source identities instead of replacing
the complete Note body. No legacy route is retired.

```bash cli-help="notes append"
dreamlake notes append "$NOTE_ID" --file addition.md --base-revision "$BASE" --json
# ACK is the revision in the successful append receipt.
dreamlake notes read "$NOTE_ID" --at "$ACK"
```

Without `--base-revision`, append reads one complete, hash-verified source
snapshot and submits an EOF insertion against that original revision. With an
original saved revision, it reads that retained snapshot using `at`; it never
swaps a rejected baseline for the latest token. Merge is the default and retains
unrelated concurrent edits. Use `--exact` when the original revision must still
be current. Overlapping identity changes or unavailable original snapshots can
reject; preserve the original baseline and addition for review.

`--text`, `--file`, `--file -`, and piped stdin retain literal text, Unicode and
line endings. When the nonempty original source lacks a final LF, append inserts
one LF before the addition, including an empty addition. Otherwise it inserts
exactly the addition. A genuinely empty insertion performs no write and JSON
reports `noChange: true` with the observed snapshot revision; it does not claim a
new acknowledgment. The EOF offset counts Unicode code points, and patch syntax
characters and source controls are escaped before transport.

Human `--dry-run` keeps the composed original source plus addition on stdout,
with the PATCH/base revision/mode on stderr. This preview is based on the
original source, not the future merged document. JSON dry-run describes the
actual PATCH payload. Successful writes print Notes v2 `note`, `hash`, `revision`,
`mode`, and `baseRevision`; use that acknowledged revision for pinned readback.
A failed or malformed acknowledgment can leave the outcome unknown. No retry
is automatic: inspect the Note before resubmitting, keeping the original draft.

Explicit `--legacy` retains the prior ETag-guarded body replacement append.
Existing `--force` retains its prior unguarded legacy behavior; it never selects
a forced v2 write. Neither compatibility choice can combine with
`--base-revision` or `--exact`. Avoid forced replacement for collaborative work.

## Insert at an original-source position (CLI 0.60.0+)

Original-revision insertion requires CLI 0.60.0 or later and the compatible Notes
v2 API, reusing the CLI 0.59.0 append snapshot/PATCH helpers. CLI 0.59.0 and earlier
use retained ETag/body replacement insertion. No legacy command or route is retired.

```bash cli-help="notes insert"
dreamlake notes insert --note "$NOTE_ID" --ind 0 --text 'Review: ' \
  --base-revision "$BASE" --json
# ACK is the revision returned by the insertion receipt.
dreamlake notes read "$NOTE_ID" --at "$ACK"
```

Insertion reads one hash-verified original snapshot, resolves the
requested position in that source, and submits one escaped literal insertion.
A supplied `--base-revision` pins the retained snapshot; rejected original tokens
are never replaced with the latest revision. Default merge preserves unrelated
concurrent edits; `--exact` requires that original revision to remain current.
Overlapping identity changes may reject and require review of the original draft.

Choose exactly one location:

- `--ind N` addresses a Unicode code-point boundary from `0` through source length,
  including both ends. Text is inserted literally, with no added newline.
- `--line N` inserts before a 1-based source line, or at EOF for one past the final
  line. The line algorithm preserves the source newline style and terminates the
  addition unless it already ends in LF. At EOF after a source with no final LF/CR,
  it also inserts the source-style newline before the addition. A final LF already
  creates an empty last line; that line and one past it both resolve to EOF.
- `--selector CSS` must match exactly one original-source HTML element. `--position`
  defaults to `append`; `before`/`after` use the outer boundaries, while
  `prepend`/`append` use the inner boundaries. Text is literal markup and gets no
  added newline. Void elements reject inner insertion; use before/after instead.

Human `--dry-run` prints the composed original source exactly, without a trailing
newline added for display. JSON previews the actual PATCH and composed `text`;
this is not a prediction of the future merged source. Empty literal insertion
sends no write and reports `noChange: true` for the observed snapshot. Empty
line-oriented insertion still follows the newline rules and can create a line.
Success returns the acknowledged v2 revision. Pin readback with `--at`; failed,
malformed, redirected or lost acknowledgments are never automatically replayed.
Keep the original baseline and text and reconcile the Note before resubmitting.

Explicit `--legacy`, existing `--force`, or existing `--if-match <etag>` select the
retained replacement path. Preserve a content ETag for that path, never an RTC
revision. These compatibility flags cannot combine with `--base-revision` or
`--exact`. Section mutation keeps its existing contract. Replacement and deletion
use the original-revision contracts below in CLI 0.60.0 or later.

## Replace and delete original-source spans (CLI 0.60.0+)

Original-revision replacement and deletion require CLI 0.60.0 or later and the
compatible Notes v2 API. CLI 0.59.0 and earlier use retained ETag/body replacement
for these editors. The original-revision editors submit precise code-point spans
through the v2 snapshot/PATCH API. Multiple matches become separate hunks in one PATCH
against one original revision, leaving the source between targets untouched.

```bash
dreamlake notes replace 'Draft' --text 'Reviewed' --all --note "$NOTE_ID" \
  --base-revision "$BASE" --json
```

```bash cli-help="notes delete"
dreamlake notes delete 'obsolete paragraph' --note "$NOTE_ID" \
  --base-revision "$BASE" --json
# Pin verification to the receipt's acknowledged revision.
dreamlake notes read "$NOTE_ID" --at "$ACK"
```

Literal queries require one match by default; `--count N` requires exactly N
matches, and `--all` selects every match. Query/regex, inclusive 1-based line
ranges, and end-exclusive Unicode code-point ranges preserve their existing
rules. Plain-source regex replacement expands JavaScript replacement tokens
against each original match, including numbered/named captures, `$&`, and `$$`.
Line replacement preserves source newline style. No match, ambiguous cardinality,
invalid targeting or range errors remain nonmutating refusals (normally exit 6).

With `--selector`, exactly one source element is selected and matching stays
within its individual decoded text pieces. Matches cannot bridge intervening
markup. Each decoded match maps back to its original raw entity/source span;
replacement `--text` escapes ampersands and angle brackets for markup. As in the
retained selector implementation, replacement text is literal after that
escaping: selector regex replacement does not expand `$1` or named backreferences.
`--html` instead replaces the selected element's inner source with literal markup
and cannot combine with a query/regex or `--text`.

Default merge uses the original snapshot identities. A supplied `--base-revision`
pins the retained original source; `--exact` requires it to remain current. A
rejected baseline is never silently swapped for the latest one. Unrelated
concurrent edits outside the targeted spans can be preserved, including edits
between disjoint matches in the same paragraph. Overlapping edits can reject;
keep the original baseline and draft for review.

Human dry-run prints the composed original source exactly; JSON carries that
`text` and the actual multi-hunk PATCH. Equal old/new spans are omitted to preserve
unchanged identities; an entirely unchanged plan sends no write and reports
`noChange: true` for the observed snapshot. Successful writes return the v2
acknowledged revision for `read --at`. Lost/malformed acknowledgments are never
replayed automatically; reconcile before resubmitting.

Explicit `--legacy`, existing `--force`, or existing `--if-match <etag>` retain
legacy replacement and failure semantics. They cannot combine with
`--base-revision` or `--exact`. These changes do not migrate section editors or
retire legacy endpoints.

The original-revision migrations of section write, `add-section`, and
`rm-section` remain unshipped. Their existing ETag-based interfaces remain
available. Runbook attachment is separate proposed work and is not included
in CLI 0.61.0; no legacy Note route or compatibility option is retired.

## Write a target body against its original source (CLI 0.61.0+)

Original-revision whole-body `write` requires CLI 0.61.0 or later and the
compatible Notes v2 API. CLI 0.60.0 and earlier keep whole-body write on the
retained ETag interface. Modern write derives bounded, exact code-point changes between an original source snapshot and your target
body, retaining unchanged source islands even inside one paragraph. It emits
ordered disjoint hunks in one v2 PATCH, rather than replacing the complete body.

```bash cli-help="notes write"
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > draft.md
# Edit draft.md without changing the saved original baseline.
dreamlake notes write "$NOTE_ID" --file draft.md --base-revision "$BASE" --json
# ACK is the successful write receipt's revision.
dreamlake notes read "$NOTE_ID" --at "$ACK"
```

A target prepared from an older source must retain that source's original
`--base-revision`. Without one, write reads one current hash-verified snapshot
and protects the subsequent request window; that cannot prove which source an
older local file came from. A supplied baseline pins the retained source with
`at`; rejected tokens are never silently exchanged for the latest revision.
Default merge preserves unrelated concurrent changes outside the planned spans;
`--exact` requires the original revision to remain current. Concurrent edits
that overlap those spans can reject and need review of the original draft.

`--text`, `--file`, `--file -`, and piped stdin preserve literal Unicode and line
endings. Modern file/stdin bytes must be valid UTF-8; malformed input rejects before
transport, preserving the existing legacy decoding separately. File and text
flags remain mutually exclusive. An empty target is an
intentional deletion of the original source, not a missing-patch no-op. An
unchanged target in merge mode sends no write and reports `noChange: true` for
the observed snapshot. With `--exact`, an unchanged target sends an empty PATCH
so the server still validates the original revision; a stale exact request
rejects even when no source characters would change. Human dry-run keeps the target body on stdout (adding a final display
LF only when absent); JSON includes the target `text` and actual PATCH. Neither
preview predicts the future merged source. Text that resembles a unified diff
still warns on stderr and is treated as a literal target body.

Alignment is exact and bounded: source and target are limited to 1,000,000 code
points each; generated patches to 8,000,000 UTF-8 bytes and 10,000 edits; alignment
work to 4,000,000 cells and retained trace storage to 250,000 units. Sparse changes
and supported dense changes preserve unchanged identities. Exceeding a limit
fails before submission (exit 5); it never falls back to a coarse rewrite.
Invalid unpaired Unicode surrogates also reject. Lost/malformed acknowledgments
are never replayed automatically; keep the original baseline and target and
reconcile the Note before resubmitting. Verify the acknowledged revision with
`read --at` after a successful write.

Explicit `--legacy`, existing `--force`, or existing `--if-match <etag>` retain
the prior whole-body replacement path. `--section` explicitly selects its
retained section-write API; section migration remains unshipped. These choices
cannot combine with `--base-revision` or `--exact`. `add-section` and `rm-section`
keep their existing contracts; no legacy route or compatibility option is retired.
