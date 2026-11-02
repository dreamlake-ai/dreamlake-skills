<!-- generated from https://docs.dreamlake.ai/notes/history.md at 0.1.110 aae4ca5d; do not edit -->

# History and saved versions

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

### Saving safely across a connection failure

A failed or lost save response does not prove that a version was not saved.
Refresh History and inspect its ID, author, time and content before saving again.
An acknowledged edit to the live draft is separate from saving a named version;
do not resend that edit to recover a failed version save.

**Catalog readers and the default catalog writer are included in the verified API release.**
Strict runtime verification and read-only version metadata/header checks are
separate from accepting a real version save; no production save was performed
for this release verification. Existing saves without an idempotency header and
existing version links retain their current workflow.

The serving implementation routes new saves
through the publication catalog by default, without changing the save endpoint,
request fields, CLI commands or existing version IDs and history. It rechecks
current edit authority and the Note's ownership binding before publication.
Runtime verification is not a live-save receipt and does not activate durable attachment purge
or ownership transfer.

Do not use a version-save POST to test readiness. An older API may ignore
`Idempotency-Key` and create an ordinary version. Only a **verified catalog-reader
release with its writer still disabled** returns
`503 version_publication_unavailable` without saving for a keyed request. Do not
adopt the header for saving or retries until the matching writer release is
separately verified; a successful POST alone proves neither support nor
idempotency.

On the verified catalog-writer release, API clients may supply a unique
`Idempotency-Key` (16–128 letters, digits, underscores or hyphens) on
`POST /namespaces/:slug/notes/:noteId/versions`. Keep that key with the original
hash, tag, summary, parent and optional retained revision. Retry against the same
server and Note while signed in as the same account; keys are scoped to that
Note and actor. Another editor must inspect history and must not reuse your key
expecting deduplication. An identical retry
reconciles the original save rather than saving the current draft again; changed
input with the same key is rejected. Only currently authorized editors can
reconcile the save. If the original upload was incomplete and its publication is
aborted, inspect history and deliberately start a new save with a new key. The
server never substitutes newer text for an unavailable original snapshot.

`503 version_save_unconfirmed` also covers transport or database failures while
reconciling a keyed save. On the verified catalog-writer release, retry only the identical original request with the same key, server, Note and
account; do not generate a new key or resend the body edit to clear the error.
A published or fully staged matching operation returns its original version.
`409 RECOVERY_IN_PROGRESS` means another executor is still active;
`409 IDEMPOTENCY_CONFLICT` means the key was reused with different input.
`409 PUBLICATION_ABORTED` requires inspecting history before an intentional new
save with a new key. A storage mismatch or network failure does not prove that
nothing was saved. Without an original idempotency key, inspect history before
considering another save; the CLI commands below do not add a key automatically.

This does not enable cross-namespace transfers or change who can read history.

### Use the CLI for saved versions

CLI **0.44.1+** supports current-draft checkpoints, version lists, and saved
text reads. Check the installed `dreamlake note tag --help`, `note hist --help`,
and `note read --help` first. `note` and `notes` are aliases; the older
`notes version` group was removed in 0.44.2.

```bash
# Keep the same explicit namespace on every command.
dreamlake note tag "$NOTE_ID" reviewed --namespace "$NOTE_NAMESPACE" --summary "Reviewed draft"
dreamlake note hist "$NOTE_ID" --namespace "$NOTE_NAMESPACE" --json
dreamlake note read "$NOTE_ID" --namespace "$NOTE_NAMESPACE" --version "$VERSION_ID" --json
```

`hist` lists saved checkpoints, not every autosaved edit. JSON is appropriate
here for parsing IDs, hashes and cursors. Save and read by immutable version ID;
tags can repeat. The CLI does not yet promote a retained `revision` to a saved
version or read its checkpoint/journal. Use the authenticated API below for
that specific gap, rather than inventing a `tag --revision` option.

### Recover a retained snapshot

Use this workflow when an earlier full draft still has a retained revision but
was never saved as a named version. It creates a version **on the same Note**;
it does not restore the old text into the live draft. An empty version list does
not prove old content is gone. Identify the exact note ID and namespace, locate
a known retained revision from earlier read receipts or recovery evidence, and
review its full source before saving. Do not guess revisions from content hashes.
Without a retained baseline, this endpoint cannot recover compacted edits,
deleted Notes, a different Note's history, or text available only in a screenshot.
Preserve any independent backup and report that limitation.

First establish a stable agent identity as described in [agent presence](docs-notes-agent-presence.md),
and reuse it for every live CLI read. Confirm that the selected API deployment
supports historical `POST /versions` (the October 8, 2026 retained-revision
extension). Older servers can silently discard an unknown `revision` property.
Even HTTP 201 and matching text are insufficient: the saved revision and
`sourceObservedAt` must also pass readback verification.

