<!-- generated from https://docs.dreamlake.ai/artifacts.md at 0.1.106 513428f0; do not edit -->

{/* FigWhat/FigPush/FigVersions/FigTrash come from the site-wide
    mdxComponents map in site.config.ts — no import needed. */}

# Artifacts

  An artifact is one renderable file — an HTML page, a React component, a
  Markdown doc, an SVG, a Mermaid diagram, or a code snippet — that you push
  from the terminal and view as a live page in the dashboard.

## Preview spacing

Artifact previews start with zero page margin and padding. This applies to the
shared renderer and the default HTML document inside its isolated iframe.
HTML and React authors can add spacing explicitly within their content; the
preview does not add an outer gutter. To show an image edge to edge, remove
padding from its authored container and use `display: block` on the image.
Fit preserves the image's aspect ratio, so a differently shaped viewport can
still leave unused space; zero padding does not crop or stretch the image.

## Reference an artifact from a Note (development preview)

```markdown
:artifact[geyang/pitch-deck]
```

Click the copy icon in the artifact header to copy
the complete `:artifact[namespace/id]` reference, including the owner namespace
and full ID. The button displays an icon instead of a shortened ID, including
in the compact layout. A check mark confirms a successful copy.
Note and artifact tabs share a 240px preferred width and a
130px minimum width in compact layouts. Long titles use an ellipsis while the
reference and close controls retain their space. The compact artifact toolbar
shows the version value; a shared artifact's owner link is in **Artifact actions**.
This copy action does not create a share link or change permissions.

