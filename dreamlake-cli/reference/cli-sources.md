<!-- generated from https://cli.dreamlake.ai/sources.md at unknown; do not edit -->

# Sources

A **Source** is a named file tree in a namespace. It has up to two layers,
merged into one **resolved view**:

- an optional **external layer** — a connected S3 bucket or Hugging Face repo.
  It is read-only for everyone, the owner included; DreamLake never writes to
  the provider.
- a **managed layer** — DreamLake-hosted storage that you upload into and
  delete from.

Reads never copy anything into DreamLake. `source upload` writes only to the
managed layer. The commands on this page need CLI 0.45.3 or later.

```bash file="terminal"
dreamlake source list
dreamlake source browse --source my-bucket datasets/
dreamlake source fetch  --source my-bucket datasets/frames.tar
dreamlake source download --source my-bucket datasets/ -r -o ./local
dreamlake source upload ./run-01 -r --source my-bucket --to uploads/run-01
```

Sources are declared like any other head collection —
`dreamlake declare source.yaml --collection sources` — see
[Declaration collections](cli-collections.md).

### How a path resolves

The managed path wins: `resolved(path) = managed(path) ?? external(path)`. A
managed file hides the external file at the same path, and a managed **file**
also hides an external **directory** of the same name and everything under it.
`stat` shows which layer a path resolves from (origin `dreamlake-storage` or
the external store).

