# LLM-Readable Docs

These docs are built to be read by agents as easily as by people. Every page
has a markdown twin, and the whole corpus is published in the formats LLM
tooling already looks for — so you can point Claude (or any agent) at DreamLake
viz and have it answer accurately.

## Fetch a single page

Append `.md` to any docs URL to get the raw markdown — no nav, no chrome:

```bash
curl https://viz.dreamlake.ai/index.md
```

Every page also advertises its markdown twin in the HTML head:

```html
<link rel="alternate" type="text/markdown" href="/index.md" />
```

## The whole site, two ways

- **[`/llms.txt`](https://viz.dreamlake.ai/llms.txt)** — a short, linked index
  of every page ([llmstxt.org](https://llmstxt.org) standard). The entry point
  an agent reads first to decide what to fetch.
- **[`/llms-full.txt`](https://viz.dreamlake.ai/llms-full.txt)** — every page
  concatenated into one markdown file. Drop the entire product into a context
  window in a single request.

## Import it as a skill

The docs are also packaged as an [Agent Skill](https://viz.dreamlake.ai/skills/dreamlake-viz.zip)
— a `SKILL.md` plus one markdown reference file per page. Install it so your
agent loads DreamLake viz knowledge on demand:

```bash
# Claude Code: drop it into your project (or ~/.claude) skills directory
curl -L https://viz.dreamlake.ai/skills/dreamlake-viz.zip -o dreamlake-viz.zip
unzip dreamlake-viz.zip -d .claude/skills/
```

> **Note:** **Always current.** Every surface above — the `.md` pages, both `llms` files,
> and the skill — is generated from the same source on each deploy, so none of
> them can drift from what you read on the site.
