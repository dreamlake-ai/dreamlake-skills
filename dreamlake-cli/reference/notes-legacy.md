# Legacy commands

These commands remain available for existing scripts and targeted section/text
operations. Their ETag checks differ from the current
[original-snapshot patch workflow](/notes/editing/). Use this page when you need
`write`, `append`, `replace`, section mutation, or body-only reads.

## Read and replace a body

```bash cli-help="notes write"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --legacy --json > legacy-baseline.json
ETAG=$(jq -er .etag legacy-baseline.json)
jq -jr .text legacy-baseline.json > note.md
# Edit note.md, then preview and submit against the saved ETag.
dreamlake notes write "$NOTE_ID" --file note.md --if-match "$ETAG" --dry-run
dreamlake notes write "$NOTE_ID" --file note.md --if-match "$ETAG" --json > legacy-receipt.json
ACK=$(jq -er .etag legacy-receipt.json)
dreamlake notes read "$NOTE_ID" --legacy --if-match "$ACK" --json
```

Legacy JSON uses `text` and `etag`, not v2 `content` and `revision`. Keep the ETag
exactly as returned, including quotes. Without an explicit `--if-match`, these
mutations normally fetch a current ETag just before writing. That protects the
request race, **not** the time spent editing an older local file. Always retain
the ETag from the read that produced your draft.

`--force` bypasses that check on supported legacy mutations. It can overwrite
concurrent work; it is not a conflict-recovery recipe. V2 `patch` rejects it.

## Sections and appending

```bash
# install.md must include the section heading.
dreamlake notes write "$NOTE_ID" --section install --file install.md --if-match "$ETAG"
```

A section includes its heading and descendants. Replacing it without its heading
removes that section boundary. Refresh your baseline for each separate edit;
the following are independent command forms, not a sequence sharing one ETag:

```bash
dreamlake notes append "$NOTE_ID" --text $'\n## Changelog\n- Shipped\n' --if-match "$ETAG"
dreamlake notes insert "$NOTE_ID" --after install --file troubleshooting.md --if-match "$ETAG"
dreamlake notes insert "$NOTE_ID" --before install --file prerequisites.md --if-match "$ETAG"
dreamlake notes rm-section "$NOTE_ID" troubleshooting --if-match "$ETAG"
```

`--after` inserts after the section and its subsections. `rm-section` removes the
whole subtree. The inserted heading determines its level; repeated titles get
suffixed anchors. Inspect `notes sections` afterward.

## Edit by text, pattern, or location

```bash
dreamlake notes find "Draft" --note "$NOTE_ID" --json
dreamlake notes replace "Draft" --text "Published" --all --note "$NOTE_ID" --if-match "$ETAG" --dry-run
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note "$NOTE_ID" --if-match "$ETAG" --dry-run
dreamlake notes insert --text "New line" --line 10 --note "$NOTE_ID" --if-match "$ETAG" --dry-run
dreamlake notes delete "obsolete paragraph" --note "$NOTE_ID" --if-match "$ETAG" --dry-run
```

Review the preview, then remove `--dry-run` for the intended edit. Ambiguous
single-match queries are refused; use `--all` deliberately. Patterns use
JavaScript syntax, including named captures, `$1`, `$<name>`, and `$&`.
Use `--` before a positional query beginning with `-`, after all options.

For an HTML-source document, selectors target its source without reserializing
the whole document:

```bash
dreamlake notes select "#contact" --note "$NOTE_ID"
dreamlake notes replace "Contact us" --text "Talk to sales" --selector "#contact" --note "$NOTE_ID" --if-match "$ETAG" --dry-run
dreamlake notes insert --text "<li>New</li>" --selector "#list" --position append --note "$NOTE_ID" --if-match "$ETAG" --dry-run
dreamlake notes replace --html "<b>done</b>" --selector "#status" --note "$NOTE_ID" --if-match "$ETAG" --dry-run
```

## Legacy diff and patch

```bash
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --legacy --json > legacy-baseline.json
ETAG=$(jq -er .etag legacy-baseline.json)
dreamlake notes diff "$NOTE_ID" --legacy --since "$ETAG"
```

Plain legacy diff output is only the unified diff on stdout, with metadata on
stderr. JSON returns `diff`, `from`, `to`, and `etag`. `--context` accepts 0–100
lines (default 3). No changes produce empty stdout. Unknown retained references
are errors.

To upload a single-file diff prepared from that exact saved body:

```bash
dreamlake notes patch "$NOTE_ID" --legacy --file draft.diff --if-match "$ETAG" --json
```

Legacy reads/diffs/patches require explicit `--legacy`; `write`, `append`, and
the section/text mutation commands retain their own interfaces. Do not supply a
v2 RTC revision where these commands expect a content ETag.

## Concurrent edits and failures

Writes go through the collaboration service. They do not require other people
to leave. A stale ETag rejects with exit `3`; inspect current text and review a
new edit. RTC unavailability is exit `4`, and rejected patches are exit `5`.
Keep your draft when a request fails. Do not assume a lost acknowledgment means
nothing was written, or use a forced archive replacement to recover.

For new agent workflows, prefer [Editing with patches](/notes/editing/).
