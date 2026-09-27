# Read a note

Set `NOTE_ID` to an ID or slug from `dreamlake notes list`. Add
`--namespace <slug>` when the note belongs to an organization. Check the
installed CLI before choosing a read contract:

```bash
NOTE_ID=release-plan
dreamlake notes read --help
```

When help lists `--view markdown`, `--toc`, `--section`, `--tag` and `--at`,
use addressable Markdown reads. Start with the outline, then pin any section or
element reads to the revision printed in the first result:

```bash
dreamlake notes read "$NOTE_ID" --view markdown --toc
REVISION='revision from the outline result'
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --section s1.1
# Or target one passage or list item instead of reading the whole section:
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --tag s1.1.p1
dreamlake notes read "$NOTE_ID" --view markdown --at "$REVISION" --tag s1.li1
```

Use the smallest read that answers the question. The Markdown view adds
address, character and line hints as comments before headings, paragraphs and
list items. List-item IDs look like `s1.li1`, and nested items have their own
IDs. Hints are not saved note text. Keep the revision with the passage. Do not
combine `--at` with `--since` or
`--if-match`, or combine multiple scope selectors. If the installed CLI lacks
these options, use the compatible legacy reads below and do not infer HTML
addresses:

```bash
dreamlake notes toc --note "$NOTE_ID"
dreamlake notes read --legacy "$NOTE_ID" --section setup
dreamlake notes read --legacy "$NOTE_ID" --start-line 40 --end-line 80
```

For a whole-source delta, retain the plain-text read's `hash` and pass it to
`--since`; `hash` and opaque write `revision` are different tokens. Use
`--json` only when a program needs parsed fields. See [reading and changes](../reference/notes-reading.md)
and [the full Notes guide](../reference/notes.md).
