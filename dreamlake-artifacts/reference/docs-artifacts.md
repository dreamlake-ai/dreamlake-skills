<!-- generated from https://docs.dreamlake.ai/artifacts.md at 0.1.158 c8ea58c6; do not edit -->

{/* FigWhat/FigPush/FigVersions/FigTrash come from the site-wide
    mdxComponents map in site.config.ts — no import needed. */}

# Artifacts

  An artifact is one renderable file — an HTML page, a React component, a
  Markdown doc, an SVG, a Mermaid diagram, or a code snippet — that you push
  from the terminal and view as a live page in the dashboard.

## Static build directories

`dl artifact push ./dist/client --site --id my-site` preserves a static
Vike/Vite build's HTML, scripts, styles and assets as separate files. The browser
loads requested files and lazy imports normally; DreamLake does not choose a new
chunking strategy. Add `--spa` only for extensionless client routes that need the
entry document as a fallback. Server-rendered applications require a static export.

Each version stores a small `dreamlake-artifact-files/1` descriptor pointing to a
complete, immutable manifest. Objects are addressed by SHA-256 and reused across
versions of the artifact; removed files disappear from the new manifest. Uploads
finish before publishing the version. Existing single-file and inline multi-page
artifacts retain their format and viewer behavior. New sites require the updated
server, app and frame; older viewers show an upgrade message. Existing packed HTML
must be rebuilt to gain deferred asset loading.

Hosting uses an isolated HTTPS origin per artifact and manifest. A short-lived
HttpOnly, partitioned cookie grants access to that version; the frame renews it
without reloading the document. Authority is checked on every network request.
Browser-cached assets can remain available for up to four minutes after revocation;
HTML revalidates. Login and share credentials stay in the parent viewer. Ordinary
workers work; persistent service workers are refused. External network requests
and nested frames are restricted by the content CSP. Browsers must permit the
partitioned session cookie. This is static hosting, with no application backend.

### Enable hosting

1. Route a dedicated wildcard content domain and TLS certificate to the server,
   preserving the Host header. Keep content origins separate from the application,
   API and trusted artifact frame. Do not enable shared caching of private responses.
2. Set server `ARTIFACT_SITE_DOMAIN` to that domain and set
   `ARTIFACT_FRAME_ORIGIN` / `ARTIFACT_APP_ORIGIN` to the deployed trusted origins.
   The GitHub deployment workflows read these nonsecret values from repository or
   environment variables and pass them to both ECS and EKS. An unset site domain
   keeps hosting disabled; changing a variable requires a deployment to take effect.
3. Build and deploy the frame with the same `VITE_ARTIFACT_SITE_DOMAIN`; its generated
   CSP allows only that content wildcard. Deploy the matching app and CLI.
4. Verify `GET /artifacts/site-capabilities`, upload a small site, and check private
   and public access, navigation, lazy imports, renewal and legacy versions.

The CLI refuses `--site` before uploading when the server does not advertise
hosting support. There is no fixed aggregate byte limit for static sites. Limits
remain 4,096 files, a 2 MiB manifest and 32 MiB per HTML document.
The CLI uses a single S3 PUT per file, with a 5 GiB per-file transfer limit;
hidden files are omitted and symlinks, unsafe paths and case collisions rejected.
File sizes and their sum must be exactly representable as nonnegative safe integers.
Large media is streamed and supports byte-range requests; only requested HTML and
the manifest are buffered under their size limits.
No database migration is required. Self-hosted deployments must provision wildcard
DNS/TLS and deploy matching components before enabling hosting. Verify the
capability endpoint and a complete browser session on the target; local tests
alone do not establish live support.

For a cross-repository browser regression, build the UI fixture with
`node scripts/build-artifact-site-fixture.mjs` and its frame with
`VITE_ARTIFACT_SITE_DOMAIN=content.test pnpm build:frame`. From `dreamlake-server`,
run `ARTIFACT_UI_ROOT=/absolute/ui ARTIFACT_CLI_ROOT=/absolute/cli pnpm exec tsx scripts/artifact-site-browser.ts`.
It uses a local HTTPS server, the actual CLI collector and gateway, and a real
Vike static build to test deferred loads, routing, isolation and legacy switching.

