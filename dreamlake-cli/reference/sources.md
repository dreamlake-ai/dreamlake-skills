# External sources

A **source** is a connected external store — S3, Dropbox, HuggingFace — that
DreamLake can read on your behalf. The `source` group browses and reads them;
it does not copy anything into DreamLake and it does not write back.

```bash file="terminal"
dreamlake source list
dreamlake source browse --source my-bucket datasets/
dreamlake source fetch  --source my-bucket datasets/frames.tar
dreamlake source download --source my-bucket datasets/ -r -o ./local
```

Sources are declared like any other head collection —
`dreamlake declare source.yaml --collection sources` — see
[Declaration collections](collections.md). This group is the read side.

## `list`

```bash file="terminal"
dreamlake source list [--namespace <slug>] [--json]
```

Lists the connected sources in a namespace. The name it prints is what every
other command's `--source` wants.

## `browse`

```bash file="terminal"
dreamlake source browse [path] --source <name> [--dirs] [-r] [-0] [--json]
```

Lists resource paths inside a source, **one level at a time** by default.
Omit `path` to start at the root.

| Flag | Meaning |
| --- | --- |
| `--dirs` | list directories instead of files |
| `-r, --recursive` | descend into subdirectories |
| `-0, --print0` | NUL-separate the paths |
| `--json` | emit JSON |

`-0` exists for exactly one reason: object keys contain spaces, and a
newline-separated list piped into `xargs` splits them in the wrong place.

```bash file="terminal"
dreamlake source browse datasets/ --source my-bucket -r -0 \
  | xargs -0 -n1 dreamlake source fetch --source my-bucket
```

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

## Sharing a source by link

A **share link** lets a signed-in person who is *not* a member of the owning
namespace open the source. Owner/Admin only, all four commands.

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

`--source <name>` and `--namespace <slug>` are accepted by `browse`, `fetch`
and `download`; `--namespace` defaults to your active login. Everything except
`download` takes `--json`. The four sharing commands take `--source <name>`,
`--namespace <slug>` and `--json`, like the rest of the group. None of them
takes `--idempotency-key`: sharing records no revision to retry against, and
both `share-off` and `shares-remove` are idempotent on their own.
