<!-- generated from https://cli.dreamlake.ai/notes/columns.md at 0.97.2 1633dd9; do not edit -->

# Columns and rows

Use these exact, case-sensitive markers on separate, unindented lines:

```markdown
<Columns>
### Findings
- Faster startup
- Lower memory use
<ColumnBreak>
### Evidence
![Benchmark chart](https://example.com/chart.png)
</Columns>
```

Each block has exactly two nonempty columns and one `<ColumnBreak>`. Column
bodies support Markdown. Pairs stack vertically on narrow screens. These are
specific Notes layout markers; they do not enable arbitrary HTML or CSS.
Nested column blocks, extra breaks, and markers inside lists, quotes, or code
fences do not create layouts. Malformed blocks remain literal source.

There is no separate row marker. For multiple rows, repeat complete pairs:

```markdown
<Columns>
First row, left
<ColumnBreak>
First row, right
</Columns>

<Columns>
Second row, left
<ColumnBreak>
Second row, right
</Columns>
```

Use a Markdown table for tabular data. Use repeated column pairs for independent
content such as an explanation beside a chart; they are not a table with shared
column sizing across rows.

Availability: video/layout grammar inspected in frontend source revision
`5f3e85a2811eba3de01d2fff433da09b2a8b626f`; deployed rendering and frontend
release version are unverified. CLI source inspected at 0.84.1. Verify in the
browser after saving; CLI/API HTML snapshots may have different rendering support.
