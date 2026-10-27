<!-- generated from https://cli.dreamlake.ai/dreamrc.md at unknown; do not edit -->

# The .dreamrc reference

`.dreamrc` has existing consumers with different schemas. This reference indexes
them without reinterpreting visualization fields as launcher options or scene
composition. New registration fields are implemented in this change; release
availability must be verified separately.

## Registration fields

| Field | Type / rule |
| --- | --- |
| `repo` | Optional repository declaration; `name` and `remote` required together. |
| `repo.name` | Nonempty registry name. |
| `repo.remote` | Credential-free HTTPS or SSH Git remote; pointer only. |
| `repo.snapshot.commit` | Full 40-hex commit or 64-hex capture digest. |
| `repo.snapshot.backend` | `s3` or `github`. |
| `repo.snapshot.archive_key` | Existing object key or pinned GitHub ref. |
| `repo.snapshot.storage_name` | Required S3 storage name. No credentials. |
| `udfs[]` | Definition list; names unique across UDFs and agents. |
| `udfs[].name` | Dotted registry name. |
| `udfs[].entrypoint` | Python `module:function`; declared, not imported during upload. |
| `udfs[].source` | Relative UTF-8 source file inside manifest root, at most 512 KiB. |
| `udfs[].projects` | Optional existing project slug list; stored affiliation. |
| `agents[]` | Agent definition list. |
| `agents[].name` | Dotted registry name. |
| `agents[].source` | Relative Markdown file with YAML frontmatter and prompt body. |
| `agents[].projects` | Existing project slugs; overrides frontmatter projects when supplied. |

See the [complete upload example](cli-runnable-upload.md) and [agent frontmatter](cli-agents.md).
The SDK compatibility change keeps `repo`, `udfs`, and `agents` out of launcher
kwargs. Older SDK versions may forward unknown root keys as extras; use a build
containing that change before combining execution and registration fields.

## Execution fields

The SDK config lookup is explicit path, `$DREAMRC`, nearest ancestor `.dreamrc`,
then home `.dreamrc`. The new registration command takes one explicit manifest
path, defaulting to `.dreamrc` in the current directory; it does not inherit a
home manifest. Current launch code resolves queue separately from runtime mode.

| Field | Meaning |
| --- | --- |
| `default_mode` | Named default mode; SDK default `local`. |
| `modes`, legacy `mode` | Mapping of names to runtime configurations. |
| `providers` | Tagged launcher declarations: SSH, EC2, GCE, SLURM, Kube. Launcher-specific kwargs are open. |
| `queue` | Existing CLI launch default, below `--queue` and `LAKESHORE_QUEUE`. |
| `backend` | Runtime backend, e.g. local or fabric. |
| `server` | Execution endpoint. |
| `runner` | Execution runner; default process. |
| `tags` | Placement/worker matching requirements. |
| `resources` | Resource requirements, passed as a mapping. |
| `image` | Container image; pin a digest for repeatable environments. |
| `env` | String environment mapping; keep credentials outside registered declarations. |
| `timeout_s` | Invocation timeout in seconds. |
| `provider` | Named provider reference. |
| `host_setup` | Ordered host preparation commands, once per worker. |
| `run_setup` | Ordered commands before every invocation. |
| `dreamlake.remote` | Destination API for in-run artifacts. |
| `dreamlake.project` | Artifact project destination. |
| `extras` | Open provider/launcher kwargs. |
| `docker.network` | Docker network setting, only with the Docker runner. |
| `kube.namespace`, `kube.context` | Kubernetes namespace/context. |
| `kube.cpu`, `kube.memory` | Positive Kubernetes quantity strings or integers. |
| `kube.gpu` | Resource name plus positive count. |
| `kube.poll_interval_s` | Integer 1–3600. |
| `kube.image` | Legacy nested image spelling; must agree with top-level image. |

Runtime fields may appear in a named mode or at the root per the existing SDK
contract. Provider-specific open fields cannot have a closed global enum;
validate them against their provider's schema. See the
[owning SDK config](https://github.com/dreamlake-ai/dreamlake-lakeshore/blob/main/dreamlake/lakeshore/config.py).

## Code capture fields

| Field | Default / meaning |
| --- | --- |
| `code.mounts[]` | Required when `code` is supplied. |
| `code.mounts[].local_path` | Source file/directory, relative to `.dreamrc`; supported env/home expansion. |
| `code.mounts[].target` | Relative unpack destination; default depends on mount count/type. |
| `code.mounts[].pypath` | `false`; adds destination to PYTHONPATH. |
| `code.mounts[].files` | `worktree` or `tracked`. |
| `code.mounts[].exclude` | Exclusion patterns. |
| `code.mounts[].exclude_from` | Relative file containing exclusion patterns. |
| `code.mounts[].exclude_vcs` | `true`; omit VCS internals. |
| `code.mounts[].include` | Paths inside directory mounts; default `["."]`. This is file selection, not configuration imports. |
| `code.workdir` | Working directory inside mounts; default first mount target. |
| `code.max_archive_mb` | Compressed archive ceiling; default 100 MiB. |
| `excludes`, `also_excludes`, `max_archive_mb` | Legacy repository-archive controls used by the existing snapshot path; not substitutes for the `code` block. |

See [snapshot/launch](cli-snapshot-launch.md) and the
[full capture bounds](https://github.com/dreamlake-ai/dreamlake-lakeshore/blob/main/docs/code-mounts.md).
Dataset dependencies use their own `datasets.yaml` list; automatic Source mounting
remains separate from manifest validation.

## Visualization and scenes

A dataset visualization `.dreamrc` uses `version: 1`, optional `name` and
`storage`, required `dataset`, and required `views`. It is validated by the
visualization package, not the execution SDK. Its complete schema is indexed in
[visualization configuration](cli-dreamrc-visualization.md).

Scene composition uses `dreamlake.layers.json`, independently from `.dreamrc`:
see [scene upload and composition](cli-scenes.md). Scene-layer references and XML
includes are not UDF config imports. Existing configurations remain valid.

## Imports, includes, and layers

No shared `.dreamrc` import/layer resolver is provided by the new registration
command. YAML anchors work within a file; they are not cross-file imports.
Do not claim scene composition semantics apply to execution or visualization.

Before adding a common resolver, specify layer order, map merges, list replacement
versus extension, field origins, include-relative paths, cycles, missing inputs,
and authorized remote references. Capture all inputs and resolved output with
hashes and provenance. Changes to an include after capture must not change an
old snapshot. Until then, unsupported composition keys must fail explicitly on
registration rather than silently disappearing.
