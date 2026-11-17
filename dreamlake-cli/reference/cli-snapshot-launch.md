<!-- generated from https://cli.dreamlake.ai/snapshot-launch.md at 0.132.0 c1903de; do not edit -->

# Snapshot & launch

Two commands run a script from this repository somewhere else.

```bash file="terminal"
dl snapshot                    # archive + register this tree → an id
dl launch train.py --queue cpu # snapshot, queue it, wait for the result
```

Both submit control requests to the **lakeshore control plane**. Neither needs
`dl login`; they need `--server` (or `$LAKESHORE_URL`) and the control-plane
token in `$LAKESHORE_CLIENT_TOKEN`. `launch --mount` is the exception: it goes
through DreamLake with your login and a mount's stored credential
([below](#launch-through-a-mount)). This transport does
not grant the control plane cloud-launch authority. Workload execution must use
an explicitly user-configured launch server with its appropriate IAM role; verify
the selected queue's execution route before submitting. No control-plane/service
IAM, ambient service credentials, operator Vault IAM user or direct hosted-backend
provider execution may substitute for that server. If the route is unverified,
hold new workload launches; snapshot preparation and read-only inspection may
continue. See [the required launch boundary](https://cli.dreamlake.ai/providers#required-launch-boundary).
This page documents command behavior, not acceptance of that architecture.

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
- **Submit it.** For example, `dl launch hello_job.py --queue cpu`.
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
  dl launch <script> --snapshot 665f0a1b2c3d4e5f60718293
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
dl launch train.py --snapshot $(dl snapshot --json | jq -r .id)
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
dl launch train.py --queue cpu
dl launch train.py --arg --epochs --arg 10
dl launch eval.py --snapshot 665f0a1b2c3d4e5f60718293 --no-wait
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
    dl launch train.py --queue cpu
    export LAKESHORE_QUEUE=cpu
    queue: cpu        # at the top level of .dreamrc
```

> **Warning:** `launch` exits **0 when the script exited 0** and **1 when it did not**. The
> script's own stdout and stderr are printed through verbatim. Under `--json`
> they are the `stdout` / `stderr` fields and the real number is `exitCode` —
> read that, not `$?`, if you need to tell "the script failed" apart from "the
> launch failed".

### Launch through a mount

`--mount` submits the same launch to a Lakeshore you mounted in DreamLake
(`dl queues mounts`), using your DreamLake login. The mount's stored
control-plane credential stays on the DreamLake server: this command never
reads, sends or prints a control-plane URL or token, and ignores
`$LAKESHORE_URL`, `$LAKESHORE_NAMESPACE` and `$LAKESHORE_CLIENT_TOKEN`.

```bash file="terminal"
dl launch hello.py --mount acme/lab --queue default --no-wait
dl launch hello.py --mount acme/lab --queue default --invocation-id 01KZCBY5MWQ7X8N2V4T6R9P0AB
```

| Flag | Meaning |
| --- | --- |
| `--mount <[namespace/]prefix>` | the mount, in your default namespace unless one is given. Excludes `--server` and `--namespace`: the mount names both |
| `--invocation-id <id>` | repeat a launch whose response was lost; returns that invocation instead of launching again |
| `--timeout-seconds <s>` | how long this command waits for the result (default 3600). A client wait only: reaching it does not cancel or kill the run |

- **Code.** The snapshot is the `.dreamrc` `code:` block, built locally. It must
  be at most 128 KiB; DreamLake checks it, stores it in the mount's
  `code-staging` storage and registers it before submitting. The legacy
  `git archive` snapshot and `--snapshot` are not accepted with `--mount`.
- **Authority.** Launching needs `lakeshore:use` in the mount's namespace and
  reading a result needs `lakeshore:read`. Only mounts created with
  management access can launch; a queue-only mount is refused
  (`queue_mount_execution_unsupported`).
- **Placement.** Unchanged: the queue's scheduler picks a worker serving it.
- **Identity.** The invocation id is printed before anything is submitted
  (under `--json`, as `Invocation: <id>` on stderr; stdout stays one JSON
  object). If the response is lost, repeat the command with
  `--invocation-id`, not without it. The repeat must be identical: the same
  queue, script and arguments, and an unchanged local `code:` tree, because
  the snapshot is rebuilt from it. Then the existing invocation is returned.
  The same id with anything changed is refused (`invocation_conflict`) and
  nothing new runs.

The result is read back through DreamLake, so the JSON record also carries the
`mount` and the `workerId` that ran it.

## Which provider ran it

`launch` names a queue; the workers serving that queue were started by a
**provider**. To see which, and whether anything is currently claiming it:

```bash file="terminal"
dl provider status -n aws-demo
```

Zero live workers for a provider is a normal state, not a fault — see
[Provider lifecycle](cli-provider-lifecycle.md).
