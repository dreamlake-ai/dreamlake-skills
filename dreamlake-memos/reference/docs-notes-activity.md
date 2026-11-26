<!-- generated from https://docs.dreamlake.ai/notes/activity.md at 0.1.233 ebffa13ba; do not edit -->

# Related resources and activity

Session and resource activity connects work across Memos, artifacts, annotations,
infrastructure stacks, repositories and agent conversations. A memo can be linked to several sessions,
and each session can work on several resources. Explicit relationships are shown
separately from observed access. Opening a memo does not automatically declare it
the session's documentation.

## Related sidebar

The Memo sidebar orders **Related → Table of contents → Comments → …**.
Attachments, variables, version history and extension views remain in **…**.
First is a position, not a forced default: each Memo restores its explicit
sidebar selection. Without a saved selection, the existing Contents/Comments
automatic choice remains. On a narrow or collapsed pane, **Related** opens the
same information in a dialog; closing it returns focus without replacing the editor.

Related groups context into one surface:

1. **Links to this memo**: incoming references from persisted Memo content and
   directed explicit resource relationships, deduplicated by source identity.
2. **Linked resources / outgoing mentions**: explicit affiliations and references
   from this Memo. Direction and reason remain visible.
3. **Contributing sessions**: sessions explicitly linked to, or recorded as creating
   or editing, this Memo. Contribution is distinct from a content backlink.
4. **Recent activity**: recorded reads and edits, loaded when expanded. Access
   alone does not establish a link; this is not a complete edit history.

Incoming content references support `:memo[ID]`, `:memo{id="ID"}`,
leaf `::memo[ID]`, their legacy `:note` equivalents, `#note:ID`, and Markdown links to DreamLake Memo
routes (`/namespace/memos/ID`, legacy `/namespace/notes/ID`, and project
`?note=ID` navigation). Fragments do not duplicate a source. Code, escaped
references, reference text inside unrelated link labels, invalid directives,
external lookalike URLs and bare IDs are excluded. ID links survive title and
filing changes. Public article links (`/namespace/public/slug`) follow the current reserved
permalink and its aliases. Editor routes also support public permalink aliases
and current catalog slugs, following the same permalink-first resolution and
viewer access as navigation. A catalog slug is an existing resource identifier,
not an arbitrary title: changing a Memo title does not change that slug. ID links
remain the stable choice across namespace moves. Conversation transcripts, arbitrary artifact
code/HTML, and program or tool output are not automatically scanned.

Content backlinks follow the persisted Memo projection. Active RTC edits can
arrive after the paced archive sync (normally up to about 30 seconds, longer
under backlog or transport failure). A removed reference disappears after that
projection updates. Existing Memos are indexed in bounded background batches.
During rolling deployments, references known to belong to an older saved body
are omitted until a bounded background audit repairs them; repair latency depends
on the indexed catalog size and archive-loop backlog.
The index stores at most 4,096 distinct reference targets per Memo; exceptionally
large reference catalogs beyond that bound are not exhaustively represented.
Explicit links persist until unlinked; unlinking does not edit source content.

Current permissions are checked on every backlink page. Deleted, archived and
inaccessible source Memos are omitted, without exposing their titles or totals.
Source rows navigate using current names and stable IDs. Browser Back restores
the Memo and selected sidebar view. Session drill-in has a return action.

Each section has independent loading, empty and retry states. **Refresh related
resources** refreshes authorized metadata; returning to the browser also refreshes
it. Expensive reads run on demand, with bounded pagination and cancellation of
obsolete requests. Metadata failures do not disable Memo editing.

### Backlinks API

`GET /resources/note/:id/backlinks?cursor=...` returns
`{resources: Resource[], nextCursor: string | null}`. Each resource has
`kind`, `id`, `name`, `url`, and `writable`, matching the relationship API's
resource descriptor. This endpoint returns incoming **Memo content** references;
explicit typed links remain in the relationships endpoint below.

Pages inspect at most 50 indexed source candidates. Permission filtering can
produce an empty page with a continuation; continue until `nextCursor` is null.
The opaque cursor expires after ten minutes and is bound to the viewer and target.
It grants no access. Invalid, expired or mismatched cursors return
`400 invalid_backlink_cursor`; restart from the first page. No workspace scan or
source-body download occurs during this lookup. This is a REST endpoint; no new
CLI, SDK or agent-tool command is implied.

## Artifact and annotation context

Artifact and annotation viewers have a collapsed side panel with **Related** and
**History** tabs. Open it to inspect linked resources, accessible saved sessions,
and recent recorded activity without replacing the content. The Memo editor can
also record explicit links to artifacts and annotations. Links do not edit content
or change access; unavailable context leaves the editor or viewer usable.

## Optional context

Memos continue to read and save when activity is unavailable or session metadata
is missing or invalid. Activity never grants access, changes content, or retries
a saved edit. An unavailable activity panel does not disable the editor.

Authorized API requests can attach `X-DreamLake-Session-Provider` (`codex`,
`claude`, `browser`, or `agent`), `X-DreamLake-Session-Id` (the external session ID),
and optionally `X-DreamLake-Session-Name`. IDs are scoped to the authenticated
owner. Existing `X-DreamLake-Agent-Id` and `X-DreamLake-Agent-Name` are accepted as
legacy agent context. This attribution is self-reported, not execution proof.

