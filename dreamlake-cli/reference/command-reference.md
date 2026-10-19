# Command reference

Every command. Run `dreamlake <command> --help` for the full option list.

## Collection defaults and help

Collection groups with a `list` command also accept listing directly on the
parent. For example, `dreamlake hosts --all` is equivalent to
`dreamlake hosts list --all`. Parent help combines the listing options and the
available subcommands; explicit `list --help` remains focused on listing.

```bash cli-help="hosts"
dreamlake hosts
dreamlake hosts --all
dreamlake hosts -h
dreamlake hosts list -h
```

The same convention applies to agents, Notes, tasks, sessions, jobs, pipelines,
workflows, runnables, run configurations, sources, connections, organizations,
teams, artifacts, scenes,
libraries, provider/storage/queue definitions, provider registrations,
service accounts, queues, infrastructure stacks, layouts, installed skills,
Vault metadata, ownership transfer requests, and their nested groups that have a `list` command.
`auth env` also lists saved login environments. Groups without a `list`
operation retain their existing behavior.

Required list scopes still apply: for example, `dreamlake providers NAMESPACE`
and `dreamlake infra --project PROJECT` supply the same scope as their explicit
`list` forms. Optional list arguments work too, such as `dreamlake tasks PREFIX`.
When a value matches a subcommand name, use explicit `list` to disambiguate it.
List options apply to the default listing; other subcommands keep their own
options and validation. Existing scripts using explicit `list` continue to work.

This convention is available in CLI 0.76.0 and later. Earlier releases require
explicit `list`.

## Auth & environments

| Command | What it does |
| --- | --- |
| `login [--env <name>]` | Log in (device flow, or `--token`). Built-in envs: `staging`, `prod` |
| `logout` | Log out of the active environment |
| `profile` | Show the current user and active environment |
| `auth env list` | List logged-in environments (`*` = active) |
| `auth env use <name>` | Switch the active environment |
| `auth env remove <name>` | Forget a saved environment |

## Vault import

| Command | What it does |
| --- | --- |
| `vault add -p <prefix> -n <name> --stdin --request-id <id>` | Create or replace with `--if-match`; retain ID for uncertain response recovery |
| `vault write-status --request-id <id>` | Authenticated metadata receipt for an identified write |
| `vault import --ssh -p <prefix> [--config <file>]` | Empty checklist, explicit profile/key selection and destination review |
| `vault import --ssh -p <prefix> --dry-run` | Metadata discovery; no private-key reads or vault calls |
| `vault import --ssh -p <prefix> --json --select <item>` | Explicit noninteractive upload; repeat `--select` for more items |
| `vault import --pass-otp -p <prefix> --dry-run --store <directory>` | Redacted OTP preview only; no upload |
| `vault import --pass-otp -p <prefix> --store <directory> --select <path>` | Selected OTP creation; HOTP inactive by default (0.16+) |
| `vault otp -p <prefix> -n <name> [--to-json]` | Owner-only code retrieval (CLI 0.13.0); Python `client.vault.otp(name, prefix=..., to_json=...)` |
| `vault otp -n <name> --activate --counter-owner dreamlake --if-match <revision>` | Activate inactive HOTP without generating a code (0.16+) |
| `vault otp -n <name> --request-file <private-path>` | Issue/recover HOTP using one immutable request intent |
| `vault list -p <prefix> [--include-deleted]` | Complete metadata list through bounded pages |
| `vault list -p <prefix> --limit 50 [--cursor <cursor>]` | One metadata page and nextCursor |
| `vault unbind --binding-id <id> --entry-id <id> --entry-revision <revision>` | Release an exact retention reference; does not revoke remote SSH access |

See [Vault operations](vault-operations.md) for the 0.16 commands and paired Python 0.13 examples.

Choose exactly one of `--ssh` or `--pass-otp`. Ordinary `--pass` is reserved and rejected.
Legacy `vault ssh sync` and `vault pass sync --otp` remain compatibility aliases.

See [Selected SSH import](ssh-sync.md) for file restrictions, revisions and partial retries.

## Data

| Command | What it does |
| --- | --- |
| `upload <path> --episode <t> --to <p>` | Upload a file or folder (resumable); `--bindr`, `--type`, `--yes` |
| `download --episode <t> --from <p> [-o <out>]` | Download a file, or a folder/episode recursively |
| `list --episode <t> [--type <k>] [--json]` | List assets in an episode |
| `list project [--json]` | List projects in your namespace |
| `list episode --project <t>` | List episodes in a project |
| `list bindr --project <t>` | List bindrs in a project |
| `list dataset --project <t>` | List datasets in a project |

