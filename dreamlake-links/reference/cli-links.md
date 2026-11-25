<!-- generated from https://cli.dreamlake.ai/links.md at 0.147.0 7d93f98; do not edit -->

# Links

`dl links` manages saved URLs. It uses the same permissions and records as the
resource's Links tab. Saving a URL does not fetch its content or share its target.
Use immutable resource IDs. Kinds are `project`, `bindr`, `node` (files/folders),
`source`, `note` (Memos), `artifact`, `annotation`, `workflow`, `env` (Scenes),
`repo`, `runnable`, `library`, `bundle`, and `session` (saved terminal sessions).

```bash cli-help="links"
dl links list project "$PROJECT_ID" --namespace "$NAMESPACE"
dl links add source "$SOURCE_ID" https://example.com/dataset --namespace "$NAMESPACE" --title "Dataset documentation"
```

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

## TypeScript

```ts
import {createClient, newSavedLinkId} from '@dreamlake/dreamlake-cli/api';
const dl = createClient({remote: 'https://api.dreamlake.ai', token: process.env.DREAMLAKE_API_KEY!});
const links = dl.links(process.env.NAMESPACE!, 'project', process.env.PROJECT_ID!);
const id = newSavedLinkId(); // retain before sending, for recovery
const {link} = await links.create({id, url: 'https://example.com/guide', title: 'Guide'});
const updated = await links.update(link.id, {expectedVersion: link.version, description: 'Getting started'});
const page = await links.list({limit: 25});
console.log(page.links, page.nextCursor);
await links.remove(updated.link.id, updated.link.version);
```

The same API is available to Python and agent tools; see [the product contract](https://docs.dreamlake.ai/links).
Available in CLI 0.147.0 and a server with the Links API. Verify `dl links --help` before running these commands.
