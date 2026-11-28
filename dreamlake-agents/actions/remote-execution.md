# Execute a remote command or open a shell

Inspect the offered `dreamlake_exec`, `dreamlake_ssh` and
`dreamlake_execution_*` tool schemas and the
[remote execution contract](https://docs.dreamlake.ai/agents/resource-tools#remote-shell-execution)
before dispatch. This action is for the built-in agent. An external agent with
local CLI access should inspect `dl exec --help` or `dl ssh --help`; do not
invent built-in-tool flags on those commands. For an SDK-only integration,
follow the documented agent API and capability contract rather than assuming
a local CLI or a new standalone execution endpoint.

1. Resolve the user's intended namespace, host and Unix account through host
   discovery. Carry the exact host and enrollment IDs into every operation.
   If multiple accounts remain plausible, ask which one; never silently choose
   a different host or account after a refusal.
2. Check whether execution tools are offered and allowed by the selected agent
   definition. If execution permission is absent, explain the documented
   permission control; discovery or read access is not authority to execute.
   Preserve existing authorization when it already covers the requested work.
3. Choose exec for a command and SSH for an interactive shell. Use a shell
   command when the user needs shell syntax; use literal argv for arguments
   that must not expand. Choose streaming when observing initial output helps,
   or async when work should continue while the agent does another task.
4. Choose a stable request ID, submit once, and retain the returned execution
   handle and cursor. Continue reading that execution; use its stdin or resize
   tools when interaction is needed. A running handle is not a completed job.
   Inspect exit status and relevant output before reporting success.
5. After an uncertain start, recover with the original request ID and identical
   inputs or the checkpointed handle. After an uncertain input/control call,
   keep the original operation ID. Never turn a lost reply into an automatic
   replacement command. Report missing state or lost authority without guessing.
6. Cancel only the execution the user intended to stop, then read until its
   observed terminal state. Report the documented limits on detached processes
   and transient output. Do not automatically index commands or output.

Read the contract for prerequisites, limits, output encoding, retention,
permission checks and the distinction between remote async execution and a
background/durable agent job. A skill release does not establish that a server
has deployed these tools. If the installed surface lacks a capability, report
that gap instead of substituting a generic resource route or broader identity.
