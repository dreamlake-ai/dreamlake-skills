<!-- generated from https://cli.dreamlake.ai/notes/getting-started.md at 0.112.1 2a2fef0; do not edit -->

# Create and find memos

## Quick start

Log in with `dl login`. Core examples require **CLI 0.29.0+** and a
compatible server; individual guides state newer feature requirements.
Check your installed version with `dl --version`.

Before an agent's first live read or edit, [set its task identity](cli-notes-collaboration.md#one-identity-per-task).
Set both `DREAMLAKE_AGENT_ID` and `DREAMLAKE_AGENT_NAME` and reuse them for the task.

```bash cli-help="memos"
# Find a note and read it directly.
dl memos search "release plan"
dl memos read release-plan

# Preview a unique wording change, apply it, then read back.
dl memos replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dl memos replace "Draft checklist" --text "Ready for review" --note release-plan
dl memos read release-plan

# Create a private note from a Markdown file.
dl memos create "Release plan" --file release-plan.md

# Cross-interface design (unreleased target APIs; verify installed --help):
# https://docs.dreamlake.ai/notes/api/
```

Read normal output directly; no `--json` or `--view` is needed. Retain the read's
revision and hash for an edit. The replacement helper requires exactly one match
and guards its own read/write window. A dry run does not reserve the memo.
For an edit prepared from an older snapshot, use a [patch with the original
baseline revision](cli-notes-editing.md).

```bash cli-help="memos list"
dl memos list --limit 10
dl memos list --shared
dl memos list --namespace acme
dl memos list --include-archived
```
`--ns` is an alias of `--namespace` on every Memos command; both are the source
namespace to look in, never a destination. `--offset N` pages by rows
(`--limit 20 --offset 20` is the second page). The CLI looks a memo ID up in
`--ns` or your configured namespace, so pass `--ns` for another workspace's
memo; the TypeScript facade (`dl.notes(noteId)`) discovers the owner itself.

```bash cli-help="memos search"
dl memos search "release plan"
dl memos search deploy --namespace acme --json
dl memos search deploy --include-archived
```

The default namespace is personal. Add `--namespace acme` for an organization's
memos. `--shared` lists memos shared with you across namespaces; read them using
the owner's namespace. Use IDs, slugs, or exact titles; prefer full IDs in scripts
because titles can repeat. Slug/title lookup includes archived memos and follows
catalog pages.
Search matches titles and indexed bodies by case-insensitive substring.

## Create or follow a memo

```bash cli-help="memos create"
dl memos create "Release plan" --text "Draft checklist"
printf '# Release plan\n' | dl memos create "Release plan" --file - --json
```
The title is optional: `dl memos create --ns your-workspace` creates an
empty memo named `Untitled`; `--file -` reads the initial source from stdin.

New memos are private unless you pass `--public`. Repeated titles get distinct
slugs; keep the returned ID. Use a file or `printf` for multiline text.

```bash cli-help="memos read"
dl memos read release-plan
# Inspect source with generated address hints; do not write the hints back.
dl memos read release-plan --view markdown
# Preserve exact source plus revision/hash for a programmatic edit baseline.
dl memos read release-plan --json > baseline.json
dl memos read release-plan --since "10 minutes ago" --format diff
# Detailed read design (unreleased target syntax):
# https://docs.dreamlake.ai/notes/api/reading/
# Reuse a stable agent identity for this task.
export DREAMLAKE_AGENT_ID=release-reviewer-a
export DREAMLAKE_AGENT_NAME="Release reviewer A"
dl memos read release-plan --linger
# Ctrl-C stops following.
```

Reads require read access; edits require write access. An inaccessible memo may
report as not found. The CLI reads server content and cannot recover an unsynced
browser draft. For older body/section scripts, see [Legacy commands](cli-notes-legacy.md).

## Current commands and the shared design

The [cross-interface API design](https://docs.dreamlake.ai/notes/api/) defines
the proposed CLI, TypeScript, Python and tool contract. Its examples are
explicitly unreleased. The commands on this page retain the current CLI syntax;
for example, creation still takes a name and live following uses `read --linger`.
The [Memos index](cli-notes.md#cross-interface-api-design) compares current behavior
with the target before you adapt an existing script.
