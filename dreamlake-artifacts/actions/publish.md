# Publish

```bash
dreamlake artifact push <file> [--title "Title"] [--id <id>] [--kind <kind>] \
    [--namespace <slug>] [--visibility public|private] [--share] \
    [--description "One sentence"] [--cover cover.png]
```

Flag semantics and the kind/extension table:
[Pushing](reference/cli-artifacts.md#pushing) or `dreamlake artifact push --help`.
After a successful push the CLI prints an **open link** (the dashboard URL,
with `?share=` appended when `--share` was used) — hand it to the user.

## Before the first write

1. Install the standalone CLI (`curl -fsSL https://dl.dreamlake.ai/install.sh | bash`,
   see the `dreamlake-cli` skill) and check `dreamlake --version` and
   `dreamlake artifact --help`. The Python package installs the SDK, not the
   supported CLI.
2. `dreamlake login` (device-auth flow). A push otherwise fails with
   `not authenticated. run 'dreamlake login' first.`
3. A push writes to the user's own namespace by default; `--namespace <slug>`
   targets another namespace the user is a member of.
4. The file passes the [author](author.md) checklist.

## Versioning is by `--id`

- `--id` is the stable artifact id. Omit it and it is slugified from the
  title. Push again with the **same `--id`** to add a new version; a different
  (or omitted, hence re-slugified) id makes a **separate artifact**.
- **Kind must match the content** (a `.jsx` React component vs. a `.js` code
  snippet). The kind is auto-detected from the extension; override with
  `--kind` when detection is wrong or the extension is unrecognised.
- Private by default. `--visibility public` makes it readable without login;
  `--share` mints a share token in the same step ([share](share.md)).

## Incremental uploads

CLI 0.39.1 and later uses incremental storage by default for
`dreamlake artifact push <file> --id <id>`: the first push establishes chunks,
later pushes send only new compressed chunks. CLI 0.38.0 through 0.39.0
requires `--incremental` to opt in. `--full` (CLI 0.39.2+) uploads the entire
file, including for older self-hosted viewers; `--no-incremental` remains a
compatibility alias and is the spelling to use on CLI 0.39.1. Both formats can
coexist in one history — keep the same `--id`. Limits, retry behaviour and
older-viewer compatibility:
[Incremental uploads](reference/cli-artifacts.md#incremental-uploads).

## Link card (title, description, cover)

Every artifact page carries Open Graph tags, so a pasted URL unfurls as a card.

- `--description` (CLI 0.85.0+): the sentence the card shows in Slack,
  Twitter/X, LinkedIn or a chat tool. Give every new artifact one; update it
  when the content meaningfully changes.
- `--cover` (CLI 0.85.0+): PNG, JPEG or WebP, at least 600×315, at most
  2 MiB, 1200×900 (4:3) recommended. Optional — without one DreamLake
  generates a cover: a screenshot of the artifact as the viewer shows it,
  taken within about fifteen minutes of a push (a new version gets a new
  screenshot); the default DreamLake card stands in until then. Pass
  `--cover` only when the user wants a specific image.
- A title, description or cover the user set **survives later pushes**: a
  push without the flag keeps the stored value, so do not restate them on
  every re-push. Change or clear them later with
  `dreamlake artifact meta set <id> …` and inspect with
  `dreamlake artifact meta show <id>`. See
  [Link previews](reference/cli-artifacts.md#link-previews) and
  [Make the link card yours](reference/docs-artifacts.md#make-the-link-card-yours).
- What the card reveals depends on visibility — see [share](share.md) before
  pasting a share link anywhere.

## Session affiliation (optional)

CLI 0.78.0 can affiliate a successful artifact write with its verified saved
agent session, and 0.79.0 adds explicitly selected conversation snapshots.
Opening an artifact does not create a link, a link grants no terminal access,
and an affiliation or archive failure never undoes or misreports a successful
upload — retry only the link/archive. Selection, automatic context, opt-out
and manual link/unlink:
[Link notes and artifacts](reference/cli-sessions.md#link-notes-and-artifacts-0780)
and
[Optional conversation upload](reference/cli-sessions.md#optional-conversation-upload-0790).

## Examples

```bash
# Dashboard (kind auto-detected as html) with its link-card description
dreamlake artifact push ./dashboard.html --title "Q1 Dashboard" \
    --description "Revenue, churn and pipeline for the quarter"

# React component with a stable id, then a new version of the same artifact
dreamlake artifact push ./chart.jsx --kind react --id sales-chart --title "Sales Chart"
dreamlake artifact push ./chart.jsx --id sales-chart

# Public (viewable without login); private with a share link in one step
dreamlake artifact push ./report.html --visibility public --title "Public Report"
dreamlake artifact push ./draft.md --share
```

An owned artifact moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
