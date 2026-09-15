# Snapshot & launch

Two commands run a script from this repository somewhere else.

```bash file="terminal"
dreamlake snapshot                    # archive + register this tree → an id
dreamlake launch train.py --queue cpu # snapshot, queue it, wait for the result
```

Both talk to the **lakeshore control plane** and nothing else. Neither needs
`dreamlake login`; they need `--server` (or `$LAKESHORE_URL`).

## `snapshot`

The repository is archived with `git archive`, honouring the `excludes` /
`also_excludes` pathspecs and the `max_archive_mb` ceiling from `.dreamrc`. A
dirty tree is snapshotted as a **real commit object without moving your
branch**, so you never have to commit in order to launch.

```text file="output"
snapshot
  server:     http://localhost:8080
  namespace:  default
  remote:     git@github.com:you/proj.git
  commit:     a1b2c3d (dirty)
✓ registered 665f0a1b2c3d4e5f60718293  (4.1 MB, kit-local)
  dreamlake launch <script> --snapshot 665f0a1b2c3d4e5f60718293
```

The server and namespace are printed **before** the write, never after. If you
are about to hit the wrong control plane, the line that tells you has to come
first.

Snapshots **dedupe on `(remote, commit)`**. Re-running on an unchanged tree
uploads nothing and gives you back the same id — and says so, because an
operator who just edited a file and expected an upload needs to know the tree
was clean:

```text file="output"
⚠ snapshot already registered — unchanged  (4.1 MB, kit-local)
  id:         665f0a1b2c3d4e5f60718293
```

| Flag | Meaning |
| --- | --- |
| `--server <url>` | control plane base URL (default `$LAKESHORE_URL`) |
| `--namespace <slug>` | control-plane namespace (default `$LAKESHORE_NAMESPACE`, else `default`) |
| `--json` | one `{ status, id, remote, commit, sizeBytes, … }` object instead of prose |

```bash file="terminal"
dreamlake launch train.py --snapshot $(dreamlake snapshot --json | jq -r .id)
```

## `launch`

```bash file="terminal"
dreamlake launch train.py --queue cpu
dreamlake launch train.py --arg --epochs --arg 10
dreamlake launch eval.py --snapshot 665f0a1b2c3d4e5f60718293 --no-wait
```

| Flag | Meaning |
| --- | --- |
| `--queue <name>` | queue to submit to (`$LAKESHORE_QUEUE`, else `queue:` in `.dreamrc`). **Never guessed** |
| `--snapshot <ref>` | launch an existing snapshot: a 24-hex id, a 40-hex commit, or `<remote>@<commit>` |
| `--arg <value>` | one argument for the script; repeat for more |
| `--no-wait` | submit and print the invocation id instead of waiting |
| `--server` / `--namespace` / `--json` | as above |

Omit `--snapshot` and the tree is snapshotted implicitly, which uploads
nothing when the commit is already registered.

The target is printed before anything is submitted:

```text file="output"
launch  train.py
  server:     http://localhost:8080
  namespace:  default
  queue:      cpu
  snapshot:   (from this working tree)
```

### The control plane picks the node

A launch names a **queue**, never a machine. A queue name that no worker
serves is not an error anywhere — the invocation just sits there, waiting for
a worker that may never arrive. That is precisely why the queue is resolved
from an explicit source and **never defaulted**. With none of the three
available, the launch stops before it spawns anything:

```text file="output"
✗ no queue — a launch has to say where it runs. Any one of:
    dreamlake launch train.py --queue cpu
    export LAKESHORE_QUEUE=cpu
    queue: cpu        # at the top level of .dreamrc
```

> **Warning:** `launch` exits **0 when the script exited 0** and **1 when it did not**. The
> script's own stdout and stderr are printed through verbatim. Under `--json`
> they are the `stdout` / `stderr` fields and the real number is `exitCode` —
> read that, not `$?`, if you need to tell "the script failed" apart from "the
> launch failed".

## Which provider ran it

`launch` names a queue; the workers serving that queue were started by a
**provider**. To see which, and whether anything is currently claiming it:

```bash file="terminal"
dreamlake provider status -n aws-demo
```

Zero live workers for a provider is a normal state, not a fault — see
[Provider lifecycle](provider-lifecycle.md).
