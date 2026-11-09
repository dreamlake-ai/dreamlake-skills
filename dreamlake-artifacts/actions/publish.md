# Publish

```bash
dl artifact push <file> [--title "Title"] [--id <id>] [--kind <kind>] \
    [--namespace <slug>] [--visibility public|private] [--share] \
    [--description "One sentence"] [--cover cover.png]
```

Flag semantics and the kind/extension table:
[Pushing](../reference/cli-artifacts.md#pushing) or `dl artifact push --help`.
After a successful push the CLI prints an **open link** (the dashboard URL,
with `?share=` appended when `--share` was used) — hand it to the user.

For customer-facing latest-only sharing, follow [share](share.md#external-customers-latest-version-only)
and inspect the saved policy after pushing.

## Before the first write

1. Install the standalone CLI (`curl -fsSL https://dl.dreamlake.ai/install.sh | bash`,
   see the `dreamlake-cli` skill) and check `dl --version` and
   `dl artifact --help`. The Python package installs the SDK, not the
   supported CLI.
2. `dl login` (device-auth flow). A push otherwise fails with
   `not authenticated. run 'dl login' first.`
3. A push writes to the user's own namespace by default; `--namespace <slug>`
   targets another namespace the user is a member of.
4. For a single-file artifact, complete the [author](author.md) checklist.
   For a static build, use the workflow below.

## Static builds

```bash
# Only with a compatible CLI and configured static-site hosting:
dl artifact push ./dist/client --site --id my-site
```

For a built application, media-heavy deck or simulation, prefer this workflow
while respecting an explicit request for a self-contained file. Check
`dl artifact push --help` and target hosting availability first; an
installed skill does not enable the feature.
Build/prerender the site, select its client output directory, and preserve the
bundler's chunks and lazy imports. Do not upload the source tree or server build.
Keep the entry page and startup work small. Leave large media, fonts, datasets
and optional modules outside the initial HTML/JavaScript, and mount useful UI
before loading inactive content. Check dynamically constructed asset paths,
not just literal imports. Follow the [loading check](performance.md) when
loading speed is part of the task. After pushing, open the viewer and check
the entry page, a nested route, reload, and an interaction that loads optional
code/data. Reuse the same artifact ID
for the next version. If hosting is unavailable, report that prerequisite;
do not silently replace the requested build with an embedded HTML bundle.

Consult the [CLI guide](../reference/cli-artifacts.md#static-sites-with-on-demand-files)
for versions, options and compatibility, and the
[hosting guide](../reference/docs-artifacts.md#static-build-directories)
for deployment requirements. Existing upload defaults are unchanged.

## Self-contained HTML pages

For the existing self-contained HTML page workflow, read
[Multiple HTML pages](../reference/cli-artifacts.md#multiple-html-pages)
before bundling or pushing. Check the installed command's `--help` and the
target viewer's support, then check the directory against the documented
content and size limits. Apply the [author](author.md) checklist to each page.
For a single-file artifact, keep the file workflow above; a new directory
option alone is not a reason to repackage an existing artifact.

## Versioning is by `--id`

- `--id` is the stable artifact id. Omit it and it is slugified from the
  title. Push again with the **same `--id`** to add a new version; a different
  (or omitted, hence re-slugified) id makes a **separate artifact**.
- **Kind must match the content** (a `.jsx` React component vs. a `.js` code
  snippet). The kind is auto-detected from the extension; override with
  `--kind` when detection is wrong or the extension is unrecognised.
- Pass `--visibility public` only when the user wants it readable without
  login; add `--share` when a share link is wanted in the same step ([share](share.md)).
  Defaults: [Visibility and sharing](../reference/cli-artifacts.md#visibility-and-sharing).

## Incremental uploads

Current CLIs store repeated pushes of the same `--id` incrementally (only new
chunks upload) and both storage formats coexist in one history, so keep the
same `--id` across versions. Reach for `--full` only when an older
self-hosted viewer must read the version. Which CLI versions default to
incremental, the opt-in and opt-out spellings, the size limit and retry
behaviour: [Incremental uploads](../reference/cli-artifacts.md#incremental-uploads).

## Link card (title, description, cover)

Every artifact page carries Open Graph tags, so a pasted URL unfurls as a card.

- `--description`: the sentence the card shows in Slack, Twitter/X, LinkedIn
  or a chat tool. Give every new artifact one; update it when the content
  meaningfully changes.
- `--cover` is optional: without one DreamLake generates a cover from a
  screenshot of the artifact shortly after each push, with the default card
  standing in until then. Pass `--cover` only when the user wants a specific
  image. Accepted formats, size bounds, the recommended shape and the CLI
  version both flags need: [Link previews](../reference/cli-artifacts.md#link-previews).
- A title, description or cover the user set **survives later pushes**: a
  push without the flag keeps the stored value, so do not restate them on
  every re-push. Change or clear them later with
  `dl artifact meta set <id> …` and inspect with
  `dl artifact meta show <id>`. See
  [Link previews](../reference/cli-artifacts.md#link-previews) and
  [Make the link card yours](../reference/docs-artifacts.md#make-the-link-card-yours).
- What the card reveals depends on visibility — see [share](share.md) before
  pasting a share link anywhere.

## Upload transport

The CLI uploads before it registers: it obtains upload credentials, writes the
bytes to the `backendUrl` and `refName` the server returned, then registers the
version. Keep that order in any client you write and never derive a storage key
from the namespace or artifact name. A `409 UPLOAD_RESERVATION_REQUIRED` on the
first registration (an upload that crossed a server upgrade or a whole-Project
transfer) means: obtain fresh credentials, re-upload to the newly returned
target, then register — retrying the registration alone cannot pick a safe
target. Credentials and signed URLs already issued keep their original finite
TTL; a transfer does not revoke them. Source:
[Whole-Project ownership transfer](../reference/cli-artifacts.md#whole-project-ownership-transfer).

## Session affiliation (optional)

A push on CLI 0.78.0+ can be affiliated with the agent session that made it; an
affiliation failure never undoes or misreports the upload, so retry only the
link, never the push. Selection, opt-out and manual link/unlink are the
`session-links` action of `dreamlake-cli`.

## Examples

```bash
# Dashboard (kind auto-detected as html) with its link-card description
dl artifact push ./dashboard.html --title "Q1 Dashboard" \
    --description "Revenue, churn and pipeline for the quarter"

# React component with a stable id, then a new version of the same artifact
dl artifact push ./chart.jsx --kind react --id sales-chart --title "Sales Chart"
dl artifact push ./chart.jsx --id sales-chart

# Public (viewable without login); private with a share link in one step
dl artifact push ./report.html --visibility public --title "Public Report"
dl artifact push ./draft.md --share
```

An owned artifact moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
