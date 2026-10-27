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
`dreamlake notes presence "$NOTE_ID"` (CLI 0.31.0+) and match the task ID and
name. The roster command does not join. If attribution is missing, check the
variables in the process doing the read or edit before treating it as a UI
regression. Never replay a successful edit just to produce a highlight, and do
not replay saved edits to test attribution.

Recent presence expires after about 60 seconds without activity; completed edit
highlights fade over 5 seconds on an exact matching live revision. Roster
readback verifies presence, not browser highlights. Only claim visual
verification after observing the highlight. See
[one identity per task](../reference/cli-notes-collaboration.md#one-identity-per-task).

## Contributing sessions

Presence IDs identify an editing task; they do not identify a resumable Codex
or Claude conversation. CLI 0.78.0+ links a successful Note write to one exact
owned registered session from `CODEX_THREAD_ID`, explicit `CLAUDE_SESSION_ID`,
or `DREAMLAKE_TERMINAL_SESSION_ID` plus `DREAMLAKE_SESSION_NAMESPACE`; missing
or wrong metadata never blocks the Note. After a warning retry only the link,
never the content edit, and never guess historical contributors from titles.
The link, register (CLI 0.82.0+) and opt-in conversation upload (CLI 0.79.0+)
commands, their visibility defaults and the terminal-panel behaviour of a
Note's contributing-session row are the `session-links` action of
`dreamlake-cli`. Sharing a Note never grants terminal access.

## Retained session tabs

Switching Notes preserves open session tabs and their panel placement. Opening
another Note's contributing session selects that session in the conversation
panel and leaves the previous session open in the background. A session already
open is focused instead of duplicated. Drag tabs between panels to arrange the
workspace. A standalone Sessions list panel can be closed; closing a panel or
tab does not terminate its session.

Viewing a Note, selecting a session tab, switching Notes and moving panels do
not create contributing-session links. Automatic affiliation follows an
acknowledged content write; explicit Link and Unlink actions remain available.
Temporary presence is separate from a persistent session association.
