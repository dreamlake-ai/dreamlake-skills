# Contributing a skill

Two rules decide where a change goes:

- A **product fact** (a command, flag, API, behaviour) is wrong or missing:
  fix the docs site in its product repository. The skill picks it up on the
  next nightly sync. Do not patch the fact into an action page.
- A **task step**, exception or troubleshooting note is wrong or missing:
  change `<skill>/actions/` here and open a PR.

## Anatomy of a skill

Every skill has exactly this shape; `_template/` is a complete example.

```
<name>/
  skill.json          metadata: name, description, requires, docs, tools (hand-written)
  SKILL.md            when to use the skill and which action to open; at most 80 lines (hand-written)
  actions/*.md        one task per page, commands first, exceptions after (hand-written)
  tools/              optional scripts; must ship tests as tools/test_*.py (hand-written)
  assets/             optional schemas, templates, examples, contracts (hand-written)
  agents/             optional, Codex UI metadata (`openai.yaml`); nothing else goes here
  reference/*.md      docs pages fetched by CI from skill.json docs[]; never edited by hand
```

`skill.json`:

```json
{
  "name": "dreamlake-artifacts",
  "description": "Author, publish, version, share and restore DreamLake artifacts.",
  "requires": ["dreamlake-cli"],
  "docs": [
    "https://docs.dreamlake.ai/artifacts",
    "https://cli.dreamlake.ai/artifacts",
    "https://cli.dreamlake.ai/projects"
  ],
  "tools": null
}
```

- `name` equals the directory name and matches `^[a-z][a-z0-9-]*$`.
- `description` is one sentence: the user goal the skill owns.
- `requires` lists every skill this one hands off to. The installer installs
  them together; CI checks that each exists and that there is no cycle.
- `docs` lists page URLs on `docs.dreamlake.ai`, `cli.dreamlake.ai` or
  `viz.dreamlake.ai`, without `.md` and without a trailing slash (only a site
  root ends in `/`). Each becomes `reference/<site>-<slug>.md`, for example
  `https://docs.dreamlake.ai/scenes/layers` becomes `reference/docs-scenes-layers.md`.
- `tools` is `null`, or `{"python": ">=3.12", "packages": ["mujoco"]}` when
  `tools/` needs a runtime.

The full schema is [`skill.schema.json`](skill.schema.json).

## The three metadata files

| File | Scope | Written by | Holds | Why it exists |
|---|---|---|---|---|
| `<name>/skill.json` | one per skill | you | name, description, `requires`, `docs` URLs, `tools` | the skill's identity; the input to everything else |
| `renamed.json` | one per repository | you | old name -> new name | one line when a skill is merged or renamed; the CLI points users at the new name |
| `catalog.json` | one per repository | `scripts/catalog.py` from every `skill.json`, `renamed.json` and the release tag | every skill's description, `requires`, `tools` and file count; the `renamed` map; the version | the one small file the CLI downloads for `skill list` and dependency resolution |
| `references.lock` | one per repository | `scripts/sync_references.py` | per fetched page: source URL, docs-site version, sha256 of the fetched bytes and of the written file | lets CI prove offline that `reference/` was not edited by hand, and shows which docs version a fact came from |

`catalog.json` is derived from `skill.json`; `check.py` fails when they
disagree. `references.lock` is kept apart from `skill.json` so that "what the
author asked for" and "what the machine fetched" can be told apart when a
check fails.

## Writing rules

- `SKILL.md` does two things: says when to use the skill, and routes the
  request to one action. Its frontmatter `description` states the task
  boundary; it is not a keyword list. It ends with a `## Canonical source`
  section naming the docs sites. Validate the description with both agents on
  three kinds of request: a representative task, an SDK request, and a
  capability the skill does not have.
- One action, one page. Commands first, exceptions after. For flag detail,
  point at a page in `reference/` or at `--help`; do not restate it.
- A wrong fact is fixed on the docs site, never patched in an action.
- Declare `requires`. Refer to other skills by name, never by path.
- `reference/` is generated. Change `docs[]` only when a new skill needs pages
  or the docs site gained a page the skill should carry; day-to-day docs
  changes need nothing here.
- Links inside a skill are relative to the file they are in and must resolve.
- Before release, install the skill into an isolated directory and read it
  back word for word.

## How reference pages are fetched

`scripts/sync_references.py` fetches `<url>.md` for every `docs[]` entry
(`index.md` for a site root). Outside fenced code blocks, it rewrites links
the docs sites emit as `/path.md`, `/path/`, `/path` or
`https://<same site>/path`: a route that is in the same skill's `docs[]` on
the same site becomes the sibling file name (anchor kept); any other route
becomes the absolute page URL. Pure `#anchor` links and links to other hosts
are untouched. The first line of every file records the source and the docs
version:

```
<!-- generated from https://cli.dreamlake.ai/artifacts.md at <version>; do not edit -->
```

## Commands

```bash
python3 scripts/check.py --offline                 # everything CI checks on a PR
python3 scripts/check.py                           # plus: every docs[] page answers 200 as Markdown
python3 -m unittest discover -s scripts -p 'test_*.py'

python3 scripts/sync_references.py                 # refresh reference/ and references.lock
python3 scripts/sync_references.py --skill <name>  # one skill only
python3 scripts/sync_references.py --check         # report drift against the live sites, write nothing
python3 scripts/sync_references.py --offline-verify

python3 scripts/catalog.py                         # regenerate catalog.json after editing any skill.json
python3 scripts/catalog.py --check
python3 scripts/package.py                         # dist/skills.tar.gz and dist/catalog.json, as the release does
```

## Adding a skill

1. Copy `_template/` to `<name>/`; set `name` in `skill.json` and in the
   `SKILL.md` frontmatter; fill `description`, `requires` and `docs`.
2. Write `SKILL.md` and the action pages. Delete the example action.
3. Run `python3 scripts/sync_references.py --skill <name>` to fetch
   `reference/`, then `python3 scripts/catalog.py`.
4. Run `python3 scripts/check.py` and the unit tests; open a PR with the
   generated `reference/`, `references.lock` and `catalog.json` included.

Merging or renaming a skill: add one line to `renamed.json`, delete the old
directory, regenerate `catalog.json`.

## Releases

Pull requests run `check.py --offline` and the unit tests. Nightly, CI fetches
every `reference/`, validates, commits any change to `main`, and when `main`
differs from the last tag it tags `vYYYY.MM.DD` (`.N` when that date is
taken), builds `skills.tar.gz` and `catalog.json`, and publishes a GitHub
release. The `dreamlake` CLI installs from that release; its own repository
pins a tag in `skills.lock`.

Push with an explicit ref, `git push origin HEAD:refs/heads/<branch>`, never a
bare `git push`.
