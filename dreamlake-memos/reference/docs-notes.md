<!-- generated from https://docs.dreamlake.ai/notes.md at 0.1.148 240f5360; do not edit -->

# Memos

Memos were previously called Notes. Existing `/notes` URLs, API fields, saved references, and document IDs remain compatible.

Read [Markdown authoring](docs-notes-markdown.md), [Embeds and query arguments](docs-notes-embeds.md),
[Panels](docs-notes-panels.md), and [Linked memo items](docs-notes-linked-items.md) for focused guides.
The [Memos API design](https://docs.dreamlake.ai/notes/api) specifies the unreleased shared-interface
target with tabbed CLI, TypeScript, Python and model-tool examples. Its proposed
methods and guarantees are not a claim of installed-client or server support.
The detailed guides and CLI/API reference are on the pages below.
[Whole Project and owned resources transfer](docs-notes-sharing.md#whole-project-and-owned-resources-transfer)
includes Artifact/Env with CLI 0.64.0+ or SDK 0.31.0+ and the matching backend;
CLI 0.63.0 / SDK 0.30.0 support the Memo-only manifest. Standalone Memo transfer
across namespaces remains unsupported. Dated release notes below describe their
original verification scope.

**Release status — October 9, 2026:** the serving API includes the verified
saved-version catalog readers, attachment compatibility readers, transactional
attachment sharing, atomic attachment move/trash, and enabled immutable attachment
uploads. The verified API release now also includes atomic attachment copy and
named-version catalog publication by default. Durable attachment purge remains
disabled. Strict runtime verification and read-only metadata/header checks do not
establish production attachment-copy, saved-version-write or user acceptance.
That October 9 verification did not enable a transfer adapter or establish
continuous Memo-read availability.

**Attachment journal release — October 10, 2026:** the known-byte text/copy
publication journal and admitted-only cancellation are enabled in the strictly
verified API release `5d64f024`. Its running image and digest were verified;
selected status checks returned anonymous 401 and authorized 404 with `no-store`.
Those two read-only checks performed no attachment write, body read, RTC call or
provider-failure recovery. CLI 0.48.2 public npm/native distribution and isolated
Linux installations are verified; the other seven OS targets were byte-verified,
not runtime-tested. Raw upload journaling, durable
purge and transfer adapters were disabled in that release. Current whole-Project
transfer support is documented separately below.

  A memo is a collaborative Markdown document. This is how a script — or a
  coding agent working through bash — edits one while people have it open.

See [Panels and agent control](docs-notes-panels.md) for artifact previews, pinned tabs,
and programmable native layouts. The session-library button in the chat tab
row opens an available terminal beside the memo, keeping the editor in place.
Session permissions remain separate from memo permissions.

In live preview, an opening H1 with content below it is positioned
above the viewport once, before interaction. Scrolling back to the title keeps it
visible; typing, blur, and idle time do not automatically hide it again. Raw
Markdown, title-only memos, and explicit search or section navigation retain
their existing behavior. Formatting remains enabled while editing. Vim visual
selections remain visible in both rich and raw views. Each connected browser session shares its cursor and selection, including other sessions of the same account. Clearing a selection updates it immediately; leaving editor focus removes its shared cursor and selection. Hidden tabs leave visible presence. Visible sessions renew presence every 30 seconds; peers expire after 90 seconds without renewal. Cursor labels size to their names, capped at 20 characters of display width with ellipsis. Remote text updates preserve the
visible text position in the memo pane; a new scroll gesture, keystroke, or
selection takes precedence over a pending viewport correction.

Use a collaborator avatar to navigate to its current cursor when the location is
available. A cursor at the beginning of the memo shows a popup saying
**Cursor is at the start of the memo** and leaves your view in place. An avatar
without a current cursor shows a popup saying **No location available**. Other
available cursor locations support the existing jump action.

History timeline previews return to the current working draft when the pointer
leaves the timeline. An explicitly placed edit marker or selected change range
keeps its historical view open; clicking a version label alone does not pin it.

## In this section

- [Writing and formatting](docs-notes-writing.md): the editor, placeholders, color, highlights and references.
- [Markdown authoring](docs-notes-markdown.md) and [Embeds and query arguments](docs-notes-embeds.md).
- [Images, rows and video](docs-notes-rows.md): `:::row` blocks, the image viewer and video.
- [Linked memo items](docs-notes-linked-items.md).
- [Browse, create and organize](docs-notes-browsing.md): the catalog, archive, projects and Bindrs, create, duplicate, summaries and links.
- [Collaboration and review](docs-notes-collaboration.md): sync, suggested edits and comments.
- [History and saved versions](docs-notes-history.md).
- [Sharing, access and transfer](docs-notes-sharing.md).
- [Files and attachments](docs-notes-files.md).
- [Session and resource activity](docs-notes-activity.md).

The **Memos API** section covers programmatic access: the [Memos API design](https://docs.dreamlake.ai/notes/api),
[reading, editing and search from the CLI](docs-notes-cli-editing.md),
[Memos v2 merge and exact patches](docs-notes-v2.md), [agent presence](docs-notes-agent-presence.md)
and [HTML reads](docs-notes-html-reads.md).

## Install

**CLI**

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dl login
```

**Python**

```bash
pip install dreamlake
dl login
```

Both read the same saved login. `pip install dreamlake` installs the Python
SDK; install the standalone CLI using the CLI tab before running
`dl login`. The Python package is not the supported CLI installer.

## For coding agents

```bash
dl init                          # once: pick your agent and scope
dl skill install dreamlake-memos
```

`dl skill update` then updates it. `dl init` chooses between
your user directory and one project, and the `dreamlake-cli` skill that the
Memos skill requires is installed with it. Without the CLI, download
`skills.tar.gz` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
and copy `dreamlake-memos/` and `dreamlake-cli/` into your agent's skills
directory.

The skill's reference pages are fetched from this guide's published
Markdown; its procedures are written in the
[dreamlake-skills](https://github.com/dreamlake-ai/dreamlake-skills) repository.
Correct a fact here first and a step there; see [Skills](https://docs.dreamlake.ai/dev/skills).