### Private managed Source objects

The deployed `privateSourceCapabilities` hosting capability lets a signed-in
Artifact reader obtain short-lived URLs for exact objects under an approved
managed Source prefix. The browser reads storage directly; the API never proxies
payload bytes. Public data-origin approval alone does not grant this access.

These are additive APIs. `GET /artifacts/site-capabilities` reports
`features.privateSourceCapabilities: true` when the hosting service supports this
flow. The existing **POST** `/namespaces/:slug/artifacts/site-session` request
still takes `{artifactId, manifest}`; its response adds `privateData` without
changing `origin`, `bootstrap`, `entry` or `ttlSeconds`. Unbound sites return an
empty array. A public-origin grant alone cannot unlock a private Source.

Approval uses `POST /namespaces/:slug/artifacts/:artifactId/site-private-data-grants`
with `{manifest, alias, sourceId, namespaceId, prefix}`. Here `namespaceId` is the
Source namespace. The approver must administer both resources: Artifact Owner or
Project ADMIN and Source administrator. Approval binds the immutable site manifest,
Artifact catalog identity and ownership epoch, Source identity and ownership epoch,
managed storage binding and a fixed HTTPS storage origin. It preserves existing
public-origin approvals. Reapproval of the same scope is idempotent; changing the
scope requires a different site manifest. No user-supplied origin can widen it. An initial upload reservation can be
approved before its first version is registered; a deleted published Artifact
cannot. The shared-bucket S3 adapter's normal `logical` state is valid, as is
`ready`; failed or destroying bindings are refused.

The site session advertises `privateData: [{alias, origin}]`. The trusted parent
viewer authenticates `POST /namespaces/:slug/artifacts/:artifactId/site-private-data-capabilities`
with `{manifest, alias, paths}` (1–128 distinct relative paths, at most 64 KiB total
UTF-8 path bytes). Aliases start with a lowercase letter and contain lowercase
letters, digits or hyphens, up to 48 characters. Paths are relative to the approved
prefix, follow Source canonical path limits, and cannot contain traversal,
encoded separators, URL syntax or empty path segments.
The response contains `{manifest, alias, origin, objects, expiresAt}`; every object
has `{path, url, headUrl, expiresAt}`. GET and HEAD URLs name only that exact managed
object, with no external Source-layer fallback. Range reads use the GET URL.

The current authenticated actor needs Artifact READ; the administrator-approved
binding delegates only its prefix, so viewers do not need Source USE. Anonymous,
share-link-only and worker sessions are refused. The server rechecks current
Artifact access, grant state, Source lifecycle, ownership epochs and storage binding
before returning URLs. Source transfer, deletion or disablement fails closed.
The default URL lifetime is fifteen minutes, shortened to the signing credential's
remaining lifetime with a safety margin. Consumers must use `expiresAt`, not assume
fifteen minutes. This storage capability expiry is separate from the **five-minute
Artifact HTML session** (`ttlSeconds: 300` and the host-only HttpOnly, Secure,
SameSite=None, Partitioned cookie). The trusted viewer manages the HTML session;
a longer-lived signed object URL does not extend Artifact access or that cookie.
URLs are bearer capabilities: keep them in memory, omit cookies
when fetching storage, and do not put them into logs or durable artifacts.

Either resource administrator can withdraw future issuance with
`DELETE /namespaces/:slug/artifacts/:artifactId/site-private-data-grants` and
`{manifest}`. Previously issued URLs remain valid until their effective expiry;
already downloaded bytes cannot be recalled. Source USE changes for a viewer do
not revoke delegated Artifact access: revoke Artifact access or withdraw the grant.

