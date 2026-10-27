# Transfer one resource's ownership

Use `ownership transfer` for a single Artifact, Env (`scene` is an alias),
Annotation, Pipeline or, in the source candidate, Source. A standalone Note uses
the same protocol through `notes transfer` (skill `dreamlake-notes`); a whole
Project uses [projects](projects.md). Each type needs its own versioned server
capability with `metadataOnly: true` and an enabled transfer plan; the CLI
recognising a type is not evidence that its adapter shipped or is active.
Pipeline needs the `pipelineTransfer` version-1 capability (CLI 0.83 lacks this
consumer); Source needs `sourceTransfer` version 1.

```bash
dreamlake ownership capabilities --namespace alice
dreamlake ownership transfer artifact ARTIFACT_ID --namespace alice --to acme --dry-run --out review.json
dreamlake ownership transfer artifact ARTIFACT_ID --namespace alice --to acme --confirm --request-file review.json
dreamlake ownership status OPERATION_ID --namespace acme
```

Request format and the `ownership preview`, `create`, `accept`, `reject`,
`cancel`, `list`, `inspect` and `manifest` commands:
[Ownership transfers](../reference/cli-ownership.md#transfer-an-individual-resource).

- Metadata only: the resource ID, opaque version, policy and stable key are
  preserved, and no content, blobs, graph, version history or RTC history is read
  or copied. Never load content to prepare a transfer.
- Requests bind type, ID, metadata version, both namespaces, preservation policy,
  preview hash and idempotency key. Review the full access inventory and
  blockers, then submit that exact file. Keep file and key after an uncertain
  response and inspect `ownership status`; the CLI never retries a mutation,
  rebuilds a preview or falls back to a legacy path.
- Access and external filing preservation are required; blockers stop
  submission without changing ownership. A Source transfer can block on external
  backing stores, active physical mutations, unsupported Project bindings or
  audiences; it copies no objects, rewrites no history and never retargets live
  provider work or credentials.
- A source-namespace actor requests and an authorized destination actor accepts
  (inbox, or `ownership accept`; expiry:
  [ownership](../reference/cli-ownership.md#source-requires-its-own-enabled-metadata-only-capability)). Personal
  namespaces need their own actor; active organization members use the server's
  current action capabilities. `--accept-if-authorized --wait` verifies
  destination authority first; `--accept-if-owner` is a compatibility alias; a
  bounded wait ending is not cancellation.
- `STALE_PREVIEW`, `LOST_AUTHORITY`, `IDEMPOTENCY_CONFLICT` and
  `RECOVERY_REQUIRED` behave as in [projects](projects.md#recovery). Exact
  saved-key replay can reach the server while new admission is paused; an unsent
  key stays blocked.
- Not enabled here: Infrastructure, Library, Workflow, Bindr, Chat, files and
  datasets. Use their own commands; never substitute a raw ownership PATCH, a
  copy/delete sequence or another resource type's capability.
- `ownership restore` is unsupported without a retained deletion snapshot
  (`PROJECT_SNAPSHOT_REQUIRED`); Source deletion is terminal
  (`SOURCE_DELETE_TERMINAL`), and Source disable/enable is the reversible action.
  A proposed 30-day recovery window is not shipped behavior.
