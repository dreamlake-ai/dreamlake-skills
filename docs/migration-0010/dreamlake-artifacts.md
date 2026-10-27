# Migration: dreamlake-artifacts

RFC 0010 S3 (content merge B). Sources: `dreamlake-artifacts` (SKILL + 6
references) and `dreamlake-artifact-authoring` (SKILL + 2 references) →
one `dreamlake-artifacts` skill. Whole-Project transfer rules are owned by
`dreamlake-cli/actions/projects.md`; this skill keeps one sentence per
affected action.

`docs[]`: docs.dreamlake.ai/artifacts, docs.dreamlake.ai/workspaces,
cli.dreamlake.ai/artifacts, cli.dreamlake.ai/projects,
cli.dreamlake.ai/sessions (all verified `.md` → 200).
`docs.dreamlake.ai/hosted-pages` was offered but not included: it documents
AI-generated container-hosted pages, a different product; SKILL.md names it
as out of scope.

| Source file / section | Destination | Notes |
| --- | --- | --- |
| `dreamlake-artifacts/SKILL.md` (frontmatter, routing, offline-frame warning, "install both") | `SKILL.md` | Warning kept as one sentence ("…blocked by the frame's CSP and the page renders blank"); authoring and CLI are one skill now, so "install both" became "read author.md before pushing" |
| `dreamlake-artifact-authoring/SKILL.md` | `SKILL.md` routing row for author + routing | |
| `artifact-authoring/references/create-content.md` § rendering environment (CSP, video-player exception, base style, Tailwind, container, theme) | `actions/author.md` § The rendering environment | Verbatim rules |
| `create-content.md` § Pick the right kind | `actions/author.md` § Pick the right kind | |
| `create-content.md` § per-kind guide + templates (react, html, markdown, svg, mermaid, code) | `actions/author.md` § Per-kind rules; templates → `assets/templates/react-app.jsx`, `page.html`, `diagram.mmd`, `diagram.svg` | svg template is new (the source gave only the skeleton rule); markdown/code need no template |
| `create-content.md` § Design quality | `actions/author.md` § Design quality | |
| `create-content.md` § Common pitfalls | `actions/author.md` § Common pitfalls | Added the `location.search`-in-html pitfall from the routing source |
| `create-content.md` § Before you push checklist | `actions/author.md` § Before you push | |
| `artifact-authoring/references/route-aware-artifacts.md` (older copy of the routing contract) | `actions/routing.md` + `assets/templates/route-aware.html` | Superseded by the `dreamlake-artifacts` copy where the two differ (Note deep-link paragraph); live docs match the newer one |
| `dreamlake-artifacts/references/routing-and-rendering.md` § Artifact paths and local routing (URL shapes, handshake, `art.` prefix, `dreamlake.route` API, history semantics, parameter rules, reserved names, limits, previews, deployment caveat) | `actions/routing.md` (rules, traps, deployment caveat) + `reference/docs-artifacts.md#artifact-paths-and-local-routing` (full contract, fetched) + `assets/templates/route-aware.html` (code sample) | The section is verbatim on the live docs page; the action keeps every rule and points to reference for the prose contract |
| `routing-and-rendering.md` § Notes & gotchas (versioning by `--id`, kind must match, `code` renders as source, private does not clear share token) | `actions/publish.md` § Versioning is by `--id`; `actions/author.md` (code kind); `actions/share.md` § Visibility and sharing are independent | |
| `references/publish.md` § Prerequisites | `actions/publish.md` § Before the first write | |
| `publish.md` § Incremental updates (0.38.0–0.39.0 opt-in, 0.39.1 default, `--full` 0.39.2+, `--no-incremental` alias) | `actions/publish.md` § Incremental uploads | All version constraints kept |
| `publish.md` § Push an artifact (command + flag list) | `actions/publish.md` (command; semantics of `--id`, `--kind`, visibility) + `reference/cli-artifacts.md#pushing` | Flag-by-flag list not restated per RFC §6; semantics with traps kept |
| `publish.md` § `--description` / `--cover` (0.85.0+), generated cover timing, 1200×900, persistence across pushes, `meta set/show` | `actions/publish.md` § Link card | |
| `publish.md` § Kind auto-detection table | `reference/cli-artifacts.md#pushing` (fetched) + one-line rule in `actions/publish.md` | dropped as a table: duplicates the CLI docs page |
| `publish.md` § Examples | `actions/publish.md` § Examples | |
| `publish.md` § open link after push | `actions/publish.md` top | |
| `publish.md` § session affiliation (0.78.0) and conversation snapshots (0.79.0) | `actions/publish.md` § Session affiliation + `reference/cli-sessions.md` | |
| `references/list-artifacts.md` | `actions/list.md` | |
| `references/sharing-and-access.md` § Visibility & sharing, revoke (0.32.4+), omit-`--share` preserves token | `actions/share.md` § Visibility and sharing are independent | Added the `share get/create/revoke` + `visibility` recipe from the cited CLI page so the action starts with a command |
| `sharing-and-access.md` § Link cards (Open Graph) | `actions/share.md` § Link cards leak before content does | |
| `sharing-and-access.md` § Browsing in the app | dropped: verbatim copy of `docs.dreamlake.ai/artifacts#browsing-in-the-app` (fetched into `reference/docs-artifacts.md`); `actions/list.md` § In the app points to it and to `reference/docs-workspaces.md` | |
| `sharing-and-access.md` sandbox-frame sentence + "Source … sources.json" provenance note | dropped: sandbox fact is in `actions/author.md`; the `sources.json` note describes the retired sync pipeline | |
| `sharing-and-access.md` § `share --help` / CLI 0.32.4 inspect-create-revoke | `actions/share.md` command block | |
| `sharing-and-access.md` § Project-derived access (0.62.0 / SDK 0.29.0, READ/WRITE/ADMIN, `DELEGATED_UPLOAD_UNSUPPORTED`, attachment authority, `canBind`) | `actions/share.md` § Project-derived access | External links to `dev/notes/project-resource-sharing` and `api/project-queries` kept as absolute URLs (not in `docs[]`) |
| `sharing-and-access.md` § Whole-Project transfer boundary (`PROJECT_STREAM_EXTERNAL_ARTIFACT_UNSUPPORTED`, streaming admission, legacy replay, never copy/delete) | `dreamlake-cli/actions/projects.md` (other agent); here one sentence in `actions/publish.md`, `share.md`, `restore.md` and `SKILL.md` | Per task instruction |
| `references/remove-and-restore.md` (soft delete, three restore paths, #1343 project placements, `--permanent` v0.4.14+ safety rule) | `actions/restore.md` | |
| `references/notes-references.md` § Reference in Notes | `actions/notes-references.md` § Rules | |
| `notes-references.md` § Fragment reference syntax | `actions/notes-references.md` § Fragment references | `docs.dreamlake.ai/notes` anchor kept as absolute URL (page owned by `dreamlake-notes`) |
| `dreamlake-artifacts/reference/` (generated) | none existed in this skill at `6a2a02dc` | CI will fetch `reference/` from `docs[]` |
