# Connect storage as a Source and verify it

Linking happens in the **DreamLake dashboard**, not the CLI: open the
**Sources** page of the namespace (`/source/<namespace>` in the app) and
connect the storage — Hugging Face and Dropbox via OAuth, S3 with bucket
credentials. Secrets are held server-side (AES-256-GCM); nothing sensitive
lands in files or schemas. If a source already exists, discover its name with
`dreamlake source list`. Sources retain data in place; they do not convert an
unsupported container.

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
browse/download is the first verification. If a workflow will consume the
source, run [check](check.md): it separates "browses" from "fetches", which
have different fixes. Command reference:
[reference/cli-sources.md](../reference/cli-sources.md); dashboard walkthrough:
[reference/docs-sources.md](../reference/docs-sources.md).

## Alternative channel — the DreamLake episode tree

Data that belongs in a DreamLake project/episode rather than external
storage uploads with the CLI directly (`dreamlake login` first):

```bash
dreamlake upload ./file-or-flat-dir --episode space[@namespace][:episode] --to path/within/episode
dreamlake list  --episode space[@namespace][:episode] --prefix some/path --json
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
