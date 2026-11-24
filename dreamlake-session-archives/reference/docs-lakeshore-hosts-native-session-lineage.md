<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/native-session-lineage.md at 0.1.225 79bd752ea; do not edit -->

# Native session relationships

**Availability:** use the source's explicitly negotiated `nativeLineageMetadata` capability. Installing a native client alone does not enable collection.

Native ancestry is metadata. It does not authorize transcript upload, indexing,
content reads, sharing, terminal attachment, or resuming another agent. It does
not rewrite the legacy managed `parentSessionId` or canonical `parentId`/`rootId`.

The address is `{nativeSessionId, componentId?}` within one authorized source.
`componentId` is the existing canonical native agent/component identifier. IDs
from different sources, roots, owners, enrollments, or providers never join.
An uncollected parent remains an unresolved native address.

| Relation | Meaning | Current evidence |
| --- | --- | --- |
| `spawn` | Explicit creator/parent | Codex spawn index or session metadata; Kimi parentAgentId; DeepSeek origin=subagent plus parentSession |
| `fork` | Explicit inherited-history source | Codex forked_from_id; Kimi forkedFrom; DeepSeek isSeeded plus a retained parentSession and absent origin |
| `component` | A session contains an agent | Claude path plus matching sessionId/agentId/isSidechain; Kimi declared agent metadata |
| `continuation` | A separately identified continuation | Reserved; no current native adapter has sufficient evidence, so ingestion rejects it |

Claude supports nested agents. Its component path and header do not identify the
immediate spawning agent. Message `parentUuid` is not a session/agent parent.
Kimi distinguishes a session fork from an agent fork inside a session. DeepSeek
`parentSession` alone does not distinguish historical forks from subagents;
`isSeeded` without a parent ID cannot identify a fork source. Current ordinary
DeepSeek forks omit that source ID; only explicitly retained historical evidence
can produce a fork edge.

## Protocol

The signed daemon negotiates configuration with
`{metadataProtocolVersion:2,lineageProtocolVersion:1}`. Only that negotiation
adds `capabilities.nativeLineageMetadata`; existing configuration requests and
strict older clients receive their original response shape.

`POST /daemon/session-archive-sources/:sourceId/lineage` uses the existing signed
enrollment/worker envelope. Its payload is `NativeLineageRequest`:

```json
{
  "apiVersion": 1,
  "sourceRevision": "current revision",
  "accountFingerprint": "exact configured account",
  "provider": "claude",
  "localRootId": "exact configured root",
  "nativeSessionId": "session-id",
  "observedAt": "2026-11-23T00:00:00.000Z",
  "edges": [{
    "parent": {"nativeSessionId": "session-id"},
    "child": {"nativeSessionId": "session-id", "componentId": "agent-id"},
    "relation": "component",
    "evidence": "claude-component-header"
  }]
}
```

The server checks current source authority, owner, enrollment, provider, local
root, account fingerprint, revision and applied device configuration in one
fenced transaction. Each immutable edge ID hashes the source and exact evidence
tuple; retries return the original observedAt. Self-links, unsupported evidence,
conflicting parents for one relation, and cycles are rejected. Graph checks stop
at 4,096 edges or 64 ancestor rounds; exceeding the bound fails closed.

`GET /namespaces/:ns/session-archive-sources/:sourceId/lineage?nativeSessionId=...`
returns `{apiVersion:1,sourceId,provider,edges,truncated}`. Each edge includes its
stable `id`, both native addresses, `relation`, `evidence`, and `observedAt`.
Omit both query fields for a bounded source-wide relationship metadata inventory.
This is not a complete session inventory: root-only sessions without relationship
evidence are absent. `componentId` without `nativeSessionId` is invalid.
Optional `componentId` narrows to the exact component; session-only queries
include its components. Responses contain at most 256 edges and never transcript
bodies. Both read and write use existing `ArchiveError` envelopes. Reads return
404 for denied/unavailable sources and 400 for malformed addresses.

`NativeSessionLineage` stores the scoped source/namespace/owner/enrollment/provider,
parent and child addresses plus indexed address keys, relation, evidence, source
revision, observedAt and createdAt. It is separate from any Context schema.

