# Read or update a memo summary

Use this for short catalog metadata separate from the collaborative body.
Before your first live memo read or edit, set and reuse the [task identity](identity.md).

```bash
NOTE_ID=release-plan
dreamlake memos summary "$NOTE_ID"                 # read
dreamlake memos summary "$NOTE_ID" --text "Decision and open questions"
dreamlake memos summary "$NOTE_ID" --file summary.txt
cat summary.txt | dreamlake memos summary "$NOTE_ID" --file -
dreamlake memos summary "$NOTE_ID" --clear
```

Summaries are optional and limited to 4,000 characters. A summary change does
not write the body or change its hash or revision. The namespace owner or memo
creator who is still a current namespace member can set or clear it; authorship
after leaving an organization and body-edit access alone are insufficient. Use
`--namespace <slug>` for an organization memo. With no setter option, the
command reads the current value; use `--json` only when a program parses
the result (its shape is in the reference). Setter options are mutually exclusive. File contents
are used as-is, including a final newline. See the [Memos reference](../reference/docs-notes-browsing.md#note-summaries).
