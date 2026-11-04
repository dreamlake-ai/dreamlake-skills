<!-- generated from https://docs.dreamlake.ai/agents/authoring.md at 0.1.114 594d5f21; do not edit -->

# Authoring agents

Agent definitions support inline Markdown or a main instruction note with
optional skill notes and folders. CLI and SDK availability depends on the
installed client version; see the linked client documentation below.

An agent is a runnable with `kind: "agent"`. Creating one saves a definition;
it does not create a session or execute its instructions. Open **Agents** to use
the same list and right-hand panel layout as Notes. **Description** contains the
name, description and instructions. **Spec** contains the runtime configuration
and instruction sources as JSON, preserving nested values. Save changes with
the panel's Save button. A referenced main note uses the normal note editor and
its own synchronization.

Use a main instruction note plus optional skill notes or project folders when
instructions should be reusable. The runnable stores references, not copies of
private note bodies. The built-in runtime resolves readable notes again when
the definition is selected, and includes their revisions in the selected
definition. Editing a source note therefore changes the next resolved definition.

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

Replace example IDs with actual note IDs and project folder node IDs. Sources
must be readable by the caller and belong to the runnable's namespace. At most
20 distinct skill references are accepted. Folder expansion is deterministic
and bounded: at most 20 folders, 200 children per folder, 50 distinct notes and
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
