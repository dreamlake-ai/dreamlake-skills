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

## Every flag, everywhere

`--source <name>` and `--namespace <slug>` are accepted by `browse`, `fetch`
and `download`; `--namespace` defaults to your active login. Everything except
`download` takes `--json`.
