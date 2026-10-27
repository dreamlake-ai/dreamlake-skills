# Route-aware artifacts

Use this when an HTML or React artifact needs shareable query/fragment state —
slides, tabs, filters, a selected item — that survives copy-link, back/forward
and a Note deep link. The complete contract (URL shapes, handshake, history
semantics, limits) is in
[Artifact paths and local routing](reference/docs-artifacts.md#artifact-paths-and-local-routing);
this page is the authoring discipline. Start from
[`assets/templates/route-aware.html`](../assets/templates/route-aware.html).

## The API

Inside HTML and React artifacts, `window.dreamlake.route` exposes `search`
(`'?slide=3&view=chart'`), `hash` (`'#overview'`), `getSnapshot()`,
`subscribe(callback)` (returns an unsubscribe function) and
`navigate({search?, hash?}, {replace?: boolean})`.

- Read values with `new URLSearchParams(route.search)`. Values can contain
  Unicode, spaces or JSON text; repeated keys and empty values are supported.
  Parse numbers/JSON and validate their meaning yourself. Encode with
  `URLSearchParams` for queries and `encodeURIComponent` for a fragment when
  building a URL.
- `navigate` merges omitted fields with the current route and returns a
  Promise; set a field to `''` to clear it. It pushes browser history by
  default; `{replace: true}` replaces the current entry.
- React: `React.useSyncExternalStore(route.subscribe, route.getSnapshot)`;
  use an effect cleanup for other subscriptions.
- Back/forward and incoming route changes update the running artifact
  **without reloading the iframe** — forms, React state and WebGL scenes
  survive. Assigning `location.search` directly in React reloads the frame;
  prefer `route.navigate`. Native HTML anchors stay inside the opaque
  `about:srcdoc` child; use the route API when an HTML route should survive
  sharing.

## Rules that keep links working

- **Route data is public, user-controlled state, never a secret.** A
  parameter is ordinary data, not permission to query private resources or
  escape the sandbox. The frame never receives the viewer's authentication or
  share token; the path identifies the resource and is not authorization.
- The shareable **viewer** link carries artifact state with the `art.` prefix
  (`?art.slide=3&art.view=chart#overview`); the frame sees the plain
  `?slide=3&view=chart`. The fragment is a plain `#overview` on both. Older
  development links using `#art=overview` are still read; new links use the
  plain fragment. The `art.` prefix never reaches the frame query.
- Parameter names (after removing `art.`) must match
  `[A-Za-z][A-Za-z0-9_.-]{0,63}`. Reserved, case-insensitively: `share`,
  `token`, `auth`, `authorization`, `cookie`, `project`, `namespace`,
  `instanceId`, `__proto__`, `prototype`, `constructor` and `dreamlake`,
  including names followed by `.`, `_` or `-`. Search plus hash is limited
  to 8192 characters. Invalid API navigation rejects; invalid link parameters
  are ignored; an oversized link route becomes empty. Host parameters such as
  `share`, auth and project fields are never blanket-forwarded.
- Only the standalone artifact detail page binds the route to browser
  history. Gallery thumbnails, file/Note previews and project-embedded
  viewers do not inherit the surrounding page's query/fragment; interactive
  previews can still use the API locally. The detail Share/Copy link includes
  the current route; public links contain no share token, private sharing
  adds only the intended read-capability token.
- Opening the frame address (`artifacts.dreamlake.ai/<ns>/<id>`) directly
  shows an embed-only page linking to the authorized viewer; it fetches no
  private content. Ad-hoc Note/file previews use `/_preview` and have no
  catalog identity.
- The existing query/download bridge and its authorization/confirmation rules
  still apply.

## Deep links from a Note

Use an ordinary Markdown link with the viewer URL, or
`:artifact[namespace/id#slide-3]` to open the hash route in the right-hand
panel ([notes-references](notes-references.md)). Never put a share token
inside rich-reference attributes.

## Deployment caveat

This contract requires the companion frame and app releases: the frame first
(with its SPA fallback `/* /index.html 200`), then the app. Older frame
deployments may lack the clean-path fallback and the route API; source
validation does not mean the feature is deployed. No server API or CLI change
is involved. If a route does not take effect, verify in the app rather than
promising support.
