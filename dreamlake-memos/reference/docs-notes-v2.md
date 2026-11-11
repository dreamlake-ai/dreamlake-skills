<!-- generated from https://docs.dreamlake.ai/notes/v2.md at 0.1.155 3f4728cb; do not edit -->

# Memos v2: merge and exact patches

Released September 24, 2026 with CLI 0.26.2, Python SDK 0.20.0 and the Memos API
backed by RTC server 0.5.1. The API retains native baselines and the authority
supplies unlocked baseline observations. Upgrade older clients before using
these examples. Deployment evidence and manual acceptance are tracked in
[the Memos master plan](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).

A v2 source read returns `note`, `hash`, `revision` and `content`. `hash` is
`sha256:` plus the exact UTF-8 source digest. `revision` is an opaque RTC write
baseline; equal text does not imply an equal revision. Keep the original source
and token together until the edit is verified. Never fetch a fresh token merely
to make an old patch pass.

```bash
set -euo pipefail
NOTE_ID=design-doc
dl memos read "$NOTE_ID" --json > baseline.json
BASE_HASH=$(jq -er '.hash' baseline.json)
BASE=$(jq -er '.revision' baseline.json)
jq -jr '.content' baseline.json > base.md

dl memos read "$NOTE_ID" --since "$BASE_HASH" --format inline-dff
dl memos read "$NOTE_ID" --since "$BASE_HASH" --format diff

# Example requires saved source exactly Hello world. without a final newline.
dl memos patch "$NOTE_ID" --format inline-dff --base-revision "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH

REVISION=$(jq -er '.revision' committed.json)
dl memos read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
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

## Keep incremental reads compact

For an agent following a memo, reuse the saved full `read --json` baseline;
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

### Verify edits without rereading the whole memo

After a successful v2 patch, verify the acknowledged revision with a delta from
your saved baseline. This uses the existing `baseline.json` from the pre-edit
read and `receipt.json` from the successful patch; `NOTE_ID` is the same memo
used for both operations, as set in [Name a memo](docs-notes-cli-editing.md#name-a-note).

```bash
BASE_HASH=$(jq -er .hash baseline.json)
ACK_REVISION=$(jq -er .revision receipt.json)
dl memos read "$NOTE_ID" --since "$BASE_HASH" \
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
recovery checks. They are not a requirement to reread the entire memo after
every targeted edit.

## Reproduce a concurrent merge and an exact conflict

Use a new private fixture with the compatible releases, an authenticated CLI,
`jq`, and Python `dreamlake` configured for the same account/namespace. These
examples deliberately issue an exact request first, inspect its rejection, and
then make a separate, explicit merge request. There is no automatic downgrade.

**CLI**

```bash
set -euo pipefail
dl memos create "Merge/exact example" --text 'Hello world.' --json > fixture.json
NOTE_ID=$(jq -er '.id' fixture.json)
dl memos read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er '.revision' baseline.json)
jq -jr '.content' baseline.json > original.md
cat > agent.patch <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH

# Simulate a second participant inserting a prefix after the agent's read.
dl memos patch "$NOTE_ID" --base-revision "$BASE" --json > human.json <<'PATCH'
@@ chars 0:0 @@
~ {+Human: +}
PATCH

# Expected conflict: stdout stays empty; stderr explains the failure; exit is 3.
set +e
dl memos patch "$NOTE_ID" --base-revision "$BASE" --exact \
  --file agent.patch --json > exact.stdout 2> exact.stderr
STATUS=$?
set -e
test "$STATUS" -eq 3
test ! -s exact.stdout
cat exact.stderr

# A separate explicit choice to merge the ORIGINAL patch and identities.
dl memos patch "$NOTE_ID" --base-revision "$BASE" \
  --file agent.patch --json > merged.json
jq '{note, mode, baseRevision, hash, revision}' merged.json
dl memos read "$NOTE_ID" --json > observed.json
jq -er '.content == "Human: Hello team."' observed.json
```

**Python**

```python
import json
import os
from pathlib import Path
import dreamlake as dl
from dreamlake import NoteChanged

note = dl.create_memo(os.environ["NAMESPACE"], "Merge/exact example",
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

## Complete an exact edit and return to merge mode

Continue with the fixture above, now containing `Human: Hello team.`. Read a
fresh baseline before making this new edit. Exact mode applies only to its
individual request; the following empty patch uses the default merge mode.

**CLI**

```bash
dl memos read "$NOTE_ID" --json > exact-baseline.json
EXACT_BASE=$(jq -er '.revision' exact-baseline.json)
cat > exact.patch <<'PATCH'
@@ chars 18:18 @@
~ {+!+}
PATCH
dl memos patch "$NOTE_ID" --base-revision "$EXACT_BASE" --exact \
  --file exact.patch --json > exact-success.json
jq '{note, mode, baseRevision, hash, revision}' exact-success.json

dl memos read "$NOTE_ID" --json > after-exact.json
NEXT_BASE=$(jq -er '.revision' after-exact.json)
printf '' | dl memos patch "$NOTE_ID" --base-revision "$NEXT_BASE" \
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
