<!-- generated from https://docs.dreamlake.ai/notes/activity.md at 0.1.102 757a8c39; do not edit -->

# Session and resource activity

This feature is in development. Deployment of the API and Notes panel is required;
these endpoints are not a claim about the currently installed CLI or live service.

Session and resource activity connects work across Notes, infrastructure stacks,
repositories and agent conversations. A note can be linked to several sessions,
and each session can work on several resources. Explicit relationships are shown
separately from observed access. Opening a note does not automatically declare it
the session's documentation.

## Sidebar panel

In the Note sidebar button group, keep Comments and Table of contents directly
available. Open the **…** popover for Attachments, Version history, and
**Session / resource activity**. Activity occupies the same sidebar column.

The panel separates two questions:

- **Related resources:** which resources are connected to this note? Explicit
  links and Note references in the currently open text appear together, with one
  row per resource and labels explaining the connection. Repeated mentions do
  not duplicate rows. References use the existing `#note:ID`, `:note[ID]` and
  `:note{id="ID"}` syntax; code examples, escaped references, link labels and
  self-references are excluded. Titles are resolved through the existing Note
  access checks. Missing or inaccessible targets are omitted.
- **Recent access:** who read or edited this resource, in which session, and
  when? Events appear newest first, grouped by day. Opening a resource does not
  create a relationship. A session can therefore appear in access history
  without being explicitly linked to the note.

A mention is derived from the current text and disappears when that reference is
removed. Explicit links persist until unlinked; unlinking does not edit the note.
Incoming mentions from other notes and references inside conversation transcripts
are not indexed yet. The panel does not claim to enumerate those sources or infer
resource identity from ordinary prose. The relationship API still returns stored
explicit links; the Notes UI adds current-text mentions at display time.

Select a session to inspect its resource activity, then return to the note's
activity.
On an editable note, **Link this browser session** creates an explicit
`documents_in` association. A session link does not grant additional access.
The panel loads on demand and can be refreshed independently. Links, mentions
and access history settle separately: an unavailable feed does not hide available
relationships or disable the note, and a failed link request does not hide access
history. Failed sections can be retried; missing metadata never blocks content.
Session details are cleared when the authenticated identity changes.

## Optional context

Notes continue to read and save when activity is unavailable or session metadata
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
`session`, `repo`, and `infra_stack`. Create an idempotent relationship with
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
| `documents_in` | Session | Note | `description` |
| `documented_by` | InfraStack | Note | `description` |
| `related_to` | Any supported resource | Another supported resource | `description` |

`GET /resources/:kind/:id/relationships` returns authorized links in both
directions. `DELETE /resource-relationships/:id` removes the association only.
Creation requires write access to the source and read access to the target;
removal requires write access to the source. A link does not share either resource.
Links use stable IDs and survive namespace moves. Inaccessible or deleted targets
are omitted. Session details are private to their authenticated owner.

## Activity

`GET /resources/:kind/:id/activity` returns up to 50 events and an opaque
`nextCursor`; pass it as `before` for the next page. A session feed contains
activity on that session's resources, filtered by the viewer's current access.
`GET /resource-sessions` lists up to 100 of the caller's recent sessions.

Successful authenticated Note metadata/body/content, InfraStack metadata/state and
Repo ID reads/edits generate metadata after the response. Opening an existing Note
editor records a view, not an edit. Repeated reads and views are coalesced
per minute. Failed or anonymous requests and presence/feed polling do not appear.
Direct RTC edits are not yet observed by this API mechanism; this feed is not a
complete edit audit. Activity is retained for 90 days. Explicit relationships and
session identities persist independently of activity retention.

A repository relationship identifies relevant source; it does not prove which
commit was applied. Use the existing operation and infrastructure state receipts
for deployment provenance.
