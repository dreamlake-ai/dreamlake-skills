# Inspect current collaboration

Complete [task identity setup](identity.md), then check installed help before
requesting selection support:

```bash
dreamlake memos presence --help
dreamlake memos presence "$MEMO_ID" --selections
```

Use this action when the user asks who is present or what they selected. Inspect
availability and observation time before interpreting the participants. If the
client or server cannot supply the requested observation, say which capability
is missing; do not infer that nobody is present or that no work happened.
Refresh the observation when the user changes their selection or asks again.

For “what changed since my last read,” compare against the revision from that
read using the [read action](read.md). If no baseline was retained, say so and
read current source. Do not turn a selection, presence entry, expired activity
feed or net diff into a claim about a human's attention or edit authorship.

Before editing a selected passage, read the named Memo and verify the source
using the [edit action](edit.md). Keep browser quote coordinates separate from
API ranges. For ongoing foreground collaboration use [follow collaboration](watch.md);
do not invent a durable watch or replay command.

For an explicit SDK request, consult the TypeScript or Python examples in the
[collaboration contract](../reference/cli-notes-collaboration.md). The built-in
agent and local MCP have their own registered tools; SDK availability does not
register those tools. Availability states, units and limits are specified in
[agent presence](../reference/docs-notes-agent-presence.md).
