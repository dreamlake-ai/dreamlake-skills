<!-- generated from https://docs.dreamlake.ai/lakeshore/hosts/native-session-lineage.md at 0.1.223 63628016d; do not edit -->

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
