<!-- generated from https://docs.dreamlake.ai/api/project-queries.md at 0.1.102 757a8c39; do not edit -->

# Project and Note queries

This reference describes the implementation branch. It does not establish that
these fields are deployed to staging or production. Verify the target server's
schema before switching a client. Existing mutation routes remain REST; Note
content, CRDT synchronization, and revision-protected editing are unchanged.

## Separate associations from choices

| Question | GraphQL | REST |
|---|---|---|
| Which projects can this viewer access? | `projectCatalog` | `GET /namespaces/:namespace/projects?search=design&page=1&pageSize=50` |
| Where is this Note actually associated? | `note.nodes` | `GET /namespaces/:namespace/resources/note/:noteId/projects?view=nodes` |
| Which Bindrs can the picker offer in this project? | `bindrs` | `GET /namespaces/:namespace/projects/:projectSlug/bindrs?view=choices&search=design&first=20` |

The GraphQL resolvers and these REST views use the same underlying visibility,
project permission, resource-readability, and association services. Their wire
shapes differ: GraphQL selects fields and wraps results in `data`; REST returns
its resource response directly. The `view=nodes` REST association view permits
authorized anonymous reads of public resources; the legacy default response
requires a signed-in caller. Unreadable resources are not exposed by the shared
service.

The existing resource-project REST response without `view=nodes` remains a
compatibility response that mixes candidate projects with `bound` and `canBind`.
New clients should use the views above instead. The existing Bindr response
without `view=choices` also keeps its prior tree-list contract.

## Note authority on filing reads (implementation)

Project access does not grant access to a filed Note. REST project-resource,
Bindr-member and folder-child listings omit unreadable Notes before name search,
sorting, page offsets and totals. Bindr-tree member counts include only visible
live members. Legacy Note reverse project and Bindr lookups return 404 when
the Note is unreadable; project-role flags do not bypass this prerequisite.
The same independent check protects GraphQL
Note metadata, children and Note associations. Cached filing names and Note IDs
are not returned when Note access is denied. Folders and other resource types
retain their existing rules.

Each filing read resolves current project access, live Note ownership and Note
access in one database read snapshot. Accepted shares qualify by the active
recipient and Note ID while the live share link remains enabled; cached grant
namespace and stored role do not replace current policy. The live Note share
role controls independent link editing. Explicit user/team Project grants also
authorize live same-namespace attachments: READ permits reading, while WRITE
and ADMIN permit supported content editing. Public Project visibility alone
does not open a private Note. Arbitrary legacy foreign-namespace mounts remain unsupported even
when both resources are readable; this change does not enable transfer bindings,
writers or cutover.

A snapshot is local to a read operation. Separate requests and GraphQL field
resolutions can observe newer state; they are not a durable access capability.
Subsequent content reads and mutations must recheck current authority.

The compatibility roots `projects`, `project` and `Namespace.projects` share
authorization within one request. A namespace's project list is read once
however many aliases select it, and `project` on a project those reads
already authorized returns that project rather than authorizing it again. The
result therefore reflects authorization from earlier in the same request.
Nothing is shared across requests, and `children` and `bindrs` still
re-authorize in their own snapshot. Their arguments, results and ordering are
unchanged; new clients should still use `projectCatalog`.

