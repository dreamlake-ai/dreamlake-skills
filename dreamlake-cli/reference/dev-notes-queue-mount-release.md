# Queue mount release

## 2026-09-15 — public 0.21.1 acceptance

All eight native downloads and the manifest match pinned source `96ebe5b`. npm accepted the eight platform packages and wrapper under `candidate-0-21-1`. A fresh registry installation with scripts disabled passed version/checksum verification, all 34 SSH/import HTTP/PTY checks and the detached HTTP queue mount/list checks. Temporary installations were removed. All eight npm platform packages now match the native manifest. Native and npm `latest` both read back as 0.21.1. [Release](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.21.1) points to the exact tested source; its attached manifest matches the native build. Other npm tags and shared installers were preserved.

The downloaded native macOS binary passed real queue, job and worker reads through the existing development mount. No resources were changed. Staging API mount/control/token-replacement/denial checks and independent cleanup passed separately; browser acceptance, production rollout and Ge review/testing remain open.

[Public native evidence](https://github.com/dreamlake-ai/dreamlake-workspace/issues/274#issuecomment-5678241620) · [Development reads](https://github.com/dreamlake-ai/dreamlake-workspace/issues/274#issuecomment-5678276172) · [npm acceptance](https://github.com/dreamlake-ai/dreamlake-workspace/issues/274#issuecomment-5678399450).

## 2026-09-15 — CLI 0.21.0 candidate verified

The candidate starts from published v0.20.1 and adds the queue mount changes
merged in [CLI #69](https://github.com/dreamlake-ai/dreamlake-cli/pull/69).
[Backend #469](https://github.com/dreamlake-ai/dreamlake-workspace/pull/469)
is merged; hosted rollout remains separate.

All 1,038 source tests, the package build and documentation build passed.
Eight native targets built, and every manifest size and SHA-256 matched.
Only macOS arm64 was executed locally. The standard installer rehearsal passed
installation, PATH setup, repeated installation, foreground/background updates,
version pinning, disabled updates and foreign-launcher refusal. Its simulated
0.21.1 update existed only on a temporary loopback server.

A copied native binary also passed mount and queue-list checks over actual
loopback HTTP with synthetic credentials and a temporary home. The checks
verified both namespace selections, DreamLake authentication, stdin token input,
proxy routing and response redaction. Temporary fixtures were removed. These
checks validate the client protocol; they do not establish hosted acceptance.

Publication, fresh published-client installation, backend rollout and browser
acceptance remain pending. The dashboard connection form remains draft pending
the host-enrollment versus queue-mount flow decision in
[UI #518](https://github.com/dreamlake-ai/dreamlake-workspace/issues/518).
Ge review and testing are not inferred from agent verification.

[Validation receipt](https://github.com/dreamlake-ai/dreamlake-workspace/issues/274#issuecomment-5677450623)
· [Queue mount guide](queues.md)
· [Release notes](release-notes.md)
· [Master #247](https://github.com/dreamlake-ai/dreamlake-workspace/issues/247)

## 2026-09-15 — combine queue commands with the Vault patch

The 0.21.0 npm upload became available after the publication script stopped at registry readback. Its pinned source predates the Vault transport fix in CLI PR #83, released separately as 0.20.2. Native latest remains 0.20.2; npm latest is 0.21.0 at this checkpoint.

Prepare 0.21.1 from the reviewed queue candidate plus the reviewed Vault fix and its native transport/import tests. Do not overwrite published 0.21.0 artifacts. Candidate `96ebe5b` passed 1,047 source tests, including nine compiled transport cases; 34 actual native CLI HTTP/PTY import checks; eight native builds with matching hashes/sizes; detached macOS HTTP mount/list checks; and a 36-page docs build. Publication, fresh registry installation and channel reconciliation are pending. Track delivery in DreamLake issues #274 and #241.
