<!-- generated from https://docs.dreamlake.ai/agents/authoring.md at 0.1.191 cd6123c2; do not edit -->

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
private memo bodies. Draft execution resolves readable memos when selected. Published execution uses the captured prompt and skill content from its immutable release. Both paths check current access; a release does not preserve a revoked permission.

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
in the [CLI agent guide](https://cli.dreamlake.ai/agents); Python 0.55.0 examples are in the
[SDK runnable API documentation](https://github.com/fortyfive-labs/dreamlake/blob/5f4c36dd4da43bb854152b90c3709a7979836bcb/docs/api/runnables.md).

## README templates and whole-agent releases

The API, local MCP adapter and agent UI support the release workflow below.

The **Prompt** tab edits instructions. **README** edits or imports a Markdown
file stored in `metadata.readme`. Use `{{prompt}}` to insert the prompt in the
preview. Replacement happens once: placeholders inside the prompt are not
recursively expanded. Existing agents default to a `{{prompt}}` README.
Keep this template outside `metadata.agent`, whose keys configure the runtime.

Edits update an editable **draft**. In **Versions**, **Publish draft** captures
and activates an immutable release. Save agent fields and finish memo sync
first. A release includes the name, description, README template, inline or
memo-backed prompt, argument and tool configuration, channel, metadata,
executable source-version reference, and the resolved instruction/skill content
with each memo's revision and hash. Folder membership is captured at publication.
The referenced memos are individually coherent reads; publication does not lock
all collaborative documents into a simultaneous cross-document transaction.

Release identity is SHA-256 of the canonical whole definition. Optional labels
are display names, not unique identifiers. Publishing identical content reuses
the original immutable release and its label. `publishedDefinitionVersion` is
the active release pointer. Existing `latestVersion` and `/versions` retain their
original executable-source SHA-256 meaning.

| REST surface, under `/namespaces/{namespace}/runnables/{id}` | Behavior |
| --- | --- |
| `GET /definition-versions?page=1&pageSize=20` | Bounded history summaries, without prompt bodies. |
| `POST /definition-versions` | Publish and activate the saved draft. Body: `{"expectedUpdatedAt":"<timestamp from GET>","label":"v1"}`. Label is optional. |
| `GET /definition-versions/{hash}` | Read the frozen definition and prompt after current source-access checks. |
| `POST /definition-versions/{hash}/activate` | Activate an existing release. Body: `{"expectedUpdatedAt":"<timestamp from GET>"}`. Preserves the draft. |

Publish and activate reject stale timestamps with HTTP 409. After an uncertain
write, read the head and history before retrying. **Activate release** provides
rollback without rewriting history or replacing a newer draft. Missing,
deleted, or inaccessible source memos prevent release detail reads and execution;
there is no fallback to the draft. Credentials and permissions remain live and
are not captured as historical authority. The captured definition is capped at 1 MiB.

`GET /agent/definitions?namespace={namespace}` defaults to published releases,
with draft compatibility for agents that have never been published. Add
`view=draft` to inspect drafts. `/agent/chat` accepts an `agentDefinition` with
`id`, catalog `revision`, optional `version` (`draft` or a full release hash),
and `arguments`. Runs retain the selected version and resolved arguments;
subsequent draft edits or activation changes cannot repoint a pinned run.

GraphQL remains read-only: `Runnable.publishedDefinitionVersion` identifies the
active release, and `agentDefinitionVersions(namespaceSlug, id, page, pageSize)`
returns bounded history summaries. Frozen bodies use the authorized REST detail
route. Built-in resource tools discover the same REST schemas. The local MCP
adapter offers `agent_definition_versions`, `agent_definition_version_get`,
`agent_definition_publish`, and `agent_definition_activate`; these do not start
an assistant turn. TypeScript, CLI and Python adapters use the same CAS contract.
