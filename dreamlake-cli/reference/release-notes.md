# Release notes

## 0.26.2 — per-request EXACT patches

Notes command handlers now allow stdout to drain before process exit, preserving
large piped JSON/source responses. Regression tests cover delayed pipe readers
with more than 128 KiB of Unicode content.

Notes v2 patches default to ordinary native CRDT synchronization against the
original snapshot identified by `--base-revision`. `--exact` explicitly selects EXACT mode for that request; `--if-match` is a compatibility alias. The CLI never fetches a newer baseline
to hide a conflict, and rejected requests leave local drafts and baselines intact.
The matching Notes v2 API retains original RTC identities. This release also
includes complete mapped HTML reads with canonical-source/hash/revision checks.
Use `--legacy` explicitly with older servers. Package and deployed acceptance
receipts are tracked in [workspace #706](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).

Versions 0.26.0 and 0.26.1 are superseded candidates. The 0.26.0 workflow was
cancelled before publishing the npm wrapper or moving native channels; immutable
versioned R2 objects and platform package uploads remain. Active install channels
stayed at 0.25.0. Version 0.26.1 was never published, and neither candidate docs
site was promoted.

## 0.26.1 — superseded, never published

`notes read --view html` emits the complete server snapshot without added
headers or newline. Embedded canonical source, identity, SHA-256 and revision
are validated before stdout; `--if-match` is guarded on both request and
readback. HTML rejects incompatible history, JSON, legacy and slicing options.
These changes ship in 0.26.2 with the matching Notes HTML server contract. Tracked in [workspace #706](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).

## 0.26.0 — superseded, publication cancelled

Historical candidate: Notes commands changed to the v2 server contract. This
candidate was superseded by 0.26.2 and must not be republished. The current
MERGE/EXACT contract above replaces its required-guard interface.

Full reads emit source with SHA-256 and opaque revision metadata. Incremental
reads and multiline stdin uploads select inline or line diff. Uploads require
the saved revision, and verification reads preserve that exact token. Explicit
`--legacy` retains the prior text/ETag interface. Requires the matching v2
server; no package release, deployment, or live verification is claimed.
Tracked in [workspace #706](https://github.com/dreamlake-ai/dreamlake-workspace/issues/706).

## 0.25.0 — Layered env stacks: `env compose`

`dreamlake env compose [stack]` materializes a layered env stack —
`dreamlake.layers.json`, schema `dreamlake.env-layers/v2` — into a runnable
env directory. The stack defaults to `./dreamlake.layers.json`; `-o/--out`
names the output directory and `--force` writes into a non-empty one. The
CLI owns stack shape validation and source resolution: registry refs
(`{"env": "ns/name[@version]"}`) fill the immutable, hash-verified cache at
`~/.dreamlake/cache/envs/`, so pinned refs with a cache hit cost zero
network, and public envs resolve without login.

Composition semantics (merge / attach / override, URDF import, compile
validation) are delegated to the Python reference engine
`dreamlake.envlayer`, installable as `pip install "dreamlake[compose]"`
(dreamlake 0.19.0 on PyPI). `DREAMLAKE_PYTHON` overrides the interpreter;
otherwise `python3`, then `python`. `env push`/`pull`/`list` need no Python.

Push discipline lands with it: `env push` (and `env create`) now refuses a
directory whose root `dreamlake.layers.json` still references local,
unpinned layers — the pushed provenance would not be re-openable.
`--push-layers` pushes each local layer directory as its own env first
(named by its basename) and stops for pinning + recompose; `--allow-local`
pushes anyway with the provenance marked non-resolvable.

Deep reference: [Env layers](https://docs.dreamlake.ai/envs/layers).

## 0.24.7 — Notes revision diffs

`dreamlake notes diff <note> --since <etag>` compares the current body with a
retained read/edit reference. `--json` includes both refs; plain output stays
pipeable. Requires the revision-diff server endpoint. Read, diff, and patch
help examples now document preserving and reusing the ETag. These examples
also flow into the generated CLI skill.

The feature merged in #114 without shipping: the published 0.24.6 binary
answers `error: unknown command 'diff'`. 0.24.7 is the version bump that
ships it. Published on the native channel (`latest` and `stable` both resolve
to 0.24.7 on dl.dreamlake.ai); as of 2026-09-23 the npm registry's newest
version is still 0.24.6, so npm users first get `notes diff` with 0.25.0.

## 0.24.6 — Note file uploads no longer crash the native binary

`dreamlake notes files upload` sent the `Bun.file()` object itself as the PUT
body. On Bun 1.3.14 on Linux, in a compiled standalone binary, that crashed the
runtime with a SIGSEGV once the response had arrived, when a GET on the same
host had run first — the shape this command takes, because it resolves the note
before uploading. The body is now `Bun.file(path).stream()`: the same file, read
lazily rather than loaded into memory. The observed run was against a loopback
server on this machine, not a remote deployment: the upload exited 0 and stored
the expected 2048 bytes there.

Whether the crash reproduces on every upload, or on other runtimes, platforms or
build modes, was not established; the fix was verified on the configuration
above. No Content-Length is set under Bun, unchanged from 0.24.5, but this
release does not prove behavior against a production HTTP/2 endpoint — whether
the HTTP/2 upload hang of 0.23.0 can recur is pending a focused test. Node keeps
its existing `createReadStream` body.

The DreamDB 0.5.7 upgrade was prepared in 0.24.5, which was not completed as a
release: only two Darwin binaries were uploaded, with no manifest and no npm
publication. It carries forward unchanged here: half-open
`[start, end)` read ranges translated to inclusive HTTP `Range` bounds,
nonce-bearing genesis objects, and the requirement to migrate a legacy dataset
before writing to it. No dependency, command, flag or output shape changes in
this release.

## 0.24.5 — DreamDB 0.5.7 and half-open byte ranges

The bundled `@dreamlake/dreamdb` moves from `^0.4.0` to `^0.5.7`. That release
passes read ranges as half-open `[start, end)`, where the end byte is excluded.
The S3 backend previously forwarded such a range straight into an HTTP `Range`
header, whose end *is* inclusive, so every ranged read fetched one byte too
many. It now translates the bound and requests `bytes=start-(end - 1)`.

Because genesis objects in 0.5.7 carry a random nonce, two datasets created
from the same schema no longer share a genesis hash. A genesis hash is
therefore an object identity, not a schema identity — do not compare one
across SDKs to infer compatibility.

**Migrate a legacy dataset before writing to it.** Datasets written by the
older DreamDB stay readable, but this release performs no automatic migration
and rewrites no existing store, so appending to an unmigrated dataset with the
new SDK is not supported. No command, flag or output shape changes.

## 0.24.4 — Notes sync and recovery guidance

The bundled CLI skill now explains browser sync states, local-draft recovery,
and view-only history. CLI commands still read the server and keep their
existing revision checks; they cannot clear a browser-held draft. This release
updates guidance and packaging, with no new Notes command or protocol.
Publication and fresh-install receipts are recorded in the GitHub release.

## 0.24.3 — native skills and docs-generated command help

Native binaries now embed all 37 generated CLI skill files. `skill list` and
`skill install` work without a checkout or environment override. Installed edits
remain protected; updates require explicit installation and reviewed `--force`.
Ten command help pages now include 26 command examples generated from reviewed docs,
including revision-checked Notes writes and patches. CI and release builds test
a copied native binary, byte readback, reinstall, conflict refusal and peer preservation.
See the [release acceptance checklist](skills.md#release-acceptance-checklist).
Publication and fresh-install receipts are recorded in the GitHub release.

## Unreleased — affected-entry preview pages

`vault kms preview --affected-limit 100` requests one retained-entry metadata page. Use `--affected-cursor` for explicit continuation. Strict output validation retains only the supported metadata and refuses silent omission by an older server. No mutation or release is included. [Guide](/dev/notes/vault-policy-tree).

## Unreleased — selected-prefix policy preview

`vault list --tree --preview-key <ref>` adds explicit `p` preview using the existing
read-only KMS endpoint. Python uses its existing `vault.kms.preview` method.
The view is counts/blockers, not an affected-entry list or mutation approval.
No activation, migration or move is performed. [Guide](/dev/notes/vault-policy-tree).

## 0.22.0 — unpublished release candidate

Adds candidate owner-only interactive metadata browsing and one-page JSON output,
with Python API parity. Actual local HTTP/Mongo and PTY acceptance passed; no
release or deployment claim. This requires the authenticated `GET /v1/vault/tree` route from backend PR576. That source is merged but not deployed at preparation time; older servers return 404 rather than a fabricated tree. [Development note](/dev/notes/vault-policy-tree).

## 0.21.2 — 2026-09-15

Adds a fixed recovery warning to human tracked-run output when the API reports an unresolved prior-daemon admission. Waiting reports each newer revision once; JSON stays unchanged and terminal results suppress the warning. Queue-mount and Vault behavior from 0.21.1 is retained.

[Implementation #88](https://github.com/dreamlake-ai/dreamlake-cli/pull/88) passed independent review, 1,253 tests and CI. Manual validation: `sh scripts/test-run-recovery.sh` exercises the real CLI against a loopback HTTP fixture. Source `b8aa4e2` is pinned by tag `v0.21.2`; release preparation #89 is merged. All eight native public binaries match the manifest. All nine npm tarballs match the reviewed generated files, and native/npm `latest` read back as 0.21.2. The stable channel remains unchanged. A fresh macOS npm install passed reviewed wrapper/native hashes and recovery/queue HTTP checks. Hosted recovery acceptance is separate. [Release and manifest](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.21.2).

## 0.21.1 — 2026-09-15

Combines the queue-mount commands from 0.21.0 with the Vault uncertain-write transport fix released in 0.20.2. The pinned artifact source is `96ebe5b`; [release preparation #84](https://github.com/dreamlake-ai/dreamlake-cli/pull/84) is merged.

All eight native downloads match the manifest. npm accepted all nine uploads, and the wrapper matches the reviewed bytes. A fresh macOS registry installation passed the binary checksum, version, 34 SSH/import HTTP/PTY checks and detached HTTP queue mount/list checks. All eight npm platform binaries match the native manifest. Native and npm `latest` read back as 0.21.1. [Release and manifest](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.21.1).

The public native macOS binary also passed queue, job and worker reads through the existing development mount, without mutations. Staging API acceptance is recorded in [#274](https://github.com/dreamlake-ai/dreamlake-workspace/issues/274#issuecomment-5677911911); production CLI/UI and Ge testing remain separate. [Delivery note](dev-notes-queue-mount-release.md).

## Unreleased

- Guarded npm staging records child return separately from unresolved registry readback, with bounded read-only visibility checks and allowlisted diagnostics. No automatic upload retry or channel change. [Evidence and limits](dev-notes-npm-publication.md).

- Require every npm platform tarball to match generated package bytes before publishing the wrapper; verify the wrapper before promoting native pointers. Delayed registry visibility retries within a bounded window and fails closed. No published versions or channels change with this source fix.

- Record independent closure of the literal OTP/pass/SSH apply criteria from combined scoped receipts and tests; source progress56/72. No runtime or package release. [Criterion matrix and limits](/dev/notes/vault-otp-source-audit).

- Add five runnable synthetic OTP import checks against published Python0.16.1 over real loopback HTTP: per-entry source changes, dropped-response uncertainty and conflict redaction. No runtime change or broad OTP/SSH completion claim. [Evidence matrix](/dev/notes/vault-otp-source-audit).

- Add synthetic OTP import regressions for a later source changing during an earlier upload. Both content replacement and symlink swaps stop dispatch while preserving completed entries. No runtime change or new deployment; [audit and recovery boundaries](/dev/notes/vault-otp-source-audit).

- **2026-09-15:** CLI **0.20.1** and Python **0.16.1** are published with `keep_alive_s = -1` for enrolled user-systemd hosts. Owned bos14 acceptance passed with unchanged process IDs and zero restarts after Python **324.72s** and CLI **302.83s** idle windows. Existing hosts can use the paired repair commands; preserve the original request ID when reconciling an uncertain response. [Publication and live evidence](https://github.com/dreamlake-ai/dreamlake-workspace/pull/520). Reboot survival and completed hosted private execution remain separate open acceptance checks.

## 0.20.2 — published native transport fix

CLI **0.20.2** disables pooled connection reuse in the native Vault transport so dropped PUT/DELETE responses remain available for explicit reconciliation instead of hidden transport retries. Fresh public native and npm installations passed all **34 HTTP/PTY import checks**; nine compiled transport checks also passed. The release preserves concurrent newer package channels; use an exact version when selecting this patch. [Publication receipt542](https://github.com/dreamlake-ai/dreamlake-workspace/pull/542) · [Audit and recovery limits](/dev/notes/vault-native-transport).

## 0.21.0 — superseded by 0.21.1

Introduced `dreamlake queues mount`, `mounts`, `inspect`, `list`, `jobs`, `workers`, `token` and `unmount`, with explicit namespaces, hidden token input and Vault storage. Native artifacts and npm packages were uploaded, but this pinned source predates the Vault transport fix in 0.20.2. Native channel promotion was held. Use the combined 0.21.1 release to retain the Vault fix. Existing 0.21.0 artifacts remain unchanged.

[Queue commands](queues.md) · [Validation and publication history](dev-notes-queue-mount-release.md).

## 0.20.1 — 2026-09-15

- Keep enrolled user-systemd hosts available while idle by explicitly setting `keep_alive_s = -1`. Existing hosts require re-enrollment with this fix. Paired CLI/Python bootstrap tests parse the generated TOML and verify re-enrollment repairs the old configuration. Published in [v0.20.1](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.20.1); hosted acceptance is tracked separately.

CLI source suite: 1,019 passed; typecheck and 33-page docs build passed. All eight platform binaries built. A fresh copied macOS ARM64 binary passed real HTTP enrollment with the unchanged portable bootstrap over a synthetic SSH wrapper; parsed configuration has keep_alive_s=-1. This published patch was based on the previous tag plus the reviewed host fix; unrelated Notes changes on main were excluded.

## 0.20.0 — 2026-09-15

Adds private repository setup with explicit selected credential mappings and authenticated capability discovery, paired with Python 0.16.0. Published to native downloads and npm from reviewed source `f34ca03`. All eight native downloads and npm platform binaries match the release manifest; the public npm wrapper matches reviewed source bytes.

- `dreamlake run --setup setup.json --allow-vault-delivery` submits a pinned public repository, uv-lock dependencies and explicitly selected env/file mappings to an enrolled host. The metadata file is explicitly selected and bounded; it contains no secret values. Unknown submission outcomes reuse the same request ID and payload.
- `dreamlake runs capabilities <namespace> --json` reports authenticated server support and limits. Host readiness is verified separately at submission.
- Existing password verification/reservation and Task commands remain included. This release does not implement remote password mutation or enable backend private execution.

[Paired CLI/Python examples](runs.md) cover submission, discovery, status and cancellation. Private production activation requires the reviewed worker termination fix and fresh acceptance. Validation: 1,019 CLI tests, typecheck and the 33-page documentation build passed. All eight platform binaries built with embedded WASM checks; the native binary reports 0.20.0 with dependencies detached. A fresh isolated registry installation passed the installed binary hash, version and capability-help checks. Public native latest and npm latest/next resolve to 0.20.0. [Release and manifest](https://github.com/dreamlake-ai/dreamlake-cli/releases/tag/v0.20.0).

## 0.19.1 — 2026-09-14

**Published to native downloads.** All eight platform binaries passed public
checksum and size verification. At this historical release checkpoint native `latest` was 0.19.1. npm accepted the
packages, but macOS arm64 was still processing, so npm `latest` remained
at 0.19.0. Version 0.20.0 above is now published and verified on both channels.

- Task commands accept `DREAMLAKE_NAMESPACE` and `DREAMLAKE_PROJECT` session
  defaults. Explicit flags take precedence; namespace still falls back to login,
  and project is required when no default is set. No shared context is persisted.
- CLI docs link to the DreamLake and Lakeshore documentation tabs.

## Password APIs — release status reconciliation

CLI tag 0.19.1 includes password verification and reservation source. Python 0.16.0 is published to PyPI with matching public artifact hashes and a fresh registry version/API check; matching hosted password acceptance is still required. The old CLI 0.19.0 candidate in [PR #66](https://github.com/dreamlake-ai/dreamlake-cli/pull/66) is superseded and must not be republished.

`vault password-rotation reserve|show|read|start|cancel|confirm` has paired Python methods. Private metadata inputs and strict response validation keep ordinary operation output free of passwords; selected recovery reads are explicit. Real HTTP/native Mongo cross-client target/jump metadata flows passed. Requires backend #370; remote mutation and rollback resolution remain unfinished. [Guide](vault-passwords.md#password-reservation-and-recovery).

### Password-only verification

`vault verify-password` and Python `verify_host_password` verify one saved password with isolated SSH and private askpass IPC. Candidate native/npm/Python real target/jump password success/denial checks passed with independent cleanup. Password rotation and fresh installed-client/hosted enrollment/KMS acceptance remain separate. [Guide](vault-passwords.md).

## 0.18.0 — 2026-09-13

Adds `vault rotate-key` preparation, pinned API requests, isolated SSH transport and recoverable phase journals. Candidate CLI/Python target and jump rotation passed real SSH acceptance with independent cleanup. CLI 0.18.0 is published to npm and native downloads, paired with Python 0.15.0. Published CLI 0.18.0/Python 0.15.0 hosted staging acceptance passed four target/jump rotations and committed-response-loss recovery, followed by verified owned cleanup ([examples #34](https://github.com/dreamlake-ai/lakeshore-examples/pull/34)). Production acceptance remains separate. The frozen release excludes the password-only verification changes above. [Development evidence](/dev/plans/host-key-rotation).

Quoted target and jump SSH arguments beginning with `-p` are preserved rather than interpreted as the vault prefix.

## 0.17.0 — 2026-09-13

**Published to npm and native downloads.** Paired Python 0.14.0 is published. All eight public native artifacts and all nine public npm tarballs match the frozen reviewed release. A fresh registry installation with scripts disabled reports 0.17.0.

- Personal owners can inspect trusted prefix KMS policies, preview retained records,
  activate empty prefixes, and explicitly start/resume populated-prefix migrations.
  Immutable request IDs recover uncertain outcomes; explicit prefixes are checked
  before resuming. The SDK never prompts or advances migration in the background.
- Conditional host-binding replacement and owner-only operation recovery retain
  both credential identities until explicit cleanup. This metadata API does not
  install or revoke remote SSH keys; remote rotation candidates are excluded.

Migration requires backend [#359](https://github.com/dreamlake-ai/dreamlake-workspace/pull/359).
The operator migration flag defaults to false and must remain disabled until all
writers enforce policy epochs. Installing this package does not enable migration,
configure customer grants, or prove hosted acceptance. [Paired KMS guide](vault-kms.md).

## 0.16.0 — 2026-09-13

**Published to npm and native downloads.** Paired Python release: 0.13.0. The matching
backend is required; package validation does not establish hosted deployment.

- HOTP import defaults inactive. Explicit counter ownership, encrypted atomic
  issuance and a private immutable request file support safe retries; source pass
  registrations are never modified. See [Vault operations](vault-operations.md).
- Metadata listing follows bounded pages; explicit `--limit`/`--cursor` supports
  one-page consumers. Retired inclusion remains owner-only.
- The npm launcher preserves explicitly selected target/jump password descriptors
  (private files/real pipes, maximum descriptor 1024), including its permission
  repair retry, while closing unrelated descriptor gaps.
- `vault unbind` releases an exact personal retention reference while preserving
  active secrets and making no claim of remote SSH revocation.

Source: [HOTP #50](https://github.com/dreamlake-ai/dreamlake-cli/pull/50),
[pagination #52](https://github.com/dreamlake-ai/dreamlake-cli/pull/52), and
[unbind #49](https://github.com/dreamlake-ai/dreamlake-cli/pull/49), plus
[descriptor fix #53](https://github.com/dreamlake-ai/dreamlake-cli/pull/53).
A separately copied candidate launcher was verified against published native 0.15
and staging, with target/jump saving and cleanup. That is not publication evidence
for this 0.16 package. All eight published native artifacts match the reviewed manifest;
a fresh npm installation reports 0.16.0.

## 0.15.0 — 2026-09-13

Selected post-enrollment SSH password/private-key saving and account-owned host
bindings are included. Target and jump credentials are selected separately;
interactive saving defaults to N, quiet grants no consent, and automation uses
explicit selections and protected descriptors. Enrollment success survives a
saving failure; uncertain writes and saved-but-unbound entries retain recovery
metadata. [CLI/Python examples](host-enrollment.md#save-selected-credentials-after-enrollment).

Paired Python release: 0.12.0. Source implementation is merged in
[CLI #47](https://github.com/dreamlake-ai/dreamlake-cli/pull/47),
[Python #34](https://github.com/fortyfive-labs/dreamlake/pull/34), and
[backend #336](https://github.com/dreamlake-ai/dreamlake-workspace/pull/336).
CLI publication is verified on npm and native downloads; all platform binaries match the release manifest and latest points to 0.15.0. Python 0.12.0 is published on PyPI/GitHub. Hosted acceptance remains pending. Earlier bos14 checks used a
synthetic source snapshot, not these release artifacts. See the [Vault Dev Note](https://docs.dreamlake.ai/dev/notes/vault-runtime/).

## Unreleased — populated-prefix KMS migration

`vault kms migrate`, bounded `resume`, and shared `status` have paired Python methods. Preview includes retained entry/write/HOTP receipt counts. Metadata output strips ciphertext/KMS identifiers and uncertainty retains the original operation ID. Source candidate only; package and hosted verification are pending.

Password reservation candidates also acknowledge retained-record schema 2 on KMS migration start/resume and preserve separate password-snapshot/total counts in metadata. Compatible backend deployment must precede these commands. Source validation: target/jump cross-client reservation and snapshot reads over real loopback HTTP/Mongo; published CLI 0.17/Python 0.14–0.15 are safely gated, new clients advance the same migration. No remote password changes are included.
