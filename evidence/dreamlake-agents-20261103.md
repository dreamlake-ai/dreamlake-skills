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

The same read-only three-case prompt was attempted with Claude Code, restricted
to Read tools and plan permission mode. The process produced no output before
its 90-second deadline and exited 124. These three acceptance cases remain
unverified; the Codex results do not stand in for them.

## Release prerequisites

1. Deploy and verify the agent/resource tools and the public
   `https://docs.dreamlake.ai/agents/resource-tools` page and its `.md` twin.
2. Add that URL to the skill's docs list and regenerate references through the
   repository fetcher, then run checks and the outstanding Claude acceptance.
3. Merge, publish the normal skills tag, perform a fresh installed readback, and
   update the CLI skills lock separately. None of those release steps has run.
