# Read or update a note summary

Use this for short catalog metadata separate from the collaborative body.
Before your first live note read or edit, set and reuse the [task identity](identity.md).

```bash
NOTE_ID=release-plan
dreamlake notes summary "$NOTE_ID"                 # read
dreamlake notes summary "$NOTE_ID" --text "Decision and open questions"
dreamlake notes summary "$NOTE_ID" --file summary.txt
cat summary.txt | dreamlake notes summary "$NOTE_ID" --file -
dreamlake notes summary "$NOTE_ID" --clear
```

Summaries are optional and limited to 4,000 characters. A summary change does
not write the body or change its hash or revision. The namespace owner or note
creator can set or clear it; body-edit access alone is insufficient. Use
`--namespace <slug>` for an organization note. With no setter option, the
command reads the current value; `--json` returns `{note, summary}`, with
`summary: null` when unset. Setter options are mutually exclusive. File contents
are used as-is, including a final newline. See the [Notes reference](../reference/notes.md#note-summaries).
