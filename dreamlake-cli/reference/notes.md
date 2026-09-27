# Notes

Read and edit the same document people have open in DreamLake. Start with a
snapshot, make a targeted patch, and read back the result. To work alongside
someone, keep the note open in your terminal with `--linger`.

Use plain-text output by default, including in coding-agent workflows and
command examples. Do not add `--json` just because an agent is calling the CLI.
Reserve it for an explicit machine consumer, such as a script that must parse
revision tokens or structured events. Those integration examples keep their
required JSON handling; ordinary reading, collaboration and selection use text.

## Start here

Log in with `dreamlake login`. These guides target **CLI 0.29.0 or later** and a
compatible DreamLake server. Check your binary with `dreamlake --version`;
[installation](/installation/) explains how to update it.

```bash cli-help="notes"
# Log in first. Replace release-plan with a note ID, slug, or title you can access.
# Discover your notes, shared notes, or notes in a team namespace.
dreamlake notes list --limit 10
dreamlake notes list --shared
dreamlake notes search "release plan" --namespace acme
# Read a note, save a revision-bearing snapshot, or follow live edits (Ctrl-C to stop).
dreamlake notes read release-plan
# Save the exact content, hash, and write revision for later comparison or edits.
dreamlake notes read release-plan --json > baseline.json
# Live presence requires a stable ID for this task session.
DREAMLAKE_AGENT_ID=release-review dreamlake notes read release-plan --linger
# Create a private note from Markdown on stdin.
printf '# Release plan\n\n- [ ] Ship the CLI\n' | dreamlake notes create "Release plan" --file -
# Inspect sections and attachments.
dreamlake notes sections release-plan
dreamlake notes files list --note release-plan
# See complete revision-safe edit recipes before changing an existing note.
dreamlake notes patch --help
dreamlake notes write --help
```

```bash cli-help="notes list"
dreamlake notes list --limit 10
dreamlake notes list --shared
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
# Follow others using a stable identity for this task.
export DREAMLAKE_AGENT_ID="codex:$(python3 -c 'import uuid; print(uuid.uuid4())')"
export DREAMLAKE_AGENT_NAME="Codex"
dreamlake notes read "$NOTE_ID" --linger --throttle 2s
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

## Manage existing share links

Unreleased: check `dreamlake notes share --help` for installed support.

Requires an authenticated login and an existing resource. These commands change
metadata only; they do not upload content or create a new version.

```bash cli-help="notes share"
# Set this to your existing Note id.
RESOURCE="your-note-id"
dreamlake notes share get "$RESOURCE"
dreamlake notes share create "$RESOURCE" --role read
dreamlake notes share revoke "$RESOURCE"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash cli-help="notes visibility"
dreamlake notes visibility "$RESOURCE" public
dreamlake notes visibility "$RESOURCE" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or an eligible Note creator may manage sharing.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and affects future admissions; accepted users retain their
accepted roles. Note IDs resolve their owning namespace automatically.

```bash cli-help="notes share revoke"
dreamlake notes share revoke "$RESOURCE" --revoke-accepted
```

Ordinary revocation clears only the link. `--revoke-accepted` also removes
accepted grants. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash cli-help="notes share access"
# Lists accepted users, their user ids, and roles as JSON.
dreamlake notes share access "$RESOURCE"
```

```bash cli-help="notes share remove"
USER_ID="user-id-from-access-list"
dreamlake notes share remove "$RESOURCE" "$USER_ID"
```

Removing a grant does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.
