<!-- generated from https://cli.dreamlake.ai/annotations.md at 0.139.0 9cde214; do not edit -->

# Annotations

`dl annotation` (also `dl annotations`) manages the annotation catalog. Title and URL
changes preserve the resource ID, immutable storage name, DreamDB content/history,
project filings and share tokens. These commands do not upload or edit label data.

```bash cli-help="annotation"
dl annotation list --namespace team
dl annotation get original-name --namespace team
dl annotation update original-name --namespace team --title "Retail Task Annotation"
dl annotation rename original-name retail-task-annotation --namespace team --json
```

`list` and `get` print JSON. `update` accepts `--title`, `--visibility private|unlisted|public`
and `--slug`; omitted fields stay unchanged. `rename <name> <slug>` changes only the
URL slug. Both mutation commands accept `--json`. Pass a current slug, old slug or
immutable storage name as `<name>`.

Slug updates read current metadata and submit the observed resource ID, slug and
revision in one PATCH request. A server without slug capability is rejected without
a write. Conflicts are not retried: read the annotation and reconcile first.
Namespace owners and organization members can change slugs. Edit-share recipients
can change titles through the API, but cannot rename URLs or change visibility.

Slugs use 1–64 lowercase ASCII letters, digits, dots, underscores or hyphens,
starting with a letter or digit. No automatic normalization occurs. Names and old
slugs are reserved within one namespace, including deleted resources; the same
spelling in another namespace is independent. Original and old URLs continue to
resolve under current permissions. Uploads continue using the immutable storage
name returned by `get`.

## TypeScript

```ts
import {createClient} from '@dreamlake/dreamlake-cli/api'
const client = createClient({remote: 'https://api.dreamlake.ai', token})
const api = client.annotations('team')
const row = await api.get('original-name')
await api.update(row.name, {
  slug: 'retail-task-annotation',
  expectedResourceId: row.id,
  expectedSlug: row.slug!,
  expectedRevision: row.slugRevision!,
})
await api.update(row.name, {title: 'Retail Task Annotation'})
```

The SDK uses explicit credentials and sends supplied fields exactly. `get` and
`update` accept an optional share token argument. See the
[canonical REST contract](https://docs.dreamlake.ai/annotations/reference).

## Share and visibility

These sharing commands and SDK methods require CLI 0.132.4 or later and the companion annotation-sharing API release.

Visibility and the signed-in collaboration link are independent. Private permits
workspace members and people already given access. Unlisted permits anonymous
direct-link reads without listing the annotation on the public profile or catalog.
Public also appears in public listings. Changing visibility does not change the
invitation token or edit permission.

```bash cli-help="annotation share"
dl annotation share get original-name --namespace team --json
dl annotation share create original-name --namespace team --role read --json
dl annotation share create original-name --namespace team --role write --json
dl annotation share revoke original-name --namespace team --revoke-accepted
```

```bash cli-help="annotation visibility"
dl annotation visibility original-name unlisted --namespace team
```

```bash cli-help="annotation get"
dl annotation get original-name --namespace team --share "$SHARE_TOKEN"
```

A signed-in recipient opens the invitation once with `--share`; subsequent reads
and permitted content writes use the retained resource identity. The current link
role is checked on every admission. Read access never grants visibility, URL rename,
deletion or sharing management.

`share access` lists accepted recipients. `share remove <resource> <user-id>`
removes an acceptance, not a block: the live link can admit that person again.
Revocation disables link-derived access. Without `--revoke-accepted`, retained
recipients regain access at the current role when sharing is re-enabled; with it,
they must open the new invitation. Already minted content URLs and scoped upload
credentials remain valid until expiry. Commands never retry an uncertain write.

```ts
const sharing = client.annotations('team').share('original-name')
await sharing.get()
await sharing.create('write')
await sharing.visibility('unlisted')
await sharing.access()
await sharing.revoke(true)
```

These methods reuse the SDK's sharing contract. They change catalog authorization,
never upload annotation content or rewrite its data/history. Content writers use
the immutable storage name and receive resource-scoped credentials.

## Related resources, sessions and history

With CLI 0.133.0+ and the companion resource-relationships API release, use the `id` returned
by `annotation get` for resource relationships and activity. These operations
preserve annotation content and sharing.

```bash
dl annotation get training-run --namespace team
dl resources link note MEMO_ID annotation ANNOTATION_CATALOG_ID --json
dl resources relationships annotation ANNOTATION_CATALOG_ID --json
dl resources history annotation ANNOTATION_CATALOG_ID --json
dl sessions link SESSION_ID --namespace owner --resource-namespace team --annotation training-run --json
dl resources sessions annotation training-run --namespace team --json
```

Verify relationship writes by reading the relationship list. To remove one, use
`dl resources unlink RELATIONSHIP_ID`; to remove a saved-session association, use
`sessions unlink` with the same options as `sessions link`. Resource relationship
commands use the 24-hex catalog ID; saved-session commands use the namespace and
annotation name or slug. A manual association does not prove authorship. Activity
is best-effort with 90-day retention, not a complete audit log. See
[resource relationships and history](https://cli.dreamlake.ai/sessions#resource-relationships-and-history)
for pagination, SDK methods and the distinction between saved sessions and
attribution contexts.
