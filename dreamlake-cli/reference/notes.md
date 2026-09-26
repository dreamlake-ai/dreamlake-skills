# Notes

Read and edit the same document people have open in DreamLake. Start with a
snapshot, make a targeted patch, and read back the result. To work alongside
someone, keep the note open in your terminal with `--linger`.

## Start here

Log in with `dreamlake login`. These guides target **CLI 0.29.0 or later** and a
compatible DreamLake server. Check your binary with `dreamlake --version`;
[installation](/installation/) explains how to update it.

```bash cli-help="notes list"
dreamlake notes list --limit 10
dreamlake notes list --shared --json
dreamlake notes list --namespace acme
```

The default namespace is your personal one. Add `--namespace acme` to each
command for an organization's notes. `--shared` lists notes shared with you
across namespaces; use the owner's namespace to read one.

Use a note's ID, slug, or exact title. Prefer its full ID in scripts: titles may
repeat, and slug/title lookup searches at most 200 notes.

```bash cli-help="notes search"
dreamlake notes search "release plan"
dreamlake notes search deploy --namespace acme --json
```

Search matches titles and indexed bodies by case-insensitive substring. Results
include matching sections. For exact locations across notes, use
[`notes grep`](/notes/reading/#search-passages).

## Read once, or stay with the note

```bash cli-help="notes read"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID"
dreamlake notes read "$NOTE_ID" --json > baseline.json
HASH=$(jq -er .hash baseline.json)
dreamlake notes read "$NOTE_ID" --since "$HASH"
```

Text output includes the note ID, content hash, write revision, and source.
Use `--json` for scripts; `jq -jr .content baseline.json` extracts the exact
source without adding a newline. Keep the snapshot while preparing an edit.

For a shared editing session, set an agent identity **once per task**, then linger:

```bash
SESSION_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
export DREAMLAKE_AGENT_ID="codex:$SESSION_ID"
export DREAMLAKE_AGENT_NAME="Codex"
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --linger
```

This prints the source and other participants immediately, then batches changes
while staying in the foreground. Ctrl-C leaves. Reuse the same identity across
that task's commands, including commands in separate tool shells.

## Create a note

```bash cli-help="notes create"
dreamlake notes create "Release plan" --text "Draft checklist"
printf '# Release plan\n' | dreamlake notes create "Release plan" --file - --json
```

New notes are private unless you pass `--public`. Repeated titles get distinct
slugs; use the returned ID or slug. Shell single quotes do not turn `\n` into
newlines: use `printf`, a file, or a quoted here-document for multiline source.

## Choose your next step

| Task | Guide |
| --- | --- |
| Read a section, inspect changes, or search passages | [Reading and changes](/notes/reading/) |
| Apply an edit while preserving concurrent work | [Editing with patches](/notes/editing/) |
| Join someone and follow their edits | [Live collaboration](/notes/collaboration/) |
| Write highlights, references, or inspect rendered HTML | [Rich content and HTML](/notes/rich-content/) |
| Upload a file or share its preview | [Attachments](/notes/attachments/) |
| Maintain an older script using body/section writes | [Legacy commands](/notes/legacy/) |

Reads require read access; mutations require write access. A read share does not
grant permission to edit. An inaccessible note may report as not found.

For the browser editor, sync recovery, and view-only time travel, see the
[DreamLake Notes guide](https://docs.dreamlake.ai/notes/). The CLI sees server
content; it cannot recover an unsynced draft held in someone else's browser.
