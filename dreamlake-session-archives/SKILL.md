---
name: dreamlake-session-archives
description: Configure namespace-bound local session discovery and restricted archive storage, inspect upload consent and historical coverage, and recover interrupted archival without granting remote execution.
---

# DreamLake session archives

Use for configured local session Sources, their archive destination and audience,
or consent and progress for session uploads. Check the deployed capabilities;
installing this skill does not enable an unreleased feature.

| Request | Action |
| --- | --- |
| Set up automatic local discovery and a personal or organization archive destination; inspect storage isolation | [Configure a session Source](actions/configure.md) |
| Upload an inspected session or approved history; inspect coverage or recover an interrupted upload | [Approve and verify archival](actions/archive.md) |

Use `dreamlake-lakeshore` for host enrollment, SSH and opening an exact native
terminal session. Use the session-links action of `dreamlake-cli` for Memo or
Artifact affiliations and the legacy explicit conversation-export command.
Do not substitute those uploads for the configured archive service.

For an explicitly SDK-only request, a missing documented SDK operation is a
capability gap: report it and do not switch to HTTP. Explain documented HTTP as
an alternative only; using it would require a change to the SDK-only constraint.
For integrations that already allow HTTP, follow the documented service contract.
Never invent a session-archive CLI command,
SDK method, storage binding screen or enterprise policy capability.

## Canonical source

[Source isolation and session archival](reference/docs-sources.md) supplies the
product contract; [terminal sessions](reference/cli-sessions.md) describes the
separate CLI surface. These references are fetched from docs.dreamlake.ai and
cli.dreamlake.ai; never edit `reference/` by hand.
