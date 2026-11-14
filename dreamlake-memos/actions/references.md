# Reference Memos and artifacts from list items

Use this to extract a list or checklist item into a linked Memo, to edit an
existing memo reference, or to insert Memo references, `:artifact[...]`,
experiment, project and folder references, and placeholder directives. It does not create a Task or mark work complete; Tasks
that link Memo items are `dreamlake-tasks`.

Preserve resource directives when editing; do not flatten an artifact,
experiment, project or folder reference into a URL or plain ID. For a Memo,
follow the current representation below and retain saved native forms exactly.

## Representation

Create or locate the Memo, retain the confirmed immutable ID, and copy its
canonical directive into the parent or Chat. Follow the current
[linked Memo representation](../reference/docs-notes-linked-items.md); never
substitute the display title, search query, slug or shortened ID. Resolve a
lookup first, then use its returned identity. Confirm duplicate-title results
by identity and owner before choosing one.

Do not generate new legacy directives from older examples, stored conversation
history or tool names. Preserve saved legacy source during unrelated edits.
If a result has no confirmed ID, inspect the existing resource before retrying;
never guess a target, switch syntax as a fallback or create a duplicate.
Read back the inserted source and open the target to verify the intended Memo.
Links do not grant access or change sharing.

## Artifact references (development preview)

For an artifact, prefer `:artifact[geyang/pitch-deck]`. The development UI and
API also accept saved `#artifact:geyang/pitch-deck` and
`:artifact{namespace="geyang" id="pitch-deck"}`. Brackets hold primary content;
braces hold optional named attributes (the remark-directive Markdown extension,
not core CommonMark); DreamLake defines the resource semantics. Bare brace IDs
are invalid. Artifact IDs are namespace-scoped, so both owner namespace and ID
are required. Do not substitute a Memo ID, short display hash, cached title or
share token. These tags grant no access and do not publish content; unavailable
artifacts stay unresolved. Keep source unchanged in reads and patches. API HTML
maps the entire reference atomically without fetching private metadata.
Production availability is not yet verified. See
[artifact references](../reference/docs-notes-writing.md#artifact-references-development-preview).

## Experiments, project and folder references

Write `:dashboard[<ns>/<dash project id>/<folder path>]` for a folder's
`.dashrc` dashboard (omit the path for the project root),
`:experiment[<ns>/<dash project id>/<experiment id>]` for one experiment, and
`:project[<ns>/<project slug>]` or `:folder[<ns>/<project slug>/<folder path>]`
for a DreamLake project or folder.

1. Take the Dash ids from the Experiments URL
   (`/<ns>/experiments/<project id>/<experiment id>`) that the user gave or that
   you read. Never substitute a project name, slug or run name for a Dash id,
   and never guess an id.
2. For `:project` and `:folder`, use the DreamLake project slug, not its
   display name.
3. Do not write `:run[...]`: in DreamLake, runs are Lakeshore function
   invocations, and `:run` is not a reference.
4. Preserve existing source exactly. An invalid path stays literal text; an
   unreadable target renders as **Unavailable …**. Neither is a reason to
   rewrite the reference, and a reference grants no access.

Syntax and badge behavior:
[experiments, projects and folders](../reference/docs-notes-linked-items.md#experiments-projects-and-folders).

## Create a Memo and link it

Prefer an existing match over creating a duplicate. Create the Memo first with
`dl memos create`, retain its returned identity and canonical directive, then insert that
directive into the parent. Keep the title only as a display label. If creation fails or its result is
unclear, inspect the Memos list before retrying; creation is not idempotent.
Do not use the retired `:note[` authoring flow.

## Fragment syntax

Existing `:note[id#overview]` and `:artifact[namespace/id#slide-3]` retain a target
within the resource. Preserve saved `:note[id]{fragment="overview"}`; do not
specify it twice. Preserve exact source and percent encoding. This release
accepts syntax only; click-target navigation and scrolling are deferred to the
common tab/view work. Never infer slide numbering or invent targets.

## Placeholders

Prefer `:placeholder[owner name]` for new directives. `:bindr[id]` and
`:asset-reference[id]{caption="plot"}` follow the same convention; saved
attribute forms remain supported. `:chatgpt-content-reference[0]` and imported
ChatGPT citations remain unresolved; never invent resources.

For missing prose, legacy forms include `[ xxxxx ]` or a descriptive label such
as `[ owner name ]`. Memos display blue boxes as `[ owner name ]`, with
**placeholder** on hover, while preserving the Markdown. Whitespace is required
immediately inside both brackets: `[text]`, `[ text]` and `[text ]` are not
placeholders. Keep actual Markdown links/references and `#note:<full-note-id>`
as references; never replace them with placeholder text. Code and task markers
stay literal. Examples: [placeholders](../reference/docs-notes-writing.md#placeholders).

## UI workflow: turn a list item into a memo

1. On a supported Memos editor, click **Turn list item into a memo** at the
   right edge of an ordered, bullet or checkbox item.
2. The first line supplies the title; the item's text and nested content become
   the new private memo body. The parent keeps its list marker or checkbox and
   replaces only that item's content with a link.
3. Open the resulting link and confirm its destination. Keep surrounding parent
   prose, list markers and checkbox state unchanged.
4. Verify the child content and parent reference. Closing the panel does not
   delete the memo.

If creation fails or the source changes concurrently, preserve the source.
Inspect the created memo or the Memos list before retrying an uncertain create;
creation is not idempotent. Undoing the parent edit does not delete the child.
Do not claim UI availability from this skill alone: the editor implementation is
a development preview until its release is verified.

## Sync recovery

Parent and child editors hold separate drafts. If either is out of sync,
download that memo's local draft before selecting **Out of sync ▾ → Use server
version**. This discards the local draft and fetches server content; it does not
overwrite the server. Do not retry extraction or write stale parent text to
bypass a hold. CLI reads cannot retrieve another browser tab's unsent draft.
Follow [reconnect and recovery](../reference/docs-notes-collaboration.md#reconnect-and-recovery).

## CLI workflow

Check installed `dl memos --help` and the current server and editor
version first. Follow [read](read.md) for an original complete source snapshot and
retain its opaque revision. Locate or create the child, read it back, then use
the revision-guarded exact patch in [edit](edit.md) to replace only the source
item with the child's returned canonical directive, using its confirmed full ID.
Re-read the returned revision to verify. On a conflict or uncertain outcome,
retain the original baseline and proposed patch; reconcile before another write.
Preserve checkbox state, list indentation, nested content and adjacent prose.
Report the new Memo ID and what moved. Never force an overwrite or invent a target.
