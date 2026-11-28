---
name: dreamlake-session-archives
description: Configure local session Sources and archives, inspect native relationships, and manage personal session names and list placement without changing provider records or granting remote execution.
---

# DreamLake session archives

Use for configured local session Sources, their archive destination and audience,
consent and progress for session uploads, or native parent/child and agent
relationships, or personal session names and list placement. Check the deployed capabilities;
installing this skill does not enable an unreleased feature.

| Request | Action |
| --- | --- |
| Give sessions useful personal names, move a child to the top level, or hide/restore a session in your list | [Manage personal session presentation](actions/presentation.md) |
| Explain native ancestry, inspect parent/child or agent membership, or reconcile authorized relationship metadata | [Inspect native relationships](actions/native-lineage.md) |
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
product contract; [native relationships](reference/docs-lakeshore-hosts-native-session-lineage.md)
supplies the evidence and collection contract;
[terminal sessions](reference/cli-sessions.md) describes the
separate CLI surface. These references are fetched from docs.dreamlake.ai and
cli.dreamlake.ai; never edit `reference/` by hand.
