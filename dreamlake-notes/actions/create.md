# Create a note

Use this when asked to make a new note. Titles can repeat; retain the returned
note ID for future commands and browser links.

```bash
dreamlake notes create "Design Doc" --text "# Design Doc\n"
```

Notes are private by default. Add `--public` only when the request explicitly
asks for a public note. For larger content, use `--file draft.md`. See the
[Notes reference](../reference/notes.md#create-and-list).
