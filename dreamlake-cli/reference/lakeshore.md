# Lakeshore resources

To connect an existing queue server and inspect its live collections, see
[Mount a queue server](queues.md) (unreleased).

Three collections describe the machinery that runs your code. They share one
registrar on the server and one implementation in the CLI, so they take the
same five verbs and differ only in the noun.

| Group | What a row describes |
| --- | --- |
| `dreamlake provider` | **how a machine gets launched** — the launcher and its credentials |
| `dreamlake storage` | **where a worker reads and writes bulk data** |
| `dreamlake queue-def` | **a queue's policy** — not its live state |

```bash file="terminal"
dreamlake provider create --file provider.json --if-exists ok
dreamlake provider list
dreamlake provider show kit-local
dreamlake provider update kit-local --description '…'    # config is a REPLACE
dreamlake provider delete kit-local --yes                # soft delete
```

Every verb takes `--namespace <slug>` (default: the active login) and `--json`.
Swap `provider` for `storage` or `queue-def` and everything below is unchanged.

## Creating a row

`kind` is **required** — this collection has no server-side default. It is the
launcher discriminator (`local`, `slurm-ssh`, `aws-ec2`, `gce`, `k8s`, …) and
it is a free string server-side on purpose, so a new launcher never needs a
schema change.

```bash file="terminal"
dreamlake provider create --name kit-local --kind local --config '{"shell":"bash"}'
dreamlake provider create --file provider.json --if-exists ok
```

| Flag | Meaning |
| --- | --- |
| `--file <path>` | JSON or YAML file holding the whole row |
| `--name <name>` | row name, unique within the namespace (overrides `--file`) |
| `--kind <kind>` | required — the launcher discriminator |
| `--description <text>` | free text |
| `--config <json\|@file>` | non-secret config, inline JSON or `@file.json` |
| `--secret <json\|@file>` | credentials — encrypted at rest, never returned |
| `--if-exists <mode>` | what a 409 means: `fail` (default) or `ok` |

Rows here are **create-only**. A 409 means the name is taken and nothing was
touched — a failure for a human typing a command, a success for a `make push`
you expect to run twice. That is what `--if-exists ok` is for:

```text file="output"
⚠ a provider named 'kit-local' already exists — nothing was overwritten
```

`dreamlake declare provider.json --collection lakeshore-providers` does exactly
what `provider create` does. `declare` is the generic writer for all five head
collections; these groups are the lifecycle for one of them.

## Secrets are one-way

`--secret` is encrypted at rest (AES-256-GCM) and is **never returned by any
route**. After a create, `show` can only tell you that a secret exists.

Three states, and the CLI maps them to flags exactly as the server defines them:

| You pass | The server does |
| --- | --- |
| neither `--secret` nor `--clear-secret` | **keeps** what is stored |
| `--clear-secret` | **clears** it (sends `secret: null`) |
| `--secret <json\|@file>` | **rotates** it |

Nothing in this CLI can print a credential back, and no output implies that it
could.

## `update` replaces `config`, it does not merge it

> **Warning:** Passing `--config '{"region":"us-west-2"}'` against a stored
> `{ region, bucket }` leaves you with `{ region }` and **no bucket**. There is
> no deep merge on this route. `show --json` first, edit the whole object, then
> pass it back. The CLI prints a warning before it writes.

Omitting a flag leaves that field exactly as it was. `--name` renames the row.

## `delete` is soft

The server stamps `deletedAt` and answers `200 { success: true }` — never a
204. The row stops appearing in every read and **its name is freed for a new
create**; nothing is erased.

Without `--yes` on a non-TTY the command **cancels and returns 0** rather than
prompting, so a script never hangs and never deletes by accident. "I
deliberately did not do the thing" is a success in this CLI, not a failure.

## Reading

```bash file="terminal"
dreamlake provider list --kind k8s --json
dreamlake provider list --page 2 --page-size 50
dreamlake provider show kit-local            # name or 24-hex id
```

`list` filters `--kind` server-side, exact match. The server clamps
`--page-size` to 1..200 and defaults to 200. `show` accepts either the row name
or its 24-hex id, and prints `config` in full.

## Permissions

Read needs `ADMIN` or `READ`; **create, update and delete need `ADMIN`**. A
member with `READ` gets a 403 on every write verb, which is why the CLI's 403
messages name the verb rather than saying "forbidden".

## Beyond CRUD

These five verbs manage the **row in DreamLake**. Standing up the
infrastructure the row describes — scaffolding terraform, resolving the
decisions, planning, applying, and putting a daemon on the result — is the
[provider lifecycle](provider-lifecycle.md), and it is designed to be driven by
an agent.
