# Public DreamLake skills

Docs are the first-class, reviewed source of product procedures and examples.
Correct the owning docs before changing a generated skill. Keep skill entrypoints
small: trigger, navigation and provenance; do not independently rewrite APIs.

For Notes/CLI/scene-generation content, read the source mapping and commands
in README.md and run `scripts/sync-docs.py` against committed source checkouts. Commit the
resulting skill files, `sources.json` and `generated-files.json` together.
Run current-source `--check` before calling synchronization complete;
`--locked` proves only reproduction, and `--verify-files` proves only integrity.
Never equate either narrower check with freshness against current docs.

Read `MAINTENANCE.md` and `catalog.json` to find each skill's edit location and
maintenance mode. Register every added skill and regenerate the inventory with
`python3 scripts/catalog.py`; run its `--check` mode before submitting changes.
The inventory must also be regenerated after source synchronization changes
the recorded revisions. It does not certify upstream freshness.

Other product skills are not yet migrated. Update their owning docs first and
review paired changes explicitly; do not describe them as automatically synchronized.
Standalone utilities are authored here: keep their skill, helpers, and supporting
docs together. Do not introduce independently maintained copies in the CLI or
Nymph. A distribution copy should be generated from its declared canonical source.
Preserve dependency bundles, client examples, command prerequisites and revision
checks. Review source exports for private operational material before publication.

Validate changed executable examples in an appropriate test environment, with
explicit setup and readback. No production mutations are implied by a docs change.
Report source sync, PR/merge, published docs, public skills and fresh installation
separately. Do not claim completion from a local build or a merged PR alone.

Detailed procedure: https://docs.dreamlake.ai/dev/skills (publication pending
until the companion workspace docs change is deployed). Existing handoff standard:
https://github.com/dreamlake-ai/dreamlake-workspace/issues/240#charlie-documentation-and-handoff-checklist

Use explicit push refs, such as `git push origin HEAD:refs/heads/<branch>`.
Do not use a bare `git push`: developer machines may have `push.default=matching`,
which can publish unrelated branches. Do not change global Git settings.
