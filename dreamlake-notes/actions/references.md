# Reference Notes and artifacts from list items

Use this to extract a list or checklist item into a linked Note, to edit an
existing note reference, or to write `:note[...]`, `:artifact[...]` and
placeholder directives. It does not create a Task or mark work complete; Tasks
that link Note items are `dreamlake-tasks`.

## Representation

The Note picker, extraction and copy button prefer `:note[<full-note-id>]`.
Saved `#note:<full-note-id>` and `:note{id="<full-note-id>"}` remain supported.
Preserve existing forms exactly; do not bulk-migrate. Keep the full returned ID,
never a short hash, cached title, Markdown link or HTML.

```markdown
1. :note[6aa9951250d9de84058e8ebb]
   - [ ] Discuss :note[6aa989ea6aff1e1960afc51f] before the demo.
```

Text before and after the token belongs to the parent. The rendered badge
resolves the title with the viewer's existing access. A reference grants no
access and does not publish the child. See
[linked note items](../reference/docs-notes-linked-items.md).

## Artifact references (development preview)

For an artifact, prefer `:artifact[geyang/pitch-deck]`. The development UI and
API also accept saved `#artifact:geyang/pitch-deck` and
`:artifact{namespace="geyang" id="pitch-deck"}`. Brackets hold primary content;
braces hold optional named attributes (the remark-directive Markdown extension,
not core CommonMark); DreamLake defines the resource semantics. Bare brace IDs
are invalid. Artifact IDs are namespace-scoped, so both owner namespace and ID
are required. Do not substitute a Note ID, short display hash, cached title or
share token. These tags grant no access and do not publish content; unavailable
artifacts stay unresolved. Keep source unchanged in reads and patches. API HTML
maps the entire reference atomically without fetching private metadata.
Production availability is not yet verified. See
[artifact references](../reference/docs-notes.md#artifact-references-development-preview).

## Fragment syntax

`:note[id#overview]` and `:artifact[namespace/id#slide-3]` retain a target
within the resource. `:note[id]{fragment="overview"}` is also accepted; do not
specify it twice. Preserve exact source and percent encoding. This release
accepts syntax only; click-target navigation and scrolling are deferred to the
common tab/view work. Never infer slide numbering or invent targets.

## Placeholders

Prefer `:placeholder[owner name]` for new directives. `:bindr[id]` and
`:asset-reference[id]{caption="plot"}` follow the same convention; saved
attribute forms remain supported. `:chatgpt-content-reference[0]` and imported
ChatGPT citations remain unresolved; never invent resources.

For missing prose, legacy forms include `[ xxxxx ]` or a descriptive label such
as `[ owner name ]`. Notes display blue boxes as `[ owner name ]`, with
**placeholder** on hover, while preserving the Markdown. Whitespace is required
immediately inside both brackets: `[text]`, `[ text]` and `[text ]` are not
placeholders. Keep actual Markdown links/references and `#note:<full-note-id>`
as references; never replace them with placeholder text. Code and task markers
stay literal. Examples: [placeholders](../reference/docs-notes.md#placeholders).

## UI workflow: turn a list item into a note

1. On a supported Notes editor, click **Turn list item into a note** at the
   right edge of an ordered, bullet or checkbox item.
2. The first line supplies the title; the item's text and nested content become
   the new private note body. The parent keeps its list marker or checkbox and
   replaces only that item's content with the raw reference.
3. The badge shows a short ID and title, truncating long titles. Click it to
   open a tab in the existing right panel, creating the panel only when absent.
   References opened from a side Note add tabs in that same side panel.
   Already-open Notes are focused; existing tabs and their drafts stay mounted.
   Edit surrounding parent prose outside the badge normally.
4. Verify the child content and parent reference. Closing the panel does not
   delete the note.

If creation fails or the source changes concurrently, preserve the source.
Inspect the created note or the Notes list before retrying an uncertain create;
creation is not idempotent. Undoing the parent edit does not delete the child.
Do not claim UI availability from this skill alone: the editor implementation is
a development preview until its release is verified.

## Sync recovery

Parent and child editors hold separate drafts. If either is out of sync,
download that note's local draft before selecting **Out of sync ▾ → Use server
version**. This discards the local draft and fetches server content; it does not
overwrite the server. Do not retry extraction or write stale parent text to
bypass a hold. CLI reads cannot retrieve another browser tab's unsent draft.
Follow [reconnect and recovery](../reference/docs-notes.md#reconnect-and-recovery).

## CLI workflow

Check installed `dreamlake notes --help` and the current server and editor
version first. Read the parent with `--json` and retain its ETag, create the
child with `notes create --file`, read the child back, then replace the exact
source item with `notes write --if-match` (the legacy conditional contract; the
revision-guarded patch in [edit](edit.md) is preferred when the installed CLI
supports it). Re-read and reconcile conflicts; never force an overwrite.
Preserve checkbox state, list indentation, nested content and all adjacent
prose. Report the new note ID and what moved.
