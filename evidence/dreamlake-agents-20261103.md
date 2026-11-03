# DreamLake agents skill acceptance

This is a draft procedure change. Product and resource-tool documentation release
are prerequisites; the skill has not been tagged or installed from a release.

- `python3 scripts/check.py --offline`: passed. Four existing optional-tool suites
  reported that pytest was not installed.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 55 tests passed, one
  existing test skipped.
- Generated references were fetched from the live CLI docs with
  `scripts/sync_references.py --skill dreamlake-agents`; no generated reference
  was edited by hand.
- The branch's skill and its `dreamlake-cli` dependency were copied into an
  isolated temporary project's `.agents/skills` and `.claude/skills` directories.

## Codex readback

A read-only run opened the installed skill and both actions. It made no network
requests or resource mutations.

1. **Create an agent using an instruction note and skills folder:** routed to
   `actions/author.md`, required namespace/project discovery, stable note/folder
   IDs, duplicate inspection and readback. It correctly reported that the
   acceptance environment had no offered creation tool and did not claim save,
   filing or execution.
2. **TypeScript SDK only:** opened the installed canonical runnable API reference.
   It did not invent a TypeScript method absent from that reference, did not
   treat a model tool name as an SDK method, and did not substitute CLI execution.
3. **Raw-byte video upload via an unavailable model tool:** routed to
   `actions/resource-api.md`, reported the missing binary transport and offered
   only documented environment-supported CLI/SDK fallback. No upload was claimed.

## Claude readback

The initial attempt timed out after 90 seconds. A retry first verified that
Claude Code 2.1.317 reported an authenticated session, without publishing
credential details. The same three-case prompt then completed successfully
within a 180-second deadline (exit 0), in the installed temporary project with
plan permission mode, restricted Read/Glob/Grep tools and no MCP servers.
No permission bypass was used.

1. **Create an agent using an instruction note and skills folder:** opened
   `actions/author.md`, checked the local references and identified the missing
   offered creation tool and missing note-reference schema. It required stable
   IDs, duplicate inspection, project verification and readback, and did not
   claim creation, attachment, filing or execution.
2. **TypeScript SDK only:** opened both actions and the installed runnable API
   reference. It reported that the installed references do not document an
   agent SDK method, distinguished the documented HTTP route from an SDK
   method, and identified the remote TypeScript reference as the next check.
   No SDK method was invented or integration executed.
3. **Raw-byte video upload via an unavailable model tool:** opened
   `actions/resource-api.md`, refused to invent an upload tool and identified
   documented CLI file-path workflows as conditional alternatives. It required
   installed-capability verification and a receipt before claiming upload.

Both runs report only what their installed references and offered tools prove.
The Claude readback surfaced older published CLI facts about SDK availability
and project filing. These references must be refreshed after the new product
documentation deploys; acceptance does not establish that the new APIs are live.

## Release prerequisites

1. Deploy and verify the agent/resource tools and the public
   `https://docs.dreamlake.ai/agents/authoring` and
   `https://docs.dreamlake.ai/agents/resource-tools` pages and their `.md` twins.
2. Add those URLs to the skill's docs list and regenerate references through the
   repository fetcher, then run checks and repeat acceptance against the updated
   installed reference closure.
3. Merge, publish the normal skills tag, perform a fresh installed readback, and
   update the CLI skills lock separately. None of those release steps has run.
