# Create a note

Use this when asked to make a new note. Titles can repeat; retain the returned
note ID for future commands and browser links.

```bash
dreamlake notes create "Design Doc" --text "# Design Doc\n"
dreamlake notes create "Design Doc" --summary "Decision and open questions"
```

Notes are private by default. Add `--public` only when the request explicitly
asks for a public note. For larger body content, use `--file draft.md`. The
optional `--summary` is limited to 4,000 characters and remains independent of
the collaborative body. See the [Notes reference](../reference/notes.md#create-and-list).

To give a namespace a profile introduction, title the note with the namespace
slug and add `--public` only when the user asked for it to be shown publicly.
Confirm the returned slug equals the namespace slug; an existing note with that
slug makes the new one receive a suffix, so make that note public instead. See
[Profile introduction](../reference/notes.md#profile-introduction).
