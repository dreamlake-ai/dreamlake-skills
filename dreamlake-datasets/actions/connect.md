# Connect storage as a Source and verify it

If the source already exists, find it with `dl source list` and skip to
verification. Otherwise create a Connection, then import a Source through it.

> `dl connection connectors` and `dl connection entry` need a CLI release that
> includes them (pending). Until then, use the web app's **Connections** page
> for discovery and browser entry; `dl connection create`, `check` and
> `oauth` are available now.

1. Discover and reuse. Read what this server accepts; never assume a connector,
   auth kind, profile or region:

   ```bash
   dl connection connectors --json
   dl connection list
   ```

   Reuse a matching Connection and go to step 4.

2. Pick the connector and auth kind from that output, by its `mode`. Ask the
   user only for a choice the output leaves open.

3. Obtain the credential without it passing through you:
   - `fields`, user can put the secret in a file or pipe it:
     `dl connection create --label <label> --connector <kind> --auth-kind <kind>`
     with `--credential-file <file>` or `--credential-stdin`, and non-secret
     inputs in `--private-config-file`. The user writes the file; delete it
     afterwards. Never put a secret on a command line, in chat or in a prompt.
   - `fields`, secret should not touch this machine:
     `dl connection entry create --connector <kind> --auth-kind <kind>`; give the
     user the printed link and tell them to finish it signed in as themselves,
     then `dl connection entry status <operation-id>` until `succeeded` and take
     the Connection id from it. `cancelled` or `expired`: start a new entry
     only if the user still wants it.
   - `oauth`: `dl connection oauth create --connector <kind> --label <label>`;
     the user signs in at the provider.
   - `none`: `dl connection create ... --no-credential`.

   Flags and inputs: `dl connection <command> --help`.

4. `dl connection check <id>`. If `unavailable`, follow its reason and repair or
   reconnect with a corrected credential before importing, rather than creating
   a second Connection. If `unverified` with `target-required`, proceed to the
   import; do not loop Check to try to turn it `available`.

5. Import through it:

   ```bash
   dl source import --connector <kind> --connection <connection-id> --target '<json>'
   ```

   Targets per connector: `dl source import --help` and
   [Managing a source](../reference/cli-sources.md#managing-a-source).

Exceptions:

- "not found" from any `dl connection` command: confirm the namespace and id
  with the user. If it still fails, report it as not found or no access without
  claiming which; do not try another identity, a service-account grant or a
  Project grant to get around it.
- A refused credential or role: report the server's message and ask the user to
  fix it on their side; never guess identities or widen permissions.
- The user prefers the web app, or asks the in-app assistant: point them to
  **Connections** in their namespace; the procedure is the same.

Then verify from a shell that the source exposes the expected paths —
the DreamLake CLI reads connected sources:

```bash
dl source list
# After choosing the exact source name:
dl source browse --source <name> [path]
dl source download <path> --source <name> -o ./out
```

For a file that needs a short-lived read capability instead of a local copy,
`dl source fetch <path> --source <name>` prints the URL when it can
be represented safely; use `--json` if signed headers are required. A CLI
browse/download is the first verification. If a workflow will consume the
source, run [check](check.md): it separates "browses" from "fetches", which
have different fixes. Command reference:
[reference/cli-sources.md](../reference/cli-sources.md); dashboard walkthrough:
[reference/docs-sources.md](../reference/docs-sources.md).

## Alternative channel — the DreamLake episode tree

Data that belongs in a DreamLake project/episode rather than external
storage uploads with the CLI directly (`dl login` first):

```bash
dl upload ./file-or-flat-dir --episode space[@namespace][:episode] --to path/within/episode
dl list  --episode space[@namespace][:episode] --prefix some/path --json
```

`upload` takes a file or a FLAT directory — upload a nested dataset tree one
directory at a time with `--to` set per directory. A `.dreamrc` at a project
folder's root makes that folder render as a dataset, same as a source root.

## Drop the `.dreamrc` and verify

Write the `.dreamrc` per [dreamrc](dreamrc.md) and place it at the dataset
ROOT in the linked storage. At the root it must NOT contain a `storage:` block
(the app injects the location; only a standalone draft adds `storage:` for
local validation).

Only when diagnosing whether a `.dreamrc` resolves fields differently from the
viewer, inspect the same resolution contract the app uses (Node, from a
checkout that has `@dreamlake/viz`); it requires a source checkout and is not
needed for ordinary source verification:

```ts
import { validateDreamrc, resolveDataset } from '@dreamlake/viz/dataset-viz'
const text = await (await fetch('https://<host>/<prefix>/.dreamrc')).text()
const rc = validateDreamrc(parseYaml(text))
const { episodes, warnings } = await resolveDataset(rc, {
  rootStorage: { driver: 'http', url: 'https://<host>/<prefix>' },
})
for (const ep of episodes) console.log(ep.name, await ep.episode.fields())
```

Every episode should enumerate and every field should carry the expected
kind (`video` / `series` / `depth` / …). Zero episodes on `format: folder`
→ the missing `index.json` manifests ([upload](upload.md)) are the first
suspect. Layout and shape rules:
[reference/viz-dataset-viz-requirements.md](../reference/viz-dataset-viz-requirements.md).

## Project-derived access

The backend and Web update are released. CLI Project attachment commands require
0.62.0 or later; Python Project support requires SDK 0.29.0 or later. Check
installed versions separately from server support.

The released Project-sharing backend retains whole-Source `ProjectSourceBinding`
references. Explicit Project READ supplies Source USE; WRITE/ADMIN supplies
supported content EDIT, not Source ADMIN, Connection/Vault credentials or
sharing management. A public Project alone never opens a private Source.
Current and later bindings follow live grants; detaching/revoking removes only
that access contribution. A Project reader may lack namespace-list authority:
use the supplied exact Source name and canonical address rather than treating
a denied list as an empty catalog. Updated clients resolve its exact name
without enumerating other Sources. See
[reference/docs-sources.md](../reference/docs-sources.md).

## Whole-Project transfer

A Source mount or reference still blocks the entire Project ownership move:
route complete-Project requests to the `projects` action of `dreamlake-cli`,
and never silently detach a Source, omit it from a manifest, or copy/delete it
to report a partial move as complete.
