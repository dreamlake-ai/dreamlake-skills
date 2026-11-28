---
name: dreamlake-agents
description: Create and maintain DreamLake agent definitions, use discovered resource APIs, and run authorized remote commands or interactive shells through the built-in agent. Agent definitions are distinct from live sessions; runner and machine setup belongs to other skills.
---

# DreamLake agents

Use this skill to author an agent or manage a DreamLake resource through the
built-in agent. Verify the installed client's help and the deployed tool catalog
before using a new capability; a skill update does not deploy the product.

| Request | Action |
| --- | --- |
| Save or manage link files | Use the saved-urls action of `dreamlake-links` |
| Define or edit an agent, attach instructions and optional skills | [Author an agent](actions/author.md) |
| Upload an agent directory (README, prompt entry, skills) or compare its versions | [Upload and review an agent directory](actions/package.md) |
| Publish a draft or activate an older agent release | [Agent releases](actions/releases.md) |
| Run a command or interactive shell on an enrolled host from the built-in agent | [Remote execution](actions/remote-execution.md) |
| Discover and execute an operation on a DreamLake resource | [Use resource APIs](actions/resource-api.md) |

For setup or login, use the setup action of `dreamlake-cli`. Use SDKs when the
user asks for an integration or the documented CLI does not support the task.
A missing capability must be reported; never invent a route, tool or flag.

## Canonical source

Product facts are in [agent authoring](reference/docs-agents-authoring.md), [the resource tools reference](reference/docs-agents-resource-tools.md),
[agent commands](reference/cli-agents.md) and
[the runnable API](reference/cli-runnable-api.md). These pages are fetched from
docs.dreamlake.ai and cli.dreamlake.ai; never hand-edit `reference/`.
