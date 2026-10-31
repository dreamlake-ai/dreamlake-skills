<!-- generated from https://cli.dreamlake.ai/notes.md at 0.97.2 1633dd9; do not edit -->

# Notes

Notes are shared Markdown documents you can read and edit in DreamLake or from
your terminal. Choose a guide for the task at hand.

## Basics

- [Create and find notes](cli-notes-getting-started.md) — login, search, create, and first read.
- [Reading and changes](cli-notes-reading.md) — sections, passage search, and change history.
- [Editing with patches](cli-notes-editing.md) — targeted edits that preserve concurrent work.
- [Live collaboration](cli-notes-collaboration.md) — task identity, presence, and following edits.
- [Saved versions](cli-notes-versions.md) — immutable checkpoints and retained history.
- [Legacy commands](cli-notes-legacy.md) — older ETag-based scripts.

## Rich content

- [Markdown and highlights](cli-notes-rich-content.md) — text color, references, and HTML snapshots.
- [Videos](cli-notes-videos.md) — upload a clip and embed its player.
- [Columns and rows](cli-notes-columns.md) — two-column blocks and repeated pairs.
- [Attachments](cli-notes-attachments.md) — upload, manage, and preview files.
- [Suggested-edit redlines](cli-notes-suggest-diff.md) — propose document changes for review.

## Management

- [Sharing and visibility](cli-notes-sharing.md) — links, access roles, and public/private visibility.
- [Project filing](cli-notes-projects.md) — create and inspect project affiliations.
- [Ownership transfers](cli-notes-transfers.md) — preview and transfer a standalone Note.
- [Archive notes and folders](https://cli.dreamlake.ai/notes/archival) — hide inactive work and restore it on edit.
- [Delete a note](cli-notes-deletion.md) — remove a whole Note.

## Cross-interface API design

The [Notes API design](https://docs.dreamlake.ai/notes/api/) is the detailed
implementation target shared by the CLI, TypeScript, Python and model-facing
tools. Its method-family pages cover [reading](https://docs.dreamlake.ai/notes/api/reading/),
[editing](https://docs.dreamlake.ai/notes/api/editing/),
[collaboration and replay](https://docs.dreamlake.ai/notes/api/collaboration/),
[resource lifecycle](https://docs.dreamlake.ai/notes/api/resources/),
[moving and renaming](https://docs.dreamlake.ai/notes/api/moving/), and
[stdin/stdout/stderr](https://docs.dreamlake.ai/notes/api/cli/).

**The redesigned examples are unreleased contracts, not installed-command
availability.** Use this CLI site's command guides and installed `--help` for
current syntax. Publishing the design does not upgrade clients, deploy server
capabilities, or update the pinned agent skill.

Current commands already support canonical source, mapped reading views,
original-revision patches, and presence/live following. The redesign changes
some defaults and argument shapes; do not substitute them into existing scripts:

| Area | Current CLI | Implementation target |
| --- | --- | --- |
| Read default | Canonical source with metadata | Source-mapped default; explicit exact-source export |
| Mapped inspection | `read --view markdown` or `--view html` | Shared mapped read contract with explicit scope and ranges |
| Line selection | Existing separate start/end flags and compatibility constraints | One `--lines START:END` pair |
| Namespace | `--namespace` in current Notes examples | Consistent `--namespace` / `--ns` source-context aliases |
| Create | Positional name required | Name and initial text optional |
| Watch | `read --linger` with current debounce/throttle behavior | Bounded `watch`, normalized events and durable net content catch-up |
| Append | Existing separator-LF behavior | Verbatim supplied text with no automatic separator |
| Move | Current filing/transfer workflows and flags | One move facade with separate destination fields |

A source revision, content hash, metadata version and watch continuation have
different purposes. Keep original edit baselines and acknowledged receipts;
never replay an uncertain mutation solely because a newer design offers a
cleaner name for it. The family pages identify remaining implementation and
protocol decisions explicitly.