Provider installation, metadata support, archive-body support, and runnable
terminal support are separate capabilities. Kimi sources support this metadata
protocol; Kimi body observations and native terminal registration remain
unsupported. No capability is inferred from the model used by a client.

## Native collection

Nymph's local `session-lineage` command inspects evidence without networking.
Its signed `session-archives report-lineage` command records one explicitly
bound session. Automatic reconciliation requires `session_archives.lineage_enabled = true`,
`work_enabled = true`, and local session-metadata permission. The default remains
off, including after upgrades. Configure and apply each source before collection.

Signed reporting and automatic reconciliation require Nymph 0.1.73 or later.
Version 0.1.72 supports local inspection but rejects the signed lineage route
before sending a report.

```sh
# Inspect one local Codex relationship without sending metadata.
nymph session-lineage --provider codex --root /absolute/codex-home --session NATIVE_SESSION_ID

# Send relationship metadata using an explicit enrolled source binding.
nymph session-archives --config /absolute/nymph.toml \
  --worker-id WORKER_ID --enrollment-id ENROLLMENT_ID \
  report-lineage --source-id SOURCE_ID --native-session-id NATIVE_SESSION_ID
```

Claude component inspection also needs `--metadata` pointing to its relative
subagent JSONL path and `--agent` with the native agent ID. Kimi inspection uses
the relative `state.json` path; DeepSeek uses its relative `.jsonl` or
`.jsonl.zstd` path. For signed reports, the equivalent flags are
`--relative-path` and `--component-id`. The configuration must contain exactly
one matching explicit source binding; a native session ID alone is not authority.

An older running daemon does not gain automatic reconciliation merely because
a newer binary is installed. Apply the configuration with a compatible worker
through the normal idle upgrade process. Preserve active terminals; forced
replacement and service restarts can interrupt their processes.

Automatic scans consider at most 128 directory entries and one bounded native
metadata file per turn, at least 250 ms apart. Completed passes repeat after
60 seconds; failed submissions retry after 30 seconds with the same immutable
edge identity. Sources are capped at 8,192 directories and 65,536 candidate files.
Restarts safely rescan; source/root/revision changes invalidate prior local state.
No lineage operation creates an archive, terminal, body upload, or indexing job.
Kimi and DeepSeek metadata do not enter the Codex/Claude archive scanner.
Kimi `history`, `configurePolicy`, provider-title, and terminal-registration
capabilities remain false. DeepSeek’s default `.jsonl.zstd` format decodes only its first independent
header frame, with 512 KiB compressed-input, 256 KiB decoded-header and 8 MiB
decoder-window limits. Later conversation frames are not decoded. DeepSeek
SQLite persistence is not yet readable by this adapter. Unsupported evidence remains absent rather than inferred.

## Personal session presentation

A personal title, list position, or archive preference is separate from recorded
ancestry. Moving a fork to the top level retains its “forked from” evidence and
all managed permission ceilings. Archiving a parent **from your list** hides
that exact parent; its remaining children appear at the top level with their
own descendants intact. It does not archive the children, stop a process,
delete a conversation, or change upload/indexing consent. Restoring the parent
restores inherited nesting unless a child has its own explicit root placement.

These preferences belong to the authenticated person and namespace. They do not
rename provider files or change another person's list. The older owner operation
`PATCH /namespaces/:ns/terminal-sessions/:id/archive` is different: it sets the
registered session's `archivedAt` and still enforces its existing control rules.

Read exact identities with the read-only endpoint:

```http
POST /namespaces/:ns/session-presentation/query
Content-Type: application/json

{"identities":[{"kind":"native","sourceId":"0123456789abcdef01234567","provider":"codex","nativeSessionId":"native-session-id"}]}
```

A registered identity is `{"kind":"registered","sessionId":"24-hex-id"}`.
Native identities require `sourceId`, `provider`, and `nativeSessionId`, plus
`componentId` for an agent/component. Providers are `codex`, `claude`, `kimi`, and
`deepseek`. A component never aliases its containing session. The server checks
current registry/source access and metadata existence; an uncollected address
reported in authorized lineage is sufficient for a preference, but grants no
content or terminal access. An unavailable native association does not prevent
an independently readable registry identity from retaining its own preference.

