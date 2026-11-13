<!-- generated from https://docs.dreamlake.ai/sources/custom-visualization.md at 0.1.158 f5167273; do not edit -->

# Custom Source visualization

A Source can render your HTML, JavaScript, CSS or statically exported React/Vite
application in its Visualize tab. Its `.dreamrc` selects the application:

```yaml file=".dreamrc"
visualize:
  type: custom
  entry: .dreamlake/visualization/index.html
```

The entry is a Source-root-relative HTML file under `.dreamlake/visualization/`.
The application is Source content: it has no Artifact catalog entry, independent
ACL, public URL or share settings. Existing dataset/annotation configurations
continue to use their existing renderers when no custom visualization is selected.

## Build and publish

Use CLI **0.121.0 or later** or Python SDK **0.48.1 or later** for publication.

Build a **static** site with relative asset URLs; for Vite, use `base: './'`.
Bundle dependencies locally. Server-side rendering, arbitrary backend processes,
external scripts and persistent service workers are not supported.

```bash
dl source visualization push ./dist --source my-data --namespace my-team
```

The publisher uploads a content-addressed generation below
`.dreamlake/visualization/<digest>/`, then changes only `visualize` in the managed
root `.dreamrc`, using its exact file revision. Existing configuration keys are
preserved. A failed asset upload does not switch the pointer; a concurrent config
edit is refused rather than overwritten. Old generations are retained; remove
unused ones through ordinary Source file operations when no longer needed.

Code assets are managed Source files. Dataset reads can use either managed files
or the Source's external connector, with the normal resolved-path rules. If only
an external `.dreamrc` exists, first copy its resolved contents into the managed
layer using a create-only write; the publisher refuses to silently shadow it.
Keep the existing configuration if a read fails or its YAML is invalid.

Limits: 1,000 files, 32 MiB per code asset and 128 MiB per published build. Symlinks
and special files are refused. Entry and asset paths must be canonical relative
paths; query strings, fragments, encoded path separators and traversal are not
accepted. Large dataset payloads belong outside the code bundle.

## Read this Source

The host injects `window.dreamlake.source` before your scripts run:

```javascript
const metrics = await window.dreamlake.source.json('metrics.json');
const text = await window.dreamlake.source.text('labels.csv');
const bytes = await window.dreamlake.source.read('recording.bin', {
  range: 'bytes=0-1023',
}); // ArrayBuffer
const page = await window.dreamlake.source.list('', { limit: 100 });
// { entries: [{ name, path, kind, size }], nextCursor }
```

Paths are relative to the **Source root**, not to the code directory. Pass
`nextCursor` as `cursor` to continue a listing. Each read is bounded to 32 MiB;
use inclusive, explicit `bytes=start-end` ranges for larger objects. A connector
must support Range and return HTTP 206 for a range request. `text` decodes UTF-8;
`json` parses that text. Rejected requests are surfaced as rejected promises.

The bridge is read-only and bound to the current Source. It has no namespace,
Source-ID override, write operation or arbitrary-URL fetch. The trusted host
fetches data through current Source authorization, then passes bytes or projected
file metadata into the isolated application. Account tokens, storage credentials
and signed read URLs are not exposed to application code. It may create local
Blob URLs from returned bytes for images, downloaded files or bounded media.

## Permissions and isolation

Source USE controls opening and reading; managed-file edit permission controls
publishing. Existing Source share-link recipients must accept the share and sign
in as required by Source access. This feature adds no anonymous access path.

Code runs on an isolated content origin with a sandbox and restrictive CSP,
sharing the isolation policy used by hosted Artifacts. It cannot access the app's
DOM, cookies or local storage. The trusted parent handles messages only from the
active frame and its exact origin. Current authority is checked for asset requests
and before releasing downloaded data. Source disablement, deletion, transfer and
access revocation prevent subsequent authorized reads. Already downloaded bytes
cannot be recalled. The five-minute code session is renewed by the host; sessions
are not an independent access grant. Source data remains a direct storage download
by the trusted browser host; only bounded code assets pass through the static host.

The publisher requires the `visualization-session` API and configured isolated
hosting. It checks server support before uploading code. If loading fails, the
Visualize view offers **Back to Browse**. Runtime application failures should be
handled by the application with a useful error state.

## Python and TypeScript

```python
from dreamlake import DreamLakeClient

client = DreamLakeClient()
result = client.sources.publish_visualization(
    'my-team', 'SOURCE_ID', './dist', entry='index.html',
)
print(result['url'])
```

```typescript
import { createClient, publishSourceVisualization } from '@dreamlake/dreamlake-cli/api';

const client = createClient({ remote: 'https://api.dreamlake.ai', token });
const result = await publishSourceVisualization(
  client.transport, 'my-team', 'SOURCE_ID', [
    { path: 'index.html', bytes: new TextEncoder().encode(html) },
    { path: 'main.js', bytes: new TextEncoder().encode(javascript) },
  ], { entry: 'index.html' },
);
```

The TypeScript SDK accepts explicit file bytes; directory traversal stays with the caller.
Both SDK publishers use the same managed code directory and revision-guarded
configuration publication. Python preserves YAML values and keys; comments may
be reformatted. Neither publisher creates an Artifact or modifies Source sharing.

## Session API

`POST /namespaces/:namespace/sources/:sourceId/visualization-session` accepts
`{entry}` under the authenticated caller's Source authority and returns
`{origin, bootstrap, entry, ttlSeconds}` with `Cache-Control: no-store`. Bootstrap
is a short-lived bearer URL for an HttpOnly, partitioned content session; never log
or persist it. The Web host owns renewal and the read bridge; opening bootstrap
alone does not provide dataset access. Ordinary Source APIs remain the authority
for browsing, read capabilities and uploads.
