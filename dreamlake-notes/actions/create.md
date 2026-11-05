# Create a memo

Use this when asked to make a new memo. Titles can repeat; retain the returned
memo ID for future commands and browser links.

```bash
dreamlake memos create "Design Doc" --text "# Design Doc\n"
dreamlake memos create "Design Doc" --summary "Decision and open questions"
dreamlake memos create "Design Doc" --file draft.md --project my-project   # file at creation (CLI 0.45.1+)
```

Add `--public` only when the request explicitly asks for a public memo
(visibility default: [quick start](../reference/cli-notes-getting-started.md#quick-start)).
For larger body content, use `--file draft.md`. The optional `--summary`
remains independent of the collaborative body (length limit:
[Memo summaries](../reference/docs-notes-browsing.md#note-summaries)).
`--project SLUG` is repeatable and absent in CLI 0.44.3
and earlier; see [move](move.md) for filing rules. See
[create and list](../reference/docs-notes-browsing.md#create-and-list).

To give a namespace a profile introduction, title the memo with the namespace
slug and add `--public` only when the user asked for it to be shown publicly.
Confirm the returned slug equals the namespace slug; an existing memo with that
slug makes the new one receive a suffix, so make that memo public instead. See
[profile introduction](../reference/docs-notes-browsing.md#profile-introduction).
