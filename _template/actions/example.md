# Publish a report as an artifact and hand back its link

<!-- Author notes (delete this block): one task per page, named after the
  task. Replace the title, "Before you start", "Steps" and "Exceptions"; keep
  commands first and exceptions after. Link flag meaning, defaults and limits
  to ../reference/<site>-<slug>.md#<heading> instead of restating them, and
  name other skills (`the setup action of dreamlake-cli`) instead of linking
  them. Rules: CONTRIBUTING.md, "Writing rules". -->

One task per page. Commands first, exceptions after. Flag details are not
restated here; they are in `reference/` or in `--help`.

## Before you start

- The `dreamlake` CLI is installed and logged in to the right environment
  (`dreamlake-cli` skill, action `setup`).
- The file renders on its own: no CDN scripts, web fonts or remote images. The
  artifact frame is offline; see [reference/docs-artifacts.md](../reference/docs-artifacts.md).

## Steps

1. Push the file. `--title` is the label people see; `--id` is the stable
   identifier that versions accumulate under.

   ```bash
   dreamlake artifact push ./report.html --title "Weekly report" --id weekly-report
   ```

   Pushing again with the same `--id` appends a version; a different `--id`
   starts a new artifact. Kinds, visibility and share flags:
   [reference/cli-artifacts.md](../reference/cli-artifacts.md).

2. Read it back and confirm the new version is listed:

   ```bash
   dreamlake artifact list --json
   ```

3. Give the user the artifact URL printed by the push. Say it rendered only if
   you opened it.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `401` or `403` on push | Wrong environment or token | `dreamlake login`; check `DREAMLAKE_REMOTE` (`dreamlake-cli` skill) |
| The page renders blank | Content loads remote assets | Inline them; the frame is offline ([reference/docs-artifacts.md](../reference/docs-artifacts.md)) |
| "Changing the title made a new artifact" | `--id` defaults to a slug of the title | Pass the old `--id` explicitly |
| Artifact must move with its project | Whole-project transfer rules | [reference/cli-projects.md](../reference/cli-projects.md); the `projects` action of `dreamlake-cli` |
