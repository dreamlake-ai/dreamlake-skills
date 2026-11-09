<!-- generated from https://docs.dreamlake.ai/notes/collaboration.md at 0.1.134 4bbe54f7; do not edit -->

# Collaboration and review

## Collaboration and sync

People can edit the same memo simultaneously. Edits merge through the existing
CRDT; checking sync does not lock the memo or wait for other editors to stop.
The status beside the memo title describes this tab:

| Status | Meaning |
|---|---|
| **Synced** | This tab matched the server revision and text checksum. |
| **Syncing** | Changes or verification are still in progress. |
| **Out of sync** | Sending is paused; inspect the recovery dropdown. |

A connected socket alone does not prove that text matches. The browser requests
a checksum calculated by the RTC server and compares it only when both hold the
same revision and no local changes are pending. Different revisions, slow
acknowledgements and delayed checks remain **Syncing**; they are not proof of
corruption. New edits invalidate the previous verification.

Typing and selection replacement stay local while the edit is applied, so
intermediate delete/insert events do not reset the cursor. Composition finishes
before an incoming update changes the editor. Updates from other people continue
to merge normally.

### Reconnect and recovery

During a temporary disconnect, the tab keeps pending operations and retries on
reconnect. It replays their original identities only against a compatible server
checkpoint. A proven text mismatch, an update that cannot be applied, or a changed
checkpoint that prevents safe replay pauses sending and retains a local draft.
It does not automatically send that held draft after a refresh.

Open **Out of sync ▾** beside the memo title:

1. Choose **Download local draft** to save your text before discarding anything.
2. Choose **Use server version** to discard the held local draft and fetch current
   server content. This does not overwrite the server memo.
3. Compare your downloaded draft with the memo, then reapply any missing changes
   in the editor.

**Download edit data** saves `note-edit-data.json` with the local editing and sync
state for inspection. It does not send edits, discard the draft or load a server
version. This is diagnostic data, not an automatic restore/import action.

A retained draft normally survives refresh in the same browser tab. Browser
storage can be unavailable; follow the warning to copy or download it before
closing or refreshing. Do not clear browser storage as a recovery shortcut.

Legacy CLI/Python edit helpers retain their conditional revision checks below.
The v2 patch interface uses merge mode by default and opt-in exact mode.
They cannot read or recover an unsent draft held in another browser tab. A fresh
CLI read describes server content, not proof that every open editor matches it.

## Activation conflicts and acknowledged edits

These activation and acknowledgement safeguards have previously passed runtime
acceptance. That does not establish readiness of the later catalog or attachment
candidates or diagnose a current read failure. Activation rechecks current access and its exact Memo
ownership/storage/room binding before returning a room. Existing signed-in public-Note and
read-share body reads remain supported; they do not acquire edit permission, and
this change does not enable anonymous API endpoints.
A busy or stale ownership lease can return `409 WRITER_FENCE_REQUIRED` or
`409 STALE_EPOCH`. Refresh the Memo's current state and preserve local drafts;
do not clear the lease or bypass ownership checks.

An acknowledged native body edit remains successful even if the subsequent
idle-sync marker or storage projection cannot be updated. Do not resend an
already acknowledged edit. Its returned revision may not yet have a retained
baseline if storage failed; fetch current Memo state and reconcile if that
revision cannot be read. These checks protect database bindings; they do not
prove complete RTC/storage exclusion or make cross-workspace moves available.

## Suggested edits

Use three tags for reviewable edits stored directly in the note:

```markdown
:insert[new text]{user="geyang"}
:delete[existing text]{user="geyang"}
:replace[existing text]{with="replacement text" user="geyang"}
```

`user` is optional display attribution. `replace` requires `with`; an empty
replacement is allowed. Add optional `reason="Why this change helps"` to explain
a suggestion. Attribute values are JSON strings. Escape literal brackets and
backslashes in the bracket body with a backslash. Insertion-menu choices fill
the signed-in user's name; scripts can supply attribution explicitly.

