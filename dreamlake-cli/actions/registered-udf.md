# Execute one registered Python UDF

Requires CLI 0.68.0 or later with `runnable run` and `runnable receipt`. Check
the installed version before using these commands. See
[the complete contract](../reference/cli-registered-udf.md).

1. Use an immutable full SHA-256 UDF reference with version-owned repo ID,
   source file and entrypoint metadata. Do not substitute mutable head fields
   or current local code. Setup/login/environment selection remains unchanged.
2. Choose an existing owned host and exact enrollment in the same namespace.
   Existing submission authority and readiness checks must pass. No provisioning.
3. Submit JSON inputs with an explicit stable request ID. On uncertain submission,
   reuse that ID and identical payload; changed payload conflicts rather than
   relaunching. A new identity is a deliberate new execution.
4. Retain the printed run reference. Retrieve its durable binding/result using
   `runnable receipt NAMESPACE/RUN_ID --json`. Use existing run logs/cancel as needed.

This is a managed host run, not a queue invocation or external Job report. Registry
and CP snapshot IDs remain null for inline single-module delivery. Archive-bound
versions, dependency installation, agents, asynchronous/generator UDFs and generalized
relaunch are unsupported. Request acceptance is not completion. Unknown/crashed
worker claims remain unresolved under the existing execution policy.

Upload, Notes, artifact and workflow tasks keep their existing guides. Use SDKs
when explicitly requested or when a documented CLI capability gap requires them;
do not route those tasks into this narrow execution adapter.
