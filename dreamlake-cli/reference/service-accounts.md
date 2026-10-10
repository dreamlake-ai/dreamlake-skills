# Service accounts

Each Nymph daemon has its own service account, owned by a personal or organization
namespace. Service accounts are separate from human users and receive explicit
resource grants through DreamLake's permission system. Owning a namespace does
not give a machine all of that namespace's permissions. Namespace owners manage
these accounts; a machine cannot grant itself access.

These commands require a server with the service-account and machine-bootstrap
APIs. Older servers return an HTTP error; the CLI does not fall back to copying
human credentials onto a machine.

## Create and inspect

```bash cli-help="service-accounts"
dreamlake service-accounts create my-team --name dreamfs-worker --description "DreamFS development daemon"
dreamlake service-accounts list my-team
dreamlake service-accounts show my-team/0123456789abcdef01234567
```

```bash cli-help="service-accounts create"
dreamlake service-accounts create my-team --name dreamfs-worker --description "DreamFS development daemon"
```

An account name starts with a lowercase letter and contains at most 63 lowercase
letters, digits, underscores or hyphens. Retrying the same name and description
returns the existing account. Changing the description or reusing a revoked name
returns a conflict. No credential is printed by account creation.

```bash cli-help="service-accounts list"
dreamlake service-accounts list my-team --page 1 --page-size 50 --json
```

```bash cli-help="service-accounts show"
dreamlake service-accounts show my-team/0123456789abcdef01234567 --json
```

`show` includes the account, its explicit project and host grants, and its bound
enrollment ID when a Nymph is registered.

## Limit access to selected resources

```bash cli-help="service-accounts project-grants"
dreamlake service-accounts project-grants set my-team/0123456789abcdef01234567 --project 111111111111111111111111 --role READ
dreamlake service-accounts project-grants remove my-team/0123456789abcdef01234567 --project 111111111111111111111111
```

```bash cli-help="service-accounts project-grants set"
dreamlake service-accounts project-grants set my-team/0123456789abcdef01234567 --project 111111111111111111111111 --role READ
```

```bash cli-help="service-accounts project-grants remove"
dreamlake service-accounts project-grants remove my-team/0123456789abcdef01234567 --project 111111111111111111111111
```

Project roles are `READ`, `WRITE` or `ADMIN`. The project must belong to the
account's namespace. Grant only the role the workload needs. The current machine
API exposes scoped metadata reads; storing `WRITE` or `ADMIN` grants does not
enable arbitrary human-user endpoints or imply machine write APIs are shipped.

```bash cli-help="service-accounts host-grants"
dreamlake service-accounts host-grants set my-team/0123456789abcdef01234567 --host 222222222222222222222222 --read --use
dreamlake service-accounts host-grants remove my-team/0123456789abcdef01234567 --host 222222222222222222222222
```

```bash cli-help="service-accounts host-grants set"
dreamlake service-accounts host-grants set my-team/0123456789abcdef01234567 --host 222222222222222222222222 --read --use
```

```bash cli-help="service-accounts host-grants remove"
dreamlake service-accounts host-grants remove my-team/0123456789abcdef01234567 --host 222222222222222222222222
```

Host permissions are independent: `--use` does not imply `--read`. Setting a host
grant replaces both permissions; omitted flags become false. Use `remove` to
remove access entirely. Hosts must belong to the same namespace.

## Provision and enroll automatically

Pass a host name when launching one EC2 instance through a registered provider.
DreamLake creates a dedicated service account automatically. To select an account
you prepared with grants, pass its unused ID with `--service-account`:

```bash
dreamlake providers instances launch my-team/333333333333333333333333 --service-account 0123456789abcdef01234567 --host-name my-team/dreamfs/worker --unix-user ubuntu --request-id dreamfs-worker-1 --json
```

The backend supplies a short-lived, single-use bootstrap credential to the
instance installer. Nymph creates its own machine identity and enrolls under the
selected account. Human account tokens and Vault credentials are not copied to
the target by this automatic enrollment path. Bootstrap material is not returned
in the launch receipt or printed by this CLI. Do not put secrets in launch layers.

Use one account per Nymph and `--count 1`; provision additional machines with
separate names and request IDs. Omit `--service-account` to create each account
automatically. Reuse the same request ID and identical inputs
to recover an interrupted launch. A launch receipt is not proof that Nymph is
online or can run a workload. Inspect the named host with `dreamlake hosts status`
and verify the intended workload before treating it as ready. Cloud bootstrap
requires the server's configured installer and control plane to be reachable.

## Associate an existing Nymph

Keep an enrolled machine running while assigning its dedicated account:

```bash cli-help="service-accounts bind"
dreamlake service-accounts bind my-team/0123456789abcdef01234567 --enrollment 444444444444444444444444
```

The account and enrollment must belong to the same namespace. One account binds
to one enrollment, and one enrollment binds to one account. Repeating the same
binding is safe; attempting to replace either side fails. Binding does not
rekey or restart Nymph. Inspect the binding with `service-accounts show` and
check the machine with `hosts status` afterward.

## Revoke

```bash cli-help="service-accounts revoke"
dreamlake service-accounts revoke my-team/0123456789abcdef01234567
```

Revocation is permanent. Use a new account for a replacement identity. If control-plane
revocation is still `pending`, the command reports that state and exits nonzero;
repeat the revoke command to retry delivery. Do not treat a pending receipt as
confirmation that the daemon credential has been disabled everywhere. Local
account access is disabled immediately, but this is not a claim that already
running jobs have been killed. Revoking an
account does not terminate its EC2 instance or delete its data; manage the cloud
instance separately through `dreamlake providers instances`.
