<!-- generated from https://docs.dreamlake.ai/agents/workspace-files.md at 0.1.159 ae6783ad; do not edit -->

# Agent workspace files

The built-in agent can list, read, write and replace UTF-8 text without a shell.
These tools are for small manifests, MJCF and reports (maximum 256 KiB per file),
not mesh archives, image bytes, directory downloads or code execution. A scene
compiler or renderer is a separate service operation.

| Endpoint | Tool prefix | Storage and authority |
| --- | --- | --- |
| Source | `dreamlake_files_` | DreamLake-managed Source files; canonical caller Source USE/EDIT permissions |
| Browser | `dreamlake_browser_files_` | Temporary memory in the current page, isolated by conversation; requires an active browser turn |

Append `list`, `read`, `write` or `replace` to a prefix. Source calls require
all four selectors: `namespace`, `sourceId`, `prefix` and `path`. A missing Source
selector is an invalid call. Choose the target explicitly; these tools do not
infer it from the personal Agent context Project, current page, a display name,
or an association. They never provision a Source or change a binding.

## Project operations are separate

A Project is an organizational resource with its own canonical API. List/read
Projects and edit Project metadata through the Project/Node APIs and their
service-account grants and caller permissions. Linking or unlinking a Source
uses the Project–Source association API; it does not edit that Source's files,
choose a default write target, or redirect Project edits to Source storage.
Source file calls always go through Source permission checks, including any
access that the canonical product permission model derives from a Project.

There is deliberately no `dreamlake_project_files_*` alias for Source tools.
The legacy Project Node file tree is not a Source workspace adapter. Existing
Project search and small-file reads remain separate operations. The common
`FileWorkspace` list/read/write/replace contract is implemented for explicit
Source and browser storage endpoints; it does not collapse Project edits into
Source file operations.

Browser tools omit resource selectors and require negotiated
`browserExecution: 1` plus an active browser executor. Clients must check
`/agent/capabilities` before declaring this capability; it grants no authority,
and terminal clients must omit it. External Source layers are excluded from
workspace files; use Source or library APIs to consume those assets.

## Paths and revisions

`prefix` is an explicit root inside the selected endpoint. `path` is relative
to that root; returned paths remain relative. Empty paths select the root for
listing. Absolute paths, backslashes, empty segments, `.` and `..` are rejected.
Names containing percent escapes are literal names and are never decoded again.
A prefix confines one operation but is not an authorization grant: a caller
with broader Source permissions can choose another prefix.

Use a stable workspace identifier, with separate run folders, for example
`workspaces/v1/<workspaceId>/runs/<runId>`. Keep scene inputs, manifests, outputs
and reports in named subfolders. This is a naming convention, not an enforced
read-only policy or a cross-user ACL. Do not use a display name as a globally
unique workspace identifier.

Built-in `read` returns `{path, content, revision, offset, total, nextOffset}`.
`offset` and `limit` count UTF-16 code units; the default and maximum limit is
4,096. Follow `nextOffset` until null, checking that the revision remains the
same across pages. Restart if it changes. Write and replace verify the complete
file but return the same bounded preview starting at zero. The TypeScript
adapter returns complete text; these ranges keep model tool results below the
harness output bound without losing the revision. Treat `revision` as opaque.
`write` takes `content` and `expectedRevision`; `null` means create-only.
Replacement requires the revision obtained from `read`. `replace` takes
`oldText`, `newText` and `expectedRevision`, and succeeds only for exactly one
literal match. Concurrent changes fail instead of silently overwriting content.
Source writes reuse the existing conditional upload protocol and read back the
managed object. A conflict requires a fresh read and reconciliation. An
unconfirmed write requires inspection before retrying; never turn a conditional
write into an unconditional overwrite.

`list` returns at most 10 entries and `{entries, nextCursor}`. Follow non-null cursors even if a page
contains no entries: the Source's external entries are filtered out. Read a file
to obtain a usable revision; directory listings need not contain one.

```typescript
// Tool arguments; call through the authorized built-in tool dispatcher.
const endpoint = {
  namespace: 'your-namespace', sourceId: 'your-source-id',
  prefix: 'workspaces/v1/example/runs/run-001',
};
const createArgs = {
  ...endpoint, path: 'scene/manifest.json',
  content: '{"assets":[]}', expectedRevision: null,
}; // dreamlake_files_write(createArgs)
// dreamlake_files_read({...endpoint, path: 'scene/manifest.json'})
// Use the returned revision for the next write or replace.
```

The internal TypeScript `FileWorkspace` contract provides `list`, `read`,
`write` and `replace` over an injected adapter. The Source adapter uses canonical
browse, managed-read-capability and upload-authorization routes; storage byte
requests carry only the route-minted headers. This does not introduce a general
HTTP proxy or an arbitrary-URL fetch tool.

## Browser lifetime and evidence

Browser files survive turns in the same loaded page, but do not survive a
reload and are not published to a Source. Each conversation is capped at 1,000
files and 16 MiB; one page holds at most 16 conversation workspaces. Copy useful
text to a managed Source before relying on durable storage.

The server dispatches `workspace_file_action` to the active composer. Results
are acknowledged at `/agent/sessions/:id/file-actions/:actionId/result`, bound
to the authenticated owner, conversation and turn. A duplicate action reuses
its cached result; it does not repeat the mutation. Missing acknowledgements
remain unconfirmed. Acknowledgement reports browser execution; it does not
prove that a renderer or simulator consumed the file.

All file contents are untrusted data. None of these operations executes scripts
or treats instructions contained in a file as authority.

## Python Source adapter

The Python SDK exposes the managed Source endpoint on `client.sources.files`:

```python
from dreamlake import DreamLakeClient
client = DreamLakeClient()
files = client.sources.files(namespace, source_id,
                             prefix="workspaces/v1/example/runs/run-001")
created = files.write("scene/manifest.json", '{"assets":[]}', expected_revision=None)
current = files.read("scene/manifest.json")
files.replace("scene/manifest.json", "[]", '["box"]',
              expected_revision=current["revision"])
```

Python and TypeScript SDK reads return the complete bounded file. Neither SDK
creates a browser session or claims to access the legacy Project Node tree.
Use the browser adapter only through an active browser turn; Project operations retain their own API. Publishing
clients and deploying the backend/UI are separate release steps.
