<!-- generated from https://docs.dreamlake.ai/notes/linked-items.md at 0.1.150 29155024; do not edit -->

# Linked memo items

Turn a list item into a memo while keeping the parent list compact.

**Development preview:** available in the Memos extraction development UI. Production UI release is not yet verified.

1. Click **Turn list item into a memo** at the right edge of any numbered, bullet or checkbox item.
2. The item text and nested content move into a new private memo. Its first line becomes the title. The parent keeps its number or checkbox.
3. The reference displays a short hash and title, with an ellipsis when the title is too long.
4. Click the reference to open an editable tab in the panel on the right. Create that panel only when absent; subsequent references add tabs there. References opened from a side Memo add tabs in that same side panel. An already-open Memo is focused instead of duplicated. On a narrow screen, navigation fills the viewport. Closing a tab does not delete the Memo.

## Plain Markdown

New Memo references use ordinary Markdown links with the full ID and owner namespace:

```markdown
1. [Design Memo](https://dreamlake.ai/geyang/notes?note=6aa9951250d9de84058e8ebb)
   - [ ] Discuss [Demo plan](https://dreamlake.ai/geyang/notes?note=6aa989ea6aff1e1960afc51f) before the demo.
```

Use the URL returned by DreamLake or copied from the Memo. Do not replace the
full ID with a title or short hash, or guess the owner namespace. Text before
and after a link remains ordinary Markdown. References inside code remain literal.

Linked memos retain their own permissions. Creating a reference does not grant access to the child or make it public. A missing or inaccessible memo displays **Unavailable memo**.

If an item changes during creation, the source stays intact and the new memo opens separately. If a request fails, inspect Memos before trying again. Undoing the parent replacement does not delete the child.

## Rich-component notation

Memo extraction and the copy-reference button produce ordinary links.
New `:note` authoring and its insertion suggestions are retired. There is no
`:memo` directive. The renderer still accepts saved `:note[<full-note-id>]`,
`#note:<full-note-id>` and `:note{id="<full-note-id>"}` references. Preserve existing
source, attributes and fragments exactly; do not bulk-rewrite stored content.

For an artifact, use `:artifact[geyang/pitch-deck]`; saved
`:artifact{namespace="geyang" id="pitch-deck"}` and `#artifact:geyang/pitch-deck`
remain supported. Brackets hold primary content; braces are only named attributes.
This is the remark-directive Markdown extension convention, not core CommonMark;
DreamLake defines resource semantics. Bare `:note{ID}` / `:artifact{namespace/id}`
are invalid. Other preferred forms are `:bindr[id]`,
`:asset-reference[id]{caption="plot"}`, `:placeholder[owner name]` and
`:chatgpt-content-reference[0]`. Imported ChatGPT forms remain unresolved;
never invent resources. Saved attribute forms and `[ owner name ]` remain supported.
The artifact extension is a development preview, not a verified production release.
Artifact IDs require their namespace; references grant no access. See
[Memos reference syntax](docs-notes-writing.md#artifact-references-development-preview).

## Experiments, projects and folders

Every path starts with the DreamLake namespace. Experiments ids are the ones in
the Experiments URL, `/<namespace>/experiments/<project id>/<experiment id>`.

```markdown
:dashboard[geyang/398712/baselines]
:dashboard[geyang/398712]
:experiment[geyang/398712/exp-3]
:project[geyang/demo-project]
:folder[geyang/demo-project/datasets/2026]
```

- `:dashboard[<namespace>/<project id>/<folder path>]` shows that folder's
  `.dashrc` charts on a panel beside the memo. Omit the folder path for the
  project root.
- `:experiment[<namespace>/<project id>/<experiment id>]` opens one experiment
  on a panel.
- `:project[<namespace>/<project slug>]` and
  `:folder[<namespace>/<project slug>/<folder path>]` link to the DreamLake
  project and to a folder inside it.

Badges show titles only after your access is checked. Otherwise they read
**Unavailable dashboard** (or experiment, project, folder) and do nothing when
clicked. A reference grants no access. Invalid paths stay literal text. Use
`:experiment`, not `:run`: in DreamLake, runs are Lakeshore function
invocations.

## Create and link a memo

Use **+ Memo** to create a Memo, or extract a list item where that action is
available. Copy its reference and insert the ordinary link in the parent.
Typing `:note[` no longer offers Memo search or creation suggestions. Do not
introduce new directives when editing an existing Memo.

## Sync recovery

Each open memo has its own collaborative state. If sending pauses, preserve the
local draft before choosing **Out of sync ▾ → Use server version**. Downloading
the parent draft does not back up unsent text in the child editor. Follow the
[Memos recovery steps](docs-notes-collaboration.md#reconnect-and-recovery) for each affected memo.
Do not retry extraction or rewrite a parent from stale text to bypass a sync hold.

## Agent skill

Linked-item extraction, raw full-ID references, concurrency checks and CLI
readback are part of the `dreamlake-memos` skill: run `dl init` once,
then `dl skill install dreamlake-memos`; or copy `dreamlake-memos/`
and `dreamlake-cli/` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
tarball into your agent's skills directory.