## Resources

| Command | What it does |
| --- | --- |
| `create project <name> [--public] [--visibility <v>]` | Create a project (private by default) |
| `update project <slug> [--name] [--description] [--visibility] [--tags]` | Update a project |
| `delete project <slug> [--yes]` | Hard-delete a project and its subtree |
| `create bindr <name> --project <t> [--episode <glob>]` | Create a bindr (episode members) |
| `update bindr <name> --project <t> [--add <glob>] [--remove <glob>]` | Add/remove episodes |
| `delete bindr <name> --project <t>` | Delete a bindr |
| `create dataset <name> --project <t>` | Create a dataset (bindr members) |
| `update dataset <name> --project <t> [--add <glob>] [--remove <glob>]` | Add/remove bindrs |
| `delete dataset <name> --project <t>` | Delete a dataset |
| `delete episode <name> --project <t> [--yes]` | Hard-delete an episode + its files |
| `delete file <path> --episode <t> [--yes]` | Hard-delete a file (or folder) |

## Declarations & versions

See [Declaration collections](collections.md).

| Command | What it does |
| --- | --- |
| `declare <file...> [--collection <n>] [--if-exists ok\|fail] [--dry-run]` | Create head rows from JSON/YAML; the collection is inferred from the payload |
| `runnable list [--kind <k>] [--module <m>]` | List runnables (`udf` \| `session` \| `agent`) |
| `runnable show <name>` | One runnable, with its full 64-char `latestVersion` and global path |
| `runnable version push <name> --source <file> [--signature <file>]` | Register a version; the key **is** `sha256(source)` |
| `runnable version list <name>` | Versions, newest first (source is not included) |
| `runnable version show <name> [version] [--at <ref>] [--source-only]` | One version; `version` is optional and defaults to `latest` |
| `runnable import <name> [--at <latest\|prefix\|sha256>] --out <dir>` | Fetch source + signature + `PINNED.json`, pinned to one version |
| `runconfig list [--provider <n>] [--host-key <hk>]` | List run configs, or the ones sharing a placement key |
| `runconfig show <name>` | One run config, runtime and extras in full |

> **Warning:** `-v, --version` is declared on the root program and Commander resolves a root
> option from any descendant, so `runnable import <name> --version <sha256>`
> prints the CLI version and **exits 0 having imported nothing**.

## Agents

See [Agents](agents.md).

| Command | What it does |
| --- | --- |
| `agents create [name] --prompt <text>` | Declare an agent from an inline prompt |
| `agents create [name] --file <path>\|-` | …from a Claude agent file, or stdin (heredoc) |
| `agents create [name] --edit` | …from a scaffold opened in `$EDITOR` |
| `agents create … --tools <csv> --model <id>` | Constrain the tool set and the model |
| `agents create … --allow/--ask/--deny <rule>` | Permission rules (repeatable) |
| `agents create … --arg 'name:type!'` | A typed prompt argument; every `{{ placeholder }}` needs one |
| `agents create … --run-config <n> --queue <n>` | Attach a machine by reference |
| `agents create … --dry-run` | Resolve, validate and print — send nothing |

## Lakeshore resources

See [Lakeshore resources](lakeshore.md). Substitute `storage` or `queue-def` for
`provider` — the five verbs are identical.

| Command | What it does |
| --- | --- |
| `provider create --name <n> --kind <k> [--config <j>] [--secret <j>]` | Create a row; `--kind` is required |
| `provider create --file <path> [--if-exists ok]` | …from JSON/YAML; `ok` makes a 409 a success |
| `provider list [--kind <k>] [--page <n>] [--page-size <n>]` | List rows in a namespace |
| `provider show <name\|id>` | One row, `config` included |
| `provider update <name\|id> [--config <j>] [--secret <j>] [--clear-secret]` | Update; `--config` **replaces** wholesale |
| `provider delete <name\|id> [--yes]` | Soft-delete; without `--yes` on a non-TTY it cancels, rc 0 |

## Provider lifecycle

See [Provider lifecycle](provider-lifecycle.md). Every one of these takes
`--json` and reports a `status` plus a `nextAction`.

| Command | What it does |
| --- | --- |
| `provider create -n <name> --provider <vendor> [--continue]` | Scaffold `.dream/providers/<name>/` and scan for unresolved decisions |
| `provider plan -n <name>` | `init` + `validate` + `plan`. Applies nothing |
| `provider apply -n <name> --yes` | Apply. **This spends money** |
| `provider connect -n <name> [--host user@host]` | Start a daemon on the result under the best supervisor available |
| `provider status -n <name>` | Recompute the phase from the world |

