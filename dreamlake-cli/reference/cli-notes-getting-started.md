<!-- generated from https://cli.dreamlake.ai/notes/getting-started.md at 0.97.1 086d6d7; do not edit -->

# Create and find notes

## Quick start

Log in with `dreamlake login`. Core examples require **CLI 0.29.0+** and a
compatible server; individual guides state newer feature requirements.
Check your installed version with `dreamlake --version`.

Before an agent's first live read or edit, [set its task identity](cli-notes-collaboration.md#one-identity-per-task).
Set both `DREAMLAKE_AGENT_ID` and `DREAMLAKE_AGENT_NAME` and reuse them for the task.

```bash cli-help="notes"
# Find a note and read it directly.
dreamlake notes search "release plan"
dreamlake notes read release-plan

# Preview a unique wording change, apply it, then read back.
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan
dreamlake notes read release-plan

# Create a private note from a Markdown file.
dreamlake notes create "Release plan" --file release-plan.md

# Cross-interface design (unreleased target APIs; verify installed --help):
# https://docs.dreamlake.ai/notes/api/
```

Read normal output directly; no `--json` or `--view` is needed. Retain the read's
revision and hash for an edit. The replacement helper requires exactly one match
and guards its own read/write window. A dry run does not reserve the note.
For an edit prepared from an older snapshot, use a [patch with the original
baseline revision](cli-notes-editing.md).

```bash cli-help="notes list"
dreamlake notes list --limit 10
dreamlake notes list --shared
dreamlake notes list --namespace acme
dreamlake notes list --include-archived
```

```bash cli-help="notes search"
dreamlake notes search "release plan"
dreamlake notes search deploy --namespace acme --json
dreamlake notes search deploy --include-archived
```

The default namespace is personal. Add `--namespace acme` for an organization's
notes. `--shared` lists notes shared with you across namespaces; read them using
the owner's namespace. Use IDs, slugs, or exact titles; prefer full IDs in scripts
because titles can repeat. Slug/title lookup includes archived notes and follows
catalog pages.
Search matches titles and indexed bodies by case-insensitive substring.

## Create or follow a note

```bash cli-help="notes create"
dreamlake notes create "Release plan" --text "Draft checklist"
printf '# Release plan\n' | dreamlake notes create "Release plan" --file - --json
```

New notes are private unless you pass `--public`. Repeated titles get distinct
slugs; keep the returned ID. Use a file or `printf` for multiline text.

```bash cli-help="notes read"
dreamlake notes read release-plan
# Inspect source with generated address hints; do not write the hints back.
dreamlake notes read release-plan --view markdown
# Preserve exact source plus revision/hash for a programmatic edit baseline.
dreamlake notes read release-plan --json > baseline.json
dreamlake notes read release-plan --since "10 minutes ago" --format diff
# Detailed read design (unreleased target syntax):
# https://docs.dreamlake.ai/notes/api/reading/
# Reuse a stable agent identity for this task.
export DREAMLAKE_AGENT_ID=release-reviewer-a
export DREAMLAKE_AGENT_NAME="Release reviewer A"
dreamlake notes read release-plan --linger
# Ctrl-C stops following.
```

Reads require read access; edits require write access. An inaccessible note may
report as not found. The CLI reads server content and cannot recover an unsynced
browser draft. For older body/section scripts, see [Legacy commands](cli-notes-legacy.md).

## Current commands and the shared design

The [cross-interface API design](https://docs.dreamlake.ai/notes/api/) defines
the proposed CLI, TypeScript, Python and tool contract. Its examples are
explicitly unreleased. The commands on this page retain the current CLI syntax;
for example, creation still takes a name and live following uses `read --linger`.
The [Notes index](cli-notes.md#cross-interface-api-design) compares current behavior
with the target before you adapt an existing script.
