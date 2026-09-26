# Reading and changes

Set `NOTE_ID` to an ID or slug from `dreamlake notes list`. Add `--namespace`
when the note belongs to an organization. The shell examples use `jq`.

## Save a snapshot

```bash
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
REVISION=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md
```

`base.md` is exact source, including its final-newline state. Plain `read > file`
also saves metadata and is **not** a source-only export.

| Field | Use it for |
| --- | --- |
| `note` | The resolved note ID |
| `content` | Complete canonical source |
| `hash` | Content identity, `sha256:<hex>`; pass to `--since` |
| `revision` | Opaque write baseline; pass unchanged to `--base-revision` |

A hash describes text. A revision also identifies collaborative state. Identical
text can have different revisions; do not substitute one token for the other.

## Read only what changed

```bash cli-help="notes diff"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
dreamlake notes diff "$NOTE_ID" --since "$HASH" --format diff
```

`notes diff` is an alias for `notes read --since`. Both accept either format:

```bash
dreamlake notes read "$NOTE_ID" --since "$HASH" --format inline-dff
dreamlake notes read "$NOTE_ID" --since "$HASH" --format diff --json > changes.json
jq -jr .patch changes.json > changes.diff
```

`inline-dff` is the current spelling and the default for one-shot incremental
reads. It shows character edits. `diff` shows a unified line diff, normally with
three context lines around changes. Nearby edits share a hunk; distant edits
remain separate. Older servers may generate broader hunks.

Incremental JSON carries `note`, `base`, `hash`, `revision`, `format`, and `patch`.
`base` identifies the source the patch applies to; `hash` and `revision` identify
the resulting snapshot. Text output includes that metadata and the offset unit
before the patch. Extract `.patch` when a consumer needs only patch text.

No text changes means an empty patch, possibly with a newer revision. Apply an
incremental patch only to source matching `base`, then verify the resulting hash.
Inspecting changes does not edit the note or advance an existing draft's original
baseline. Preserve `baseline.json` and `base.md` until that edit is resolved.

Retained time references also work:

```bash
dreamlake notes read "$NOTE_ID" --since "2 hours ago"
```

The server resolves times and retention. Prefer a saved hash for “since my last
read.” There is no hidden last-read state. Unknown or expired references fail;
the CLI does not silently replace them with the latest revision.

## Read one section

```bash cli-help="notes sections"
dreamlake notes sections release-plan
dreamlake notes sections release-plan --json
```

Use the returned heading anchor to read a passage. Partial reads currently use
the explicit compatibility interface:

```bash
dreamlake notes read "$NOTE_ID" --legacy --section outline --numbered
dreamlake notes read "$NOTE_ID" --legacy --start-line 40 --end-line 80
```

Sections include their heading and all subsections, ending at the next heading
of the same or higher level. Duplicate headings receive suffixed anchors;
`preamble` addresses text before the first heading. Lines are 1-based and inclusive.
A partial read is not a complete patch baseline: its validator covers the whole
note, while its source is only a slice. Never upload that slice as the whole body.

## Search passages

```bash
dreamlake notes find "Draft" --note "$NOTE_ID" --json
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive
dreamlake notes grep "deploy" --glob 'spec-*' --limit 20
dreamlake notes toc --note "$NOTE_ID"
```

`search` finds notes; `find` searches one note; `grep` returns locations across
notes as `slug:line:column`. Literal queries are case-insensitive by default;
regex queries are case-sensitive by default. JSON hits include the legacy ETag
and character range. Use the [legacy editing interface](/notes/legacy/) with
those validators, or capture a full current snapshot for a v2 patch.

## Verify a particular revision

```bash
# REVISION came from a read or a successful patch receipt.
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
```

A matching read returns that snapshot. A mismatch exits `3` with no source on
stdout. After a successful patch, a later read conflict means someone changed
the note again; it does not mean your acknowledged patch failed. Inspect a fresh
read and reconcile before making another edit.

Next: [Editing with patches](/notes/editing/) or
[Live collaboration](/notes/collaboration/).