The injected `window.dreamlake.requestPrivateData({alias, paths})` bridge talks only
to the trusted viewer origin, with a per-document request nonce, bounded pending
requests, thirty-second timeout and navigation cleanup. The viewer supplies the
active Artifact identity and manifest; site code receives no account token.
Storage CORS must allow the isolated site origin for GET/HEAD/Range and expose the
headers the application needs. For the default hosted content domain, append
`https://*.artifact-content.dreamlake.ai` to the existing managed bucket CORS
rule's allowed origins; preserve the upload rules and other existing origins.
Expose `Content-Range`, `Content-Length`, `ETag` and `Accept-Ranges`. CORS does not
make the bucket public: keep Block Public Access enabled and require signed URLs.
No Source bucket CORS provisioning/IaC is currently owned by this repository.
CSP admits only the binding's fixed storage origin.

Use a release-specific Source prefix and verify application object/manifest hashes.
This pins the binding, not the bytes against an authorized Source writer; it is not
object-lock. The deployed backend and trusted viewer/frame support this flow. Existing
ordinary/public Artifacts and unbound site sessions retain their behavior; no
broad account cookie, account bearer token or server byte-proxy is added to site
code. Data indexing and search can remain entirely in the browser, or use the
server-side search below where a release has been pinned for it.

#### Server-side private search

Available for releases DreamLake has pinned server-side; other sites receive 404.

A bound site can ask DreamLake to search an index stored under its approved
private prefix, instead of downloading the model and index into the page:

```
GET /_dreamlake/private-search?alias=data&mode=search&q=jump%20right&limit=120
```

The request goes to the site's own content origin, so the five-minute Artifact
HTML session cookie is the only credential: no account token, signed URL or
cross-origin request is involved. Authorization is the same as for
`site-private-data-capabilities`: the session must be eligible for private data
(`privateData` was non-empty) and the current approved binding must still be
valid. Anonymous, share-link-only and worker sessions are refused with 403.
Because loading or queueing can take seconds, current Artifact access and the
approved grant and binding are checked again after ranking; a revocation in
between returns 403 instead of records.

Only releases that DreamLake has pinned server-side for a specific Source prefix
and alias can be searched; the site cannot name a release, model or object path.
Pinned releases verify their search manifest and model file hashes before serving.

| Parameter | Meaning |
|---|---|
| `alias` | Private data alias of the approved binding (required) |
| `mode` | `init` (first page and facets), `search` (default) or `variants` |
| `q` | Query text, at most 256 characters; empty browses in catalog order |
| `filters` | JSON object of the release's supported filters, at most 4 KiB |
| `limit` | Results to return, 1–1000, default 120. Semantic results are re-requested from the top with a larger `limit` (the top 1000 at most); `capped` marks the end |
| `offset` | Browse offset for the next catalog page (empty `q`) |
| `group` | `1` groups source segments |
| `group_key` | Source group for `mode=variants` |

The response is JSON with `items` (catalog records), `total`, `hasMore`, `offset`
for browse pages, `ranking`, `textEvidence` and `timing`. Responses are
`Cache-Control: no-store`. Status codes: 400 for invalid parameters; 401 when the
Artifact session expired (retry after the viewer renews it); 403 without private
data access; 404 when no release is pinned for the binding; 503 with `Retry-After`
while the release is loading, unavailable (for example after its Source binding
changed, until the service restarts) or busy. Previews and downloads
keep using `requestPrivateData` and signed storage URLs.

#### Publish the binding

