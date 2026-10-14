# Connect And Verify

## 3. Link the storage as a source

Linking happens in the **DreamLake dashboard**, not the CLI: open the
**Sources** page of the namespace (`/source/<namespace>` in the app) and
connect the storage — Hugging Face and Dropbox via OAuth, S3 with bucket
credentials. Secrets are held server-side (AES-256-GCM); nothing sensitive
lands in files or schemas.

Then verify from a shell that the source exposes the expected paths —
the DreamLake CLI reads connected sources:

```bash
dreamlake source list
# After choosing the exact source name:
dreamlake source browse --source <name> [path]
dreamlake source download <path> --source <name> -o ./out
```

For a file that needs a short-lived read capability instead of a local copy,
`dreamlake source fetch <path> --source <name>` prints the URL when it can
be represented safely; use `--json` if signed headers are required. A CLI
browse/download is the first verification. Only when diagnosing whether a
`.dreamrc` resolves fields differently from the viewer, use the Node
`@dreamlake/viz` resolver below; it requires a source checkout and is not
needed for ordinary source verification. If a workflow will consume the
source, the `remote-source-check` skill wraps the path check.

## 4. Alternative channel — the DreamLake episode tree

Data that belongs in a DreamLake project/episode rather than external
storage uploads with the CLI directly (`dreamlake login` first):

```bash
dreamlake upload ./file-or-flat-dir --episode space[@namespace][:episode] --to path/within/episode
dreamlake list  --episode space[@namespace][:episode] --prefix some/path --json
```

`upload` takes a file or a FLAT directory — upload a nested dataset tree one
directory at a time with `--to` set per directory. A `.dreamrc` at a project
folder's root makes that folder render as a dataset, same as a source root.

## 5. Drop the `.dreamrc` and verify

Write the `.dreamrc` per the [`dreamlake-dataset-viz`](../../dreamlake-dataset-viz/SKILL.md)
skill and place it at the dataset ROOT in the linked storage. At the root it
must NOT contain a `storage:` block (the app injects the location; only a
standalone draft adds `storage:` for local validation).

For resolver-level diagnosis only, inspect the same resolution contract the app
uses (Node, from a checkout that has `@dreamlake/viz`):

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
→ the missing `index.json` manifests are the first suspect. Layout and
shape rules: https://viz.dreamlake.ai/dataset-viz/requirements.md

## Project-derived access

The backend and Web update are released. CLI Project attachment commands require
0.62.0 or later; Python Project support requires SDK 0.29.0 or later. Check
installed versions separately from server support.

The released Project-sharing backend retains whole-Source `ProjectSourceBinding` references.
Explicit Project READ supplies Source USE; WRITE/ADMIN supplies supported content
EDIT, not Source ADMIN, Connection/Vault credentials or sharing management.
A public Project alone never opens a private Source. Current and later bindings
follow live grants; detaching/revoking removes only that access contribution.
A Project reader may lack namespace-list authority: use the supplied exact Source
name and canonical address rather than treating a denied list as an empty catalog.
Updated clients resolve its exact name without enumerating other Sources.
See the [owning Source guide](https://docs.dreamlake.ai/sources/).


## Whole-Project transfer boundary

With the compatible backend, the whole-Project move includes ordinary Project
files/images/videos, supported byte-backed leaves and owned Notes. A Project
mount or reference of this resource blocks the entire transfer; do not silently detach
it, copy/delete it or report a partial move as complete. Existing resource sharing
and Project-derived content access remain released. See the
[owning transfer contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer/).
Requires CLI 0.63.0+ or Python SDK 0.30.0+ and an enabled, accepted Project
adapter. This resource remains outside the executable manifest; do not assume
Project-sharing support also enables its ownership transfer.
