# DreamLake Skills

Public [Claude](https://claude.ai/code) **skills** for working with
[DreamLake](https://dreamlake.ai) — each is a self-contained `SKILL.md` that teaches
an AI agent (Claude Code, or any Skills-compatible client) how to perform a DreamLake
task correctly.

## Available skills

| Skill | What it does |
|---|---|
| [`dreamlake-artifacts`](./dreamlake-artifacts/SKILL.md) | Publish, version, share, and view renderable artifacts (HTML/React/Markdown/SVG/Mermaid/code) via the `dreamlake artifact` CLI |
| [`workflow-generator`](./workflow-generator/SKILL.md) | Generate DreamLake WorkflowSpec v1 JSON (stages, compute/agent/sampler/control nodes, typed edges) from a natural-language goal, then validate + push via `dreamlake workflow push` (CLI ≥ 0.5.0) |

## Installation

Each top-level directory is one skill. To make a skill available to Claude Code, copy
its directory into your skills folder:

```bash
# Project-scoped (this repo/checkout only)
mkdir -p .claude/skills
cp -r dreamlake-artifacts .claude/skills/

# — or — user-scoped (all your projects)
mkdir -p ~/.claude/skills
cp -r dreamlake-artifacts ~/.claude/skills/
```

Claude will discover the skill by its `name`/`description` frontmatter and invoke it
when a task matches.

## Contributing a skill

Add a new top-level directory `my-skill/` containing a `SKILL.md` with YAML
frontmatter:

```markdown
---
name: my-skill
description: One or two sentences on what this skill does and when to use it.
---

# My Skill

...instructions...
```

Keep skills accurate to the shipped CLI/UI, concrete, and command-first.
