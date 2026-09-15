# npm publication gate

## 2026-09-15 — processing is not publication

During CLI 0.21.2 publication, npm accepted the Windows arm64 upload before its tarball became readable. Publishing platform packages first did not prevent the wrapper's `latest` tag from moving early. The release was completed only after all nine packages matched the reviewed bytes and the supported publisher finished native readback.

The proposed publisher gate derives required platforms from the generated wrapper's exact optional dependencies. It reads each tarball from npm, checks SHA-512 registry integrity and every generated file's SHA-256, and only then publishes the wrapper. It also verifies the wrapper before moving native pointers. Unavailable metadata/downloads retry up to 30 attempts with 30-second pauses; a byte or package mismatch fails immediately. An exhausted window stops publication. Resume through the existing publisher once processing completes; do not bypass the gate.

## How to test

```shell
python3 scripts/test-npm-publication.py
```

The offline tests exercise a delayed registry with real tarball verification, corrupted bytes, retry exhaustion and the actual shell publisher's ordering. They assert that an incomplete platform gate prevents both wrapper publication and the pointer step. No npm publication, credentials, remote mutation or install occurs.

For an existing generated release, this read-only command independently checks its platform packages:

```shell
python3 scripts/verify-npm-publication.py release/0.21.2/npm
python3 scripts/verify-npm-publication.py release/0.21.2/npm --wrapper
```

The release must already have been built with the reviewed source. Temporary downloads are cleaned automatically. This source change does not publish another release.

## 2026-09-15 — guarded publisher outcome evidence

The separate frozen-candidate publisher now distinguishes `create_returned` from
`readback_unresolved`. npm exit0 does not establish publication. Its single upload
is followed by at most six read-only visibility checks; only authoritative
absence permits another check. Errors and mismatched bytes stop immediately.
No uncertain upload is automatically retried, and no later package advances
until exact byte readback succeeds. This differs from the older shell publisher
window described above.

Sanitized diagnostics retain only PUT HTTP status numbers and known npm error
codes. Raw child output and credentials never enter the journal. The observed
0.22.0 Darwin arm64 attempt stays unresolved; its original diagnostics were not
captured, so a particular HTTP response is not claimed. This source change makes
no publication or channel move.

```shell
python3 -m unittest discover -s scripts/release_guard -p 'test_*.py' -v
```

Local tests cover delayed exact visibility after one upload, exhausted absence,
error/mismatch stops, no subsequent package upload, and diagnostic redaction.

## 2026-09-15 — observed HTTP 202 and scanning

npm's [publish-time scanning guidance](https://github.blog/changelog/2026-07-28-npm-publish-time-malware-scanning-and-dual-use-metadata/) describes a typical five-minute delay, sometimes fifteen minutes or more; this is not an SLA. A scan can result in availability, manual review or blocking. The 0.22.0 Linux arm64 attempt now has an actual recorded PUT 202, followed by exhausted bounded visibility checks. Unlike the original Darwin arm64 attempt, this response status was captured. The original uncertainty and later evidence remain separate.

HTTP 202 indicates accepted processing, not failure or proof of installability. The publisher stopped before the next package. Preserve the journal and reconcile read-only until exact bytes appear; no automatic re-upload or latest promotion follows a timeout. Use npm for metadata and the Python verifier for frozen byte checks:

```shell
npm view @dreamlake/dreamlake-cli-linux-arm64@0.22.0 version dist.integrity --registry https://registry.npmjs.org --json
python3 scripts/release_guard/publish.py reconcile --target npm --root /absolute/frozen-candidate-checkout
```

A 404 or elapsed waiting window does not prove rejection. Manual-review or blocked states may require maintainer follow-up. The documented [staged queue/history](https://github.blog/changelog/2026-09-03-multiple-trusted-publishing-configurations-for-npm/) is not evidence that this direct publish was staged. This note adds an operator procedure; it performs no publication and changes no channel.