The bracket form is canonical. The browser also accepts a curly-body alias for
all three kinds; optional named attributes follow in a separate pair of braces:

```markdown
and I:insert[ think this works]
and I:insert{ think this works}
:delete{old text}{reason="No longer needed"}
:replace{old text}{with="new text" user="geyang"}
```

A suggestion can directly follow ordinary text without an intervening space.
Leading and trailing spaces inside its body are preserved when accepted.
Curly bodies support balanced nested braces; escape a literal brace or backslash
with a backslash. Canonical bracket bodies retain their existing bracket escaping.
These aliases apply to suggested edits, not other directive types.

Insertions are underlined and deletions struck through in the memo. A replacement
shows both. Inline mode shows these text changes without cards or hover popups.
Sidebar cards identify the action on the left as `insert:`, `delete:` or
`replace:` rather than a generic suggestion label.
Switch to Sidebar in a wide pane for **accept · reject** actions. Compact cards
replace the table of contents in its existing column and follow passages visible
in the current viewport. Dense groups scroll inside that column. Hovering or
focusing a card or text anchor highlights the corresponding annotation. Narrow
panes fall back to Inline while retaining the Sidebar preference.

Accept applies the proposed text: insert keeps new text, delete removes old
text, and replace substitutes its `with` value. Reject removes an insertion or
restores the original text of a deletion/replacement. Each decision replaces
only that exact tag in one undoable editor operation and uses the memo's normal
collaborative save. If the source changed before the action, it refuses the stale
operation. Memo writers can accept/reject; read-only views show the proposal
without write controls. No separate suggestion collection or replies are added.

Incomplete or malformed tags remain literal. Tags inside code, Markdown links,
or comments do not become suggested edits. Supported kinds are intentionally
limited to insert, delete, and replace; use comments for questions or discussion.

## Comments (development preview)

Comments use `:comment[text]` for text stored in the memo and
`:comment[cmt_<24 hex digits>]` for a saved comment reference. Both accept optional
`{user="geyang"}` attribution and `mode="inline"` to keep an occurrence inline. Braces after a bracket contain metadata only;
there is no `type`, `text`, `ref`, or `userId` field. Attribution is a display
label; the server records the authenticated creator separately. Escape brackets
and backslashes with a backslash. Use `\cmt_...` inside brackets when an ID-shaped
string should be literal text. Code spans and fenced code remain literal.

In the rich editor, typing `:comment{` starts a saved-comment draft. Keep typing
in the note: its side box mirrors the body. The editor supplies a hidden draft
key for retry safety; this key does not create a saved comment object. Closed
drafts first save after 800 ms of inactivity once their body contains at least
two non-whitespace characters, or with any nonempty body when the caret or focus
leaves the comment. Empty and whitespace-only drafts never create objects.
IME composition defers writes. Saving never moves the
caret or replaces active text. Once the caret leaves and the latest body is
acknowledged, source becomes `:comment[cmt_...]{user="..."}` (the optional user
attribute is retained when supplied). Newly typed comment brackets and brace
drafts automatically include the signed-in user's namespace as `user`. Opening
a saved comment edits its object while the reference stays fixed. In Sidebar
view the borderless editor and its Save action share the comment container;
Save waits for the latest save before closing. Comments have no replies; conversations belong in chats.

The sidebar starts with Comments when review annotations are present. In
**Settings → Sidebar suggestions**, Automatic learns a small preference model
from comment use and corrections; fixed Comments and Contents modes disable
that automatic choice. The model makes at most one decision per memo visit,
when preview is enabled and the pane has room. Choosing a tab or collapsing the
sidebar takes priority for the rest of that visit. Narrow panes keep annotations
inline. An empty Comments view falls back to Contents without erasing the choice.

New choices do not create per-note preference records. Existing saved memo
choices remain readable for compatibility. Learning is saved per account in
this browser, with eight numeric context features, at most 32 recent feedback
records, and an 8 KiB total storage cap. Records exclude memo identifiers,
titles, authors and bodies. Settings shows observation counts, storage use,
recent outcomes and selection probabilities. You can choose how often the
other view is tried, stop keeping recent records, clear records, or reset
learning. Disabling or clearing the record history does not erase the aggregate
model; Reset learning clears both while preserving your settings.