The response is `{entries:[...]}` in input order. Each entry contains:

```json
{
  "identity": {"kind":"native","sourceId":"0123456789abcdef01234567","provider":"codex","nativeSessionId":"native-session-id"},
  "aliases": [{"kind":"native","sourceId":"0123456789abcdef01234567","provider":"codex","nativeSessionId":"native-session-id"}],
  "revision": 0,
  "titleOverride": null,
  "placement": "inherit",
  "archived": false
}
```

`aliases` includes the supplied identity and any independently authorized exact
registry/native association. Match aliases exactly, including namespace,
source, provider and component; never join by title or an unscoped native UUID.
One unreadable or nonexistent identity fails the whole batch with `404`; no
partial result is returned. Batches contain 1–100 identities. The query has a
10-second work budget and returns `503` if it cannot finish. A failed query is
unknown state, not permission to overwrite with default values.

Change only the intended fields using the returned revision:

```http
PATCH /namespaces/:ns/session-presentation
Content-Type: application/json

{"identity":{"kind":"native","sourceId":"0123456789abcdef01234567","provider":"codex","nativeSessionId":"native-session-id"},"expectedRevision":0,"patch":{"titleOverride":"Investigate source catalog","placement":"root"}}
```

Patch fields are `titleOverride` (trimmed, nonempty text up to 128 Unicode
characters and 512 UTF-8 bytes, or `null` to restore the normal title),
`placement` (`inherit` or `root`), and `archived` (boolean). Control characters,
invalid Unicode and bidirectional override/isolate characters are rejected.
The response `{entry,previous}` supplies the new state and the previous state.
Undo must use `entry.revision` as `expectedRevision` and restore only the fields
changed by that action from `previous`. A newer change returns `409
session_presentation_revision_conflict`; re-read instead of overwriting it.

Preferences persist across browsers and devices. Storage is bounded to 4,096
identity entries and 4 MiB per account; exceeding either limit returns `409
session_presentation_capacity` without losing existing entries. Metadata-only
labels stay metadata-only. Collectors cannot overwrite personal names or
placement. No transcript bytes are read or indexed by these endpoints. The
built-in resource API exposes the query as a read operation and the patch as a
write operation under the same authenticated boundaries.

## Saved conversation provenance

The archive revision is the retained native byte snapshot. Its conversation
reader is a bounded projection, not a promise that every native record is a
readable message. Compressed native snapshots are retained as encoded
originals;
the message reader does not currently decode them. Tool output, developer context, encrypted blocks and hidden
reasoning are not extracted or indexed. Keep the native revision when a
projection is partial; uploading or reading it does not decrypt opaque content.

`GET /namespaces/:ns/session-archive-sources/:sourceId/sessions/:sessionId/revisions/:revisionId/messages`
returns the existing message page with optional `message.provenance`:

- `inter-agent`: `nativeMessageId`, `author`, `recipient`, and `opaqueContent`.
  The compatibility role is `assistant`; display the agent route rather than
  presenting this as a human request. `opaqueContent: true` means some native
  blocks remain unavailable, including encrypted task payloads. A visible
  envelope alone is not the complete task.
- `inherited`: `nativeSessionId` identifies the explicitly copied source history.
  Preserve the original message role and label it inherited history, not a new
  request to the current child. This native ID grants no access to that session.

Codex inter-agent projection accepts only the exact native agent-message
shape and its plaintext input-text blocks. Inherited response history requires
an exact current-session header, an explicit parent ID, a matching copied
parent header and a new-task boundary within the first 512 KiB/256 records.
If canonical chat events occur in that prefix, response mirrors stay omitted.
Unknown or incomplete provenance never enables a generic response-item fallback.
Pagination retains the bounded provenance in a signed, actor/revision-scoped
cursor, with fresh source authorization on each page. Captured ranges without
that verified prefix do not infer inherited history.
