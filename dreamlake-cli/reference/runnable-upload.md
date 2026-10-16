# Register UDFs and agents

Registration gives definitions names in a namespace. It does not execute or
publish them. Use a CLI release containing `runnable register` and `agents edit`; check
installed help before using these commands. Registration is separate from execution.

```bash cli-help="runnable register"
dreamlake runnable register .dreamrc --dry-run
dreamlake runnable register .dreamrc --namespace acme
```

`upload` is an alias for `register`. The offline preview reads the explicitly
declared files and shows their SHA-256 hashes. Registration uploads those exact
UTF-8 definition bytes, including complete modules with imports and helpers.
It does not upload the entire Git repository or execute imports.

```yaml
repo:
  name: udf-recipes
  remote: https://github.com/acme/udf-recipes.git
udfs:
  - {name: recipes.add, entrypoint: "tasks.math:add", source: tasks/math.py}
  - {name: recipes.multiply, entrypoint: "tasks.math:multiply", source: tasks/math.py}
  - {name: recipes.normalize, entrypoint: "tasks.text:normalize", source: tasks/text.py}
agents:
  - {name: recipes.triage, source: agents/triage.md, projects: [research]}
```

A [complete project](https://github.com/dreamlake-ai/dreamlake-cli/tree/main/examples/runnable-project)
contains the source files, agent prompt and manifest. Replace the repository
URL with your own. Project references must already exist in the chosen namespace.
The example does not need an existing project until you add `projects`.

Definition names are unique dotted registry names. Source paths resolve relative
to the manifest and must stay inside its directory, including symlink targets.
The current definition limit is 512 KiB per UTF-8 file. Existing declarations
with different metadata or prompts are refused; edit them explicitly. A bulk
upload is not atomic: earlier entries can have succeeded if a later one fails.
Retain receipts and inspect current state before retrying.

## Repository and archive pointers

A `repo` declaration registers a Git remote pointer; it does not fetch or verify
that remote. An optional `repo.snapshot` registers an already-stored archive
pointer using the existing snapshot API:

```yaml
repo:
  name: udf-recipes
  remote: https://github.com/acme/udf-recipes.git
  snapshot:
    commit: REPLACE_WITH_FULL_40_HEX_COMMIT_OR_64_HEX_DIGEST
    backend: s3
    storage_name: code-archives
    archive_key: snapshots/REPLACE_WITH_DIGEST.tar.gz
```

For GitHub use `backend: github` and an exact Git commit as `archive_key`;
`storage_name` applies to S3. Pointer registration never uploads, downloads,
validates, or executes the archive bytes. A conflicting existing snapshot receipt
is refused. The runnable and source-version metadata record `repo_id`, optional
`snapshot_id`, `source_file`, and `entrypoint`. These references still require
worker-side source/tree verification before execution.

`dreamlake snapshot` is the existing execution-control-plane capture/upload path;
it is a different API from declaration registry snapshots. Do not interchange
their IDs without an explicit bridge.

## One definition at a time

```bash
dreamlake declare udf.yaml --collection runnables
dreamlake runnable version push recipes.add --source tasks/math.py
dreamlake runnable version show recipes.add --source-only
dreamlake agents create triage --scope recipes --prompt 'Triage failed runs.'
```

```yaml
# udf.yaml
module: recipes
qualname: add
kind: udf
```

See [all `.dreamrc` fields](dreamrc.md), [agent editing](agents.md), and the
[registry API](runnable-api.md). A launchable bundle runnable and unified replay
remain planned; a repo pointer alone is not a runnable execution contract.

## Direct registration

A manifest is optional when registering one definition:

```bash
dreamlake runnable register --name recipes.add --source tasks/math.py --entrypoint tasks.math:add
dreamlake runnable register --name recipes.triage --kind agent --source agents/triage.md
```

Direct source paths resolve from the current directory and remain inside it.
The default kind is UDF. Use a manifest to register a shared repo/snapshot pointer
or a collection of definitions. Agent frontmatter still carries projects/context.

The private registration API and the execution control plane have separate
snapshot identities. Never pass a registry snapshot ID to `launch --snapshot`
without a verified bridge.

With a GitHub snapshot, the registration preflight verifies each uploaded source
against that exact local Git commit and captures its file paths for the Files
panel. The manifest must be at the Git root and `archive_key` must equal the full
commit. Definition contents are included for display; other paths can be listed
without their contents. This is not verification that the remote GitHub endpoint
has delivered that commit, nor verification of S3 archive bytes. Existing immutable
snapshot manifests must match rather than being overwritten.

## Execute a pinned UDF

CLI 0.71.0 introduced execution of one registered Python module on an exact
same-namespace enrolled host:

```bash
dreamlake runnable run udf/NAMESPACE/recipes.add@FULL_SHA256 \
  --target NAMESPACE/GROUP/HOST --enrollment-id ENROLLMENT_ID \
  --request-id YOUR_STABLE_REQUEST_ID --inputs inputs.json
dreamlake runnable receipt NAMESPACE/RUN_ID
```

The immutable version must bind an authorized repository, source file, and
matching entrypoint. This executor rejects registry snapshot bindings and does
not deliver a complete repo, install project dependencies, or execute agents.
Retain the same request ID and inputs when recovering an uncertain submission.
Inspect `dreamlake runnable run --help` for its supported runtime.
