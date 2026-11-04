---
name: dreamlake-agents
description: Create and maintain DreamLake agent definitions, and use the built-in agent's discovered resource APIs while preserving resource permissions and recovery. Agent definitions are distinct from live sessions; runner and machine setup belongs to other skills.
---

# DreamLake agents

Use this skill to author an agent or manage a DreamLake resource through the
built-in agent. Verify the installed client's help and the deployed tool catalog
before using a new capability; a skill update does not deploy the product.

| Request | Action |
| --- | --- |
| Define or edit an agent, attach instructions and optional skills | [Author an agent](actions/author.md) |
| Discover and execute an operation on a DreamLake resource | [Use resource APIs](actions/resource-api.md) |

For setup or login, use the setup action of `dreamlake-cli`. Use SDKs when the
user asks for an integration or the documented CLI does not support the task.
A missing capability must be reported; never invent a route, tool or flag.

## Canonical source

Product facts are in [agent authoring](reference/docs-agents-authoring.md), [the resource tools reference](reference/docs-agents-resource-tools.md),
[agent commands](reference/cli-agents.md) and
[the runnable API](reference/cli-runnable-api.md). These pages are fetched from
docs.dreamlake.ai and cli.dreamlake.ai; never hand-edit `reference/`.
