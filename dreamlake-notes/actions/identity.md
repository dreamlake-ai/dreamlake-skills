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

## Contributing sessions and optional history

Presence IDs above identify an editing task; they do not identify a resumable
Codex/Claude conversation. CLI 0.78.0+ links successful Note writes to one exact
owned registered session from `CODEX_THREAD_ID`, explicit `CLAUDE_SESSION_ID`, or
`DREAMLAKE_TERMINAL_SESSION_ID` plus `DREAMLAKE_SESSION_NAMESPACE`. Missing or wrong
metadata must not block the Note. Retry only `sessions link` after a warning, not
the successful content edit; never guess historical contributors from titles.

With explicit user opt-in, CLI 0.79.0+ accepts `DREAMLAKE_CONVERSATION_FILE` for an
exact native export, or `sessions upload-conversation SESSION_ID --namespace NS
--file EXPORT --json`. This uploads readable conversation text under the saved
session's permissions. No setting means metadata only. A Note's contributing
sessions row opens the saved terminal in the panel to the right; it never requires
a transcript upload first. Conversation history is a separate reading action.
If the descriptor has no verified host binding, the terminal panel explains the
missing connection; **Check connection again** reloads it without selecting a host.
The original host must retain its native state; sharing a Note does not grant
terminal access. See [the CLI session guide](https://cli.dreamlake.ai/sessions/).


With CLI 0.82.0+ and the matching API, missing native sessions are registered
as metadata before affiliation; no host/terminal discovery is needed. New
sessions default public. Use `DREAMLAKE_SESSION_VISIBILITY=private` for a private
new registration; existing privacy is retained. For a metadata failure after a
successful save, register the exact native UUID with `sessions register`, then
link its returned saved ID. Never replay the Note write. Review custom secrets
before selecting a conversation export; client/server redaction is not exhaustive.

## Retained session tabs

Switching Notes preserves open session tabs and their panel placement. Opening
another Note's contributing session selects that session in the conversation
panel and leaves the previous session open in the background. A session already
open is focused instead of duplicated. Drag tabs between panels to arrange the
workspace. A standalone Sessions list panel can be closed; closing a panel or
tab does not terminate its session.

Viewing a Note, selecting a session tab, switching Notes, and moving panels do
not create contributing-session links. Automatic affiliation follows an
acknowledged content write; explicit Link/Unlink actions remain available.
Temporary presence is separate from a persistent session association.