Use the same authenticated remote and token for both CLI and REST. In the
following example, provision `DREAMLAKE_API_KEY` through your normal secret
mechanism; do not paste it into notes, shell history, or receipts. Explicitly set
`DREAMLAKE_REMOTE` to the intended HTTPS API, `NOTE_NAMESPACE`, the stable
`NOTE_ID`, and `OLD_REVISION`. Preserve `DREAMLAKE_AGENT_ID` and
`DREAMLAKE_AGENT_NAME` from identity setup. Review the pinned source first:

```bash
# These variables must already identify the intended account, Note and baseline.
dreamlake note read "$NOTE_ID" --namespace "$NOTE_NAMESPACE" \
  --view source --at "$OLD_REVISION"
```

The executable example below uses Python's standard library for the missing
REST operation and the CLI for full source reads. Run it from a private working
directory after reviewing the old draft. It creates `recovery-evidence` with
owner-only permissions and refuses to overwrite an earlier attempt. It sends
**one** POST, retains the request and response, and verifies by the returned ID.
Do not remove that directory to work around an uncertain outcome.

```python
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

required = ("DREAMLAKE_REMOTE", "DREAMLAKE_API_KEY", "NOTE_NAMESPACE",
            "NOTE_ID", "OLD_REVISION", "DREAMLAKE_AGENT_ID", "DREAMLAKE_AGENT_NAME")
for key in required:
    if not os.environ.get(key):
        raise SystemExit(f"Set {key} before running recovery")
remote = os.environ["DREAMLAKE_REMOTE"].rstrip("/")
if urllib.parse.urlsplit(remote).scheme != "https":
    raise SystemExit("Use the intended HTTPS API")
ns, note, revision = (os.environ[k] for k in ("NOTE_NAMESPACE", "NOTE_ID", "OLD_REVISION"))
if not re.fullmatch(r"[a-f0-9]{24}", note):
    raise SystemExit("Use the resolved stable Note ID")
os.umask(0o077)
evidence = Path("recovery-evidence")
evidence.mkdir(mode=0o700)  # Existing evidence stops a second submission.
def keep(name, value):
    with (evidence / name).open("x", encoding="utf-8") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
def read_source(name, *extra):
    raw = subprocess.check_output([
        "dreamlake", "note", "read", note, "--namespace", ns,
        "--view", "source", "--json", *extra], text=True)
    value = json.loads(raw)
    keep(name, value)
    assert value["note"] == note and isinstance(value["content"], str)
    digest = hashlib.sha256(value["content"].encode("utf-8")).hexdigest()
    assert value["hash"] == "sha256:" + digest
    return value
old = read_source("retained.json", "--at", revision)
assert old["revision"] == revision
before = read_source("live-before.json")
payload = {"revision": revision, "hash": old["hash"][7:],
           "tag": "Recovered retained draft", "summary": "Reviewed historical source"}
# Set reviewed tag/summary above; add parentId only for intentional ancestry.
keep("request.json", {"remote": remote, "namespace": ns, "note": note,
                     "startedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                     "payload": payload})
base = remote + "/namespaces/" + urllib.parse.quote(ns, safe="") + "/notes/" + note
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(NoRedirect)
def api(path, body=None):
    request = urllib.request.Request(base + path,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + os.environ["DREAMLAKE_API_KEY"],
                 "Content-Type": "application/json"},
        method="GET" if body is None else "POST")
    with opener.open(request, timeout=30) as response:
        return response.status, json.load(response)
try:
    status, saved = api("/versions", payload)
except urllib.error.HTTPError as error:
    keep("post-error.json", {"status": error.code,
                            "body": error.read().decode("utf-8", errors="replace")})
    raise SystemExit("Stopped: inspect post-error.json and the outcome rules below")
except (urllib.error.URLError, TimeoutError, OSError, ValueError):
    raise SystemExit("Outcome unknown: reconcile history before another POST")
keep("post-response.json", {"status": status, "version": saved})
assert status == 201
version_id = saved["id"]
assert re.fullmatch(r"v_[0-9]{13}_[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", version_id)
def verify_metadata(value):
    assert value["id"] == version_id
    assert value["revision"] == revision and value["hash"] == payload["hash"]
    assert value["tag"] == payload["tag"] and value["summary"] == payload["summary"]
    assert value.get("parentId") == payload.get("parentId")
    observed = dt.datetime.fromisoformat(value["sourceObservedAt"].replace("Z", "+00:00"))
    assert observed.tzinfo is not None
verify_metadata(saved)
verified = json.loads(subprocess.check_output([
    "dreamlake", "note", "read", note, "--namespace", ns,
    "--version", version_id, "--json"], text=True))
keep("verified-version.json", verified)
verify_metadata(verified)
assert verified["sourceObservedAt"] == saved["sourceObservedAt"]
assert verified["text"] == old["content"]
assert hashlib.sha256(verified["text"].encode("utf-8")).hexdigest() == payload["hash"]
after = read_source("live-after.json")
assert before["content"] == after["content"], "Live text changed; inspect concurrent edits"
print("Verified historical version:", version_id)
```

