# Snapshot & launch

Two commands run a script from this repository somewhere else.

```bash file="terminal"
dreamlake snapshot                    # archive + register this tree → an id
dreamlake launch train.py --queue cpu # snapshot, queue it, wait for the result
```

Both talk to the **lakeshore control plane** and nothing else. Neither needs
`dreamlake login`; they need `--server` (or `$LAKESHORE_URL`).

## Run here, or submit

The usual setup is a Terminal open on a machine you already have. The shell
runs on that machine, and so does everything on this page. Get the project
there first. These examples put each repository in its own directory under
`~/public/`. That is only a convention: nothing creates it, and the name does
not make anything public.

```bash file="terminal"
mkdir -p ~/public && cd ~/public
git clone https://github.com/you/hello-job.git    # first time; later: git -C hello-job pull
git clone https://github.com/you/shared-lib.git   # a sibling, used as ../shared-lib
cd hello-job                                       # .dreamrc is here
```

`.dreamrc` lives at the project root, in the repository. Every `local_path` in
it is a path on **this** machine, the one the Terminal is open on, resolved
from the directory containing `.dreamrc`. It is not a path on the laptop
running your browser, and nothing is uploaded from the browser.

From that shell there are two different ways to run a script:

- **Run it here.** For example, `python hello_job.py --message hi`. There is no
  snapshot and no queue, and `code:` is not read. Its dependencies must be
  installed on this machine.
- **Submit it.** For example, `dreamlake launch hello_job.py --queue cpu`.
  - It runs on whichever worker serves the queue, possibly another machine.
  - The selected code is archived here, uploaded to the namespace's
    `code-staging` storage, and unpacked on the worker.
  - The worker needs the script's dependencies and `dreamlake-lakeshore`
    already installed. A snapshot ships code only.

## `snapshot`

Both commands run through the Python SDK's bridge
(`python -m dreamlake.lakeshore.bridge`), so the interpreter they use must
have a `dreamlake-lakeshore` that ships it. **`dreamlake-lakeshore` 0.4.0 and
earlier do not**, and the command stops at "cannot import dreamlake-lakeshore".
The bridge is merged on the SDK's `main`
([dreamlake-lakeshore#24](https://github.com/dreamlake-ai/dreamlake-lakeshore/pull/24))
but is not yet released to PyPI.

With no `code:` block in `.dreamrc`, the repository you are standing in is
archived with `git archive HEAD`: **committed files only**. A dirty tree is
refused rather than shipped half-done. Commit first, or declare the code you
want shipped in a `code:` block (below).

```text file="output"
snapshot
  server:     http://localhost:8080
  namespace:  default
  remote:     git@github.com:you/proj.git
  commit:     a1b2c3d
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

## Choosing the code: `.dreamrc` `code:`

A `code:` block decides what ships: one or more directories or files, from
inside or outside the repository, each placed at a chosen path. Relative
paths resolve from the `.dreamrc` file, so launching from a subdirectory
ships the same thing. Files are taken as they are on disk, with VCS
directories and your excludes removed.

```yaml file=".dreamrc"
queue: cpu
code:
  workdir: hello
  mounts:
    - local_path: hello
      target: hello
      exclude: ["*.pkl", "results/"]
    - local_path: ../shared-lib
      target: libs/shared
      pypath: true
```

The worker unpacks the snapshot into a fresh directory, runs the script from
`workdir`, and puts only the `pypath` mounts on `PYTHONPATH`. An unchanged
tree reuses its snapshot. The full key table, bounds and unsupported Jaynes
features are in the SDK's
[code mounts reference](https://github.com/dreamlake-ai/dreamlake-lakeshore/blob/main/docs/code-mounts.md).
This requires the same SDK bridge, which is not yet on PyPI.

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
