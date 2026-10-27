# Public DreamLake skills

The docs sites (docs.dreamlake.ai, cli.dreamlake.ai, viz.dreamlake.ai) are the
source of product facts: commands, flags, APIs, behaviour. This repository is
the source of task procedures: when to use a skill and the steps, exceptions
and checks of each action. Keep the two apart. A wrong fact is fixed on the
docs site in its product repository; a wrong step is fixed here in
`<skill>/actions/`. Do not restate facts from memory in an action, and do not
patch a product fact into a skill.

Every skill has one shape: `skill.json`, `SKILL.md`, `actions/`, optional
`tools/` and `assets/`, and a generated `reference/`. `reference/` holds the
docs pages listed in `skill.json` `docs[]`, fetched by CI with
`scripts/sync_references.py` and recorded in `references.lock`. Never edit
`reference/` by hand; CI overwrites it and `check.py` rejects edits. To give a
skill another docs page, add its URL to `docs[]` and run the sync.

Validation is `python3 scripts/check.py` (use `--offline` to skip the live
URL check) plus `python3 -m unittest discover -s scripts -p 'test_*.py'`.
Regenerate `catalog.json` with `python3 scripts/catalog.py` after changing any
`skill.json` or `renamed.json`. [CONTRIBUTING.md](CONTRIBUTING.md) is the
single procedure: the lifecycle, the layout, the writing rules, how to maintain,
create, split, rename or retire a skill, the size caps (defined once under
"Maintain an existing skill"), the acceptance a PR needs and the release flow.
Do not maintain a second policy here or in any skill.

Releases are date tags cut by the nightly workflow; the `dreamlake` CLI
installs from the release assets `skills.tar.gz` and `catalog.json`. A merged
PR is not a release, and a release is not an installation: when reporting,
state the merge, the tag and a fresh install read-back separately.

Review every page for private operational material before it is published:
this repository and its releases are public.

Use explicit push refs, such as `git push origin HEAD:refs/heads/<branch>`.
Do not use a bare `git push`: developer machines may have
`push.default=matching`, which can publish unrelated branches. Do not change
global Git settings.
