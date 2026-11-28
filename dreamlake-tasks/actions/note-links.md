# Link Memo items: prompt, comments, details, acceptance

Links reference existing Memos or sections; linking creates or edits no Memo
content. Use IDs returned by the Memos APIs (`dl memos list`; skill
`dreamlake-memos`) and resolve section anchors against the actual document.

```bash
dl tasks notes add vault/entries/write-recovery --role agent_prompt --note-id NOTE_ID_PROMPT --section recovery-agent
dl tasks notes add vault/entries/write-recovery --role comment --note-id NOTE_ID_DISCUSSION --section review-feedback
dl tasks notes add vault/entries/write-recovery --role details --note-id NOTE_ID_DESIGN
dl tasks notes list vault/entries/write-recovery --to-json
```

Roles include `agent_prompt`, `comment`, `details` and `acceptance`. Linking
needs access to the existing Memo in the same namespace; reads omit
inaccessible references. Section keys are references, not validated editor
anchors. The detail panel groups links by role and opens the linked item.
Comments use Memos content for this first proposal; no separate comment or post
API and no immutable discussion timeline is implied. Prompt revision pinning is
optional and must match Memos capabilities; record what the agent actually read
when execution evidence needs it. A text-only task needs no Memo; never
duplicate Memo bodies in Task metadata. See
[link memo items](../reference/cli-tasks.md#link-note-items-prompt-comments-and-details).

To reference a Task from a Memo, use the references action of
`dreamlake-memos`. Copy the reference from the Task detail view or use the
procedure in the [Task CLI guide](../reference/cli-tasks.md#copy-a-task-reference-for-a-memo).
Preserve any existing hidden links recorded in
[the contract](../assets/tasks-contract.md#display-and-text-links).
