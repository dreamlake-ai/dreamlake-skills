# Pipelines

A pipeline is Python source that the server parses into a node graph. Each
upload of the source produces a new immutable version, identified by a
12-character hash.

## Creating and updating

```bash file="terminal"
dreamlake pipeline create my-pipeline --file ./pipeline.py --message "initial"
dreamlake pipeline list
dreamlake pipeline show my-pipeline
```

Passing `--file` (or `--source` for an inline string) runs the parser and
creates a version. Without either, `create` makes an empty pipeline.

```bash file="terminal"
dreamlake pipeline update my-pipeline --file ./pipeline.py --message "fix sampling"
dreamlake pipeline update my-pipeline --rename better-name
dreamlake pipeline update my-pipeline --tags robotics,training
dreamlake pipeline delete my-pipeline        # soft — versions survive
```

`--tags` replaces the existing tags rather than adding to them.

## Versions and nodes

```bash file="terminal"
dreamlake pipeline version list my-pipeline
dreamlake pipeline version show my-pipeline a1b2c3d4e5f6

dreamlake pipeline node list my-pipeline a1b2c3d4e5f6
dreamlake pipeline node show my-pipeline a1b2c3d4e5f6 tr_source
```

`version show` and `node show` always emit JSON — they exist to be piped
into something else.

## Writing back execution state

`node state` is the endpoint an execution engine uses to report progress.

```bash file="terminal"
dreamlake pipeline node state my-pipeline a1b2c3d4e5f6 tr_source \
  --status running --started-at 2026-07-29T10:00:00Z

dreamlake pipeline node state my-pipeline a1b2c3d4e5f6 tr_source \
  --status done \
  --artifacts '{"iframe_url":"https://...","segments_data":[{"start":0,"end":10}]}'
```

`--status` accepts `idle`, `queued`, `running`, `waiting`, `done`, `error`,
or `blocked`. Use `--error` with `--status error`.

`--artifacts` takes a JSON object. Three keys are understood:

| Key | Type | Meaning |
| --- | --- | --- |
| `iframe_url` | string | Human review page, rendered in an iframe |
| `source_url` | string | Original data source |
| `segments_data` | any | Segment annotation data |

Invalid JSON is rejected before the request is sent.

## Agent workspaces

```bash file="terminal"
dreamlake pipeline workspace host --dist ./dist.tar.gz
dreamlake pipeline workspace upload --workspace-id ws_123 --dist ./dist.tar.gz
```

`host` uploads a built frontend bundle and returns a `page_url` to open,
allocating a workspace for it. `upload` replaces the contents of a workspace
you already have, and optionally takes `--source` alongside `--dist`.
