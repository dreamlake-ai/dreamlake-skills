<!-- generated from https://cli.dreamlake.ai/notes/getting-started.md at 0.92.0 a5d6dff; do not edit -->

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
```

```bash cli-help="notes search"
dreamlake notes search "release plan"
dreamlake notes search deploy --namespace acme --json
```

The default namespace is personal. Add `--namespace acme` for an organization's
notes. `--shared` lists notes shared with you across namespaces; read them using
the owner's namespace. Use IDs, slugs, or exact titles; prefer full IDs in scripts
because titles can repeat and slug/title lookup searches at most 200 notes.
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
dreamlake notes read release-plan --since "10 minutes ago" --format diff
# Reuse a stable agent identity for this task.
export DREAMLAKE_AGENT_ID=release-reviewer-a
export DREAMLAKE_AGENT_NAME="Release reviewer A"
dreamlake notes read release-plan --linger
# Ctrl-C stops following.
```

Reads require read access; edits require write access. An inaccessible note may
report as not found. The CLI reads server content and cannot recover an unsynced
browser draft. For older body/section scripts, see [Legacy commands](cli-notes-legacy.md).
