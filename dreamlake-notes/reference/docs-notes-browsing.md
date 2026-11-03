<!-- generated from https://docs.dreamlake.ai/notes/browsing.md at 0.1.110 999238cf; do not edit -->

# Browse, create and organize

## Browsing in the app

`/<namespace>/profile?tab=notes` and `/<namespace>/notes` reuse the same
Notes catalog. Your own namespace and organizations you belong to show
resources and actions allowed by your permissions. Signed-out visitors and
signed-in visitors to other namespaces see public resources only, without
creation or modification controls. Profile uses an avatar rail; the application
uses resource navigation for the namespace in the URL.

Your own Notes catalog retains Shared with me and recent organization notes. Private Note share links require sign-in under the server's per-person grant rules.

The application sidebar shows the resource owner's avatar and links, including
for anonymous public readers. Your signed-in identity and personal/organization
switcher are separate from that owner. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

The detail header returns anonymous readers to `/<namespace>/profile?tab=notes`
and signed-in readers to `/<namespace>/notes`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.

### Archive notes and folders

The web controls and initial archive endpoints are deployed. See the
[archive API contract](https://docs.dreamlake.ai/api/archival) for HTTP, client and tool interfaces.
Notes and folders have a separate nullable `archivedAt` field. Archiving does not
delete content, revoke access, remove project filings, or remove bindr membership.
Tags remain independent labels.

The note toolbar and note rows in catalogs, projects and bindrs offer **Archive**
and **Unarchive**. Folder rows offer the same controls. **Show archived** includes
archived items in the current list. Note body previews span the row width below
the title; the bindr timestamp sits with the metadata.

- `PATCH /namespaces/:slug/notes/:noteId` accepts `{"archived":true}` or
  `{"archived":false}`, subject to the Note's rename permission.
- `PATCH /nodes/:id` accepts the same body for folders, using the existing
  project write permission. Send archive changes separately from edits.
- Note catalogs, project resource/bindr listings, and node children/search
  exclude archived items by default. Pass `includeArchived=true` to include them.
  Filtering occurs before page counts and pagination.
- An archived folder hides its subtree in those project listings without
  changing every child's own archive flag. A note filed elsewhere keeps its
  independent state.
- A successful content, metadata or attachment edit restores an archived Note.
  Editing a file or folder, or adding a child, restores its archived folder
  path. Note edits restore the paths of its valid live project filings.
  Independently archived siblings and deleted items remain untouched.
- Opening a Note or synchronizing unchanged content does not restore it.
  Content restoration occurs when the changed body is durably saved; a failed
  save leaves archive state intact.

### Project and bindr associations

In **New note**, choose **private** or **public** below the name; a note is
private unless you choose public, and the projects it is filed into never change
that choice. Anyone can read a public note, including signed-out visitors.
Projects are optional: a note can be filed under none, one or several. Below
the visibility choice, the dialog lists the projects where you can create
content, each with a checkbox, its name and its slug; check as many as you need.
The list header shows how many are selected and offers **Clear selection**. In
the search field, the arrow keys move through the list, Enter checks or
unchecks a project, and Escape clears the search. From the notes list nothing
is preselected; from a project's **+ new note**, that project is preselected
and can be unchecked, in which case the note opens on its own page. If you
cannot create content in any project, the dialog says so and creates the note
without one.

Search matches names and slugs across every project you can read, not only the
loaded pages, and lists those you can write to. The list loads more projects as
you scroll. Selected projects come first, then suggestions that combine recent
projects with successful note creations in this browser: frequency decays with
a 14-day half-life and recent use adds a boost. Checking a project does not
move it; after a search is cleared, selections return to the top. History is
scoped to the signed-in user and workspace, bounded to 128 projects and pruned
after 180 days; cancelled or failed drafts do not train it.

The notes list and grid show the projects each note is filed in, as links to
those projects: two per list row and one per grid card, with a **+N** button that
expands the rest in place. Only projects you can read are listed, so a note with
no line may still be filed in projects you cannot see. A project from another
namespace is prefixed with that namespace, and same-named projects show their
slug. `GET /namespaces/:slug/notes` and `GET /me/notes/shared` return these as
`projects: [{ id, slug, name, namespaceSlug }]` on each row.

Adding a project or bindr from a note changes membership while keeping the
current note, URL, search and panes open. Choose a destination project inside
the association picker. Bindrs belong to that project; identical bindr names in
different projects are separate destinations. A bindr association uses the
existing mounted note node, not a new copy or arbitrary filesystem placement.

Pending operations disable duplicate submissions. A failed bindr addition may
leave a successfully added project association; retry the bindr addition after
reviewing the inline status. Removing an association uses the same context
preservation behavior and retains the last-project guard. Use the separate
**Open project** or **Open bindr** links when you want to navigate.

### Matching passages

Searching the Notes catalog shows up to two distinct matching passages beneath
each result title, with matching words highlighted. Hover or focus a passage to
open a line-based popover, or use **Preview matches** from the keyboard. The
popover shows multiple matching paragraphs with their line breaks and all query
highlights. Repeated excerpts appear once with an occurrence count; expand them
to choose the exact section and occurrence. Selecting a
passage opens the note in the existing pane and selects the matching occurrence
when its current source still agrees with the result. Identical wording at
different source positions remains distinct. A changed source reports **Match
changed** and asks you to choose a current occurrence instead of using stale
offsets. Title-only matches open the note normally.

The current catalog query and list scroll survive opening a passage. Source-only
matches that cannot be mapped safely to rendered Markdown remain visible in the
explicit source excerpt; the interface does not guess a rendered position.

### Resource subviews

Project file and folder details use native draggable sibling view tabs. Files
offer **Preview** and **Details**; folders offer their available **Files**,
**README**, **Visualize** and **Episodes** views. Each tab identifies its resource
and subview. In the project view, selecting another resource reuses the existing
resource tab slots instead of accumulating README/Files pairs for visited folders.
Open note tabs remain in place. Drag a tab to an edge to compare views side by side, or into a panel's
center to group it. Closing a subview leaves its siblings open; **Views** reopens
closed views. Tab switches retain mounted view state. Existing source-browser
URL-owned view controls keep their navigation behavior. ML-Dash run inspectors
use the same native tabs for **Params** and **Log**, while detail pages keep
their existing separate log panel.

## Create and list

The implementation of Shared with me resolves each Note's live owner and uses
its current namespace slug in the returned route. Cached namespace fields on an
accepted-share record are historical provenance, not authorization or routing
facts. The read does not repair or mutate those records. Current namespace
members receive the Note through their normal catalog; other active recipients
retain their accepted access while sharing remains enabled. A public Note stays
readable after its share link is disabled, without retaining share-based editing
permission. Deleted Notes, deleted owner namespaces and revoked acceptances are
omitted. This reader change does not enable ownership transfer.

**CLI**

```bash
dreamlake notes create "Design Doc"
dreamlake notes create "Design Doc" --file draft.md
dreamlake notes create "Design Doc" --text "# Design Doc"
dreamlake notes create "Design Doc" --public        # default is private

dreamlake notes list
dreamlake notes list --limit 20
dreamlake notes list --shared                       # what others sent you
dreamlake notes list --json
```

**Python**

```python
import dreamlake as dl

note = dl.create_note(
    "<namespace>", "Design Doc", text="# Design Doc\n",
)
note.id, note.namespace, note.etag

dl.list_notes("<namespace>")
dl.list_notes("<namespace>", limit=20, offset=20)
dl.shared_with_me()
```

Titles may repeat — the slug takes a suffix — so keep `note.id` rather than
the name you passed.

### Duplicate a note

The note's **Duplicate** action creates an independent private note from the
current visible editor text, including local edits not yet synchronized. It
copies the attachment snapshot captured when the request is admitted, preserving
exact bytes, logical paths and content types. The source's body, RTC room,
sharing and history stay unchanged; the copy has a new room and no inherited
share link or saved-version history.

The optimized server contract is
`POST /namespaces/:slug/notes/:noteId/duplicate` with
`{name, text, projects?, bindrIds?}`. It requires current namespace membership,
independent source-read authority, and write access to every requested project
and bindr. The text is literal Unicode, with at most 4 MiB of UTF-8 bytes; it is
not trimmed or normalized. Requested bindrs must belong to requested projects.

A successful 201 returns `{note, rtc: {rtcDocId}, contentSha256, sizeBytes, files}`.
`contentSha256` is lowercase SHA-256 hex over the acknowledged UTF-8 text;
`sizeBytes` is its UTF-8 byte count. Each file receipt is
`{path, etag, sizeBytes, contentType}`, where `etag` is lowercase SHA-256 hex of
the copied bytes. The browser verifies the text receipt instead of rereading the
entire body. The server initializes only the new native room, verifies its text,
and copies attachments with two bounded get/hash/put workers; it does not send
attachment bytes through the browser or reset an existing room.

Concurrent attachment mutation between admission and publication is rejected.
Later source edits do not change the captured copy. A failed operation after
creation returns `duplicate_incomplete` and `createdNoteId`; the partial note
and original room binding are retained for inspection. A timeout without a
receipt is also uncertain: inspect the created notes before trying again.
Neither server nor browser automatically replays an uncertain creation or deletes
its possible result. This endpoint does not add a CLI command or SDK method.

## Note summaries

> **Note:** A compatible Notes server exposes summary metadata. Published CLI 0.94.0 has
> neither `notes summary` nor `notes create --summary`; Python 0.32.1 has no
> summary helpers. TypeScript `notes.create` accepts an optional `summary`.
> Check client and server capabilities separately.

A note may have a short, optional summary for catalogs and quick context. The
summary is metadata separate from the collaborative body. Body edits and
revision checks leave it unchanged. Summaries can contain up to 4,000
characters; older notes without one return `null`.

The owner of the namespace or the Note's creator who is still a current member
of that namespace can set or clear a summary, the same as for a title or
visibility change. Other users with body-edit access cannot change it. For the REST API, `POST /namespaces/:slug/notes` accepts an
optional `summary`; `PATCH /namespaces/:slug/notes/:noteId` accepts a string to
set it or `null` to clear it. Omitting the field from PATCH preserves the
existing summary. `GET /notes/:noteId` and catalog list responses return the
summary separately from the body. A summary update does not create a body
revision or change its content hash.

Python SDK 0.32.1 does not expose `summary` in `create_note` or provide
`Note.summary`, `read_metadata`, or `update_summary` helpers. Use the
REST metadata endpoints above for summaries; do not pass those unsupported
arguments to the Python SDK.

GraphQL's authorized `Query.note(namespaceSlug:, id:)` returns the nullable
`Note.summary` field alongside `id`, `name`, and visible project/Bindr
associations. It is a metadata-only read; body content is not returned. Use the
REST metadata PATCH to update the summary.

## Link to a note in the browser

Use the note's full `id` in browser links:

```text
https://dreamlake.ai/<namespaceSlug>/notes?note=<noteId>
```

Read `namespaceSlug` and `id` from `dreamlake notes create --json` or
`dreamlake notes list --json`. Do not substitute the title or human-readable
slug in this URL: the browser detail route expects the ID, even though the
CLI accepts slugs and titles. Use the returned owner namespace rather than
assuming your personal namespace. The ID is sometimes called the note hash;
it is the `note` query parameter, not a `#` URL fragment.

In the development preview, the path controls the list pane independently of the
active note:

- `/<namespace>/notes` lists notes.
- `/<namespace>/projects` lists projects; `/projects/<project>` opens a project.
- `/<namespace>/bindrs` lists Bindrs; `/bindrs/<bindrId>` opens a Bindr.

Append `?note=<full-note-id>` to any of these paths to open a note. Switching
list context keeps that note open. The note header's contextual list button
hides or restores the list pane. Older note and project links redirect to these
routes. List search includes ordering; default status/category chips are omitted
from the compact panes. Project and Bindr member ordering is applied before
pagination so it covers the entire result set.

Inside another DreamLake note, prefer `:note[<full-note-id>]` (development preview) for a native note
reference. A browser link does not change visibility or grant access to a
private note.

## Profile introduction

A namespace's public note whose slug equals the namespace slug is shown at the
top of its profile Overview, for personal and organization namespaces. To add
one, create a note titled with the namespace slug and make it public; to remove
it, make it private or delete it. Notes are private by default and are never
published automatically.

A note's slug is derived from its title when the note is created and does not
change when the title changes, so retitling the introduction keeps it in place.
If another note already holds the slug, a new note receives a numbered suffix
and does not match; make the existing note public instead. Renaming the
namespace changes which slug matches.

The Overview shows the note's body in a card, without its title or a link to the
note. Unlike other note views, which show HTML in a note as text, it renders the
HTML subset a GitHub profile README uses: layout tables, images, links,
`<details>`/`<summary>` and text formatting such as `<b>`, `<br>` and `<sub>`,
with Markdown inside them. Only `align`, `alt`, `colspan`, `height`, `href`,
`open`, `reversed`, `rowspan`, `src`, `start`, `title`, `valign` and `width`
attributes are kept. Images load only from absolute `http(s)` URLs; links may
be `http(s)`, `mailto` or relative, and open in a new tab. Everything else is
dropped, including scripts, event attributes, `style`, `class`, `id`, `data-*`,
SVG, MathML, forms and embedded frames. Attach note files with Markdown image
syntax; an HTML `<img>` does not resolve `files/` paths.

`GET /namespaces/:slug/introduction` returns the note's metadata and a
short-lived presigned body URL, or `note: null` and `content: null` when the
namespace has no live public match. It ignores credentials: members and share
link holders receive the same public-only answer as anonymous readers, so a
private note with the matching slug is never returned. Unknown or deleted
namespaces, and namespaces whose owning user or organization is deleted, return
404. Like other read-only content reads, the body is the last persisted
snapshot and can trail an open editing session by a few seconds.

## Contributing session registration

Switching Notes preserves open session tabs and their panel placement. Opening
another Note's contributing session selects that session in the conversation
panel and leaves the previous session open in the background. A session already
open is focused instead of duplicated. Drag tabs between panels to arrange the
workspace. A standalone Sessions list panel can be closed; closing a panel or
tab does not terminate its session.

Viewing a Note, selecting a session tab, switching Notes, and moving panels do
not create contributing-session links. Automatic affiliation follows an
acknowledged content write; explicit Link/Unlink actions remain available.
Temporary presence is separate from a persistent session association.

CLI 0.82.0+ with the matching session API records native Codex/Claude provenance
after an acknowledged content write. If a native UUID has no saved descriptor,
metadata-only registration creates one without a host enrollment or terminal
launch. A native UUID and a DreamLake saved session ID are different identifiers.

New sessions default to PUBLIC, including automatic registration and imports.
Existing private/team records keep their sharing. Set
`DREAMLAKE_SESSION_VISIBILITY=private` for a private new automatic registration,
or `DREAMLAKE_SESSION_AFFILIATION=0` to disable affiliation. This policy applies
to sessions only; it does not change the Note's visibility.

A metadata warning never invalidates an acknowledged Note save. Retry only
session registration, linkage or explicit conversation upload; do not repeat the
Note write. Use `dreamlake sessions register --provider codex --session
<native-uuid> --cwd /original/directory --json`, then `sessions link <saved-id>
--namespace <personal-namespace> --resource-namespace <note-namespace> --note
<note-id>`. A target-discovery 403 is separate from metadata registration and
must not be repaired by changing credentials or restarting a terminal.

Conversation upload stays explicit. Recognized credentials are redacted by both
CLI and API, and historical archive reads are sanitized. Review custom secrets
before selecting an export: pattern redaction is not exhaustive. Public readers
can read public session metadata and saved conversations but cannot execute in
the terminal or read private resources merely because they are linked.
