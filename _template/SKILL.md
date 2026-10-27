---
name: dreamlake-example
description: Template for a DreamLake skill; copy it to start a new one. It performs no real task. A real description states the user goal this skill owns and the neighbouring goals it does not cover.
---

# dreamlake-example

This directory is the one shape every skill in this repository has. Copy it to
`<name>/`, set `name` in `skill.json` and in the frontmatter above, and replace
this text. A SKILL.md does two things: it says when to use the skill, and it
routes the request to exactly one action page. It carries no procedures, no
command listings and no product facts of its own.

## When to use

- The user wants the example task done (state the goal in the user's words).
- Not for neighbouring goals another skill owns; name that skill instead, for
  example `dreamlake-cli` for installation, login and environment selection.

## Route the request

| Request looks like | Open |
|---|---|
| "Publish this report and give me the link" | [actions/example.md](actions/example.md) |

An action page is one task: commands first, exceptions after. It does not
repeat flag details; it points at a page in `reference/` or at `--help`.

## Rules

- Product facts (commands, flags, behaviour) come from `reference/`, never from
  memory. A wrong fact is fixed on the docs site, not patched here.
- Other skills are referred to by name (`dreamlake-cli`), never by path.
- `requires` in `skill.json` lists every skill this one hands off to; the
  installer installs them together.

## Canonical source

The pages in `reference/` are fetched by CI from the DreamLake docs sites and
listed in `skill.json` under `docs`:

- https://docs.dreamlake.ai — product concepts and behaviour
- https://cli.dreamlake.ai — the `dreamlake` command line
- https://viz.dreamlake.ai — dataset visualisation and `.dreamrc`

Every page is fetchable as Markdown at `<page-url>.md`, and each site's whole
corpus at `/llms-full.txt`. Do not edit `reference/`; CI overwrites it.
