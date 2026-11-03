# CLI namespace-selection skill acceptance

The exact branch copy of `dreamlake-cli` and its full dependency closure (no additional required skills) was installed into isolated `.claude/skills` and `.agents/skills` directories. Both installed SKILL.md files were read back in full. The agents read only local branch skill files; no DreamLake commands, external resource requests, credential changes or configuration writes were performed.

The generated environments reference was fetched from the published owning CLI docs at `0.102.0 320c576`. Reference files and references.lock were regenerated with `scripts/sync_references.py`; none were edited by hand. The procedure stays in the existing setup action and checks installed help before selection.

## Validation

- `python3 scripts/check.py --offline`: passed; one optional scene-tools dependency skip warning.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 55 passed.
- `python3 scripts/sync_references.py --offline-verify`: passed.
- `python3 scripts/catalog.py --check`: passed.
- Skill Creator frontmatter validation: passed.
- `git diff --check`: passed.

## Six final behavior checks

| Agent | Request | Result |
| --- | --- | --- |
| Claude Code | Make subsequent CLI work use fortyfive | Passed: setup action, installed version/help checks, actual namespace name, read-only confirmation, explicit arguments preserved. |
| Claude Code | Public TypeScript SDK-only namespace default | Passed: documented explicit SDK namespace; no CLI configuration mutation or invented SDK-wide setter. |
| Claude Code | Switch an open GUI chat through the CLI command | Passed: unsupported CLI capability refused; separate conversation `/su fortyfive` identified. |
| Codex | Make subsequent CLI work use fortyfive | Passed: setup action, installed version/help checks, actual namespace name, read-only confirmation, explicit arguments preserved. |
| Codex | Public TypeScript SDK-only namespace default | Passed: documented explicit SDK namespace; no CLI configuration mutation or invented SDK-wide setter. |
| Codex | Switch an open GUI chat through the CLI command | Passed: unsupported CLI capability refused; separate conversation `/su fortyfive` identified. |

The initial Codex negative authorization test was stopped by the service content filter and is not counted as acceptance. The final unsupported-capability scenario instead tests the benign CLI/GUI scope boundary; both runtimes completed all three final requests. Claude used restricted Read-only tools without MCP; Codex used its read-only sandbox. Existing authentication was used without changes.

## Claude Code results

I read the branch copy only: `SKILL.md`, which routes all three requests to the `setup` action, then `actions/setup.md`, and its referenced section "Select the default CLI namespace" in `reference/cli-environments.md`. I also checked `reference/cli-command-reference.md`. Nothing was executed and no configuration was touched.

**Case 1: "Make my subsequent DreamLake CLI work use the fortyfive namespace."**
Routed to the setup action, namespace-selection section of the environments reference. This is the supported case. The procedure is:

```bash
dreamlake --version      # must be 0.102.0 or later; su is absent before that
dreamlake su --help      # confirm the installed binary has the command
dreamlake su fortyfive
dreamlake hosts list     # read-only confirmation that the scope took effect
```

- The selection is a local CLI default, stored in the user config and bound to the current remote and credential fingerprint. It does not change login identity, grant permissions, or move resources.
- The account must own the namespace or belong to the fortyfive organization, or the command fails with an access error.
- Any explicit `--namespace` or namespace-qualified target still wins for that one invocation and must be preserved.
- Login, environment switch, and logout clear the selection, so it has to be re-run after those.
- If the command is missing, use the documented upgrade path. Do not edit the config file by hand or change credentials as a substitute.

**Case 2: "Integrating the public TypeScript API; should I run dreamlake su?"**
Routed to the setup action, same reference section. The answer is no. The environments reference states the public TypeScript API requires an explicit namespace on each call, for example a hosts client constructed with the namespace string, and never reads CLI configuration. The setup action adds that for an SDK-only request you use the SDK's documented namespace argument instead of changing CLI config. Running `su` would change CLI scope without affecting SDK behavior. Pass "fortyfive" explicitly in the SDK calls, or wrap that in your own application-level default.

**Case 3: "Use dreamlake su to switch my open GUI chat to fortyfive."**
Routed to the setup action, same reference section. This is a capability boundary. The reference says `su` changes local CLI scope only and explicitly "does not switch the GUI". The GUI conversation has its own separate, conversation-scoped selection, the built-in agent command `/su <namespace>` typed inside the chat. The setup action also scopes the CLI task away from GUI session changes. So the correct response is to not run the CLI command for this purpose and direct the user to the in-chat `/su fortyfive` instead. If they also want later CLI work in fortyfive, that is the separate Case 1 procedure.

## Codex results

Read only the specified branch copy. No DreamLake commands were executed or settings changed.

For all three cases, I read `SKILL.md`, selected `actions/setup.md`, and read the local generated `reference/cli-environments.md`, particularly “Select the default CLI namespace.”

1. **Subsequent CLI work in `fortyfive`:** The documented procedure is:
   ```bash
   dreamlake --version
   dreamlake su --help
   dreamlake su fortyfive
   ```
   Requires CLI **0.102.0+** and membership in `fortyfive`. Then verify with a read-only operation from the intended task. Explicit namespace arguments still take precedence. Login, environment switching, and logout clear the selection. If `su` is unavailable, use the documented upgrade path.

2. **Public TypeScript SDK default:** Do **not** run `dreamlake su` for this. The public TypeScript API never reads CLI configuration and requires explicit namespaces, for example:
   ```ts
   client.hosts('fortyfive')
   ```
   Supply `fortyfive` explicitly at the relevant SDK calls; the read reference documents no SDK-wide namespace default.

3. **Currently open GUI chat:** `dreamlake su fortyfive` cannot switch its namespace; it changes local CLI scope only. The reference identifies built-in agent **`/su fortyfive`** as a separate, conversation-scoped selection. Use that within the applicable GUI conversation; the CLI cannot perform the requested GUI switch.


Merge, dated release assets, native CLI availability and fresh released installation are separate verification stages. Native CLI 0.102.0 and its owning docs were published before this reference sync; these acceptance runs do not make an npm publication claim.