These roots remain unbounded. `projects` without `namespaceSlug` and
`namespaces { projects }` return every visible project in one response, and the
GraphQL endpoint does not reject queries by depth, alias count or cost. The
request-local sharing above is a partial cost reduction
([#1370](https://github.com/dreamlake-ai/dreamlake-workspace/issues/1370)),
not a limit.

## Query a Note's locations

```graphql
query NoteLocations($namespace: String!, $noteId: ID!) {
  note(namespaceSlug: $namespace, id: $noteId) {
    id
    name
    nodes {
      id
      name
      path
      project {
        id
        slug
        displayName
      }
      bindrs {
        id
        name
        parentId
      }
    }
  }
}
```

Variables below use illustrative values. Replace them with a namespace and Note
ID that the caller can read:

```json
{
  "namespace": "example-team",
  "noteId": "000000000000000000000001"
}
```

`nodes` contains actual resource Nodes in visible projects, never candidate
projects. An empty list means no visible associations, not proof that no hidden
association exists. An unreadable or missing Note returns `note: null`.

`Node.path` is the existing comma-delimited **ancestor path**, not the full file
path or a parent ID. For example, a Node named `API design` with
`path: ",example-project,design-docs,"` sits beneath that ancestor path. Project
ownership comes from `projectNodeId` and the resolved `project`, not parsing the
path. No folder or storage migration is part of these reads.

`node.bindrs` means Bindrs **tagging that Node**, not every Bindr owned by the
project. It is resolved through membership records. Project objects retain the
GraphQL `Node` type and stable ID for Apollo normalization.

The equivalent REST view returns `{ nodes, total }`; each Node includes its
project and attached Bindrs. No `bound` or `canBind` field is needed in that view.

## Search project choices

```graphql
query ProjectChoices($namespace: String!, $search: String, $page: Int, $pageSize: Int) {
  projectCatalog(namespaceSlug: $namespace, search: $search, page: $page, pageSize: $pageSize) {
    projects {
      id
      slug
      displayName
      permissions {
        role
        project { read update delete manageGrants }
        content { read create delete }
      }
    }
    total
    page
    pageSize
    totalPages
    canCreate
  }
}
```

```json
{
  "namespace": "example-team",
  "search": "design",
  "page": 1,
  "pageSize": 50
}
```

The catalog is scoped to one namespace and returns authorized projects,
including project-specific grants. Search is performed on the server. The
default page size is 50; the maximum is 200. Fetch subsequent pages when needed
instead of treating the first page as the complete set of projects.

`projectCatalog` also accepts `counts: Boolean = true`. A picker that never
shows `bindrCount`, `datasetCount`, `pipelineCount` or `activeJobCount` can pass
`counts: false` so the server skips their aggregation on every page; those four
fields then return `null`. Projects, `total`, `canCreate`, `role` and
`permissions` are the same either way. Omitting the argument keeps the counts.
A server without this argument rejects the whole query, so check the target
schema before sending it.

`canCreate` is permission to create a project in the namespace.
`permissions.content.create` is permission to add content within a particular
project. For an add-project picker, exclude projects already present in
`note.nodes` and offer projects with content creation permission. The mutation
still checks project authorization and resource readability. Under the
released backend [Project resource access contract](https://docs.dreamlake.ai/dev/notes/project-resource-sharing),
new attachments also require the resource's independent sharing-management
permission: read access alone cannot redistribute it. Authorization is
re-evaluated in the mutation transaction.

## Search Bindr choices on demand

```graphql
query BindrChoices($projectId: ID!, $search: String, $first: Int, $after: String) {
  bindrs(projectId: $projectId, search: $search, first: $first, after: $after) {
    nodes { id name parentId projectNodeId }
    pageInfo { endCursor hasNextPage }
  }
}
```

```json
{
  "projectId": "000000000000000000000002",
  "search": "design",
  "first": 20,
  "after": null
}
```

The default page size is 20; the maximum is 100. Run this only when the picker needs choices. For another page, pass the returned
`endCursor` as `after`; reset the cursor whenever the project or search changes.
Treat cursors as opaque. REST uses the same `{ nodes, pageInfo }` response shape
and accepts the cursor as an URL-encoded `after` query parameter. The REST path
identifies the project by namespace and slug; GraphQL uses its Node ID.

These are live listings, not transactionally frozen snapshots. Concurrent edits
may change choices between requests. Mutations remain authoritative and must
revalidate permissions and membership constraints.

## Execute a GraphQL request

Save any query above to `query.graphql` and its variables to `variables.json`.
Set the API base URL and an existing DreamLake token in your shell environment:

```bash
export DREAMLAKE_API_URL='http://localhost:3001'
# Set DREAMLAKE_TOKEN securely to your existing token; do not commit it.
python3 - <<'PY'
import json
import os
import urllib.request

with open('query.graphql') as source:
    query = source.read()
with open('variables.json') as source:
    variables = json.load(source)
request = urllib.request.Request(
    os.environ['DREAMLAKE_API_URL'].rstrip('/') + '/graphql',
    data=json.dumps({'query': query, 'variables': variables}).encode(),
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.environ['DREAMLAKE_TOKEN'],
    },
)
with urllib.request.urlopen(request) as response:
    result = json.load(response)
if result.get('errors'):
    raise RuntimeError(result['errors'])
print(json.dumps(result['data'], indent=2))
PY
```

GraphQL errors can arrive with HTTP 200; inspect `errors` before using `data`.
For Apollo clients, select stable IDs and keep project objects as `Node`.
Refresh associations after existing REST mutations. Cancel superseded picker
requests, prevent stale identity responses from entering the cache, and isolate
explicit anonymous previews from authenticated cache entries.

## Ownership preservation inventory

`GET /namespaces/:namespace/ownership/resources/project/:id/manifest` requires
current source namespace ownership. Project ADMIN alone does not authorize this
inventory. The response adds `preservation` alongside the existing structure,
filings, grant IDs and `expectedVersion`:

| Field | Meaning |
|---|---|
| `preservation.projectGrants` | Existing grant `id`, `projectId`, `granteeId`, `teamId`, `role`, `kind` (`direct-user`, `team`, or `invalid`) and `recipientState`. Team eligibility is not established. |
| `preservation.noteShares` | Accepted record `id`, `noteId`, `userId`, cached `namespaceId`, `ownerMatches`, `storedRole`, `sharingEnabled`, live `linkRole` and `recipientState`. Includes all live source-owned Notes filed in this project, even if not selected for transfer. |
| `recipientState` | `active`, `unavailable`, or `unresolved`; legacy identities that cannot be checked remain explicit. These states do not establish effective destination access. |

`linkRole` is `read` or `write` while sharing is enabled, otherwise `null`.
It can differ from the accepted record's `storedRole`; namespace membership may
confer stronger access. No bearer token, private Note body or storage key is
returned. Foreign-owned and deleted Notes do not expose their acceptance records.
The source version binds the inventory and sharing policy. Incomplete parent
inventory or an aggregate above 10,000 Note identities, grants and accepted
records returns `422 MANIFEST_TOO_LARGE`, never a truncated preservation list.

Project transfer previews also include this inventory and `destinationAuthority`
with `action: "ownership.accept"`, the requested `namespaceId`, checked `actorId`
and `allowed`. Authority and inventory are read in the same transaction. A
source-only caller receives `allowed: false` without destination names or
authority-parent details. Authorized authority evidence participates in the
preview dependency hash; it is not durable acceptance or a reservation.

These fields report existing access records, not approved retention. Whole-Project
execution requires the complete owned-Note manifest, an enabled Project adapter
and explicit destination-owner acceptance under the selected retention policy.
Reading the manifest or preview changes no grant, filing or ownership.

## External Note filing evidence

The same owner-only manifest and project preview add `externalFilings` for all
live source-owned Notes filed in the root project, including unselected Notes.
Each record retains `filingId`, `projectId`, `noteId` and
`currentNoteNamespaceId`. A preview adds `proposedNoteNamespaceId` only when that
Note is explicitly selected. This does not select or move the external project.

`currentActorProjectRead` and `currentActorNoteRead` are independent observations
in the same transaction. Source ownership establishes the caller's current Note
authority; every external project's current `project:read` policy is checked
separately. Project roles and Bindr tags never grant authority over a foreign
Note. The future required policy is `project-and-note`; every record retains
`disposition: "requires-reviewed-cross-owner-support"`. Current access is not
proof of access after the proposed owner changes, nor a new reader capability.

Only a caller with current access to the external project receives its
`projectNamespaceId`, filing `path`/`name` and `bindrMemberships` (membership ID
and Bindr ID). Those fields are `null` when denied; opaque filing/project/Note
IDs remain so a reference cannot silently disappear. Private parent, filing,
Bindr membership provenance and grant data enter deterministic source hashes,
not the response. Current actor/project decisions enter preview dependencies.

The complete external inventory has a separate 10,000-record aggregate limit
across Note identities, filings, project parents, Bindr memberships, Bindrs and
project grants. Overflow returns `422 MANIFEST_TOO_LARGE`. Missing, deleted or
mismatched project/Bindr parents and unresolved namespace identity return
`422 EXTERNAL_FILING_RECONCILIATION_REQUIRED`; no partial evidence is returned.
Existing per-Note bounds and execution gates still apply. Artifact ownership
and its adapter remain separate, unsupported work. No reference or grant is
detached, approved for retention or mutated by these reads.

## Project resource inheritance

Public Project metadata access never opens a private attachment. Explicit
Project user/team grants contribute READ or supported content WRITE to current
and future attachments. Resource-own permissions and other live Project grants
remain valid; removal affects only its corresponding contribution.

In the compatibility project-choice response, `canBind` requires Project WRITE
or ADMIN plus independent resource sharing-management authority for a new
attachment. A readable resource or public visibility does not permit
redistribution. Grouping an existing live attachment into a Bindr in that same
Project requires Project write authority and resource readability, without
another sharing-management check. `bindable=true` uses the same rule.

Resource lists filter before paging and totals, and reverse Project/Bindr queries
check resource readability. A filing Node requires both underlying resource read
permission and access to its containing Project. Canonical resource references
are resolved from live catalog identities, including historical mounts without
`metadata.resourceRef`; editable filing titles are not resource addresses.

## Completed-transfer filings and historical read aliases

The [whole-Project transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer) removes
other-Project Note mounts by default, ending their inherited access without
deleting the moved Notes or their data. Explicit opt-in preserves
approved existing foreign-namespace Note mounts only through private completed
journal evidence and current ownership history. The destination approves their
existing live Project audience; implicit public READ never exposes private Notes.
A later aborted transfer requires exact source-restoration proof. Arbitrary new
foreign mounts or expanded cross-namespace Project grants remain unsupported.

Resource references use the Note's canonical current namespace. Filing Project
navigation retains its own namespace. Old namespace Note/NoteFile URLs may resolve
only as verified read aliases and reauthorize in the current namespace; all writes
remain canonical. Historical content/publication addresses are not rewritten.
Whole-Project transfer is production-accepted; same-namespace sharing continues
independently. See the transfer contract for the bounded live verification scope.

REST filing Node/Project responses carry their actual `namespaceSlug`;
GraphQL `Project.namespace { slug }` identifies the filing Project's namespace.
Server-derived, top-level `resourceNamespaceId`/`resourceNamespaceSlug` identify
the canonical Note namespace independently, joined from current live Note and
Namespace records. Editable Node metadata cannot supply those fields; unresolved
owners return null rather than a guessed namespace.
Do not derive a Project backlink from the Note's namespace or Project name alone:
retained Projects in different namespaces may have the same name.

Project URLs can retain their original filing context with a
`noteNamespace` selector for the current Note owner. A new Note created/extracted
inside that foreign-Project Note pane uses the Note-owner namespace and omits an
automatic foreign Project mount; Project-column creation uses the actual Project
namespace. These routes retain their independent creation checks.

## Whole-Project transfer plan and blocked items

`GET /namespaces/:slug/ownership/resources/project/:id/transfer-plan` requires
current source-namespace owner authority. A compatible backend includes direct
ordinary files, images, videos and supported byte-backed leaves alongside the
Project and its owned Notes. The optional `fileCounts` object reports `file`,
`image` and `video` counts; other supported byte-backed leaves count as files.
Clients must still inspect the complete server plan and execution readiness.

A rejected plan can return HTTP 422 with owner-only
`error.details.blockers`. Each blocker includes `code`, `action` and, where
applicable, `item: { id, name, path, kind }`. For example, an episode Node can
produce `UNSUPPORTED_PROJECT_CONTENT`. Direct Project files retain their existing
storage metadata; a missing physical object does not become a transfer blocker. The dialog lists these affected
items rather than showing only a generic failure. No storage key, signed URL,
credential or private execution journal belongs in this response.

This list does not make the inventory partial or authorize transfer around a
blocked item. Fix the item, obtain a fresh complete plan and review again. Existing
authorization and not-found responses must not disclose this owner-only inventory.
See the [transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer) for scope, storage
semantics and existing signed-URL lifetimes.

## Active Project transfer listing

`GET /namespaces/:slug/ownership/transfers` accepts `direction=incoming|outgoing`
(default `incoming`). Incoming listing requires current `ownership.accept`
authority; outgoing requires `ownership.transferOut`. The optional `resourceType`
accepts only canonical `project`, `source` or `note`, never internal execution
keys. Omitting it keeps the existing supported-resource listing.

By default, or with `activeOnly=false`, the response remains
`{ apiVersion: 1, operations: [...] }` for at most the most recent 100 requests;
it has no `hasMore` field and is not complete history. `activeOnly` accepts only
`true` or `false`. With `activeOnly=true`, the database query excludes expired
pending requests and selects unexpired `pending`, `preparing`, `committing`,
`aborting` and `recovery-required` states. The response is
`{ apiVersion: 1, operations: [...], hasMore: boolean }`, with at most 100
operations. `hasMore` signals the bounded query limit, not an exact total.

The Web Projects banner and default Transfers page request
`activeOnly=true&resourceType=project`. This keeps newer completed history from
hiding older active requests. A capped response is displayed as `100+`, without
claiming an exact count of pending requests. An active response missing `hasMore`
is an incompatible response, not an empty inbox. These query options add no
endpoint, schema migration, CLI flag or SDK argument. Public Project resource
references remain `project` across compatible execution versions.

## Recursive Project search (implementation)

The Project/folder browser can request ranked descendant search:

```http
GET /nodes/children?namespace=example&project=robotics&search=report&recursive=true&pageSize=50
```

Use `parentId` instead of `namespace` and `project` to search within one folder.
The server authorizes the containing Project and checks current resource access
on every page. Results never cross the Project boundary. Direct matches come
first, followed by descendants; within each group, exact names precede name
prefixes and then substrings. Equal ranks use stable path/name order. Returned
`searchParentPath`, `searchAncestors`, and `pathIds` describe the actual parent
chain, so opening a nested result preserves its breadcrumb.

The response identifies `searchMode: "project-recursive-v1"` and returns `nodes`,
`hasMore`, and `nextCursor`. It does **not** return an exact total or page count.
Send `after=<nextCursor>` with the same search scope to continue. An empty page
with `hasMore: true` means the bounded candidate page contained no readable
results; it does not mean the search is exhausted. The browser continues normal
cursor pagination rather than fetching every folder or filtering a downloaded
Project tree. Servers without this mode produce an explicit unavailable/upgrade
message; the browser does not silently substitute direct-child-only results.

Cursors are encrypted and authenticated with a purpose-separated key derived
from the existing server signing secret. Their scan positions can include
unreadable candidates and must never be exposed as plain or merely signed JSON.
They bind the actor, namespace, Project, folder path, query, mode, and rank
position, expire after one hour, and grant no access. Changing the query/scope,
expiry, or signing-key rotation requires restarting the search.

Each request returns at most 50 results and examines at most 200 matching
candidates for resource authorization. These are **not** bounds on index keys
examined: sparse case-insensitive substring searches can scan more keys within
the scoped Project. Candidate queries use the existing unique
`Node(namespaceId, path, name)` index with an explicit hint and index-order sort;
raw candidate work shares a 2-second database `maxTimeMS` budget. Resolving only
the returned page's ancestry has a separate 2-second database budget and a
2,500-ancestor metadata limit. Authorization and the complete HTTP request are
not covered by those two database budgets. Exhausted query, index, or ancestry
budgets return an explicit unavailable/error response rather than an unindexed
fallback or a misleading empty success. Provision/verify that existing index
and the signing-key configuration before enabling the new browser consumer.

Ordinary browsing without `recursive=true` keeps its existing child-only
ordering, page offsets, counts, and response format. This change adds no CLI
command, mutation, payload download, or new public skill procedure.