## Fabric

See [Snapshot & launch](snapshot-launch.md).

| Command | What it does |
| --- | --- |
| `snapshot [--server <url>] [--namespace <slug>]` | Archive this tree, upload it, register it; prints the snapshot id |
| `launch <script> --queue <name>` | Snapshot, queue, wait. Exit code is the **script's** |
| `launch <script> --arg <v> --arg <v>` | Pass arguments to the script |
| `launch <script> --snapshot <ref> --no-wait` | Launch an existing snapshot and return the invocation id |

## Sources

See [Sources](sources.md).

| Command | What it does |
| --- | --- |
| `source list` | One page of sources in a namespace |
| `source create <name> [--description <text>]` | Create an empty managed-only source (owner only) |
| `source import` | Import an external source (S3, Hugging Face) |
| `source browse [path] --source <n> [--dirs] [--files] [-r] [-0]` | List paths in the resolved view, one level by default; `--dirs`/`--files` filter |
| `source stat <path> --source <n>` | One exact path in the resolved view, with metadata and origin layer |
| `source fetch <path> --source <n>` | Mint a short-lived public download URL for one file |
| `source download <path> --source <n> [-o <dir>] [-r]` | Write bytes to local disk |
| `source upload <path> --source <n> [--to <prefix>] [-r]` | Upload into the managed layer; **silently replaces** existing managed paths |
| `source metadata` | Rename a source, or change its description |
| `source delete-object` | Delete one managed object (immediate, physical) |
| `source delete-prefix` | Queue a recursive delete of one managed directory |
| `source external-set` / `external-remove` | Attach or replace / detach a source's external layer (the provider is untouched) |
| `source enable` / `disable` | Enable (configuration validated first) or disable a source |
| `source check-access` | Probe a source's upstream (changes nothing) |
| `source editors` / `editor-add` / `editor-remove` | List, grant or remove per-source Editors |
| `source references` | Which projects and bindrs organize this source |
| `source share` / `share-off` / `shares` / `shares-remove` | Turn a share link on or off, list or remove admissions |

## Libraries

Asset libraries — a plain directory of 3D assets, searchable per asset.
Guide: [docs.dreamlake.ai/libraries](https://docs.dreamlake.ai/libraries/).

`--embed` shells out to the `dreamlake` Python package and must produce
vectors from the same model as the server's query encoder (**SigLIP2**,
`open_clip/ViT-B-16-SigLIP2/webli`), or the server ignores them and search
stays keyword-only — by design, with no error. `dreamlake` 0.25.0 and later
default to SigLIP2, so a current toolchain needs no flag; `--model siglip2`
pins it explicitly, and `--model clip` is the legacy escape hatch that
yields a keyword-only library here. The push prints the encoder it used
(`vectors: … (open_clip/ViT-B-16-SigLIP2/webli, 768-d)`) and warns when
that is not the space DreamLake queries — upgrade with
`pip install -U "dreamlake[embed]"`, or pass `--model siglip2`. Verify with
`library info <ns>/<name>` — `semantic` must be `true`.

Discovery labels each asset's `kind` from its files: MJCF and URDF by
sniffing the XML, `mesh`/`image` from a single model or image file, and
`splat` either from a single `.ply`/`.splat`/`.spz`/`.ksplat` or from a
compressed-splat **directory** — `meta.json` plus its WebP planes
(`format: sog`), or `lod-meta.json` with one set per node subdirectory
(`format: lod`). The `format` reaches the manifest, which is what selects
the 3D viewer in the web app. A `dreamlake.yml` `kind:`/`format:` still
overrides detection.

