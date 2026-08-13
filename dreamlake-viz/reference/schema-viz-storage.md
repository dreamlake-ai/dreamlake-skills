# Storage

A source's **storage** answers one question: _where do the bytes live, and how do
I reach them?_ The [adapter](reference/schema-viz-adapters.md) above it sees one uniform
interface (a `Storage`):

```ts
interface Storage {
  // logical path → a fetchable URL (signed/expiring when the backend needs it)
  resolveUrl(path: string, opts?: { ttlSeconds?: number }): Promise<string>
  // list one directory — bounded, non-recursive
  list(path: string, opts?: { token?: string; limit?: number }): Promise<Listing>
}
interface Listing {
  entries: Entry[]
  nextToken?: string
}
interface Entry {
  name: string
  path: string
  type: 'file' | 'dir'
  size?: number
}
```

A driver is named by `storage.driver` in a [source](reference/schema-viz-schema.md).

> Storage deals only in `Entry.type` (`'file'` / `'dir'`) — directory structure.
> It knows **nothing** about a field's [`kind`](reference/schema-viz-concept.md#kind-is-the-joint-the-system-turns-on)
> (`video`/`series`/…); that is the [adapter](reference/schema-viz-adapters.md)'s job. The two
> are different concepts that both happen to be called "kind" in some backends —
> see the note in the example below.

## Choosing a driver

`schema-viz` is a **stateless public component** — it holds no credentials and
has no login session, so it can never authorize private data on its own. That
single fact drives the choice:

| Your data is…                                                                | Driver                                | Auth                                 |
| ---------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------ |
| **Public** (a public HF/GitHub URL, an S3 public bucket, your own `public/`) | the built-in **`http`**               | none                                 |
| **Private** GitHub / HuggingFace / DreamLake                                 | a driver **injected by the host app** | the host's session, never the schema |

The schema **never contains a token**. Public data needs none; private data is
brokered by the host application, which owns the login session.

## The `http` driver (public)

The only built-in driver. `resolveUrl` joins `basePath` + path (absolute URLs
pass through); `list` reads a co-located `index.json` (a static host can't
enumerate a folder itself).

```yaml
# a public HuggingFace dataset — basePath is its `resolve` URL
storage: { driver: http, basePath: https://huggingface.co/datasets/lerobot/aloha_static_coffee/resolve/main }

# a folder of files you serve yourself — list() reads index.json in that folder
storage: { driver: http, basePath: /viz-samples/episode_365/ }
```

| Key        | Type   | Default | Notes                                                      |
| ---------- | ------ | ------- | ---------------------------------------------------------- |
| `basePath` | string | `""`    | Prefix for every relative path; absolute URLs pass through |

For directory discovery (the [`filesystem`](reference/schema-viz-adapters.md) adapter), drop
an `index.json` in the folder listing its files.

## Private data — injected by the host

The **host app provides the driver** via the `extensions.storages` prop (or a
global registration). The schema only names it; the driver's `resolveUrl`/`list`
call the app's **own authorized endpoint**, and viz never sees a token. This is
exactly how the DreamLake project storage works — `list` hits `/nodes/children`
and `resolveUrl` hits `/nodes/{id}/download`, both through the app's `apiGet`,
which attaches the session bearer token:

```tsx
// In the DreamLake app (NOT in viz) — apiGet attaches the session token.

class DLProjectStorage implements Storage {
  constructor(private rootId: string) {}
  async list(path = ''): Promise<Listing> {
    const parentId = path || this.rootId
    const res = await apiGet<{ nodes: Node[]; totalPages: number }>(
      BASE_URL,
      `/nodes/children?parentId=${parentId}&page=1`
    )
    const entries: Entry[] = res.nodes.map((n) => ({
      name: n.name,
      path: n.id, // ref = node id
      // n.kind is the DreamLake NODE type (folder/episode/file) — NOT a viz Field
      // `kind`. Storage only uses it to decide dir-vs-file; the adapter assigns
      // the field kind later, from the filename.
      type: n.kind === 'folder' || n.kind === 'episode' ? 'dir' : 'file',
    }))
    return { entries }
  }
  // A node id → a short-lived AUTHORIZED download URL (works for <video>/<img>).
  resolveUrl(path: string): Promise<string> {
    return apiGet<{ url: string }>(BASE_URL, `/nodes/${path}/download`).then((r) => r.url)
  }
}
export const dlProjectStorageFactory: StorageFactory = (cfg) =>
  new DLProjectStorage(cfg.root as string)
```

```tsx
// The schema stays token-free — it only names the driver + the folder node.
const schema = {
  version: 1,
  sources: { clips: { adapter: 'filesystem', storage: { driver: 'dlProject', root: '<node id>' } } },
  panels: [{ view: 'videoStack', source: 'clips', fields: ['*'], columns: 3 }],
}

<DatasetPreview schema={schema} extensions={{ storages: { dlProject: dlProjectStorageFactory } }} />
```

Why this shape:

- **No token in the schema.** It is safe to commit, share, and serialize;
  authorization is the host's concern, resolved at request time.
- **Authorized URLs, not headers.** `<video>`/`<img>` fetch their `src` directly
  and cannot attach an `Authorization` header — so private _media_ must come back
  as a signed/redirected URL. The `/nodes/{id}/download` URL is exactly that.
- **Stateless viz.** Standalone (e.g. this docs site) viz reaches only public data
  via `http`; private access lights up only when a host injects its driver.

### Register once, or per preview

`extensions.storages` adds a driver **for that preview, only if free** — handy for
a one-off. When a page mounts **several** ``s sharing the same
driver, register it **once at app boot** instead — every preview sees it, and a
global registration can also override a built-in:

```tsx

registerStorage('dlProject', dlProjectStorageFactory)
```

`registerStorage` overwrites; an `extensions` entry is skipped if the name is
taken. (`registerAdapter` and `registerView` work the same way.) Because the
factory's `resolveUrl` reads the token **at request time** (via `apiGet`), a
once-registered driver always uses the current session.

## Writing your own driver

Any driver implements the same two methods. Recommended patterns: **dedupe
in-flight requests** (memoize the `Promise` per path), **cache signed URLs with
near-expiry renewal** (a `<video>` may stream for minutes), and **pass absolute
URLs through**.

## What storage does not do

- **It does not know formats.** It hands back URLs/bytes; parsing belongs to the
  [adapter](reference/schema-viz-adapters.md).
- **It does not fetch media content.** It returns a _URL_; the `<video>`/`<img>`
  streams the bytes.
- **It does not recurse.** `list` is one directory.

Next: [Adapters](reference/schema-viz-adapters.md) — turning storage bytes into a Model.