Use DreamLake CLI **0.107.0 or newer** for the released `privateData` configuration.
Check `dl --version`; an older installed binary is not upgraded merely
because the service or docs changed. The [CLI Artifact reference](https://cli.dreamlake.ai/artifacts)
owns the command and configuration details. For example, an `artifact.config.json`
can contain the following generic binding (replace both IDs and the prefix):

```json
{
  "schema": "dreamlake-artifact-config/1",
  "privateData": {
    "alias": "data",
    "sourceId": "111111111111111111111111",
    "namespaceId": "222222222222222222222222",
    "prefix": "releases/reviewed-release"
  }
}
```

Publish the static build with `dl artifact push ./dist/client --site
--site-config ./artifact.config.json`. The CLI checks the server capability before
uploading, then approves the binding after the immutable manifest is stored and
before registering the version. Neither a token nor a storage URL belongs in the
site configuration. A new data binding requires a new immutable site manifest,
usually by updating the site's pinned data-release configuration.

#### Fetch one object from site code

The injected bridge is available inside the hosted static Artifact. The following
TypeScript module caches capabilities in memory, refreshes them before expiry,
and retries a storage 401/403 **once** with a newly requested capability. It never
passes account credentials to the iframe or storage. Handle a second failure as
an access or availability error, rather than retrying indefinitely.

```ts
type Capability = {
  path: string; url: string; headUrl: string; expiresAt: string;
};
type PrivateBatch = {
  manifest: string; alias: string; origin: string;
  objects: Capability[]; expiresAt: string;
};
declare global {
  interface Window {
    dreamlake: {
      requestPrivateData(input: {alias: string; paths: string[]}): Promise<PrivateBatch>;
    };
  }
}
const cache = new Map<string, Capability>();
async function capability(path: string, refresh = false): Promise<Capability> {
  const cached = cache.get(path);
  if (!refresh && cached && Date.parse(cached.expiresAt) > Date.now() + 120_000) {
    return cached;
  }
  const batch = await window.dreamlake.requestPrivateData({alias: 'data', paths: [path]});
  const item = batch.objects.find(object => object.path === path);
  if (!item || batch.alias !== 'data' || !Number.isFinite(Date.parse(item.expiresAt)) ||
      Date.parse(item.expiresAt) <= Date.now()) {
    throw new Error('Private data capability is unavailable');
  }
  for (const value of [item.url, item.headUrl]) {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.origin !== batch.origin || url.username || url.password || url.hash) {
      throw new Error('Private data origin mismatch');
    }
  }
  if (cache.size >= 256) cache.delete(cache.keys().next().value!);
  cache.set(path, item);
  return item;
}
export async function fetchPrivateObject(
  path: string, options: {method?: 'GET' | 'HEAD'; range?: string} = {},
): Promise<Response> {
  const method = options.method ?? 'GET';
  for (let attempt = 0; attempt < 2; attempt++) {
    const item = await capability(path, attempt === 1);
    const response = await fetch(method === 'HEAD' ? item.headUrl : item.url, {
      method, credentials: 'omit', redirect: 'error',
      headers: options.range ? {Range: options.range} : undefined,
      signal: AbortSignal.timeout(30_000),
    });
    if (attempt === 0 && [401, 403].includes(response.status)) {
      await response.body?.cancel();
      continue;
    }
    if (!response.ok) throw new Error(`Storage HTTP ${response.status}`);
    return response;
  }
  throw new Error('Private data request failed');
}
```

Pass paths relative to the approved prefix, for example
`await fetchPrivateObject('search-manifest.json')`. For a partial binary read use
`{range: 'bytes=0-4095'}` and validate the expected 206 response, Content-Range and
application checksum. The bridge only obtains capabilities; it does not download,
transform or cache object bytes for your application.

## Preview spacing

Artifact previews start with zero page margin and padding. This applies to the
shared renderer and the default HTML document inside its isolated iframe.
HTML and React authors can add spacing explicitly within their content; the
preview does not add an outer gutter. To show an image edge to edge, remove
padding from its authored container and use `display: block` on the image.
Fit preserves the image's aspect ratio, so a differently shaped viewport can
still leave unused space; zero padding does not crop or stretch the image.

## Reference an artifact from a Memo (development preview)

```markdown
:artifact[geyang/pitch-deck]
```

Click the copy icon in the artifact header to copy
the complete `:artifact[namespace/id]` reference, including the owner namespace
and full ID. The button displays an icon instead of a shortened ID, including
in the compact layout. A check mark confirms a successful copy.
Memo and artifact tabs share a 240px preferred width and a
130px minimum width in compact layouts. Long titles use an ellipsis while the
reference and close controls retain their space. The compact artifact toolbar
shows the version value; a shared artifact's owner link is in **Artifact actions**.
This copy action does not create a share link or change permissions.

Use the owner namespace and stable artifact ID returned by the artifact CLI.
Brackets hold primary content; optional named attributes belong in braces, following
the [remark-directive extension](https://github.com/remarkjs/remark-directive), not core CommonMark.
DreamLake defines the resource semantics. Saved `:artifact{namespace="geyang" id="pitch-deck"}`
and `#artifact:geyang/pitch-deck` also work in the local development
UI. The tag resolves the title and opens the artifact panel to the right of the Memo without changing
permissions or visibility. Static API HTML preserves the reference as an unresolved,
atomic source span; it does not embed artifact content or share-token URLs.
Production deployment is not yet verified. See [Memos reference syntax](https://docs.dreamlake.ai/notes/writing#artifact-references-development-preview).

### Slide and section reference syntax

`:artifact[geyang/pitch-deck#slide-3]` retains an existing target ID; `#/3` is
valid only if the artifact defines that route. Clicking sends the fragment to
the reusable panel through `dreamlake.route.hash`, retaining its running iframe. See [fragment syntax](https://docs.dreamlake.ai/notes/writing#fragment-reference-syntax-development-preview).

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
switcher are separate from that owner. See [Profiles and workspaces](docs-workspaces.md).

The detail header returns anonymous readers to `/<namespace>/profile?tab=artifacts`
and signed-in readers to `/<namespace>/artifacts`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.

In the development UI, project and bindr grids also show an artifact's saved
cover. The card keeps its type icon when no cover is available or the image
cannot load; it does not render the artifact body to make a project thumbnail.

## Push one

```bash
dl artifact push ./report.html
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

Artifacts are **private** by default. Choose who can view them:

| | Command | Who can view |
|---|---------|--------------|
| 🔒 private | *(default)* | Only you and namespace members |
| 🔗 share link | `push --share` | Signed-in recipients with a valid share token |
| 🔗 unlisted | `--visibility unlisted` (CLI 0.104.8+), or the artifact menu | Anyone with the URL, no login; hidden from public profiles |
| 🌐 public | `push --visibility public` | Anyone, no login |

Choose **Private**, **Unlisted**, or **Public** in the artifact’s **⋯ → Share → Visibility** menu. Unlisted artifacts stay in the owner’s artifact list but are excluded from public profile lists and public feeds. Their direct URLs work without a share token or sign-in. Unlisted is not private: anyone who receives the URL can open it.

The artifact metadata endpoint accepts `visibility: "unlisted"`; omitting visibility on later pushes preserves the choice. Copy share link uses the plain URL for both public and unlisted artifacts.

In the artifact's **⋯ → Share** menu, turn on **Most recent version only**
to let recipients see only the latest registered version. The same link follows
future updates automatically. Namespace members retain access to history;
other readers, including public visitors and saved share recipients, cannot
retrieve earlier versions through the API or old static-site sessions. Turn it
off to share history again. Existing shares keep their current behavior until
you enable it. Content a recipient already downloaded cannot be recalled.

CLI 0.110.1+ can change the same policy without uploading a new version:

```bash
dl artifact share latest-only report on
dl artifact share get report --json
dl artifact share latest-only report off
```

Use `artifact share create report --latest-only` to enable it while creating a
share link, or `artifact push ./report.html --id report --share --latest-only`
when publishing. `--no-latest-only` disables it; omitting both flags preserves it.
See [CLI sharing controls](https://cli.dreamlake.ai/artifacts#share-only-the-most-recent-version).

The TypeScript SDK (CLI package 0.110.1+) exposes
`api.artifacts("my-team").share("report").latestOnly(true)`;
`publish` and `register` accept `shareLatestOnly?: boolean`.
Python 0.42.1+ exposes
`client.artifacts.set_share_latest_only("my-team", "report", True)`.
Pass `false` / `False` to allow recipient history again. These setters check
management permission, resolve renamed slugs and update only the sharing policy.

Both SDK catalog `get` methods return `shareLatestOnly` as a boolean. For example,
with an authenticated TypeScript `api` client:

```ts
await api.artifacts("my-team").share("report").latestOnly(true);
const saved = await api.artifacts("my-team").get("report");
if (saved.shareLatestOnly !== true) throw new Error("Policy not confirmed");
```

Python uses the normal client import and the same metadata field:

```python
from dreamlake import DreamLakeClient

client = DreamLakeClient()
client.artifacts.set_share_latest_only("my-team", "report", True)
saved = client.artifacts.get("my-team", "report")
assert saved["shareLatestOnly"] is True
```

The metadata endpoint accepts `shareLatestOnly: true` (or `false`) alongside
`visibility` and `share`. Only namespace members may change this setting;
omitting it on a subsequent push preserves the saved choice.

## Make the link card yours

Every artifact page carries Open Graph tags, so a link pasted into Slack,
Twitter/X, LinkedIn or a chat tool unfurls as a card: a title, a description
and a cover image. Set what the card says at push time, or afterwards (CLI
0.85.0+):

```bash
dl artifact push ./report.html --id q1-dashboard \
  --description "Revenue, churn and pipeline for the quarter" \
  --cover ./cover.png

dl artifact meta set q1-dashboard --description "Revenue, churn and pipeline"
dl artifact meta set q1-dashboard --cover ./cover.png
dl artifact meta show q1-dashboard
dl artifact meta set q1-dashboard --clear-description --clear-cover
```

What a card shows follows the sharing table above:

| | Card |
|---|------|
| 🔗 unlisted | `--visibility unlisted` (CLI 0.104.8+), or the artifact menu | Anyone with the URL, no login; hidden from public profiles |
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
dl artifact delete report              # → Trash (restorable)
dl artifact restore report             # bring it back
dl artifact delete report --permanent  # erase forever — no undo
```

## Let Claude do it

Install the [artifacts skill](https://github.com/dreamlake-ai/dreamlake-skills)
and ask Claude to *"push this dashboard as a dl artifact and share it"*:

```bash
dl init                              # once: pick your agent and scope
dl skill install dreamlake-artifacts
```

One skill covers both halves: preparing content for the offline rendering
frame, and publishing, versioning and sharing it. `dl skill update`
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

For a deep link from a Memo, use an ordinary Markdown link with this URL, or
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

## Artifact panels in Memos (development preview)

Use `:artifact[namespace/id]` to open the shared artifact viewer beside a Memo,
including Memos within a project. Append the artifact's own hash route to select
a slide: `:artifact[geyang/landing-pages#slide-3]`. Clicking a second reference to
the same artifact selects its existing panel and applies the new fragment. The
artifact receives it through `dreamlake.route.hash`; its own code defines what
that fragment means. The surrounding Note/project URL stays unchanged.

This is the same viewer used by standalone artifact pages and project items,
including version selection, preview zoom, and permission-checked management
controls. Closing the panel leaves the Memo open. Tags grant no access, and
never contain a share capability. Full artifact links remain available with
Control/Command-click. These panel changes require the companion UI release;
publishing these docs or uploading an artifact alone does not deploy them.

## Manage an existing link

CLI 0.32.4 adds `artifact share get/create/revoke` and `artifact visibility`
without another upload. Inspect with `get` before changing access and after the
requested change. Follow the [complete CLI sharing recipe](https://cli.dreamlake.ai/artifacts#manage-existing-share-links).

Omitting `--share` on a later push preserves the existing token; it does not
stop sharing. Use `dl artifact share revoke <id>` to clear the token.
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
supports Project, ordinary Project files/images/videos and owned Memos.
A mount/reference of this resource blocks
the entire transfer rather than silently excluding it. Its existing independent
sharing and released Project-derived content access remain available.

## Rename an artifact title

Artifact managers can choose **Rename title** in the artifact menu, or **Rename**
on its project-tree row. The display title and every live project filing update
atomically, including filings in other namespaces. A title already used by a
sibling in any filing causes a 409 conflict and leaves the entire edit unchanged.
Project write access alone does not grant permission to rename the artifact.

Clients use the existing metadata endpoint,
`POST /namespaces/:namespace/artifacts/:artifactId`, with `{ "title": "New title" }`.
Use the immutable `artifactId`, not a mutable URL slug. Title editors should also
send `expectedResourceId` from the latest detail response: a missing or replaced
catalog then returns 409 instead of creating an empty artifact. This optional
guard applies to title-only edits; older metadata creation clients remain supported.
Blank titles are rejected.
This metadata-only edit preserves the URL, immutable identity, content, every
version, visibility, grants, Session links and sharing settings. Existing CLI,
TypeScript and agent callers of this endpoint receive the same filing updates;
no content upload or replacement artifact is needed.

## Rename an artifact URL

Native slug rename changes the canonical URL without creating another artifact.
The catalog `resourceId` and `artifactId` are immutable; `artifactId` remains the
DreamDB scalar for every version. Detail responses include `slug` and
`slugRevision`. Existing IDs and previous slugs remain valid aliases, including
version and share links. Every alias resolves the same catalog and its current
access policy. Rename does not change the title, visibility, grants, share token,
latest-only sharing, Session links, project filings, or stored content.

Members can use **Rename URL** in the artifact menu or the CLI `artifact rename`.
The API is `PATCH /namespaces/:namespace/artifacts/:id-or-slug/slug`:

```json
{
  "slug": "session-work-map",
  "expectedResourceId": "0123456789abcdef01234567",
  "expectedSlug": "session-work-map-20261014",
  "expectedRevision": 0
}
```

Read all expected values from the latest detail response. The transaction checks
current membership, resource identity, the slug revision and ownership/storage
fences. A collision or stale revision returns 409 without a partial rename.
Re-read before retrying. Slugs use 1–128 ASCII letters, digits, dots, underscores
or hyphens, starting with a letter or digit. Reserved aliases cannot be reused by
another resource, even after deletion or purge.

Uploads must use the broker's opaque `backendUrl` and immutable `artifactId`.
Clients addressing a slug request upload credentials with `resolveSlug: true`
and use the returned `artifactId` for DreamDB reads/writes and registration.
Older clients must upload using the immutable ID; slug-based credential requests
without this capability fail with 409 before issuing credentials. Rename never
rewrites existing records or copies version history. After an ownership transfer,
source aliases still check the destination's current ACL; the destination uses
the immutable ID until explicitly assigned a slug in that namespace. Source
aliases do not authorize writes across namespaces.

## Unlisted through APIs and tools

The catalog endpoint `POST /namespaces/:slug/artifacts/:artifactId` and version
Apply endpoint accept `visibility: "unlisted"`. Omitting visibility preserves
its current value. To change only visibility, send `{ "visibility": "unlisted" }`
to the catalog endpoint after checking that the existing artifact is manageable.
The catalog endpoint is an upsert; client visibility commands check existence first.

CLI 0.104.8+ supports `dl artifact visibility report unlisted` and
`dl artifact push ./report.html --id report --visibility unlisted`.
The [TypeScript API](https://cli.dreamlake.ai/artifacts) supports Unlisted in
publish, register, and `artifacts(namespace).share(id).visibility("unlisted")`.
Python 0.41.1+ exposes
`DreamLakeClient().artifacts.set_visibility("my-team", "report", "unlisted")`,
with `get(namespace, artifact)` for readback and `list(namespace)` for the catalog.

Built-in agents discover the canonical artifact operation using
`dreamlake_resource_api_discover` and execute metadata updates using
`dreamlake_resource_api_write` with write permission enabled. The route schema
includes all three values. [Local MCP](https://docs.dreamlake.ai/lakeshore/agents/mcp) provides
`artifact_get` and `artifact_visibility_set` directly.
