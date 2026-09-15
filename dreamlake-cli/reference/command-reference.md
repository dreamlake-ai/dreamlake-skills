# Command reference

Every command. Run `dreamlake <command> --help` for the full option list.

## Auth & environments

| Command | What it does |
| --- | --- |
| `login [--env <name>]` | Log in (device flow, or `--token`). Built-in envs: `staging`, `prod` |
| `logout` | Log out of the active environment |
| `profile` | Show the current user and active environment |
| `env list` | List logged-in environments (`*` = active) |
| `env use <name>` | Switch the active environment |
| `env remove <name>` | Forget a saved environment |

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

See [External sources](sources.md).

| Command | What it does |
| --- | --- |
| `source list` | Connected sources in a namespace |
| `source browse [path] --source <n> [--dirs] [-r] [-0]` | List paths inside a source, one level by default |
| `source fetch <path> --source <n>` | Mint a short-lived public download URL for one file |
| `source download <path> --source <n> [-o <dir>] [-r]` | Write bytes to local disk |

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

## Video and search

| Command | What it does |
| --- | --- |
| `video upload <file> [--user] [--project]` | Upload a video straight to BSS |
| `video download <id> [-o <out>]` | Download a video by BSS id |
| `vectorize --episode <t> \| --project <t>` | Run CLIP + LLaVA over a scope and index the embeddings |

> **Warning:** `video upload` writes to blob storage only — the file gets no catalog entry,
> so `list` will not show it and no command can delete it. Use
> `dreamlake upload` unless you specifically need the raw blob path.
> `vectorize` additionally needs an external vectorize service and Qdrant.

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
