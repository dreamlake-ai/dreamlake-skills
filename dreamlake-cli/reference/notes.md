# Notes

Read and edit the same document people have open in DreamLake. Start with a
snapshot, make a targeted patch, and read back the result. To work alongside
someone, keep the note open in your terminal with `--linger`.

**Read Notes directly with `dreamlake notes read <note>`.** Do not add
`--json` or `--view` for ordinary human or agent reads. Inspect the normal
output directly and retain its revision/hash when preparing edits. JSON is
for an explicitly requested structured integration, not agent convenience.

## Start here

Log in with `dreamlake login`. These guides target **CLI 0.29.0 or later** and a
compatible DreamLake server. Check your binary with `dreamlake --version`;
[installation](installation.md) explains how to update it.

```bash cli-help="notes"
# Find a note, then read it directly (use the ID or slug from search).
dreamlake notes search "release plan"
dreamlake notes read release-plan

# Change one phrase: preview, apply, then read back. Exactly one match is required.
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan
dreamlake notes read release-plan

# Create a private note from a Markdown draft you have written.
dreamlake notes create "Release plan" --file release-plan.md

# Collaborate on the same note; every agent uses its own stable task ID and name.
export DREAMLAKE_AGENT_ID=release-reviewer-a
export DREAMLAKE_AGENT_NAME="Release reviewer A"
dreamlake notes select --text "Ready for review" --note release-plan
dreamlake notes read release-plan --linger
# Ctrl-C stops following. A second agent uses a different identity on the same note.
# For edits prepared from an earlier read, use an original-baseline merge patch:
dreamlake notes patch --help
```

```bash cli-help="notes"
# Find a note, then read it directly (use the ID or slug from search).
dreamlake notes search "release plan"
dreamlake notes read release-plan

# Change one phrase: preview, apply, then read back. Exactly one match is required.
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan
dreamlake notes read release-plan

# Create a private note from a Markdown draft you have written.
dreamlake notes create "Release plan" --file release-plan.md

# Collaborate on the same note; every agent uses its own stable task ID and name.
export DREAMLAKE_AGENT_ID=release-reviewer-a
export DREAMLAKE_AGENT_NAME="Release reviewer A"
dreamlake notes select --text "Ready for review" --note release-plan
dreamlake notes read release-plan --linger
# Ctrl-C stops following. A second agent uses a different identity on the same note.
# For edits prepared from an earlier read, use an original-baseline merge patch:
dreamlake notes patch --help
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
[`notes grep`](notes-reading.md#search-passages).

## Make a small wording change

```bash cli-help="notes replace"
# Read first. Replace exactly one phrase; review the dry run before applying.
dreamlake notes read release-plan
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan
dreamlake notes read release-plan
```

Zero or multiple matches fail without changing the note. This helper guards its
own read/write window. An edit prepared from an older snapshot should use
`notes patch` with that snapshot's original `--base-revision`; a dry run does
not reserve the note or pin a later replacement to that preview.

## Make a small wording change

```bash cli-help="notes replace"
# Read first. Replace exactly one phrase; review the dry run before applying.
dreamlake notes read release-plan
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan --dry-run
dreamlake notes replace "Draft checklist" --text "Ready for review" --note release-plan
dreamlake notes read release-plan
```

Zero or multiple matches fail without changing the note. This helper guards its
own read/write window. An edit prepared from an older snapshot should use
`notes patch` with that snapshot's original `--base-revision`; a dry run does
not reserve the note or pin a later replacement to that preview.

## Read once, or stay with the note

```bash cli-help="notes read"
# Read the note directly; no output-format flag is needed.
dreamlake notes read release-plan
# Inspect only changes since a prior time.
dreamlake notes read release-plan --since "10 minutes ago" --format diff
# Discover section anchors, then read just the relevant section.
dreamlake notes sections release-plan
dreamlake notes read release-plan --legacy --section checklist
# Live collaboration requires a stable identity for this task.
DREAMLAKE_AGENT_ID=release-reviewer-a dreamlake notes read release-plan --linger
```

Text output includes the note ID, content hash, write revision, and source.
Keep that output while preparing an edit. The structured integration examples
in the editing guide are optional compatibility recipes, not normal reads.

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
| Read a section, inspect changes, or search passages | [Reading and changes](notes-reading.md) |
| Apply an edit while preserving concurrent work | [Editing with patches](notes-editing.md) |
| Join someone and follow their edits | [Live collaboration](notes-collaboration.md) |
| Write highlights, references, or inspect rendered HTML | [Rich content and HTML](notes-rich-content.md) |
| Upload a file or share its preview | [Attachments](notes-attachments.md) |
| Maintain an older script using body/section writes | [Legacy commands](notes-legacy.md) |

Reads require read access; mutations require write access. A read share does not
grant permission to edit. An inaccessible note may report as not found.

For the browser editor, sync recovery, and view-only time travel, see the
[DreamLake Notes guide](https://docs.dreamlake.ai/notes/). The CLI sees server
content; it cannot recover an unsynced draft held in someone else's browser.

## Manage existing share links

Available in CLI 0.32.4 and later; check `dreamlake notes share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash cli-help="notes share"
# Find the release plan and inspect its source and current sharing.
dreamlake notes search "release plan"
NOTE="release-plan" # Replace with the id or slug from search.
dreamlake notes read "$NOTE"
dreamlake notes share get "$NOTE"

# Give signed-in recipients read access, then verify the returned link.
dreamlake notes share create "$NOTE" --role read
dreamlake notes share get "$NOTE"

# When link access is no longer needed, revoke it and verify.
dreamlake notes share revoke "$NOTE"
dreamlake notes share get "$NOTE"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash cli-help="notes visibility"
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes visibility "$NOTE" public
dreamlake notes visibility "$NOTE" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or an eligible Note creator may manage sharing.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and changes the role evaluated on subsequent requests for
everyone admitted through the link. Note IDs resolve their owning namespace automatically.

```bash cli-help="notes share revoke"
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes share revoke "$NOTE" --revoke-accepted
```

Ordinary revocation clears the link and blocks subsequent link-derived access,
including for prior recipients. Their acceptance records remain: enabling
sharing again restores access under the current link role. `--revoke-accepted`
also deletes those records, so recipients must accept a valid link again. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash cli-help="notes share access"
NOTE="release-plan" # Your existing note id or slug.
# List acceptance records and stored roles as a readable table.
dreamlake notes share access "$NOTE"
```

```bash cli-help="notes share remove"
NOTE="release-plan" # Your existing note id or slug.
USER_ID="user-id-from-access-list"
dreamlake notes share remove "$NOTE" "$USER_ID"
```

The access list defaults to a readable table; use `--json` for a structured
integration. It returns stored roles, which may lag behind the live link role.
Use `share get` to inspect the current link role.

Removing an acceptance record does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.
