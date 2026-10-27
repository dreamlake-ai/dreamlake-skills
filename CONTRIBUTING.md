# Contributing

This file is the one procedure for this repository: how a skill is shaped,
maintained, created, accepted and released. README.md, AGENTS.md and the
templates point here and restate nothing.

## Lifecycle

```
edit <name>/ ──▶ python3 scripts/check.py ──▶ PR (check.yml: check.py --offline + unit tests)
   ──▶ merge to main ──▶ nightly (nightly.yml): sync_references.py ──▶ commit ──▶ tag vYYYY.MM.DD
   ──▶ release: skills.tar.gz + catalog.json ──▶ users: dreamlake skill update
   ──▶ dreamlake-cli repository bumps skills.lock to the tag (its embedded dreamlake-cli skill)

product fact changed ──▶ edit the product repository's docs/pages ──▶ docs site deploys
   ──▶ next nightly refreshes reference/ (no skill edit)
```

Two rules decide where a change goes:

- A **product fact** (a command, flag, API, behaviour) is wrong or missing:
  fix the docs site in its product repository. The skill picks it up on the
  next nightly sync. Never patch the fact into an action page.
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
- `description` is one sentence of at most 300 characters stating the task
  boundary: what the skill owns and, when it helps routing, what it does not.
- `requires` lists every skill this one hands off to. The installer installs
  them together; CI checks that each exists and that there is no cycle.
- `docs` lists page URLs on `docs.dreamlake.ai`, `cli.dreamlake.ai` or
  `viz.dreamlake.ai`, without `.md` and without a trailing slash (only a site
  root ends in `/`). Each becomes `reference/<site>-<slug>.md`, for example
  `https://docs.dreamlake.ai/scenes/layers` becomes `reference/docs-scenes-layers.md`.
- `tools` is `null`, or `{"python": ">=3.12", "packages": ["mujoco"]}` when
  `tools/` needs a runtime.

The full schema is [`skill.schema.json`](skill.schema.json).

## The metadata files

| File | Scope | Written by | Holds | Why it exists |
|---|---|---|---|---|
| `<name>/skill.json` | one per skill | you | name, description, `requires`, `docs` URLs, `tools` | the skill's identity; the input to everything else |
| `renamed.json` | one per repository | you | old name -> new name | one line when a skill is merged or renamed; the CLI points users at the new name |
| `catalog.json` | one per repository | `scripts/catalog.py` from every `skill.json`, `renamed.json` and the release tag | every skill's description, `requires`, `tools` and file count; the `renamed` map; the version | the one small file the CLI downloads for `skill list` and dependency resolution |
| `dist/catalog.json` (release asset only) | one per release | `scripts/package.py` | the committed `catalog.json` plus `assets.skills.tar.gz` = `{sha256, bytes}` of the tarball | lets the installer verify the download; the committed file never carries `assets` |
| `references.lock` | one per repository | `scripts/sync_references.py` | per fetched page: source URL, docs-site version, sha256 of the fetched bytes and of the written file | lets CI prove offline that `reference/` was not edited by hand, and shows which docs version a fact came from |

`catalog.json` is derived from `skill.json`; `check.py` fails when they
disagree. `references.lock` is kept apart from `skill.json` so that "what the
author asked for" and "what the machine fetched" can be told apart when a
check fails.

## Writing rules

- `SKILL.md` does two things: says when to use the skill, and routes the
  request to one action. Its frontmatter `description` states the task
  boundary; it is not a keyword list. It ends with a `## Canonical source`
  section naming the docs sites.
- One action, one page. Commands first, exceptions after. Keep the *why* and
  *when*; for what a flag means, its defaults, limits, formats or package
  dependencies, link the exact section: `../reference/<site>-<slug>.md#<heading>`
  (a real heading of the fetched page, not a `#` comment inside a code block)
  or say `--help`. Do not restate it: the nightly fetch cannot fix a hand-written copy.
