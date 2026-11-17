# Connect storage as a Source and verify it

If the source already exists, find it with `dl source list` and skip to
verification. Otherwise linking is two steps: a **Connection** holds the
credential, and a **Source** reads through it. Sources keep data in place; they
do not convert an unsupported container.

1. Ask the server what it accepts — connector kinds, auth kinds and their mode,
   inputs and storage profiles differ per deployment; never assume S3 profiles,
   regions or auth kinds:

   ```bash
   dl connection connectors            # --json for options and conditional fields
   dl connection list                  # reuse an existing Connection when one fits
   ```

2. Create the Connection the way its mode requires:
   - `fields` (S3 access key or role, Hugging Face token): the user writes the
     credential to a JSON file or pipes it on stdin; you run
     `dl connection create --label <label> --connector <kind> --auth-kind <kind>
     --credential-file <file>` (or `--credential-stdin`) with non-secret inputs
     in `--private-config-file`. Never put a secret on the command line, in a
     prompt, in chat or in a file you leave behind; delete the credential file
     after.
   - When the secret should not pass through this machine:
     `dl connection entry create --connector <kind> --auth-kind <kind>`, give
     the user the printed link to finish in the browser — signed in as the same
     user who ran the command; nobody else can complete it — then
     `dl connection entry status <operation-id>` until `succeeded` and read the
     Connection id from it.
   - `oauth`: `dl connection oauth create --connector <kind> --label <label>`;
     the user signs in at the provider.
   - `none`: `dl connection create ... --no-credential`.

   S3 `role` works only with the `aws` profile, and its trust policy must
   already allow DreamLake's AWS identity (ask the deployment operator for it;
   never guess one or widen IAM to make it work).

   Then `dl connection check <id>`. `available` proves the credential, not a
   bucket; `unverified` (`target-required`) means that way in cannot be checked
   without a target; `unavailable` names a reason to fix before importing.
   Bucket and prefix access is decided by the import in step 3.

3. Import the Source through it:

   ```bash
   dl source import --connector <kind> --connection <connection-id> --target '<json>'
   ```

   For S3 the target names only the bucket and prefix; the Connection picks the
   endpoint. Use `dl source import --help` for the other connectors' targets.

Only the namespace's credential managers (personal owner, organization owners)
can do step 1 or 2; anyone else gets "not found". Service accounts and
background agent runs cannot manage Connections, and Connections cannot be
granted to an agent service account — do not try to work around it with a
grant. Registering a machine with Nymph needs no Connection. Every command and
flag: <https://cli.dreamlake.ai/connections>; concepts:
<https://docs.dreamlake.ai/connections>.

The web app does the same in **Connections** (`/<namespace>/connections`, then
**+ new connection**) and **Sources**; the DreamLake assistant in the web app
hands secret entry to that form and reads back the Connection id. Python SDK
users have `client.connections` and `client.sources.import_external`.

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