> **Note:** DreamDB sources — structured collections and records, with video sliced into
> fragments — are created and pushed with the DreamLake Python SDK, not with this
> CLI; see [DreamDB](https://docs.dreamlake.ai/lakeshore/dreamdb/). To render a
> Source's files with a `.dreamrc`, see
> [docs.dreamlake.ai/sources](https://docs.dreamlake.ai/sources/).

## Who can do what

This reflects the current server code, and applies only to a DreamLake service
that has Source v1 enabled — the server must serve the Source v1 routes; a
recent CLI alone is not enough. For an authenticated request on such a
service, a caller with no access gets 404; a caller with some access but not
enough gets 403.

| Action | Who |
| --- | --- |
| `list`, `browse`, `stat`, `fetch`, `download` | any namespace member, a read share-link holder, or a Project READ grant on a project the source is bound to |
| `upload`, `delete-object`, `delete-prefix` | EDIT on an **active** source: the namespace owner (personal owner or org OWNER), a per-source Editor (a user, team or service account added with `editor-add`), a redeemed write share link, or a Project WRITE/ADMIN grant on a project the source is bound to |
| `create`, `import`, `metadata`, `external-set`/`external-remove`, `enable`/`disable`, `delete-source` (+ `-status`/`-retry`), `editors`/`editor-add`/`editor-remove`, `references`, `share`/`share-off`/`shares`/`shares-remove` | namespace owner only |

Plain organization members are read-only unless made an Editor. Help text says
"Owner/Admin only"; organizations currently have only OWNER and MEMBER roles,
so in practice that means the owner. On a **disabled** source only the owner
keeps settings access; uploads and reads are refused.

## `list`

```bash file="terminal"
dreamlake source list [--limit <n>] [--cursor <c>] [--name-contains <t>] [--provider <id>] \
  [--external | --no-external] [--lifecycle active|disabled] [--namespace <slug>] [--json]
```

Lists one page of sources in a namespace. The name it prints is what every
other command's `--source` wants.

## `create`

```bash file="terminal"
dreamlake source create <name> [--description <text>] [--namespace <slug>] [--idempotency-key <key>] [--json]
```

Creates an empty, managed-only source. Owner only. To attach an external store,
use `dreamlake source import` (see `dreamlake source import --help`).

## `browse`

```bash file="terminal"
dreamlake source browse [path] --source <name> [--namespace <slug>] [--dirs] [--files] [-r] [-0] [--json]
```

Lists paths in the resolved view, **one level at a time** by default. Omit
`path` to start at the root.

| Flag | Meaning |
| --- | --- |
| `--dirs` | list only directories |
| `--files` | list only files (for piping into `fetch`/`download`) |
| `-r, --recursive` | descend into subdirectories |
| `-0, --print0` | NUL-separate the paths |
| `--json` | emit JSON |

`-0` exists for exactly one reason: object keys contain spaces, and a
newline-separated list piped into `xargs` splits them in the wrong place.

```bash file="terminal"
dreamlake source browse datasets/ --source my-bucket -r --files -0 \
  | xargs -0 -n1 dreamlake source fetch --source my-bucket
```

## `stat`

```bash file="terminal"
dreamlake source stat <path> --source <name> [--namespace <slug>] [--json]
```

Shows one exact path in the resolved view, with its metadata and the layer it
resolves from.

## `fetch` — one short-lived URL

```bash file="terminal"
dreamlake source fetch <path> --source <name> [--json]
```

Mints a **public, short-lived download URL** for one file and prints it.
Nothing is downloaded.

> **Warning:** `fetch` returns a pre-signed URL: anyone holding the string can read that
> object until it expires. It is meant for handing one file to a process that
> speaks HTTP and nothing else. Do not paste it into a ticket, a commit message,
> or a chat channel.

## `download` — bytes on disk

```bash file="terminal"
dreamlake source download <path> --source <name> [-o <dir>] [-r]
```

Writes the file to local disk. With `-r` it takes a folder path and downloads
every file underneath it, preserving the tree. `-o` sets the output directory
(default: the current one).

Quote any path containing spaces — the argument is a path *inside the source*,
not a shell glob, and the shell will get there first if you leave it bare.

## Upload files into a Source

```bash file="terminal"
dreamlake source upload <path> --source <name> [--to <prefix>] [-r] \
  [--namespace <slug>] [--idempotency-key <key>] [--json]
```

Writes into the source's **managed layer**. `--source` is required; `--to`
defaults to the source root. Uploading to an episode is a different command —
see [Uploading](cli-uploading.md).

- A single file lands at `<to>/<basename>`.
- A directory needs `-r`, and its **contents** land under `<to>/` — the
  directory's own name is not added. `upload ./run-01 -r --to datasets/run-01`
  writes `datasets/run-01/<relative path>`.
- At most **1,000 files and 10 GiB** per command, checked before anything is
  sent. Split a bigger tree into several commands with different `--to`.
- An empty directory is refused. A symlink or special file — the argument or
  anywhere inside the directory — refuses the **whole** command; nothing is
  skipped silently.
- Paths follow server rules: no leading or trailing `/`, no backslash, no
  control characters, no empty, `.` or `..` segments, at most 1024 bytes in
  total and 255 bytes per segment. Nothing is normalized — a non-canonical
  path is rejected. Paths under `.dreamfs` are reserved.
- Bytes go straight from your machine to storage through short-lived
  (60-minute) presigned URLs, one file after another. There is no finalize
  step: a completed file is visible on the next `browse` or `stat`.

> **Warning:** If the path already exists in the managed layer, the upload **replaces** it.
> The CLI sends no "only if absent" condition and asks nothing, and whether the
> previous bytes can be recovered depends on storage configuration — it is not
> guaranteed. If the path exists only in the external layer, the external store
> is not changed, but the new managed file now **shadows** it in the resolved
> view. Upload into a fresh prefix, and `browse` the target before you upload.

If a transfer fails partway through, files that already completed stay
written — there is no rollback — and in-progress multipart parts are abandoned.
Re-running the command uploads every file again and replaces every destination
path, including any change someone made there after the first attempt. Prefer
a fresh prefix, and `browse` before re-running into a shared one.

If the authorization request never answers (timeout, network), the CLI prints
the idempotency key it used and suggests retrying with
`--idempotency-key <same key>`. The key only guards against duplicate
concurrent submissions: it does not protect content and does not guarantee the
same upload plan. Any rerun, with or without it, replaces every destination
path again. An empty key is refused; the maximum is 255 characters.

Output is each canonical path, then `Uploaded N file(s), B bytes`. With
`--json`: `{uploaded, totalBytes, files: [{path, bytes}]}`.

### Step by step

Namespace `my-team`, source `robot-data` — add `--namespace my-team` to each
command if that is not your active login.

1. Find the source, or create an empty managed-only one (owner only):

   ```bash file="terminal"
   dreamlake source list
   dreamlake source create robot-data --description "Robot recordings"
   ```

2. Check that the target prefix is fresh — expect nothing, or not found:

   ```bash file="terminal"
   dreamlake source browse uploads/2026-10-15 --source robot-data
   ```

3. Upload a file. It lands at `uploads/2026-10-15/calib.yaml`:

   ```bash file="terminal"
   dreamlake source upload ./calib.yaml --source robot-data --to uploads/2026-10-15
   ```

4. Upload a folder:

   ```bash file="terminal"
   dreamlake source upload ./run-01 -r --source robot-data --to uploads/2026-10-15/run-01
   ```

5. Validate — list what landed, check the layer and metadata, and compare a
   round trip:

   ```bash file="terminal"
   dreamlake source browse uploads/2026-10-15 --source robot-data -r --files
   dreamlake source stat uploads/2026-10-15/calib.yaml --source robot-data
   dreamlake source download uploads/2026-10-15/calib.yaml --source robot-data -o ./check
   cmp ./calib.yaml ./check/calib.yaml
   ```

## Managing a source

Who may run each one is listed in [Who can do what](#who-can-do-what):
`delete-object` and `delete-prefix` need EDIT; `check-access` needs USE and
namespace membership; the settings, editor and deletion-operation routes are
owner-only. The permission for `connectors` is not covered there. Run any of
them with `--help` for its flags.

| Command | What it does |
| --- | --- |
| `source connectors` | Which connection kinds each source connector accepts |
| `source import` | Import an external source (S3, Hugging Face) |
| `source metadata` | Rename a source, or change its description |
| `source delete-object` | Delete one managed object (immediate, physical) |
| `source delete-prefix` | Queue a recursive delete of one managed directory |
| `source delete-status` / `delete-retry` | Read or retry a directory deletion |
| `source external-set` | Attach or replace a source's external layer |
| `source external-remove` | Detach a source's external layer (the provider is untouched) |
| `source enable` | Enable a source (its configuration is validated first) |
| `source disable` | Disable a source |
| `source check-access` | Probe a source's upstream (changes nothing) |
| `source delete-source` (+ `-status` / `-retry`) | Queue deletion of a whole source |
| `source editors` / `editor-add` / `editor-remove` | List, grant or remove per-source Editors |
| `source references` | Which projects and bindrs organize this source |

> **Warning:** `delete-object` removes one managed object physically and immediately;
> `delete-prefix` queues a recursive delete of a managed directory. Neither
> touches the external layer. The CLI has no undo, and recovery is not
> guaranteed — it depends on storage configuration that is not documented here.

## Sharing a source by link

A **share link** lets a signed-in person who is *not* a member of the owning
namespace open the source. Owner/Admin only, all four commands — in practice
the namespace owner, since organizations currently have only OWNER and MEMBER
roles.

```bash file="terminal"
dreamlake source share --source my-bucket --role read   # turn it on, print the link
dreamlake source shares --source my-bucket              # who the link admitted
dreamlake source shares-remove --source my-bucket --user u_123
dreamlake source share-off --source my-bucket [--forget]
```

`--role read` grants the whole resolved tree, read-only. `--role write` adds
upload, overwrite and delete **in the managed layer only** — the external layer
is read-only for everyone, the owner included. A share covers the whole source
or none of it; there is no way to share one directory.

> **Warning:** The token in the link is a bearer credential with **no expiry** — it lives
> until you turn the link off. The CLI keeps no copy: not in your config, not in
> a cache, not in any log, and no other response carries the token. If you lose
> the link, re-run `share` — on an already-shared source the token is **reused**,
> so you get the **same** link back, with no rotation and no effect on anyone
> already holding it.

That reuse is why changing `--role` from read to write does not invalidate the
links you already handed out.

`shares` lists whoever redeemed the link. Redeeming records an admission for
whoever presented the token without checking membership first, so a member or an
Editor who clicks a link appears there too — and the row grants them nothing
they did not already have, since membership and the link are independent and the
stronger one wins. An empty list does not mean nobody can read the source.

`shares-remove` is **not a block.** It returns one person to "has not been
admitted"; the link they still hold re-admits them the next time they open it.
Keeping the link open while durably excluding one person is not supported — the
link's three states (off, read, write) are the whole model. To exclude someone,
turn the link off. Removal is idempotent, so retrying it is always safe.

`share-off` clears the token either way, so the URL people hold stops working in
both spellings. What `--forget` changes is whether anyone needs a URL at all to
come back. Without it the admission records are kept, and turning sharing back
on lets everyone already admitted straight back in **with no link** — the
admission is what authorizes them, so nothing has to be redistributed. With
`--forget` the records are deleted, so everyone must redeem a link again; since
re-enabling mints a **fresh** token, that means the link the next `share`
prints, not the one they kept.

> **Warning:** Turning the link off stops **new** access immediately, but reads and writes are
> served by short-lived URLs the client uses directly against storage, and one
> already issued cannot be recalled: 5 minutes for a managed-layer or S3 read,
> 1 hour for any write, and a documented 4 hours for a Dropbox read. A Hugging
> Face read has no bound and needs none — this version serves only public,
> ungated files and hands back the Hub's own unsigned URL. Storage does not
> re-check expiry mid-transfer either, so a download that started inside the
> window runs to completion.

## Every flag, everywhere

`--namespace <slug>` is accepted across the group and defaults to your active
login; every command that acts on one source takes `--source <name>`.
Everything except `download` takes `--json`. `create`, `import`,
`upload`, the delete commands, `enable`/`disable`,
`external-set`/`external-remove` and `editor-add`/`editor-remove` take
`--idempotency-key`; `metadata` does not. The four sharing commands take `--source <name>`,
`--namespace <slug>` and `--json`, like the rest of the group. None of them
takes `--idempotency-key`: sharing records no revision to retry against, and
both `share-off` and `shares-remove` are idempotent on their own.

## Project ownership-transfer boundary

A Source binding or reference still blocks the entire
[`project move`](cli-projects.md#move-a-whole-project-and-its-supported-resources)
request. The expanded workflow supports owned Notes, Artifacts and Envs, not
Sources, Workflows or Annotations. `ProjectSourceBinding` stays unchanged; there
is no Source migration or implicit Connection/credential transfer. Do not skip
its manifest entry, silently detach it or simulate an ownership move with
copy/delete. Standalone Source transfer remains execution-gated.