- A wrong fact is fixed on the docs site, never patched in an action.
- Declare `requires`. Refer to other skills by name (`the publish action of
  dreamlake-workflows`), never by path.
- `reference/` is generated. Change `docs[]` only when a new skill needs pages
  or the docs site gained a page the skill should carry; day-to-day docs
  changes need nothing here.
- Links inside a skill are standard Markdown: relative to the file that holds
  them, never to the skill root, and `check.py` fails any that do not resolve.
  From `SKILL.md` write `actions/publish.md` and `reference/cli-artifacts.md`;
  from `actions/*.md` write `../reference/cli-artifacts.md`, `../assets/x.json`
  and `share.md` for a sibling action; from `assets/<dir>/*.md` add one more
  `../`. A link must stay inside its skill.
- Stay under the size caps in [Maintain an existing skill](#maintain-an-existing-skill);
  past them, split by user goal rather than trimming steps.

## Maintain an existing skill

| You want to | Do |
|---|---|
| Change a step, an exception or a troubleshooting note | Edit `<name>/actions/<action>.md`; keep the page one task. Run `python3 scripts/check.py --offline`. |
| Fix a wrong product fact | Open the docs page it came from (first line of the `reference/` file names the URL) and fix it in that product repository's `docs/pages`. The next nightly refreshes `reference/`. Never patch the action. |
| Add or drop a reference page | Edit `docs[]` in `<name>/skill.json` (page URL without `.md`; `curl -fsI <url>.md` must be 200), then `python3 scripts/sync_references.py --skill <name>`; commit `reference/` and `references.lock` with the change. |
| Add a tool | Script in `tools/` plus `tools/test_<tool>.py`; tests must skip cleanly when a package is absent (`pytest.importorskip("mujoco")`); declare the runtime in `skill.json.tools`. `check.py` runs the tests under pytest. |
| Add an asset | Schema, template, example or contract in `assets/`; link it from the action as `../assets/<file>`. |
| Rename or retire a skill | `git mv <old> <new>` (or delete the directory); add `"<old>": "<new>"` to `renamed.json`; update `requires` in every dependent `skill.json`; replace mentions by name; write `docs/migration-<topic>/<old>.md` (source section -> destination); `python3 scripts/catalog.py`. |
| Split a skill that grew past the caps | New directory with its own `skill.json` (`requires` the parent when it hands off to it); `git mv` the actions; turn cross-skill links into names; split `docs[]` by what each action links and re-sync both skills; migration note as above; README table row. |

### Size caps

These are defined here and referenced everywhere else:

- about 50 KB of hand-written text per skill (SKILL.md + actions + text assets; `tools/` and `reference/` do not count);
- about 12 actions;
- `SKILL.md` at most 80 lines (`check.py` enforces this one).

Past a cap, split by user goal; do not trim steps to fit. The split of
`dreamlake-lakeshore` out of `dreamlake-cli` in `docs/migration-0010/` is the
worked example.

## Create a new skill

1. `cp -R _template <name>`; delete the comment blocks the template carries.
2. `skill.json`: `name` equal to the directory; `description` of at most 300
   characters written as task boundaries; `requires`; `docs[]`; `tools`.
3. Verify every `docs[]` URL serves Markdown: `curl -fsI <url>.md` returns 200
   (`index.md` for a site root). Pages are listed at `<site>/llms.txt`.
4. `SKILL.md` (at most 80 lines): the trigger (when to use, when not), a routing
   table from request to one action, and the `## Canonical source` section.
5. One action per task in `actions/`: commands first, exceptions after, flag
   detail as links into `../reference/`.
6. `python3 scripts/sync_references.py --skill <name>`, then
   `python3 scripts/catalog.py`, then `python3 scripts/check.py` (online: checks
   the URLs) and `python3 -m unittest discover -s scripts -p 'test_*.py'`.
7. Add the row to the README skills table (description from `skill.json`).
8. Run the acceptance below and open the PR with `reference/`,
   `references.lock` and `catalog.json` included.

## Acceptance before merge

1. Install the **branch working tree's** copy of the skill and its whole
   `requires` closure (transitive: a required skill's own `requires` come
   too) into a temporary project for both agents. Never use
   `dreamlake skill install` for this step: it installs the released bundle,
   so it would test the old version. Resolve the closure from `catalog.json`
   (run `python3 scripts/catalog.py` first if `skill.json` changed):

   ```bash
   closure=$(python3 -c 'import json,sys;c=json.load(open("catalog.json"))["skills"];s=set();q=[sys.argv[1]]
   while q: n=q.pop(); s.add(n); q+=[r for r in c[n]["requires"] if r not in s]
   print(" ".join(sorted(s)))' <name>)
   tmp="$(mktemp -d)"; mkdir -p "$tmp/.claude/skills" "$tmp/.agents/skills"
   for s in $closure; do cp -R "$s" "$tmp/.claude/skills/" && cp -R "$s" "$tmp/.agents/skills/"; done
   ```

   Only after the release does `dreamlake skill install <name> --agent claude --dir "$tmp"`
   (and `--agent codex`) re-check what users actually get.
2. Open the installed `SKILL.md` and read it back word for word.
3. Start Claude Code and Codex in `$tmp` and run three requests each: a
   representative task; an SDK-only request; a capability the skill does not
   have. Pass means: the agent opens the intended action; the SDK request is
   handled or declined the way `SKILL.md` says; the unsupported capability is
   refused without invented commands.
4. Paste the six results (three per agent) in the PR.

## PR checklist

- [ ] The change is a step/exception (here) or a fact (docs site), not a fact patched into an action.
- [ ] `python3 scripts/check.py --offline` and `python3 -m unittest discover -s scripts -p 'test_*.py'` pass; output in the PR.
- [ ] No hand edits under any `reference/`; `references.lock` and `catalog.json` regenerated when `docs[]` or `skill.json` changed.
- [ ] Flag semantics are links into `../reference/<page>.md#<heading>`, not restated.
- [ ] Links are file-relative and stay inside the skill; other skills are named.
- [ ] `requires` closure is right; `renamed.json` updated for a rename or merge.
- [ ] Moved or retired files have a note under `docs/migration-<topic>/`.
- [ ] Size caps respected, or the skill was split.
- [ ] Acceptance results for both agents pasted.
- [ ] Nothing private or operational in any page: this repository and its releases are public.

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
python3 scripts/check.py --offline                 # everything CI checks on a PR, incl. every tools/test_*.py under pytest
python3 scripts/check.py                           # plus: every docs[] page answers 200 as Markdown
python3 -m unittest discover -s scripts -p 'test_*.py'   # the scripts' own tests; tools/ tests live with their skill

python3 scripts/sync_references.py                 # refresh reference/ and references.lock
python3 scripts/sync_references.py --skill <name>  # one skill only
python3 scripts/sync_references.py --check         # report drift against the live sites, write nothing
python3 scripts/sync_references.py --offline-verify

python3 scripts/catalog.py                         # regenerate catalog.json after editing any skill.json
python3 scripts/catalog.py --check
python3 scripts/package.py                         # dist/skills.tar.gz and dist/catalog.json, as the release does
```

## Releases

Pull requests run `check.py --offline` and the unit tests. Nightly, CI fetches
every `reference/`, validates, commits any change to `main`, and when `main`
differs from the last tag it tags `vYYYY.MM.DD` (`.N` when that date is
taken), builds `skills.tar.gz` (every skill directory plus the committed
`catalog.json` at the archive root, so a manual installer can read `requires`
offline) and the release `catalog.json` (the committed catalog plus the
tarball's `assets` hash and size), and publishes a GitHub release. The
`dreamlake` CLI installs from that release; its own repository pins a tag in
`skills.lock` and embeds the `dreamlake-cli` skill at that tag.

Push with an explicit ref, `git push origin HEAD:refs/heads/<branch>`, never a
bare `git push`.
