<!-- generated from https://cli.dreamlake.ai/links.md at 0.152.2 26fd86b; do not edit -->

# Links

Links are `.url` files in the normal Project, Source, and Bindr file lists.
They use the same selection, preview, download, rename, move, and membership
behavior as other files in that surface. **New link** creates one from a name
and an HTTP(S) URL. Its preview opens the saved address with the web preview
controls. Some websites block embedding; **Open in browser** opens the target.
Saving a link does not fetch its target or grant access to it.

```bash cli-help="links"
dl links file https://docs.dreamlake.ai/ --output Documentation.url
```

```bash cli-help="links file"
dl links file https://docs.dreamlake.ai/ --output Documentation.url
# Upload to a Project folder; omitting :episode selects the Project root.
dl upload Documentation.url --episode "$PROJECT@$NAMESPACE" --to /references
# Or upload and add to a Bindr in the Project:
dl upload Documentation.url --episode "$PROJECT@$NAMESPACE" --to /references --bindr "$BINDR_NAME"
# Or save to a Source's managed files:
dl source upload Documentation.url --source "$SOURCE_NAME" --to references
```

`links file` prints file contents when `--output` is omitted. With `--output`
it creates a new `.url` file and refuses to overwrite an existing path.
The ordinary upload commands retain their existing destination and collision
rules. A Source's external layer remains read-only; uploads use managed storage.

The portable UTF-8 file format is:

```ini
[InternetShortcut]
URL=https://docs.dreamlake.ai/
```

A file must contain exactly one `URL` in its `InternetShortcut` section.
Previews accept HTTP(S) URLs without embedded credentials and link files up to
64 KiB. Queries and fragments, including DreamLake workspace URLs, are retained.
The file's name is its list title. Compact panels hide controls and metadata;
at the narrowest width, they hide the icon too.

## TypeScript

```ts
import {createClient, encodeLinkFile, parseLinkFile} from '@dreamlake/dreamlake-cli/api';
const dl = createClient({remote: 'https://api.dreamlake.ai', token: process.env.DREAMLAKE_API_KEY!});
const files = dl.files({kind: 'source', namespace: process.env.NAMESPACE!, sourceId: process.env.SOURCE_ID!, prefix: 'references'});
const saved = await files.write('Guide.url', encodeLinkFile('https://example.com/guide'), null);
console.log(parseLinkFile(saved.content));
const current = await files.read('Guide.url');
await files.write(current.path, encodeLinkFile('https://docs.dreamlake.ai/'), current.revision);
```

`null` creates only; edits require the current file revision. These are normal
file operations, so they preserve the file API's permissions and conflict checks.
See the runnable `examples/saved-links/links.ts` example.

## Compatibility with earlier saved URLs

The earlier `links list/get/add/update/remove` commands and `client.links(...)`
address legacy resource sidecars. They remain available to recover existing data;
they do not create files and there is no separate Links tab. For each saved
reference you want in a file list, read its URL, create a `.url` file, upload and
verify it, then remove the old record only if you want to retire it. Existing
records are never silently deleted or copied to a new visibility scope.

```bash cli-help="links list"
dl links list bindr "$BINDR_ID" --namespace "$NAMESPACE" --limit 25 --json
# Pass the returned nextCursor to continue:
dl links list bindr "$BINDR_ID" --namespace "$NAMESPACE" --cursor "$CURSOR"
```

```bash cli-help="links add"
dl links add project "$PROJECT_ID" https://docs.dreamlake.ai/ --namespace "$NAMESPACE" --title "Documentation" --description "API reference"
```

```bash cli-help="links get"
dl links get project "$PROJECT_ID" "$LINK_ID" --namespace "$NAMESPACE" --json
```

```bash cli-help="links update"
dl links update project "$PROJECT_ID" "$LINK_ID" --namespace "$NAMESPACE" --expected-version 1 --title "Product documentation"
```

```bash cli-help="links remove"
dl links remove project "$PROJECT_ID" "$LINK_ID" --namespace "$NAMESPACE" --expected-version 2
```

List returns one bounded page and a continuation cursor. Updates and removal
require the version from a read. On `409`, read again and reconcile the change.
`add` prints its recovery ID before sending; `--id` supplies your own 24-character
lowercase hexadecimal ID. After an uncertain response, read that ID. Repeating
identical content with the same ID is safe; do not retry with a new ID.

Source IDs are included in `dl source list --json` and source creation JSON
starting in CLI 0.147.1. Use that `id` as the saved Link parent; the Source name
continues to identify ordinary `dl source` commands.
