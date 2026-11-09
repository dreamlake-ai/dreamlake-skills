# Author an agent definition

Inspect the surface you will use before creating anything. In the built-in
agent, inspect the offered tools and the creation schema; shell access and a
CLI installation are not prerequisites. When using the CLI, run:

```bash
dl agents --help
dl agents create --help
dl agents list --plain
```

1. Resolve the intended namespace and project. Inspect existing definitions to
   avoid creating a duplicate when the user meant to edit one.
2. Use the deployed built-in agent creation tool if it is offered, or the
   installed CLI command documented in [agent commands](../reference/cli-agents.md).
   For an SDK-only request, use the TypeScript example in
   [agent commands](../reference/cli-agents.md), [agent authoring](../reference/docs-agents-authoring.md)
   and [the runnable API](../reference/cli-runnable-api.md) rather than inventing
   a client method.
3. Keep the main instructions separate from optional skills. Resolve requested
   memos and folders to stable IDs using available read tools; do not guess IDs
   or copy permission grants from a prompt. Check the live creation schema for
   the supported instruction forms and project filing.
4. Read back the definition, instruction references and project filing. Give
   the user its editor link and identify anything that failed.
5. If creation timed out or returned an uncertain outcome, inspect existing
   definitions and the tool receipt before retrying. Do not create a second
   definition merely because the response was lost.

Creating or editing a definition does not mean running it. Treat a request to
launch a session as a separate action. If the live tools do not expose the new
creation or note-reference capability, report that limitation and retain the
user's draft without claiming it was saved.

The permission and execution model is in
[the resource tools reference](../reference/docs-agents-resource-tools.md).