The initial exploration rate is 5%. Comment use is a small positive signal;
dismissing Comments or manually opening it after Contents corrects the model.
Inactivity is never positive feedback. A decision without an explicit correction
is evaluated after 60 visible, focused seconds; incomplete visits are discarded.
These signals estimate interface usefulness, not user satisfaction.

**Comments → Inline / Sidebar** changes the current view, independently of
storage. Inline comments show the author label and italic text in the author's
collaboration color, with faint brackets around the body. Sidebar comments use
`[…]` anchors and compact bracketed cards. Short comments wrap in full; longer
comments show four lines with **Read more** to expand a scrollable reading view.
**Edit** opens the saved-comment editor separately. The editor grows with its
text up to a bounded height, then scrolls. Cards replace
the table of contents in the same column, follow visible passages, and scroll
within the column when densely packed. Hovering or focusing the anchor or card
highlights its matching annotation. Inline mode has no annotation cards or hover
previews; explicitly opening a saved comment opens its editor beside the clicked
comment, within the visible window, without scrolling the memo to the top.
The editor's **Resolve** action saves pending changes before removing that comment
occurrence from the memo; **Save** closes the editor without removing it.
The **Inline this** button sits after the resolve checkmark. At rest it is a
Lucide chevron; hover or keyboard focus animates it into a left arrow pointing
at a vertical line. Reduced-motion preferences show the same states without
animation. The action saves pending edits and adds `mode="inline"` to that
occurrence, keeping it in the paragraph with the Comments sidebar open.
Use the right chevron in its editor to return it to the sidebar. Both actions
use editor history, and Undo restores the previous occurrence.
Readers without note-edit permission do not see these actions. Narrow panes
fall back to Inline while retaining the Sidebar preference. Read-only readers can open accessible saved comments but
cannot change them. Rendering, loading, and remote text replay never create
comment objects. A brace draft pasted by a script without an editor creation
key remains source text; use the API to create a saved object deliberately.

The same completion menu handles supported tag names after `:`, accessible
resource targets within `[`, and supported attributes within `{`. The `user`
attribute offers people lookup. Free text stays valid; searching does not save
or convert it. Comment bodies are free text: typing inside `:comment[` does not
search saved comments. Existing saved-comment references still render normally.

### Collection API

These endpoints require the matching server version. They are not a CLI release
claim. Paths are relative to the DreamLake API base.

| Method and path | Contract |
|---|---|
| `POST /namespaces/:slug/notes/:noteId/comments` | Body `{body, creationKey, user?}`; authenticated origin-note writer only. Key is 16–128 ASCII letters, digits, `_`, or `-`. |
| `GET /namespaces/:slug/notes/:noteId/comments?q=...` | Up to 30 accessible origin-note comments, newest first; optional body substring search. |
| `GET /namespaces/:slug/comments/:commentId` | Read the object under its original memo's permissions. |
| `PATCH /namespaces/:slug/comments/:commentId` | Body `{body, revision}`; compare-and-swap update; stale revision returns 409. |

Returned objects include `id`, `noteId`, `body`, optional `user`, `createdBy`,
`revision`, timestamps and `canEdit`. Bodies are nonempty and at most 20,000
characters. Retrying creation with the same note/key returns the existing object
without overwriting it. A different key deliberately creates a different object.
Reads of public origin memos allow anonymous callers; private origins and deleted
origins do not become visible through a copied reference. Invalid credentials
are rejected, and mutations still require authentication and write permission.

Retain local text on a failed save or revision conflict. Retry uncertain creation
with the same key, and never overwrite a newer object from an older draft.
The editor retains recovery state for the current browser session; the keyed
body remains in the memo until acknowledged and collapsed. A changed object
requires reconciliation, with the local draft available to copy. A lost response
can safely be retried. Deleting an anchor does not delete its saved object.
