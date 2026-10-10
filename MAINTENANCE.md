# Skill ownership and maintenance

This repository distributes skills from several sources. A copy here does not
always mean this is the place to edit it. The inventory below covers every skill;
CI rejects unregistered skills and stale inventory rows.

## Where to make a change

- **Generated:** edit the owning source docs and task guides, commit them, then
  run the source synchronizer. The repository containing those sources owns the
  procedure. `sources.json` records the exact exported revisions and guide hashes.
- **Manual product:** the skill procedure currently lives here, but product facts
  belong to the linked product docs. Change those docs first when behavior
  changes, then review the corresponding skill edits in the same delivery.
  These skills have no automatic source-freshness guarantee. The links identify
  review targets, not a claim that those docs were verified by this inventory.
- **Standalone:** this repository owns the skill, helper, and supporting guide.
  Maintain them together here. External API docs remain authoritative for API
  behavior. `launch-codex-chat` is in this category and is not bundled in the
  DreamLake CLI or implemented in Nymph.

The owning repositories' maintainers review their respective source changes.
This inventory does not assign individual people or GitHub review permissions.

<!-- catalog:start -->
18 skills: 3 generated, 13 manual product, 2 standalone.

| Skill | Maintenance | Edit location | Docs to review | Related skills |
|---|---|---|---|---|
| [dreamlake-annotations](dreamlake-annotations/SKILL.md) | Manual product | [edit](dreamlake-annotations/) | [docs 1](https://docs.dreamlake.ai/annotations) | [video-labeling-workflow](video-labeling-workflow/SKILL.md) |
| [dreamlake-artifact-authoring](dreamlake-artifact-authoring/SKILL.md) | Manual product | [edit](dreamlake-artifact-authoring/) | [docs 1](https://docs.dreamlake.ai/artifacts) | [dreamlake-artifacts](dreamlake-artifacts/SKILL.md) |
| [dreamlake-artifacts](dreamlake-artifacts/SKILL.md) | Manual product | [edit](dreamlake-artifacts/) | [docs 1](https://docs.dreamlake.ai/artifacts), [docs 2](https://cli.dreamlake.ai/artifacts) | [dreamlake-cli](dreamlake-cli/SKILL.md), [dreamlake-artifact-authoring](dreamlake-artifact-authoring/SKILL.md) |
| [dreamlake-cli](dreamlake-cli/SKILL.md) | Generated | [edit](https://github.com/dreamlake-ai/dreamlake-cli/tree/main/docs) | Source docs | [dreamlake-artifacts](dreamlake-artifacts/SKILL.md), [dreamlake-notes](dreamlake-notes/SKILL.md), [dreamlake-scenes](dreamlake-scenes/SKILL.md), [dreamlake-libraries](dreamlake-libraries/SKILL.md), [dreamlake-source](dreamlake-source/SKILL.md), [workflow-publish](workflow-publish/SKILL.md) |
| [dreamlake-dataset-viz](dreamlake-dataset-viz/SKILL.md) | Manual product | [edit](dreamlake-dataset-viz/) | [docs 1](https://viz.dreamlake.ai/dataset-viz/spec.md) | [dreamlake-source](dreamlake-source/SKILL.md), [sim-to-mcap](sim-to-mcap/SKILL.md) |
| [dreamlake-envs](dreamlake-envs/SKILL.md) | Manual product | [edit](dreamlake-envs/) | [docs 1](https://docs.dreamlake.ai/scenes/) | [dreamlake-scenes](dreamlake-scenes/SKILL.md) |
| [dreamlake-libraries](dreamlake-libraries/SKILL.md) | Manual product | [edit](dreamlake-libraries/) | [docs 1](https://docs.dreamlake.ai/libraries/) | [dreamlake-cli](dreamlake-cli/SKILL.md), [dreamlake-scene-generation](dreamlake-scene-generation/SKILL.md) |
| [dreamlake-notes](dreamlake-notes/SKILL.md) | Generated | [edit](https://github.com/dreamlake-ai/dreamlake-workspace/tree/main/docs/skill-guides/notes) | [docs 1](https://cli.dreamlake.ai/notes/) | [dreamlake-cli](dreamlake-cli/SKILL.md) |
| [dreamlake-scene-generation](dreamlake-scene-generation/SKILL.md) | Generated | [edit](https://github.com/dreamlake-ai/dreamlake-workspace/tree/main/docs/skill-guides/scene-generation) | Source docs | [dreamlake-scenes](dreamlake-scenes/SKILL.md), [dreamlake-libraries](dreamlake-libraries/SKILL.md) |
| [dreamlake-scenes](dreamlake-scenes/SKILL.md) | Manual product | [edit](dreamlake-scenes/) | [docs 1](https://docs.dreamlake.ai/scenes/) | [dreamlake-cli](dreamlake-cli/SKILL.md), [dreamlake-scene-generation](dreamlake-scene-generation/SKILL.md) |
| [dreamlake-source](dreamlake-source/SKILL.md) | Manual product | [edit](dreamlake-source/) | [docs 1](https://docs.dreamlake.ai/sources/) | [dreamlake-cli](dreamlake-cli/SKILL.md), [remote-source-check](remote-source-check/SKILL.md), [dreamlake-dataset-viz](dreamlake-dataset-viz/SKILL.md) |
| [launch-claude-remote](launch-claude-remote/SKILL.md) | Standalone | [edit](launch-claude-remote/) | [docs 1](https://code.claude.com/docs/en/remote-control), [docs 2](https://code.claude.com/docs/en/permission-modes) | [launch-codex-chat](launch-codex-chat/SKILL.md) |
| [launch-codex-chat](launch-codex-chat/SKILL.md) | Standalone | [edit](launch-codex-chat/) | [docs 1](https://learn.chatgpt.com/docs/app-server) | None recorded |
| [remote-source-check](remote-source-check/SKILL.md) | Manual product | [edit](remote-source-check/) | [docs 1](https://docs.dreamlake.ai/sources/) | [dreamlake-source](dreamlake-source/SKILL.md), [video-labeling-workflow](video-labeling-workflow/SKILL.md) |
| [sim-to-mcap](sim-to-mcap/SKILL.md) | Manual product | [edit](sim-to-mcap/) | [docs 1](https://viz.dreamlake.ai/dataset-viz/reference.md) | [dreamlake-dataset-viz](dreamlake-dataset-viz/SKILL.md) |
| [video-labeling-workflow](video-labeling-workflow/SKILL.md) | Manual product | [edit](video-labeling-workflow/) | [docs 1](https://docs.dreamlake.ai/workflows/) | [workflow-generator](workflow-generator/SKILL.md), [workflow-publish](workflow-publish/SKILL.md), [remote-source-check](remote-source-check/SKILL.md) |
| [workflow-generator](workflow-generator/SKILL.md) | Manual product | [edit](workflow-generator/) | [docs 1](https://docs.dreamlake.ai/workflows/) | [dreamlake-cli](dreamlake-cli/SKILL.md), [workflow-publish](workflow-publish/SKILL.md), [video-labeling-workflow](video-labeling-workflow/SKILL.md) |
| [workflow-publish](workflow-publish/SKILL.md) | Manual product | [edit](workflow-publish/) | [docs 1](https://docs.dreamlake.ai/workflows/) | [dreamlake-cli](dreamlake-cli/SKILL.md), [workflow-generator](workflow-generator/SKILL.md), [video-labeling-workflow](video-labeling-workflow/SKILL.md) |

Recorded generated-source snapshots (not a freshness assertion):

- `cli`: [577c320fe108](https://github.com/dreamlake-ai/dreamlake-cli/commit/577c320fe108a75c4d54ef933025ed3daad818df)
- `workspace`: [a252e195eef8](https://github.com/dreamlake-ai/dreamlake-workspace/commit/a252e195eef8d2898dfd4a1978dd3923e66b730f)

Upstream freshness: **not checked by this report**.
<!-- catalog:end -->

This table is generated from [catalog.json](catalog.json). Update the metadata
and run `python3 scripts/catalog.py`; do not edit table rows directly. The
recorded source revisions are taken from [sources.json](sources.json), so the
inventory does not maintain a second freshness timestamp.

## Which duplicates are intentional?

| Overlap | Current relationship | Maintenance rule |
|---|---|---|
| CLI docs, bundled `dreamlake-cli`, public `dreamlake-cli` | Generated distribution copies; CLI releases can contain an older snapshot | Edit CLI source once, regenerate, synchronize; do not patch either generated copy |
| CLI Notes references and `dreamlake-notes/reference` | Selected CLI pages are copied with link rewriting by `sync-docs.py` | Preserve generated copies needed for independent installation |
| CLI artifact guide and `dreamlake-artifacts` | Broad CLI guide and separately maintained focused procedures | Review both when publishing or sharing behavior changes; migrate the focused procedure to generated source before treating it as synchronized |
| CLI/workspace scene and library docs, `dreamlake-scenes`, `dreamlake-libraries`, scene generation | Shared product facts; packaging assets and composing scenes are different tasks | Keep task boundaries, compare manual skills against owning docs, and avoid adding another independent API reference |
| Source connection, source checking, and dataset visualization | Related handoffs; visibility checks overlap, visualization is a separate task | Keep the handoffs explicit; maintain one authoritative product contract in source docs |
| Workflow design, fixed video template, workflow publishing, broad CLI guide | Different entrypoints share validation and publishing operations | Route specialized skills to `workflow-publish`; reconcile its procedure with product docs until generated |

The inventory's related-skill column identifies review candidates, not exact
byte duplicates or proven contradictions. It is not an exhaustive semantic
duplication detector. Do not remove generated references just to eliminate
identical bytes: a skill may need them when installed on its own. Likewise,
do not make the CLI bundle depend on a catalog skill it does not ship.

## What each check proves

| Check | Evidence | Does not prove |
|---|---|---|
| `python3 scripts/catalog.py --check` | Every skill has an edit location and mode; generated ownership agrees with the manifest; this table and README discovery are complete | Procedure accuracy, source freshness, or deployed state |
| `python3 scripts/sync-docs.py --verify-files` | Generated bytes and provenance match committed hashes | Agreement with current source docs |
| `sync-docs.py --workspace … --cli … --check --locked` | Outputs reproduce the recorded source commits | Agreement with newer source commits |
| `sync-docs.py --workspace … --cli … --check` | Outputs match the supplied source checkouts' committed HEADs | That those checkouts are current upstream, or that docs/CLI have been released |

Public CI runs the first two checks and offline tests. It has no credentials for
private source repositories and does not continuously synchronize product docs.
Before a generated-skill change is called current, fetch the owning repositories,
select the intended reviewed revisions, and run the current-source check. Include
the revisions and result in the PR. For manual product skills, identify the docs
reviewed and related skills checked. For standalone skills, test the helper and
its failure paths without requiring access to a user's live services.

Source changes should eventually open synchronization PRs from trusted source
repository workflows, using narrowly scoped publishing credentials. That
automation is not configured by this change. Never expose private source tokens
to public pull-request jobs or label an integrity-only job as a freshness check.

## Adding a skill without another independent copy

1. Choose its canonical source. Product procedures belong beside the owning
   docs; standalone utilities can live here. Existing manual product skills are
   migration work, not a template for adding more independent product copies.
2. Check the inventory's related skills. Prefer routing to an existing procedure
   when it is available to the target installation; otherwise generate needed
   reference material from the same source.
3. Add a `catalog.json` entry and a README discovery row. A generated entry must
   be backed by `generated-files.json` and a source key in `sources.json`.
4. Regenerate the inventory and run catalog checks, integrity checks, and tests.
   A standalone skill's scripts and documentation are reviewed in the same PR.
5. Report the source PR, catalog PR, CLI release, live docs, and installed copy
   separately. Publishing a catalog skill does not add it to the CLI bundle.

The [source synchronization instructions](README.md#docs-first-maintenance)
describe the full generated-skill procedure.
