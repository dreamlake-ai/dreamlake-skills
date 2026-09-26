# Editing with patches

A patch describes changes to the source you read. Save that source and its
revision, submit the patch against that original revision, then verify the
acknowledgment. **MERGE is the default; EXACT is an option for one request.**

## Try a complete edit

This creates a new private test note. It requires login, write access, and `jq`.
The initial source is exactly `Hello world.` without a trailing newline.

```bash cli-help="notes patch" notes-example="inline-roundtrip"
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
status=0
diff -u before.md after.md > draft.diff || status=$?
# diff exits 1 when differences exist; values above 1 are errors.
test "$status" -le 1
dreamlake notes patch "$NOTE_ID" --format diff --base-revision "$BASE" \
  --file draft.diff --json > line-receipt.json
ACK=$(jq -er .revision line-receipt.json)
dreamlake notes read "$NOTE_ID" --if-match "$ACK" \
  --json > line-verified.json
```

Only a single-file unified patch is accepted. Preserve context, line counts,
CRLF, and `\ No newline at end of file` markers. File labels do not select the
note. An empty patch is a no-op, not a deletion of the document.

## Preview and input

`--dry-run` prints the proposed request without submitting it. It does **not**
ask the server to validate the patch or prove that a later write will succeed.
Input can be a here-document, a pipe, `--file -`, `--file path`, or `--diff string`.
Choose one. Explicit file/string input conflicts with redirected stdin;
interactive stdin is refused. Patches are limited to 8,000,000 UTF-8 bytes.

## Handle a failure

| Exit | Meaning | Next action |
| --- | --- | --- |
| `1` | Invalid options, authentication, transport, or missing baseline | Read the diagnostic; retain your files |
| `3` | Stale EXACT/read precondition or invalid original identities | Inspect current state and review the edit |
| `4` | RTC acknowledgment unavailable; outcome may be ambiguous | Read resulting state before deciding whether to resubmit |
| `5` | Patch rejected against its original snapshot | Correct the patch using that source |

The CLI does not automatically retry an HTTP patch. Separate requests do not
share an idempotency receipt. If an acknowledgment is lost, keep the original
baseline and draft, inspect the note, and reconcile. Never attach a newer revision
to an old patch merely to make it pass. A later successful read does not by itself
prove whether an earlier ambiguous request committed.

Next: [Live collaboration](/notes/collaboration/). For existing section/text
mutation scripts, see [Legacy commands](/notes/legacy/).
