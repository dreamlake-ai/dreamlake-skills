# Layout control

`dreamlake layout` controls an existing page through the same high-level layout
controller used by application interactions. The controller resolves named,
spatial, size and content queries; UIKit owns the lower-level panel mechanics.

## Connect to a local browser

Use a browser session you started with a loopback Chrome DevTools Protocol (CDP)
endpoint. Supply its address explicitly. The CLI does not launch a browser, enable
remote debugging, select the first tab, or expose a network service. CDP grants
control of that browser session; keep the endpoint private and use a dedicated
profile. HTTPS/WSS and HTTP/WS loopback endpoints are accepted; remote hosts are
not supported by this transport.

```bash cli-help="layout pages"
# Use the endpoint of your explicitly enabled local debugging session.
dreamlake layout pages --cdp http://127.0.0.1:9222
```

Choose a page ID from the result. The page must register the layout protocol
`window.dreamlakeLayouts` version 1. DreamLake registers mounted PageViewLayout
instances. Multiple layouts are listed explicitly; select the intended one.

```bash cli-help="layout list"
dreamlake layout list --cdp http://127.0.0.1:9222 --page PAGE_ID
```

## Inspect, resolve, apply

```bash cli-help="layout inspect"
dreamlake layout inspect --cdp http://127.0.0.1:9222 --page PAGE_ID --layout LAYOUT_ID
```

Inspection returns a revision and flat regions with stable session IDs, bounds,
names, roles, active tabs, pins and safe view descriptors. IDs are scoped to the
mounted layout session. Refreshing or unmounting the page invalidates them.

Write a request to a JSON file. Obtain `SOURCE_TAB_ID` and `CURRENT_REVISION` from
inspection and substitute them before running this example:

```json
{
  "action": "open",
  "view": {
    "kind": "artifact",
    "resource": "geyang/demo",
    "title": "Demo",
    "content": { "namespace": "geyang", "artifactId": "demo" }
  },
  "destination": { "role": "preview", "select": "last" },
  "mode": "preview",
  "role": "preview",
  "reuse": "existing",
  "fallback": {
    "destination": { "id": "SOURCE_TAB_ID" },
    "placement": "right"
  },
  "ifRevision": 1
}
```

The revision above is illustrative; use the current inspection value. Resource
loading remains subject to the page's normal authorization. Layout placement
success does not prove the artifact loaded successfully.

```bash cli-help="layout resolve"
dreamlake layout resolve request.json --cdp http://127.0.0.1:9222 --page PAGE_ID --layout LAYOUT_ID
```

Resolve returns the chosen destination, planned effect and reason without changing
the layout. `apply` re-resolves against current state; `ifRevision` prevents a stale
plan from changing a layout the user has rearranged.

```bash cli-help="layout apply"
dreamlake layout apply request.json --cdp http://127.0.0.1:9222 --page PAGE_ID --layout LAYOUT_ID
```

Results are JSON. Non-ready resolutions and unsuccessful applications exit nonzero.
After a timeout or disconnection, inspect before retrying: the command may already
have applied. Never blindly retry a `new-instance` request.

## Requests

The canonical [UIKit layout controller](https://uikit.dreamlake.ai/components/layout-controller)
defines the complete schema and forkable starting-layout → request → result catalog.

- `open`: destination query, tab or directional placement, resource reuse,
  preview replacement, and explicit no-match fallback.
- `activate`, `close`, `pin`: explicit tab ID; pin protects replacement, not explicit close.
- `name`: bind a name to a resolved panel or spatial area.
- `move`: move a tab to a panel or beside an area.

The browser registry and CLI use the same serializable requests. No credentials,
document bodies, editor state, or executable predicates belong in descriptors.
Content queries compare metadata values supplied by the application.

This release's transport controls a selected local browser session. It does not
provide unattended remote workspace control or persist live session IDs across reloads.
