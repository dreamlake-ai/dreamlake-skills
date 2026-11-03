# Host move skill release acceptance

The branch copy of `dreamlake-lakeshore` and its complete `requires` closure (`dreamlake-cli`) were copied into isolated `.agents/skills` and `.claude/skills` directories. SKILL.md was read back in full. No production resources, credentials, or access settings were changed by these acceptance executions.

The current procedure distinguishes the missing native CLI command from the documented published Python API. Its generated product reference was fetched from the owning live enrollment guide at docs version `0.1.110`, source `30598db3`. The native CLI command is not claimed released.

## Validation

- `python3 scripts/check.py --offline`: passed; one optional scene-tool dependency skip warning.
- `python3 scripts/sync_references.py --offline-verify`: passed.
- `python3 scripts/catalog.py --check`: passed.
- `python3 -m unittest discover -s scripts -p "test_*.py"`: 55 passed.
- Concurrent main reference updates were reconciled by regenerating from the live docs, not by editing or choosing a generated conflict side.

## Six behavior checks

| Agent | Request | Result |
| --- | --- | --- |
| Codex | Move a private laptop when the installed native CLI lacks the operation | Passed: use the documented published Python fallback; verify deployment/identity and preserve preview guards. |
| Codex | Python SDK-only preview/apply with safe retry | Passed: documented methods, no shell substitution, exact durable request replay and current-state readback. |
| Codex | Public/member-wide sharing and bypassing migration blockers | Passed: unsupported widening and bypass are refused; private access and blockers remain enforced. |
| Claude Code | Move a private laptop when the installed native CLI lacks the operation | Passed: missing CLI support does not block the available documented Python API. |
| Claude Code | Python SDK-only preview/apply with safe retry | Passed: requested SDK language retained, methods taken from the fetched guide, full request guards preserved. |
| Claude Code | Public/member-wide sharing and bypassing migration blockers | Passed: unsupported widening and bypass are refused; private access and blockers remain enforced. |

The two capability/fallback cases per agent were rerun after the procedure update. The unchanged unsupported-sharing/blocker-boundary cases reuse the earlier successful branch-installed executions. Existing agent authentication was used without changes. The successful Claude runs used restricted local Read access; Codex ran read-only.

## Current Codex capability and SDK results

Both requests pass under the updated procedure.

1. **Move the laptop:** use the documented Python fallback. The missing native `hosts move` command is a CLI capability gap; it does not block the available Python API and matching server. Resolve the exact laptop Host ID and enrollment in `alice`, preview its move to `acme`, then apply the reviewed preview within the authorized scope. Confirm retained personal ownership, private visibility, destination name, session-sharing removals, run policies and all blockers. Read back destination inventory and exact enrollment status afterward.

2. **Python-only integration:** use the documented methods directly, without subprocesses:
   ```python
   from dreamlake import DreamLakeClient

   client = DreamLakeClient()
   preview = client.hosts.move_preview("alice", host_id, "acme")
   ```
   Return the complete preview for review. After review, require `preview["executable"]` and construct:
   ```python
   request = dict(
       destination_namespace="acme",
       request_id=request_id,
       expected_revision=preview["revision"],
       preview_hash=preview["previewHash"],
   )
   receipt = client.hosts.move("alice", host_id, **request)
   ```
   Before submission, durably save the reviewed preview, source namespace, Host ID and exact request. After a timeout or ambiguous result, replay that same `move` call unchanged. Never replace the request ID, refresh guards silently, or remove blocking dependencies. A historical replay receipt requires a fresh current-state readback.

For both, `DreamLakeClient()` uses the documented shared `~/.dreamlake` authentication configuration; documented connection overrides are `DREAMLAKE_REMOTE` and `DREAMLAKE_API_KEY`. Confirm the effective deployment and personal identity, authority in both namespaces, and exact host ownership without exposing credentials. The SDK-only integration consumes configured authentication; it need not invoke CLI login.

Native CLI release, published SDK capability, deployed API support and live verification are separate claims. Terminal and metrics functionality also require separate verification.

Only local references were read; no DreamLake commands, external requests or mutations were performed.

## Current Claude capability and SDK results

Both requests route to the **host-move** action; the skill's own sources resolve them as follows.

**Request 1: move laptop alice to acme, keep private, native CLI lacks `hosts move`**

- **Action:** proceed via the documented Python SDK fallback. The action file says an absent CLI command is a client capability gap, not proof the server or SDK lacks the operation, and when no SDK language is specified the published Python API may complete the task with the same guards (`actions/host-move.md:10-20`).
- **Authentication:** instantiate the Python client with its documented default credentials, as the guide's example does, after confirming the intended deployment and signed-in namespace. Keep credentials out of output. Authority is required in both alice and acme plus ownership of the exact host.
- **Next step:** resolve the single laptop host ID and source namespace from inventory, not every "my computers" row. Confirm the user wants placement moved, not just an agent namespace switch. Call `move_preview('alice', host_id, 'acme')`, review name, owner, private visibility, sessions and runs policies, access changes and blockers, and stop if not executable. Apply with the same preview's revision and hash and an explicit request ID. Then read acme inventory and exact host status. Privacy is preserved by the server: the host keeps its owner and stays private (`reference/docs-lakeshore-hosts-enroll.md:113-118`).
- **Separation:** state that the native CLI command is unavailable in the installed build, that the Python API and Compute dialog are independent of CLI packaging, and that the server's preview response is the live availability check (`reference:107-111`). Never substitute a raw ownership update or re-enrollment.

**Request 2: Python SDK-only preview/apply integration with safe retry**

- **Action:** write it against only the two documented Python methods, `client.hosts.move_preview` and `client.hosts.move`, with the keyword arguments shown in the guide. No shell commands, no TypeScript, no invented methods.
- **Authentication:** same documented client construction. The guide does not specify token environment variables for Python, so the integration should not hardcode one. Document that as a verification item against the Python host API reference.
- **Guards to preserve:** check the preview's executable flag and surface blockers rather than detaching dependencies. Bind apply to the preview's revision and hash and a caller-supplied request ID. Persist the full request tuple before submitting if the caller must survive a restart.
- **Safe retry:** on timeout or ambiguous response, replay the exact same tuple. Never mint a new request ID, never silently fetch a newer preview. Treat a conflict as a stop, treat a replayed receipt as historical, and read current host status afterward. Authorization is rechecked on every retry.
- **Separation:** code existence is not rollout. The integration should report implementation, client release and live server verification as three separate statements, and should not claim native CLI support.

**One gap to flag.** The guide's Python example is illustrative and the full method contract lives in the linked Python host API docs, which are not in the local reference set. Exact exception types, return shapes and the auth configuration must be verified there before claiming the integration is complete.

## Unchanged unsupported boundary results

Codex: public/member-wide sharing and blocker bypass are unsupported. The action prohibits widening permissions, detaching dependencies, deleting sessions or rotating keys to force a move through; leave the move unapplied.

Claude Code: making the laptop public to organization members is outside this private move, and blockers must be reported rather than bypassed. The action prohibits detaching dependencies, deleting sessions, rotating keys or otherwise forcing a blocked move through.

Product deployment, live docs, the dated skill tag/assets, and a fresh released installation are separately verified release stages. A merged PR or an SDK installation alone does not prove the server or native CLI rollout.
