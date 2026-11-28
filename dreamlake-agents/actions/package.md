# Upload an agent directory and review what changed

Check that the installed client has these commands. If any is missing, report
that and keep the user's directory; do not rebuild the upload from API calls.

```bash
dl agents push --help
dl agents files --help
dl agents diff --help
```

```bash
dl agents push ./my-agent --namespace YOUR_NAMESPACE --dry-run
dl agents push ./my-agent --namespace YOUR_NAMESPACE
dl agents files NAME --namespace YOUR_NAMESPACE
dl agents diff NAME --namespace YOUR_NAMESPACE
```

1. Lay the directory out as [agent commands](../reference/cli-agents.md)
   describes: a README for people, one prompt entry, and one directory per
   skill. Write the README for someone deciding whether to use the agent. Do
   not paste the prompt into it.
2. Keep the prompt entry short and stable: role, boundaries, and when to use
   each skill. Put procedures that will keep changing in skills, so a later
   change touches one skill and leaves the prompt alone.
3. Inside a skill, refer to its own supporting files by relative path from its
   skill file. They are stored with the skill and never run by DreamLake; a
   script helps only a runtime that can read and run files itself.
4. Run the dry run and read every line before the real upload. Resolve each
   warning about a link to a file that is not in the directory.
5. After the upload, run `diff` and show the user the changed files. Uploading
   changes the draft only; publishing is the separate
   [releases action](releases.md), using the exact line the upload printed.

When only a skill was meant to change, `diff` should list that skill and
nothing else. If the prompt entry also shows as changed, stop and compare the
directory with the stored prompt before publishing.

If an upload fails partway, read the error before doing anything else. It names
any memos the run created. Upload the same directory again: the command picks
those memos up instead of creating new ones. Never delete them to clean up.

An agent whose prompt is stored inline is refused. Converting it moves the
prompt into a memo, after which people need access to that memo to run the
agent. Ask the user before passing the conversion flag.

The file names and the split between prompt and skills are conventions, not
locks. `files` names what actually protects each file. When the user wants
someone to maintain skills without being able to change the prompt, the answer
is memo access: grant writing on the skill memos and not on the prompt memo.
Do not tell a user that the layout itself prevents prompt edits.

Limits, flags and the stored shape are in
[agent commands](../reference/cli-agents.md) and
[agent authoring](../reference/docs-agents-authoring.md).
