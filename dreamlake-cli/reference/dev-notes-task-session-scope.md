# Task session scope defaults

## 2026-09-14 — Implementation and release preparation

For [Workstream #301](https://github.com/dreamlake-ai/dreamlake-workspace/issues/301),
`dreamlake tasks` resolves namespace and project independently: explicit flags,
then `DREAMLAKE_NAMESPACE` / `DREAMLAKE_PROJECT`. Namespace retains its login
fallback; project fails before network access when absent. No shared context file
is introduced, and the existing namespace/project syntax and order remain intact.
Agent runners must supply session variables to each process and restore them when
resuming a session. Other command groups keep their existing behavior.

The task suite covers environment defaults, independent flag overrides, absent
project and login fallback. CLI 0.19.1 binaries compile for all eight supported
platforms, with a detached macOS startup smoke check. Merge, package publication,
docs deployment and hosted readback remain separate release steps; see the
[release record](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.19.1)
for final publication status.

## 2026-09-14 — Native release and documentation deployed

[CLI PR #70](https://github.com/dreamlake-ai/dreamlake-cli/pull/70) merged after
CI passed. The final local suite passed all 997 tests. Native 0.19.1 is published
and the `latest` pointer reads back correctly after checksum/size verification of
all eight public binaries. A read-only hosted task list using environment scope
also succeeded. The task docs and cross-documentation links are deployed at
[cli.dreamlake.ai/tasks](https://cli.dreamlake.ai/tasks/).

The main npm package and seven platform packages read back at 0.19.1. The
[macOS arm64 package](https://www.npmjs.com/package/@dreamlake/dreamlake-cli-darwin-arm64?activeTab=versions)
is still marked **Validating** by npm automated review. A fresh npm installation
therefore cannot yet run on macOS arm64; npm `latest` was restored to 0.19.0.
Native installation is verified. After review completes, verify a fresh npm
installation before promoting npm `latest` to 0.19.1. No server schema, permissions
or task records changed.
