<!-- generated from https://docs.dreamlake.ai/dev/notes/project-resource-sharing.md at 0.1.102 757a8c39; do not edit -->

# Project resource access inheritance

The Project-sharing backend is released at revision
`a7736bd3346824dc504c90de4354ff8994130738`. The companion Web update is
released at `0d015e6c13ece3fec811286f3926000f6fa82b30`; CLI 0.62.0 and Python
SDK 0.29.0 are published with isolated installed-package checks. Source, server,
Web and installed client versions must still be checked separately.

Production checks confirm public Project reads, hidden private Notes, owner
attachment/detachment and preservation of independent access. Explicit recipient
READ/WRITE has real-MongoDB regression coverage; its production matrix still
requires a second controlled identity. Live storage credentials have not been
probed for cross-resource denial. Short-lived URLs and existing RTC sessions
retain the limits below.

A resource keeps its namespace owner and independent sharing policy. Its
effective access is the union of that policy and every live Project attachment.
Project READ grants content reading; WRITE and ADMIN grant supported content
editing, never resource ownership, sharing management, deletion or infrastructure credentials. Resource-scoped, short-lived upload
credentials follow the supported content write policy.
Public Projects expose only independently public resources to general visitors.
A public Project alone never authorizes a private resource: visitors need an
explicit Project grant or access under the resource's independent policy. Explicit user/team grants cover private attachments
regardless of Project visibility, including attachments added later. Sharing never copies Note/Source share tokens or acceptance
records, and never stores a snapshot of attachments at grant time.

Removing an attachment, deleting a Project, removing a grant or
leaving its team removes only that source of access. Independent membership,
public visibility, links and other Project grants continue to apply. The same
rule applies at canonical resource URLs, not only inside Project views.

Attachments require Project content-create authority and the resource's own
sharing-management authority. A readable resource cannot be attached by a reader
to redistribute it. Existing idempotent attachments do not grant a new scope.
Expanding Project grants rechecks sharing authority over its
current attached resources. New cross-namespace attachments remain unsupported. The
[whole-Project transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer) has a narrow
exception for existing filings explicitly approved in completed transfer history;
it does not permit arbitrary new foreign mounts or Project grant expansion.

Making a Project public never republishes its private attachments. No public
confirmation or sharing-time snapshot is necessary for publication. The public
Project's implicit READ is not a grant to its private resources. Existing
namespace membership and independent resource grants retain their meaning.

Source references continue to use `ProjectSourceBinding` and refer to the whole
Source; Bindr references retain `BindrSourceReference`. No extra relationship
table is introduced. Unifying these existing relations with resource Nodes and
BindrMember is a future optimization that requires its own migration, not a
prerequisite for this access contract. Live Source references contribute USE/EDIT
for content under this contract, never Source ADMIN or Connection credentials. Env attachments use live resource nodes,
like Note, Artifact, Annotation and Workflow. Infrastructure state, Vault secrets
and Host credentials are not published by a content grant.

Issued read URLs and resource-scoped upload credentials retain their existing
finite lifetime after revocation. Storage operations already in progress cannot
be rolled back by a later database grant change. Native Note RTC room
capabilities retain their existing revocation limitation; a database grant change
must not be described as immediate eviction of an already connected editor.
Ownership transfer remains a separate, execution-gated feature.

## Release compatibility and acceptance

There is no Prisma schema change or required data migration. Existing explicit
Project grants immediately cover existing attachments when the server changes;
review their recipients and attachment inventory before enabling this behavior.
No publication-time snapshot or copied share-link records are introduced.

Release the backend before the Web client and optional CLI/Python releases.
Older servers do not support the Env attachment type, Source by-name fallback,
or this inherited authorization contract. The Web change does not modify the
artifact-frame protocol and requires no companion frame release. Historical
resource mounts resolve canonical addresses from the live catalog at read time,
without modifying stored metadata or guessing addresses from filing titles.

Project-only writers must receive credentials with a resource-specific session
policy. Static custom-S3/MinIO identities and unscoped STS fallback are refused
with `DELEGATED_UPLOAD_UNSUPPORTED` (403). Configure a working scoped broker for
delegated uploads; validate that issued credentials cannot read/write another
resource prefix against the actual storage policy before production acceptance.
Unit validation of the requested session policy does not prove live bucket
policy enforcement.

Acceptance covers anonymous/public-only visitors, explicit READ and WRITE,
later attachments, multiple Projects, revocation/detachment, independent share
links, and historical mounts. Backend production evidence currently covers the
public/private and owner attachment path; explicit recipient and live storage
isolation checks remain separate. Web production reads and installed CLI/SDK
request contracts have also been verified; they do not replace that cross-user
production matrix. Ownership transfer is separate.
