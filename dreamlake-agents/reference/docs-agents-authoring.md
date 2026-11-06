<!-- generated from https://docs.dreamlake.ai/agents/authoring.md at 0.1.124 b7138276; do not edit -->

# Authoring agents

Agent definitions support inline Markdown or a main instruction memo with
optional skill memos and folders. CLI and SDK availability depends on the
installed client version; see the linked client documentation below.

An agent is a runnable with `kind: "agent"`. Creating one saves a definition;
it does not create a session or execute its instructions. Open **Agents** to use
the same list and editor layout as Memos. The main instruction memo uses the
full Memos editor, including automatic synchronization, source/preview mode,
version history, comments, attachments and template Variables. **Spec** is a
view in the editor's right sidebar; it contains the agent name, description,
runtime configuration and instruction sources as JSON, preserving nested values.
Use the sidebar menu to switch between Spec, History, Variables and the other
memo views. The spec draft stays intact while switching views. Save spec changes
with its **Save** button; instruction text synchronizes independently.

Agents created in the UI start with a main instruction memo. When creating an
agent inside a project, its main memo is filed there too.
For an existing inline agent, save any draft and choose **Enable memo editor**
to preserve its Markdown in a main memo and start using memo history. Conversion
checks for concurrent agent changes before linking the memo. If an operation
cannot be confirmed, the source and any created memo are kept for recovery.
Changing an existing instruction-note reference waits for pending memo edits to
finish syncing. On narrow screens, use **Open memo sidebar** to show Spec.

Use a main instruction memo plus optional skill memos or project folders when
instructions should be reusable. The runnable stores references, not copies of
private memo bodies. The built-in runtime resolves readable memos again when
the definition is selected, and includes their revisions in the selected
definition. Editing a source memo therefore changes the next resolved definition.

## Create through the resource API

Send an authenticated `POST /namespaces/{namespace}/runnables` with:

```json
{
  "name": "Reviewer",
  "module": "agents",
  "qualname": "reviewer",
  "kind": "agent",
  "projects": ["example-project"],
  "content": {
    "instructionNoteId": "0123456789abcdef01234567",
    "skills": [
      { "kind": "note", "id": "123456789abcdef012345678" },
      { "kind": "folder", "id": "23456789abcdef0123456789" }
    ]
  },
  "metadata": {
    "agent": {
      "runtime": "builtin-v1",
      "tools": ["dreamlake_notes_read"]
    }
  }
}
```

Replace example IDs with actual memo IDs and project folder node IDs. Sources
must be readable by the caller and belong to the runnable's namespace. At most
20 distinct skill references are accepted. Folder expansion is deterministic
and bounded: at most 20 folders, 200 children per folder, 50 distinct memos and
16,000 combined instruction characters. Empty main instructions cannot run.

For inline instructions, omit `content` and supply a `markdown` string instead.
Both sources cannot be populated together. Project filing and runnable creation
are atomic: failed filing leaves no new runnable. Existing project members can
read filed agents; write members can edit them through their inherited access.

## Read, update, archive and delete

| Request | Behavior |
| --- | --- |
| `GET /namespaces/{namespace}/runnables?kind=agent` | Paginated agent catalog; archived entries are excluded by default. Add `includeArchived=true` to include them. |
| `GET /namespaces/{namespace}/runnables/{id}` | Read an accessible definition, including its `updatedAt`. |
| `PATCH /namespaces/{namespace}/runnables/{id}` | Update supplied fields. Include `expectedUpdatedAt` from the read to reject a concurrent change with HTTP 409. |
| PATCH body `{ "archived": true }` | Hide from ordinary discovery while retaining the definition, filings and history. |
| PATCH body `{ "archived": false }` | Restore discovery. Other edits do not automatically restore an archived agent. |
| `DELETE /namespaces/{namespace}/runnables/{id}` | Soft-delete the runnable and remove its project filings. Immutable version history remains. |

To replace inline instructions with references, patch both `content` and
`markdown: null`. To switch back, patch `content: null` and the new `markdown`.
Metadata updates replace the supplied metadata object, so retain unrelated keys
when editing `metadata.agent`. Renaming a filed agent updates its filing names;
a name collision rejects the entire change.

The Agents list supports archive, restore, confirmed deletion and dragging an
agent to the saved sidebar. A project can create an agent from its add menu.
In the built-in prompt, `/agent` and `@agent` open the definition picker;
`/agents` opens the agent list. Selecting a definition prepares a prompt; sending
that prompt starts its run.
The built-in assistant can also create definitions and operate resource APIs;
see [Resource tools](docs-agents-resource-tools.md). CLI and TypeScript examples live
in the [CLI agent guide](https://cli.dreamlake.ai/agents); Python 0.40.0 examples are in the
[SDK runnable API documentation](https://github.com/fortyfive-labs/dreamlake/blob/562156a5ea17caa08d1ee4c0671be68320be621e/docs/api/runnables.md).
