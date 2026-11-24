<!-- generated from https://docs.dreamlake.ai/dev/notes/project-resource-sharing.md at 0.1.226 2adcb7d24; do not edit -->

# Project resource access inheritance

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
Expanding Project grants rechecks sharing authority over its current attached
resources. New cross-namespace attachments remain unsupported. The
[whole-Project transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer) has a narrow
exception for existing filings explicitly approved in completed transfer history;
it does not permit arbitrary new foreign mounts or Project grant expansion.

Bindr tagging can reference an existing Memo filing approved by completed
transfer history. The caller needs current read authority for the Memo and its
filing, plus content-create authority in the Bindr's Project. The server rechecks
these inside the transaction and fences the Memo, Project and filing. Invalid
transfer proof, removed filings and revoked access are refused, including repeats
of an existing tag. A tag adds no attachment or sharing grant. An existing
grant-admitted Memo filing can be tagged only within its admitted Project,
while the grant and current read authority remain valid. The grant's audience,
role ceiling, expiry and ownership stay unchanged. Revocation removes its
filing and tags; expired or invalid grants reject new tags and repeated tags.
Other grant-admitted resource types and cross-Project grant tagging remain
unsupported.

Making a Project public never republishes its private attachments. No public
confirmation or sharing-time snapshot is necessary for publication. The public
Project's implicit READ is not a grant to its private resources. Existing
namespace membership and independent resource grants retain their meaning.

Project Source references cover the whole Source. They grant USE or EDIT for
content within the Project's access policy. Source administration and Connection
credentials require independent authority. Project content grants cover supported
Env, Memo, Artifact, Annotation and Workflow attachments. Infrastructure state,
Vault secrets and Host credentials require independent authority. A Host filing
organizes the Host in the Project. See
[Hosts in Projects](https://docs.dreamlake.ai/lakeshore/hosts/browser-terminal#hosts-in-projects).

Issued read URLs and resource-scoped upload credentials retain their existing
finite lifetime after revocation. Storage operations already in progress cannot
be rolled back by a later database grant change. Native Memo RTC room
capabilities retain their existing revocation limitation; a database grant change
must not be described as immediate eviction of an already connected editor.
Ownership transfer remains a separate, execution-gated feature.

## Client compatibility and uploads

Project-derived access and Env attachments require a server that supports the
access contract. Project attachment commands require CLI 0.62.0 or later.
Python Project attachment support requires SDK 0.29.0 or later. Existing
explicit grants apply to existing attachments when
the server supports this contract. Historical mounts resolve the resource's
canonical address from the live catalog.

Project-only uploads use resource-scoped temporary credentials. If the storage
connection cannot issue scoped credentials, the server returns
`DELEGATED_UPLOAD_UNSUPPORTED` (403). This can occur with static custom S3 or
MinIO credentials, or an unscoped STS fallback.
