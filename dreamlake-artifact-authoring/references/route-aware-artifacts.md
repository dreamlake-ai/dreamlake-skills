# Route Aware Artifacts

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

For a deep link from a Note, use an ordinary Markdown link with this URL.
Rich `:artifact[namespace/id]` references remain resource references; route
attributes are not part of their grammar in this change. Do not put a share
token inside rich-reference attributes.

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
