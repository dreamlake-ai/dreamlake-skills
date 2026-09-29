# Linked note items

Turn a list item into a note while keeping the parent list compact.

**Development preview:** available in the Notes extraction development UI. Production UI release is not yet verified.

1. Click **Turn list item into a note** at the right edge of any numbered, bullet or checkbox item.
2. The item text and nested content move into a new private note. Its first line becomes the title. The parent keeps its number or checkbox.
3. The reference displays a short hash and title, with an ellipsis when the title is too long.
4. Click the reference to open an editable tab in the panel on the right. Create that panel only when absent; subsequent references add tabs there. References opened from a side Note add tabs in that same side panel. An already-open Note is focused instead of duplicated. On a narrow screen, navigation fills the viewport. Closing a tab does not delete the Note.

## Plain Markdown

Only the full note ID is saved in the reference:

```markdown
1. :note[6aa9951250d9de84058e8ebb]
   - [ ] Discuss :note[6aa989ea6aff1e1960afc51f] before the demo.
```

You can edit text before and after the reference. The short hash and title are display values, not stored Markdown. Renaming the child does not change its ID; reopening the parent resolves its current title. References inside code remain literal text.

Linked notes retain their own permissions. Creating a reference does not grant access to the child or make it public. A missing or inaccessible note displays **Unavailable note**.

If an item changes during creation, the source stays intact and the new note opens separately. If a request fails, inspect Notes before trying again. Undoing the parent replacement does not delete the child.

## Rich-component notation

The Note picker, extraction and copy button prefer `:note[<full-note-id>]`.
The renderer preserves saved `#note:<full-note-id>` and `:note{id="<full-note-id>"}`.
Keep existing source unchanged; never bulk-migrate notation. Display titles and
short hashes are never reference IDs.

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
[Notes reference syntax](https://docs.dreamlake.ai/notes/#artifact-references-development-preview).

## Sync recovery

Each open note has its own collaborative state. If sending pauses, preserve the
local draft before choosing **Out of sync ▾ → Use server version**. Downloading
the parent draft does not back up unsent text in the child editor. Follow the
[Notes recovery steps](https://docs.dreamlake.ai/notes/#reconnect-and-recovery) for each affected note.
Do not retry extraction or rewrite a parent from stale text to bypass a sync hold.

## Agent skill

[Download the linked-note skill](https://docs.dreamlake.ai/skills/dreamlake-note-references.zip). Extract `dreamlake-note-references` into your agent's skills directory. The skill covers raw token storage, nested item extraction, concurrency checks, and CLI readback.
