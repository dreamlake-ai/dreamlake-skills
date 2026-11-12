<!-- generated from https://cli.dreamlake.ai/annotations.md at 0.122.0 ee0b243; do not edit -->

# Annotations

`dl annotation` (also `dl annotations`) manages the annotation catalog. Metadata
changes preserve the resource ID, immutable storage name, DreamDB content/history,
project filings and share tokens. These commands do not upload or edit label data.

```bash cli-help="annotation"
dl annotation list --namespace team
dl annotation get original-name --namespace team
dl annotation update original-name --namespace team --title "Retail Task Annotation"
dl annotation rename original-name retail-task-annotation --namespace team --json
```

`list` and `get` print JSON. `update` accepts `--title`, `--visibility private|public`
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