Hash the JSON-decoded **complete** `content` as UTF-8, preserving Unicode,
trailing newlines, and the empty string. Do not hash a section, annotated
Markdown, HTML, terminal metadata, or text modified by trimming or `jq -r`.
The source read uses `sha256:<digest>`; the API requires the raw lowercase
64-character digest. The opaque revision identifies the RTC baseline, not just
its text: two different revisions can have the same hash. `sourceObservedAt`
is the baseline's observation time, not necessarily the original edit time;
`createdAt` is when this version was saved. Full source reads need not contain
`sourceObservedAt`.

If a receipt/readback is missing, malformed, or has the wrong ID, revision,
hash, source time, or text, stop and keep the evidence. Do not declare recovery
complete, remove `revision`, fall back to saving the live draft, or issue another
POST to test support. If the live text changed during verification, inspect
concurrent edits without overwriting them. Saving a historical version itself
does not write the live body.

### Reconcile an uncertain save

A save without an idempotency key creates a distinct version; tags are **not
idempotency keys**. On the verified catalog-writer release, an exact
same-key retry may instead reconcile the original version as described above.
A timeout, lost connection, unreadable response, generic 5xx, or failure
after submission may leave a saved version behind. Do not blindly repeat the
POST, including after a failed verification read.

Inspect saved metadata on the **same remote, namespace and Note**, starting
with the first page and continuing through `nextCursor` using `--before`:

```bash
dreamlake note hist "$NOTE_ID" --namespace "$NOTE_NAMESPACE" --json
# Repeat for each non-null nextCursor until the attempt's time range is covered.
dreamlake note hist "$NOTE_ID" --namespace "$NOTE_NAMESPACE" --before "$NEXT_CURSOR" --json
# Read each plausible candidate by immutable ID.
dreamlake note read "$NOTE_ID" --namespace "$NOTE_NAMESPACE" --version "$CANDIDATE_ID" --json
```

Each page has at most 50 entries. Compare candidates with the retained request:
revision **and** hash, tag, summary, explicit parent (or null), and submission
time range. Then verify the candidate ID, `sourceObservedAt`, and full `text`
against the saved evidence as above. A matching hash with a different revision
is not a match. If a matching version exists, reuse its ID; if several match,
record their IDs and report that the individual request's attribution is
uncertain. Do not create a duplicate to obtain a clearer receipt or delete
versions automatically. Finding no match on a partial page, or immediately
after a timeout, does not prove that the original save failed. Continue read-only
reconciliation; retry only after the outcome is resolved and a new save is an
intentional decision. This unkeyed workflow has no request deduplication guarantee.

For a structured rejection from the compatible server:

- `409 note_changed`: no version was saved by that rejected request. Recheck
  the retained source/revision/hash; never replace its hash with the live hash.
- `404 revision_not_found`: the selected baseline is unavailable. Preserve
  independent evidence; this is not an empty saved-version list.
- `400`, authentication/access failures, or `404 parent_not_found`: correct the
  target, access or request before proceeding. History still requires editor access.
- The historical route's structured `503 history_unavailable` or
  `503 invalid_baseline` is a baseline-read failure **before** saving. Resolve
  that specific read problem first. A generic 503/5xx is still an unknown outcome;
  do not infer this pre-save guarantee from HTTP status alone.

This workflow does not archive every future edit, reconstruct already compacted
history, or add a rollback UI. Restoring text into the working draft is a separate,
explicitly requested edit with its own reviewed current baseline.

### Version API

These authenticated endpoints are scoped to `/namespaces/:slug/notes/:noteId`:

**Historical recovery:** `POST /versions` also accepts an optional
`revision` copied from a retained full source read. With it, the server saves
that note's immutable retained baseline instead of reading the live draft.
`hash` must match the retained source; a mismatch returns `409 note_changed`,
and an unavailable revision returns `404 revision_not_found`. This does not
replace the live body, change its collaboration session, or restore deleted
notes. Editor access is still required. A recovered version's `createdAt`
records when it was saved; `sourceObservedAt` records the baseline observation.
Omit `revision` to retain the existing current-draft consistency check. Do not
retry a failed stale-current save as a historical save without reviewing the
intended retained content. The CLI does not yet expose this extension.

- `POST /versions` accepts `{hash, revision?, tag?, summary?, parentId?}`. `hash` is the lowercase
  SHA-256 of the UTF-8 body the user intends to save. The server compares it
  with the specified retained baseline, or a coherent current read when
  `revision` is omitted, and returns `409 note_changed` on mismatch.
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
not a content write. Use `note tag`, `note hist`, and `note read --version`
for ordinary saved-version work. Retained-revision promotion and checkpoint/journal
reads currently require authenticated REST; the Python SDK has no saved-version helpers.