| Command | What it does |
| --- | --- |
| `library push <dir> [--namespace <ns>] [--library <n>]` | Push a directory as a library (assets discovered by convention, sha256-diff incremental); `--thumbnails`, `--embed`, `--model <name>`, `--dry-run`, `--verify` |
| `library push <dir> --force` | Override the drift guard — without it, push refuses to delete assets added remotely since this directory last registered |
| `library pull <ns>/<name> [--asset <id>] [-o <dir>] [--json]` | Materialize files, hash-verified and incremental — byte-identical local files are skipped, a non-empty directory is synced (extras never deleted); `--all` adds platform artifacts |
| `library list [--namespace <ns>] [--all] [--json]` | Libraries in a namespace, or every visible library |
| `library search <query> [--library ns/a,ns/b] [--json]` | Per-asset search, one line per hit + `N of T hits · semantic on\|off` footer; filters `--kind --category --tag --license --limit --offset` |
| `library stat <ns>/<name> [--asset <id>] [-o <dir>] [--json]` | Freshness check against a local directory — `up-to-date` (rc 0) / `stale` / `absent` (rc 1); transfers no bytes, and an unchanged revision reuses the locally cached manifest (`--verify` re-downloads) |
| `library info <ns>/<name> [--asset <id>] [--json]` | Library summary (facet counts, size, semantic) or one asset's decision card (files, bytes, digest, effective license); `--verify` bypasses the local manifest cache |
| `library add <ns>/<name> <path> [--id <id>] [--title …] [--replace] [--dry-run] [--json]` | Add ONE asset to a remote library, no full local copy needed; `--replace` updates an existing id in place |
| `library rm <ns>/<name> <assetId…> [--dry-run] [--json]` | Remove assets remotely (the server reclaims their files); refuses to empty a library |

## Scenes

See [Scenes](scenes.md).

| Command | What it does |
| --- | --- |
| `scene push <dir> [--name] [--entry] [--type] [--visibility] [--thumbnail <png>]` | Push a directory as a new scene version (unchanged files are not re-uploaded); `--thumbnail` sets the cover image |
| `scene push <dir> --push-layers \| --allow-local` | Push a composed scene whose stack still references local layers — see [Scenes](scenes.md) |
| `scene create <dir> [...]` | Push the FIRST version — fails if the name already exists |
| `scene list [--namespace <ns>] [--json]` | List scenes in a namespace |
| `scene pull <name>[@<version>] [-o <dir>] [--force]` | Download a version, hash-verified |
| `scene compose [stack] [-o <dir>] [--force]` | Materialize a layered stack (`dreamlake.layers.json`) into a runnable scene directory (needs `pip install "dreamlake[compose]"`) |
| `scene delete <name> [--permanent]` / `scene restore <name>` | Soft-delete / restore; `--permanent` purges storage |

## Experiments workspace binding

See [Experiments workspace binding](experiments.md). Unreleased; requires matching
DreamLake and Dash server changes. All commands require `--namespace <slug>`.

| Command | What it does |
| --- | --- |
| `experiments workspaces` | List verified eligible managed Dash workspaces |
| `experiments binding` | Inspect the current binding and revision |
| `experiments connect <workspace>` | Preview a unique slug or stable ID; apply requires stable ID, `--instance-id`, `--apply`, and `--expected-revision` |
| `experiments disconnect` | Preview local detachment; apply requires `--apply --expected-revision`, retaining remote data |

## Skills

See [Agent skills](skills.md).

| Command | What it does |
| --- | --- |
| `skill list [--json]` | Bundled skills, and whether each is installed at project or global scope |
| `skill install [name] [--global] [--dir <path>] [--force]` | Copy one into `.claude/skills/`; refuses to overwrite without `--force` |

## Artifacts

| Command | What it does |
| --- | --- |
| `artifact push <file> [--title] [--kind] [--id]` | Push a new version; kind is auto-detected from the extension |
| `artifact push <file> [--visibility <v>] [--share]` | Make it public, or issue a `?share=` token |
| `artifact list [--namespace <ns>] [--json]` | List artifacts in a namespace |
| `artifact delete <id> [--yes]` | Soft-delete (restorable) |
| `artifact delete <id> --permanent` | Purge storage and catalog — irreversible |
| `artifact restore <id>` | Restore a soft-deleted artifact |

## Workflows

| Command | What it does |
| --- | --- |
| `workflow push <file> [--name]` | Validate a WorkflowSpec v1 and push it as a new version |
| `workflow list` / `workflow show <name>` | List workflows / show one |
| `workflow update <name> [--description] [--tags]` | Update metadata |
| `workflow delete <name> [--yes]` | Soft-delete (version history survives) |
| `workflow push-run <name> <file>` | Send one run-trace snapshot |
| `workflow watch-run <name> <file> [--interval <s>]` | Send snapshots until the run finishes |

## Pipelines

