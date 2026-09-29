# Set the task identity

Before an agent's first live read or edit, set both variables unless the user
explicitly requests unattributed work. Successful saves alone do not prove
agent attribution: without the ID, presence and fading edit highlights are absent.

Generate the identity once in the task environment, preserving an existing one:

```bash
export DREAMLAKE_AGENT_ID="${DREAMLAKE_AGENT_ID:-codex:$(python3 -c 'import uuid; print(uuid.uuid4())')}"
export DREAMLAKE_AGENT_NAME="${DREAMLAKE_AGENT_NAME:-Codex}"
```

Use the current agent's readable name. Reuse this ID across reads, edits and
linger sessions; concurrent tasks need distinct IDs. An export does not survive
independent shell tool calls. Retain the generated value in task context and
inject those same literal values into every later Notes command environment.
Do not generate a new UUID for each command or change global shell configuration.

No separate join is needed. After the first intended live read, inspect
`dreamlake notes presence "$NOTE_ID"` (CLI 0.31.0+) and match the task ID and name.
The roster command does not join. If attribution is missing, check the variables
in the process doing the read/edit before treating it as a UI regression.
Never replay a successful edit just to produce a highlight.

Recent presence expires after about 60 seconds without activity; completed edit
highlights fade over 5 seconds on an exact matching live revision. Roster readback
verifies presence, not browser highlights. Only claim visual verification after
observing the highlight. See [agent collaboration](../reference/notes-collaboration.md).