## Relationships

Register a conversation with `POST /resource-sessions`:

```json
{"provider":"codex","externalId":"your-conversation-id","name":"Launch API work"}
```

Use its returned `session.id` as a resource reference. Supported kinds are `note`,
`artifact`, `annotation`, `session`, `repo`, and `infra_stack`. Create an idempotent relationship with
`POST /resource-relationships`:

```json
{
  "source": {"kind": "session", "id": "RETURNED_SESSION_ID"},
  "relation": "documents_in",
  "target": {"kind": "note", "id": "NOTE_ID"}
}
```

| Relation | Source | Target | Optional properties |
|---|---|---|---|
| `defined_by` | InfraStack | Repo | `directory`, `ref`, `description` |
| `works_on` | Session | InfraStack or Repo | `description` |
| `documents_in` | Session | Memo, Artifact or Annotation | `description` |
| `documented_by` | InfraStack | Memo | `description` |
| `related_to` | Any supported resource | Another supported resource | `description` |

`GET /resources/:kind/:id/relationships` returns authorized links in both
directions and a `nextCursor`. Pass it as `cursor` to continue. Each page examines
at most 100 candidate links; hidden resources can yield an empty page with a
continuation. Other owners' private session links are excluded before paging. `DELETE /resource-relationships/:id` removes the association only.
Creation requires write access to the source and read access to the target;
removal requires write access to the source. A link does not share either resource.
When an artifact or annotation is the source, relationship management requires
namespace membership or inherited project write access. Read access suffices when
it is the target of a relationship from a source the caller can manage. A shared annotation's content edit
permission alone does not grant link management. Artifact and annotation detail
responses expose this separate capability as `canManageLinks`. An incoming Memo link remains
removable only by a writer of that source Memo.

Links use stable IDs and survive namespace moves. Inaccessible or deleted targets
are omitted. Session details are private to their authenticated owner. Restoring
a soft-deleted annotation revives its existing catalog identity and therefore
restores still-authorized relationships and retained activity; it is not a new
resource with the same name.

### Catalog identities

Memo, artifact and annotation references use stable 24-character catalog IDs,
not titles, slugs or storage names. Get an artifact's `resourceId` from
`GET /namespaces/:slug/artifacts/:artifactId` (also present in catalog list entries),
or an annotation's `id` from
`GET /namespaces/:slug/annotations/:name`. Both endpoints apply current read
permissions. For example, link a Memo to an annotation:

```json
{
  "source": {"kind": "note", "id": "MEMO_CATALOG_ID"},
  "relation": "related_to",
  "target": {"kind": "annotation", "id": "ANNOTATION_CATALOG_ID"}
}
```

### Saved terminal sessions

Saved terminal sessions are separate from the owner-private conversation context
registered by `/resource-sessions`. Their saved IDs are 24-character IDs;
conversation context IDs are 64-character hashes. Neither can substitute for the
other, and neither is a credential.

`GET /namespaces/:slug/resources/:resourceType/:resourceId/sessions` lists
currently readable saved sessions and returns `canManageLinks`, `hasMore`, and
`nextCursor`. Types are `note`, `artifact`, and `annotation`; use the Memo catalog
ID, artifact logical ID/current slug, or annotation immutable name/current slug,
respectively. Optional `pageSize` is 1–50 (default 25); send `cursor` to continue.
Permission filtering can produce an empty page with a continuation.

`PUT` or `DELETE` at the same path plus `/:sessionId` links or unlinks a saved
session. Both require a JSON body with `sessionNamespaceSlug`. The caller must
be able to manage resource links and read the saved session. Repeating the same
operation is idempotent. `GET /namespaces/:slug/terminal-sessions/:id/resources`
returns authorized links in the reverse direction. These affiliations grant no
new resource permissions or artifact/annotation execution authority.

## Activity

`GET /resources/:kind/:id/activity` returns up to 50 events and an opaque
`nextCursor`; pass it as `before` for the next page. A session feed contains
activity on that session's resources, filtered by the viewer's current access.
`GET /resource-sessions` lists up to 100 of the caller's recent sessions.

Successful authenticated Memo metadata/body, InfraStack metadata/state and
Repo ID reads/edits generate metadata after the response. Artifact catalog detail,
preview metadata reads, catalog registration/apply, slug and preview metadata writes,
plus annotation catalog creation/detail/title/visibility/slug changes, also
record activity against their stable catalog IDs. Upload credentials and read-token
grants do not prove content was read or changed and generate no such event. Opening an existing Memo
editor records a view, not an edit. Repeated reads and views are coalesced
per minute. Failed or anonymous requests and presence/feed polling do not appear.
Direct RTC edits are not yet observed by this API mechanism; this feed is not a
complete edit audit. The standalone `GET /notes/:noteId/content` endpoint is not
currently recorded. Relationship changes are represented by the current explicit
links, not additional activity events. Edits retain request identity, so a repeated
HTTP request can produce another event even when its relationship write is
idempotent. Activity is retained for 90 days. Explicit relationships and
session identities persist independently of activity retention.

A repository relationship identifies relevant source; it does not prove which
commit was applied. Use the existing operation and infrastructure state receipts
for deployment provenance.