| Command | What it does |
| --- | --- |
| `pipeline create <name> [--file <p>] [--message <m>]` | Create a pipeline; `--file` also creates the first version |
| `pipeline list` / `pipeline show <name>` | List pipelines / show one |
| `pipeline update <name> [--file] [--rename] [--tags]` | New version, or metadata changes |
| `pipeline delete <name> [--yes]` | Soft-delete (version history survives) |
| `pipeline version list <name>` | List versions, newest first |
| `pipeline version show <name> <hash>` | Full version data (JSON) |
| `pipeline node list <name> <hash>` | Nodes in a version, with state |
| `pipeline node show <name> <hash> <node>` | One node (JSON) |
| `pipeline node state <name> <hash> <node> --status <s>` | Write back execution state |
| `pipeline workspace host --dist <p>` | Host a bundle, get a `page_url` |
| `pipeline workspace upload --workspace-id <id> --dist <p>` | Replace a workspace's contents |

## Organizations

| Command | What it does |
| --- | --- |
| `org list` / `org show <slug>` | List your orgs / show one |
| `org create <slug> [--name] [--description]` | Create an org (you become OWNER) |
| `org update <slug>` / `org delete <slug>` / `org leave <slug>` | Manage an org |
| `org member list <org>` | List members |
| `org member add <org> <user> [--role]` | Add a member (by email/name) |
| `org member role <org> <user> --role <r>` | Change a member's role |
| `org member remove <org> <user>` | Remove a member |

## Teams

| Command | What it does |
| --- | --- |
| `team list [<org>]` | Teams in an org, or all your teams |
| `team show <org> <team>` | Show a team (members, sub-teams) |
| `team create <org> <team> [--visibility] [--parent]` | Create a team (nested via `--parent`) |
| `team update <org> <team>` / `team delete <org> <team>` / `team leave <org> <team>` | Manage a team |
| `team member list <org> <team>` | List members |
| `team member add <org> <team> <user> [--role]` | Add a member |
| `team member role <org> <team> <user> --role <r>` | Change a role |
| `team member remove <org> <team> <user>` | Remove a member |

## Terminal sessions

See [Terminal sessions](sessions.md). Requires CLI 0.74.1+ and matching API and terminal gateway deployments.

| Command | What it does |
| --- | --- |
| `sessions targets` | Discover authorized targets and exact enrollments |
| `sessions list` / `sessions show ID` | Read saved descriptors |
| `sessions create --target ID --cwd PATH --codex-session UUID` | Save without executing; discover or explicitly pin `--enrollment` |
| `sessions resume UUID --target ID --cwd PATH` | Save/find and attach interactively; `--json` saves only |
| `sessions open ID` | Reattach in this terminal; Ctrl-] detaches |

## The CLI itself

See [Installation](installation.md).

| Command | What it does |
| --- | --- |
| `install [target]` | Install or re-install the native binary under `~/.local` |
| `self-update [target]` | Update to the newest release on your channel |
| `doctor` | Print install and auto-update diagnostics |
| `-v, --version` | Print the version and exit — **root only**; passing it to a subcommand exits 0 without running it |

> **Note:** `<t>` is a target string: `project[@namespace]` for `--project`, or
> `project[@namespace][:episode]` for `--episode`. `@namespace` defaults to
> your own.

## Unreleased prefix KMS policies

`vault kms show`, `preview --key`, `activate --key --request-id`, and `status <request-id>` use an explicit personal `--prefix` for policy operations. Activation requires an operator-approved key reference and an empty prefix. [Paired CLI/Python usage](vault-kms.md).

## Library immutable-generation compatibility

When the server requires Library upload protocol 2, `library push`, `library add`
and `library rm` publish a complete immutable generation. Unchanged local files
are uploaded into that generation; retained remote files and generated artifacts
are streamed through a private local cache rather than left pointing at an old
mutable prefix. This costs more upload traffic than the legacy differential
path, but an old cleanup can never delete a newly published generation.

The CLI negotiates the server's upload capabilities before writing. It uses the
legacy path only when the server explicitly allows it or the older server has
no capability endpoint. A v2 failure, missing required session support or unknown
capability response never downgrades to a legacy write. No new command flag is
needed. The server floor is independently gated and must not activate before a
compatible CLI and reader fleet are accepted.

Re-run the same command after interruption. The private local journal keeps the
stable session key, exact full-content fingerprint, prepared multipart plans and
completed-part ETags. The CLI reads authoritative per-session file presence
before retrying; it does not treat 412 or NoSuchUpload as success. Lost register
acknowledgements resolve through the durable session receipt. Expired sessions
start a fresh unique generation automatically. A changed source or a revision
conflict cannot rebase an existing session or fall back to the old protocol.
Local upload snapshots prevent concurrent source edits from changing the bytes
already planned for that session. Successful publication removes signed plans
and temporary snapshots; ordinary generated-file caches retain their existing
cache behavior. A previous publication receipt records its own published
revision, even if another writer has already advanced the current library.
