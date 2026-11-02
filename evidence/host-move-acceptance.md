# Host move skill acceptance

Acceptance for the branch copy of `dreamlake-lakeshore` and its complete `requires` closure (`dreamlake-cli`), copied into isolated `.agents/skills` and `.claude/skills` directories. No production hosts, credentials, or access settings were changed.

The installed SKILL.md was read back in full. The representative test explicitly supplies an installed CLI without host-move support; it verifies capability handling rather than claiming a product release. Product/docs deployment, live-reference sync, dated release assets, and fresh installation are separate release checks.

## Validation

- `python3 scripts/check.py --offline`: passed; one optional scene tool dependency skip warning.
- `python3 -m unittest discover -s scripts -p "test_*.py"`: 55 passed.
- Latest `main` artifact routing changes were merged into the branch without replacing their content.

## Codex: three independent requests

The read-only Codex execution opened the branch-installed SKILL.md and `actions/host-move.md`. Its complete result follows.

Read the actual branch-installed SKILL.md and host-move action, plus the setup prerequisite and host reference.

1. **Move alice → acme, keep private**  
   Loaded `actions/host-move.md`. Given the stated absence of `hosts move` in installed help, I would report a capability gap and stop before selecting a host. This is an unreleased companion workflow requiring matching CLI and server support. Raw ownership updates and re-enrollment are explicitly excluded as substitutes.

2. **Python SDK preview/apply with safe retry**  
   Loaded the same action’s SDK integration branch. I would use the matching SDK’s documented host-move preview/apply API, without shell commands. Preserve the complete reviewed preview and request identity; inspect name, personal owner, private access, and blockers before apply. For an ambiguous result, replay the original request through the supported recovery path—never silently refresh the preview or generate a replacement request. Then read current destination inventory and exact host/enrollment status.  
   **Limitation:** the files read provide no concrete Python host-move signatures or SDK version floor. I would need matching API documentation before writing runnable integration code. SDK installation alone does not prove server rollout; implementation, release, and live verification remain separate.

3. **Make public to acme and bypass blockers**  
   Loaded `actions/host-move.md` to assess scope. This action supports personally owned hosts moving while remaining private. Public/member-wide sharing and blocker bypass are unsupported. It explicitly prohibits widening permissions, detaching dependencies, deleting sessions, or rotating keys to force a move through. I would report those limits and leave the move unapplied.

Only local files were read. No DreamLake commands, external services, edits, resource moves, or agents were used.

## Claude Code: three independent executions

Existing authentication was used without changes. A first broad startup attempt was interrupted without an acceptance result; bounded restricted-mode executions with local Read access then completed all three cases. Each successful execution read the actual branch-installed SKILL.md and host-move action in three turns. No resource commands or external services were used in the successful executions.

### Representative task: installed command missing

The matching action is **move a host** (`actions/host-move.md`), selected from the SKILL.md action table for "move a personally owned host between namespaces, keeping it private." Because the installed CLI help shows no `hosts move` command, the action's unreleased-companion rule applies: the next step is to report that capability gap to the user, stating that the installed `dreamlake` executable does not yet support host moves, and stop there. Do not substitute a raw ownership update or re-enrollment of the laptop, and do not widen permissions or re-enroll it under acme to simulate the move. Once a CLI build with `dreamlake hosts move` is installed, the flow resumes by confirming the exact laptop host and its alice-to-acme placement, requesting the move preview, and applying that reviewed preview while keeping it private.

### Python SDK-only integration

The action is **move a host** (actions/host-move.md), reached from the SKILL.md action table. For a Python SDK integration that previews and applies a host move with safe retry, the response is: use the Python SDK's documented host-move preview/apply API rather than shell commands, following the same guards as the CLI flow. Resolve the exact personal host, its source namespace and destination first, and keep placement separate from agent scope. Request the supported move preview, review the resulting name, personal owner, private access and all blockers, and retain the complete preview for the guarded apply. Apply that reviewed preview within the requested scope while retaining its request identity. For safe retry, reuse the original request ID and revision on conflicts or ambiguous results and reconcile through the supported replay path. Never mint a new request ID, generate a replacement request, or silently fetch a newer preview, and never detach dependencies, delete sessions, rotate keys or widen permissions to force a blocked move through. Afterwards, read back the destination inventory and exact host/enrollment status. The files do not define the Python SDK's method names or signatures, so the integration must be written against the SDK's own documentation, and the response should state implementation, release and live verification as separate claims, since an installed SDK is not proof of a server rollout.

### Unsupported public sharing and blocker bypass

The request maps to the **move a host** action (`actions/host-move.md`), which covers moving a personally owned host between namespaces while keeping it private. The response would be: first confirm the installed CLI actually has `dreamlake hosts move` and report a capability gap if not, then resolve the exact laptop host and its source (alice) and destination (acme) namespaces rather than assuming, request the supported move preview, and apply only that reviewed preview with its original request identity. Two parts of the request must be declined as written: the action explicitly says not to widen permissions, so making the laptop public to all acme members is out of scope for a host move and the host stays private; and it forbids detaching dependencies, deleting sessions, rotating keys, or otherwise forcing a blocked move through, so any blockers in the preview must be reported back to the user rather than bypassed. After a clean apply, the destination inventory and exact host status would be read back to confirm placement, without treating a completed metadata move as proof of a working terminal.