Use the owner namespace and stable artifact ID returned by the artifact CLI.
Brackets hold primary content; optional named attributes belong in braces, following
the [remark-directive extension](https://github.com/remarkjs/remark-directive), not core CommonMark.
DreamLake defines the resource semantics. Saved `:artifact{namespace="geyang" id="pitch-deck"}`
and `#artifact:geyang/pitch-deck` also work in the local development
UI. The tag resolves the title and opens the artifact panel to the right of the Note without changing
permissions or visibility. Static API HTML preserves the reference as an unresolved,
atomic source span; it does not embed artifact content or share-token URLs.
Production deployment is not yet verified. See [Notes reference syntax](https://docs.dreamlake.ai/notes#artifact-references-development-preview).

### Slide and section reference syntax

`:artifact[geyang/pitch-deck#slide-3]` retains an existing target ID; `#/3` is
valid only if the artifact defines that route. Clicking sends the fragment to
the reusable panel through `dreamlake.route.hash`, retaining its running iframe. See [fragment syntax](https://docs.dreamlake.ai/notes#fragment-reference-syntax-development-preview).

## Browsing in the app

`/<namespace>/profile?tab=artifacts` and `/<namespace>/artifacts` reuse the same
Artifacts catalog. Your own namespace and organizations you belong to show
resources and actions allowed by your permissions. Signed-out visitors and
signed-in visitors to other namespaces see public resources only, without
creation or modification controls. Profile uses an avatar rail; the application
uses resource navigation for the namespace in the URL.

Shared with me, trash and modification controls remain restricted to permitted member views. Public artifacts can be read without sign-in. Private share links require the recipient to sign in.

The application sidebar shows the resource owner's avatar and links, including
for anonymous public readers. Your signed-in identity and personal/organization
switcher are separate from that owner. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

The detail header returns anonymous readers to `/<namespace>/profile?tab=artifacts`
and signed-in readers to `/<namespace>/artifacts`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.

In the development UI, project and bindr grids also show an artifact's saved
cover. The card keeps its type icon when no cover is available or the image
cannot load; it does not render the artifact body to make a project thumbnail.

## Push one

```bash
dreamlake artifact push ./report.html
```

That's it. The CLI prints an **open link** — click it to see your artifact
rendered at `dreamlake.ai/<you>/artifacts`.

| Kind | File |
|------|------|
| `html` | Any self-contained page |
| `react` | A component file that defines `App` |
| `markdown` | `.md` docs |
| `svg` / `mermaid` | Diagrams |
| `code` | Anything else — rendered with syntax highlighting |

## Version it

Push the same `--id` again and you get a new version — nothing is overwritten,
and the viewer has a version picker.

## Share it

Artifacts are **private** by default. Two ways to open them up:

| | Command | Who can view |
|---|---------|--------------|
| 🔒 private | *(default)* | Only you and namespace members |
| 🔗 share link | `push --share` | Signed-in recipients with a valid share token |
| 🌐 public | `push --visibility public` | Anyone, no login |

You can also toggle visibility and copy links from the artifact's page — the
Share button does the same thing.

## Make the link card yours

Every artifact page carries Open Graph tags, so a link pasted into Slack,
Twitter/X, LinkedIn or a chat tool unfurls as a card: a title, a description
and a cover image. Set what the card says at push time, or afterwards (CLI
0.85.0+):

```bash
dreamlake artifact push ./report.html --id q1-dashboard \
  --description "Revenue, churn and pipeline for the quarter" \
  --cover ./cover.png

dreamlake artifact meta set q1-dashboard --description "Revenue, churn and pipeline"
dreamlake artifact meta set q1-dashboard --cover ./cover.png
dreamlake artifact meta show q1-dashboard
dreamlake artifact meta set q1-dashboard --clear-description --clear-cover
```

What a card shows follows the sharing table above:

| | Card |
|---|------|
| 🌐 public | The real title, description and cover. |
| 🔗 share link | The same real card — **anyone holding the link sees it, a chat tool's preview bot included**. The content itself still needs a signed-in viewer. |
| 🔒 private, no token | A generic DreamLake card, identical to a link that points nowhere. Nothing about the artifact leaks. |

A title, description or cover you set is yours: a later `push` keeps all
three unless it passes `--title`, `--description` or `--cover` again, and
`meta set --clear-…` returns a field to automatic. Without a description the
card shows a one-line summary built from the title and kind. Without a cover,
DreamLake renders one for you — a screenshot of the artifact as the viewer
shows it, within about fifteen minutes of a push, refreshed for every new
version — and the default DreamLake card stands in until then. The gallery
and your artifacts list use the same cover and description, so a published
artifact appears there as a picture rather than a live frame.

Covers are PNG, JPEG or WebP, at least 600×315 and at most 2 MiB; make them
1200×900 (4:3) — the shape of the generated covers and the default card, and
what the gallery and list wells are cut for. Keep the subject centred: a 16:9
chat card shows the middle band of a 4:3 image. Platforms cache a card for days: a changed cover or a revoked
share link can keep showing in messages already posted.

## Delete it (safely)

`delete` is a soft delete: the artifact moves to your gallery's **trash** tab
and any share link stops working. Restore it any time — or erase it forever.
With a server that includes the issue #1343 fix (not yet released), either way
it leaves every project it was filed in; a restored artifact comes back
unfiled, so add it to a project again.

```bash
dreamlake artifact delete report              # → Trash (restorable)
dreamlake artifact restore report             # bring it back
dreamlake artifact delete report --permanent  # erase forever — no undo
```

## Let Claude do it

Install the [artifacts skill](https://github.com/dreamlake-ai/dreamlake-skills)
and ask Claude to *"push this dashboard as a dreamlake artifact and share it"*:

```bash
dreamlake init                              # once: pick your agent and scope
dreamlake skill install dreamlake-artifacts
```

One skill covers both halves: preparing content for the offline rendering
frame, and publishing, versioning and sharing it. `dreamlake skill update`
brings in new releases without touching files you have edited. Without the
CLI, download `skills.tar.gz` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
and copy `dreamlake-artifacts/` and `dreamlake-cli/` into `~/.claude/skills/`
(or a project's `.claude/skills/`).

## Next steps

    Every flag — ids, kinds, namespaces, visibility.

    The REST endpoints behind push, share, and trash.

## Artifact paths and local routing

The artifact render iframe uses a meaningful resource path and ordinary local
query/fragment state:

```text
https://artifacts.dreamlake.ai/geyang/pitch-deck?slide=3&view=chart#overview
```

There is no internal instance ID in its URL. The path identifies the resource;
it is **not authorization**. The DreamLake viewer performs the authorized content
read, then sends the content to this isolated frame through a validated handshake.
The frame never receives the viewer's authentication or share token.

The corresponding shareable **viewer** link is:

```text
https://dreamlake.ai/geyang/artifacts/pitch-deck?art.slide=3&art.view=chart#overview
```

Only this outer viewer query uses `art.` to distinguish artifact state from
host parameters such as `share`. The fragment is ordinary `#overview` on both
URLs. Earlier development links using `#art=overview` are still read, but new
links use the plain fragment. The `art.` prefix never reaches the frame query.

Opening the frame address directly shows an explicit embed-only page with a
link to the authorized DreamLake viewer. It does not fetch private content,
invent a public read endpoint, or copy capability query fields into that link.
Public/private/share-link rules continue to be enforced by the viewer and API.
Ad-hoc Note/file previews have no catalog identity and use `/_preview`; catalog
thumbnails and artifact detail viewers use the actual namespace/artifact path.

Inside HTML and React artifacts this becomes `dreamlake.route.search ===
'?slide=3&view=chart'` and `dreamlake.route.hash === '#overview'`. Read strings
with `new URLSearchParams(dreamlake.route.search)`. Values can contain Unicode,
spaces, JSON text, or other strings; use `URLSearchParams` to encode queries
and `encodeURIComponent` for a fragment when building a URL. Repeated keys and
empty values are supported. Parse numbers/JSON and validate their meaning in
your artifact. Route data is public, user-controlled state, never a secret.

```html
<div id="slide"></div>
<button id="next">Next slide</button>
<script>
  const route = window.dreamlake.route;
  function render() {
    const params = new URLSearchParams(route.search);
    document.getElementById('slide').textContent = params.get('slide') || '1';
  }
  const unsubscribe = route.subscribe(render);
  render();
  document.getElementById('next').onclick = async () => {
    const params = new URLSearchParams(route.search);
    params.set('slide', String((Number(params.get('slide')) || 1) + 1));
    await route.navigate({ search: params.toString(), hash: '#overview' });
  };
</script>
```

`navigate({search?, hash?}, {replace?: boolean})` merges omitted fields with
the current route and returns a Promise. Set a field to `''` to clear it.
It pushes browser history by default; `{replace: true}` replaces the current
entry. `subscribe(callback)` returns an unsubscribe function; callbacks read
the new snapshot using `getSnapshot()` or the `search`/`hash` getters. React
artifacts can use `React.useSyncExternalStore(route.subscribe, route.getSnapshot)`.
Use an effect cleanup for other subscriptions.

Back/forward and incoming route changes update the running artifact without
reloading its iframe or resetting forms, React state, or WebGL scenes. The
outer render frame's `location.pathname`, `location.search`, and `location.hash`
reflect the clean artifact address. Use `dreamlake.route` for navigation without
reloads and for a common API across HTML and React. HTML still runs inside an
opaque, sandboxed `about:srcdoc` child; its own `location` is not the outer frame
URL. The route API supplies the same values without weakening that sandbox.

The host owns browser history; the frame mirrors route changes with
`replaceState`, preventing duplicate history entries. Reloading the iframe
performs a fresh handshake and reloads authorized content for the same path.
Directly assigning `location.search` in React reloads the frame; prefer
`route.navigate` to preserve component state. Native React fragment changes
mirror to the host using replace semantics; native HTML anchors stay in the
opaque child. Use the route API when an HTML route should survive sharing.

Only the standalone artifact detail page binds this API to browser history.
Gallery thumbnails, file/Note previews, and project-embedded viewers do not
inherit the surrounding page's query/fragment. Interactive previews can use
the route API locally. The detail Share/Copy link includes the current route.
Public links contain no share token; private sharing adds only the intended
read-capability token. Updating a route preserves host authorization in the
address bar but never exposes it to artifact code.

Parameter names (after removing `art.`) must match
`[A-Za-z][A-Za-z0-9_.-]{0,63}`. Reserved names, case-insensitively, are `share`,
`token`, `auth`, `authorization`, `cookie`, `project`, `namespace`, `instanceId`,
`__proto__`, `prototype`, `constructor`, and `dreamlake`, including names
followed by `.`, `_`, or `-`. Search plus hash is limited to 8192 characters.
Invalid API navigation rejects; invalid link parameters are ignored and an
oversized link route becomes empty. Host parameters such as `share`, auth,
and project fields are never blanket-forwarded. A parameter is ordinary data,
not permission to query private resources or escape the sandbox. The existing
query/download bridge and its authorization/confirmation rules still apply.

For a deep link from a Note, use an ordinary Markdown link with this URL, or
`:artifact[namespace/id#slide-3]` to open its hash route in a right-hand panel.
Do not put a share token inside rich-reference attributes.

This contract requires the companion frame and app changes. Release the frame
first, including its SPA fallback (`/* /index.html 200`), then the app. The new
frame accepts old root `/#af...` handshakes for existing hosts; only legacy root
URLs interpret the fragment as protocol state. Modern paths use a per-document
boot challenge and host instance identity exchanged exclusively in messages,
checked together with the source window and allowed/pinned parent origin.
Repeated readiness for the same document does not reinitialize the artifact.
After reload, messages from the previous document cannot complete new requests.

The new host can answer an old frame's ready message if that renderer loads,
but older frame deployments may lack the clean-path fallback and route API.
Do not deploy the host before the new frame is verified. Source validation
does not mean this feature is deployed. No server API or CLI change is required.

## Artifact panels in Notes (development preview)

Use `:artifact[namespace/id]` to open the shared artifact viewer beside a Note,
including Notes within a project. Append the artifact's own hash route to select
a slide: `:artifact[geyang/landing-pages#slide-3]`. Clicking a second reference to
the same artifact selects its existing panel and applies the new fragment. The
artifact receives it through `dreamlake.route.hash`; its own code defines what
that fragment means. The surrounding Note/project URL stays unchanged.

This is the same viewer used by standalone artifact pages and project items,
including version selection, preview zoom, and permission-checked management
controls. Closing the panel leaves the Note open. Tags grant no access, and
never contain a share capability. Full artifact links remain available with
Control/Command-click. These panel changes require the companion UI release;
publishing these docs or uploading an artifact alone does not deploy them.

## Manage an existing link

CLI 0.32.4 adds `artifact share get/create/revoke` and `artifact visibility`
without another upload. Inspect with `get` before changing access and after the
requested change. Follow the [complete CLI sharing recipe](https://cli.dreamlake.ai/artifacts#manage-existing-share-links).

Omitting `--share` on a later push preserves the existing token; it does not
stop sharing. Use `dreamlake artifact share revoke <id>` to clear the token.
Revocation blocks link-derived access while sharing is disabled; recorded
recipients may regain access if sharing is enabled again. Public visibility
and namespace membership are independent of the link.

A whole-Project ownership move can retain existing Artifact tokens and
share visits only with the reviewed preserve-access choice, the compatible
catalog/token/proxy API and executors from
[PR1170](https://github.com/dreamlake-ai/dreamlake-workspace/pull/1170), old readers
drained, and `ARTIFACT_TRANSFER_SHARING_ENABLED=true` (default off). Old URLs then
act as read-only aliases checked against the current owner and live sharing;
visits do not become standalone grants. Older/disabled APIs retain their
preservation blockers, and Env links remain unsupported. This is a server
capability, not a new share command or proof that a running deployment has it.
See the [whole-Project contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer#artifact-and-env-storage-and-access).

## Project attachment access

Independent resource share links remain available. Explicit Project user/team
READ grants add read access to all current and future attached resources; WRITE
and ADMIN add supported content editing. They do not grant resource sharing
management, deletion, ownership transfer or infrastructure credentials. Public Project visibility
alone never exposes private attached resources. Resource-own access and all live
Project grants are combined at the canonical resource URL.

Detaching a resource, revoking a Project grant, or leaving its granted team
removes only that source of access. A resource attached to several Projects keeps
access through the others. No resource share links or acceptance records are
created, copied or revoked by Project sharing. Attach requires the target
Project's content-create permission and the resource's own sharing-management
permission; readable content cannot be redistributed by a reader.
A resource owned by another namespace attaches only through its owner's
[cross-namespace mount grant](https://docs.dreamlake.ai/api/external-mounts).

The Project-sharing backend and Web update are released. CLI attachment
commands require 0.62.0 or later; Python Project support requires SDK 0.29.0
or later. Check installed client versions separately from server support.
Ownership transfer remains separately execution-gated.

Project content writers may obtain temporary upload credentials only when the
backend can restrict them to that resource. Custom S3/MinIO static credentials
and an unscoped STS fallback are never issued through Project-only authority;
these configurations return `DELEGATED_UPLOAD_UNSUPPORTED` (403) rather than
exposing the server identity. Existing namespace-member upload behavior remains
separate from Project inheritance.

The [whole-Project and owned-Notes transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
supports Project, ordinary Project files/images/videos and owned Notes.
A mount/reference of this resource blocks
the entire transfer rather than silently excluding it. Its existing independent
sharing and released Project-derived content access remain available.
