# Link Memo items: prompt, comments, details, acceptance

Links reference existing Memos or sections; linking creates or edits no Memo
content. Use IDs returned by the Memos APIs (`dreamlake memos list`; skill
`dreamlake-memos`) and resolve section anchors against the actual document.

```bash
dreamlake tasks notes add vault/entries/write-recovery --role agent_prompt --note-id NOTE_ID_PROMPT --section recovery-agent
dreamlake tasks notes add vault/entries/write-recovery --role comment --note-id NOTE_ID_DISCUSSION --section review-feedback
dreamlake tasks notes add vault/entries/write-recovery --role details --note-id NOTE_ID_DESIGN
dreamlake tasks notes list vault/entries/write-recovery --to-json
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

To reference a Task from a Memo, keep the hidden-link form in
[the contract](../assets/tasks-contract.md#display-and-text-links): the stable
Task ID stays in the link while the visible text may change.
