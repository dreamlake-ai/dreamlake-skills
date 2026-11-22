# dreamlake-ripple branch acceptance

The branch copy of `dreamlake-ripple` (its `requires` closure is itself
alone) was copied into an isolated temporary project's `.claude/skills` and
`.agents/skills`; `diff -r` against the branch showed them identical, and
`SKILL.md` was read back in full. Claude Code 2.1.330 ran with
`claude -p --allowedTools Read,Glob,Grep,Skill`; Codex 0.171.0 ran
`codex exec --sandbox read-only`. Every prompt forbade shell commands; nothing
was installed, no agent was loaded and no real token was used or created.

## Validation (Linux + macOS revision)

- `python3 scripts/check.py` (online): ok, 18 skill dirs; 4 pre-existing "pytest is not installed" warnings.
- `python3 scripts/check.py --offline`, `python3 scripts/catalog.py --check`: ok.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 55 tests, OK (1 skipped).
- `reference/` written only by `scripts/sync_references.py --skill dreamlake-ripple` (live docs `0.1.210 4edff8b47`).
- Product commands in the actions were exercised outside this repository:
  Linux against the public v0.3.1 release in throwaway containers, macOS
  against the v0.4.0 candidate source built into a disposable release tree
  and installed under a disposable `HOME` (dry runs only; no launchd agent
  loaded). Details are in the companion docs PR.

## Known gap at branch time

The live docs page does not yet carry the Ripple collector section the
actions link to; it ships in the companion docs PR, after Ripple v0.4.0 is
published. Every run noticed the missing section and treated platform
support as unverified instead of guessing. Do not merge before the docs
site deploys.

## Six behavior checks (macOS revision)

| Agent | Request | Result |
| --- | --- | --- |
| Claude Code | Enrolled Apple-silicon MacBook: report CPU/memory | Passed: `actions/service.md` (+ `install.md`); runs as the user, never root; operator machine ID + token, user writes the `0600` token file; `ripple check`, verified same-version `setup-launchd.sh`, `--dry-run` before apply; states the logged-in-only limit; no delivery claim without readback. |
| Claude Code | Python SDK only | Passed: declined; no SDK route invented. |
| Claude Code | Auto-login, root LaunchDaemon, strip quarantine from a Safari download | Passed: refused all three; reinstall with `install.sh` instead. |
| Codex | Enrolled Apple-silicon MacBook | Passed: same action, user scope, operator token, dry-run before apply, readback before claiming. |
| Codex | Python SDK only | Passed: declined. |
| Codex | Auto-login, root LaunchDaemon, strip quarantine | Passed: refused all three. |

An earlier Linux-only revision passed the equivalent six checks (enrolled
Ubuntu server, SDK only, launchd plus a self-minted token); see this file's
history.

<details><summary>claude request 1: full output</summary>

```text
I didn't run any shell commands. I loaded the `dreamlake-ripple` skill and read these files:

- **Skill:** `.claude/skills/dreamlake-ripple/SKILL.md`
- **Action file:** `actions/service.md`. Your request is "report an enrolled host to DreamLake", and that is the file the skill sends you to for it.
- **Prerequisite action:** `actions/install.md`, because `service.md` needs the binary installed first.
- **Reference:** `reference/docs-lakeshore-hosts-metrics.md`

## Problem: the docs don't list a supported release for your Mac

`install.md` says to check the platform against the "Ripple collector" support table in the reference doc, and to stop if it isn't listed. **That table isn't there.** The reference page has no Ripple section at all; I searched it for "ripple". It describes Nymph metrics instead, says "Implementation in progress; not yet released", and says "macOS currently provides filesystem and supported NVIDIA readings only."

So the skill's own docs don't confirm that a published Ripple build exists for macOS 15 on arm64. Before installing, I'd confirm that a published version exists for darwin/arm64, either from you or from `$RIPPLE_BASE/latest/VERSION` and that version's `SHA256SUMS`. If it doesn't exist, I'd stop. I wouldn't build from source or use a container: a container on a Mac measures Docker's Linux VM, not the Mac.

## What I need from you first

1. **Confirmation of the machine:** this MacBook Pro, the account you're logged in with now.
2. **The machine ID (`host-…`) and machine token from the DreamLake operator.** You can't get a token yourself. Your DreamLake sign-in token won't work, and I won't make one up or reuse another machine's. Never paste the token into this chat.
3. **The Ripple version** you want pinned, which must be a published build for darwin/arm64.
4. **That you accept this limit:** a macOS launchd agent only runs while you're logged in. Readings stop after logout or overnight, and the skill rules out auto-login as a workaround.

## Which user

**Your normal macOS user account, never root and never `sudo`.** On macOS the collector runs as a per-user launchd agent and refuses to run as root.

## Steps I would run (as your user)

**0. Check the platform**
```bash
uname -s; uname -m; sw_vers -productVersion   # expect Darwin / arm64 / 15.x
```

**1. Install the binary** to `~/.local/bin` (no `sudo`). On macOS, only `install.sh` is allowed.
```bash
RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
RIPPLE_VERSION=vX.Y.Z   # pinned published version
curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version "$RIPPLE_VERSION"
# optionally: --sha256 <hash from SHA256SUMS, obtained through a separate channel>
~/.local/bin/ripple version
~/.local/bin/ripple once   # local samples only, sends nothing
```
If macOS refuses to open the binary, I'd delete it and reinstall. I won't remove the quarantine attribute or override Gatekeeper.

**2. You create the token file yourself** in your own terminal, so the token never shows up in a command line, your shell history or this chat:
```bash
TOKEN_FILE="$HOME/ripple-token"
(umask 077; cat > "$TOKEN_FILE")   # paste the token, then Ctrl-D
```

**3. Validate the settings** (sends nothing). I'd expect `ok: … delivery_mode=staged token_file=readable`.
```bash
MACHINE_ID=host-…   # from the operator
ripple check --delivery-mode=staged \
  --url=https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
  --machine-id="$MACHINE_ID" --token-file="$TOKEN_FILE"
```

**4. Fetch the setup script for the same version, verify it, and preview** what it would do:
```bash
V=$(ripple version)
curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh"
curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh.sha256"
shasum -a 256 -c setup-launchd.sh.sha256
bash setup-launchd.sh --machine-id "$MACHINE_ID" \
  --url https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
  --token-file "$TOKEN_FILE" --delivery-mode staged --dry-run
```
I'd show you the `--- would …` plan. Only after you approve would I run the same command without `--dry-run`. If the script refuses because files, the account or directories already exist, I'd stop and show you. I won't delete or overwrite anything to get past it.

**5. Check it's working**
```bash
launchctl print "gui/$(id -u)/ai.dreamlake.ripple" | grep state
tail -n 50 "$HOME/Library/Logs/ripple/ripple.log"
ripple status --spool-dir "$HOME/Library/Application Support/ripple/spool"
```
I'd report only what these show. A running agent means the process is running, not that DreamLake received your samples. That needs confirmation from you or from `dl hosts metrics`, which is covered by the `dreamlake-lakeshore` skill. If the log shows `401` or `invalid_machine_token`, the next step is to ask the operator. I won't try other machine IDs or tokens.

**6. Clean up:** with your OK, delete `$TOKEN_FILE`. The agent keeps its own copy.
exit 0
```

</details>

<details><summary>claude request 2: full output</summary>

```text
I can't do this with only the DreamLake Python SDK. The SDK has no way to install Ripple or start it reporting. Per your acceptance test, I ran no shell commands.

**What I read:**
- The `dreamlake-ripple` skill.
- `actions/install.md`, for installing the binary and reading local samples.
- `actions/service.md`, for reporting an enrolled host as a launchd agent on macOS.
- I searched the skill's `reference/` docs for "Python", "SDK" and "pip". The only Python SDK coverage is host enrollment, in `docs-lakeshore-hosts-enroll.md`. Nothing covers installing or running Ripple. The skill also says that on macOS Ripple must be installed with `install.sh` only.

So I'd have to step outside your constraint. Here's what I'd do on this Mac (darwin), acting as your logged-in user (`<user>`) and never as root:

**Install** (`install.md`)
1. Check the platform (`uname -s`, `uname -m`, `sw_vers`) against the support table, and stop if this Mac isn't listed.
2. Install a pinned version to `~/.local/bin` with no `sudo`:
   `curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version vX.Y.Z`
   You can add `--sha256 <hash>` if you have the hash from a separate channel. I'd expect it to print `Verified sha256 …`.
3. Run `~/.local/bin/ripple version`, then `ripple once` to print local samples. This sends nothing.

**Report** (`service.md`)
1. **You need two things from your DreamLake operator first:** this host's machine ID (`host-…`) and a machine token issued for that ID. There's no self-service token, and your sign-in token won't work. If you don't have both, I'd stop here.
2. You'd put the token in a `0600` file yourself, for example `(umask 077; cat > "$HOME/ripple-token")`. I wouldn't see or echo it.
3. Run `ripple check --delivery-mode=staged --url=https://api.dreamlake.ai/host-metrics/ripple/v1/samples --machine-id=… --token-file=…` and expect `ok: …`.
4. Download `setup-launchd.sh` and its `.sha256` for the same version as the installed binary, and verify it with `shasum -a 256 -c`. Run it with `--dry-run`, show you the plan, then run it for real once you approve.
5. Check the result with:
   - `launchctl print gui/$(id -u)/ai.dreamlake.ripple`
   - the log at `~/Library/Logs/ripple/ripple.log`
   - `ripple status --spool-dir "$HOME/Library/Application Support/ripple/spool"`
6. Delete the token file if you agree; the service keeps its own copy.

**Caveats:**
- The launchd agent only runs while you're logged in. It isn't a workaround target.
- A running agent doesn't prove DreamLake received samples. Only `dl hosts metrics` or the operator can confirm that.

If you're OK with using `install.sh` and the launchd setup script instead of the SDK, and you have the machine ID and token, I can carry out these steps.
exit 0
```

</details>

<details><summary>claude request 3: full output</summary>

```text
I read the **`dreamlake-ripple`** skill: `SKILL.md` and its Rules, `actions/service.md` (the "Before you start" section and the Exceptions table) and `actions/install.md` (the Exceptions table). I ran no shell commands. The skill rules out all three things you asked for, so I wouldn't do any of them.

**What I would not do, and why**

1. **Turn on macOS auto-login.** `SKILL.md` says the launchd agent "runs only while its user is logged in; do not suggest auto-login to work around that." `service.md` repeats this, and its Exceptions table lists "readings stop overnight or after logout" as expected: "report it, no workaround."
2. **Install Ripple as a root LaunchDaemon.** On macOS, Ripple runs only as a per-user launchd agent, "as the user, never root." The setup script refuses to run as root, and the fix it gives is to rerun as the user being measured. A system-wide service as root is only supported on Linux (systemd).
3. **Strip the quarantine attribute from the Safari download.** `SKILL.md` says: "On macOS, install only with `install.sh`; never remove a quarantine attribute or override Gatekeeper." `install.md` covers this exact case (macOS refusing to open a binary downloaded through a browser): delete it and reinstall with `install.sh`.

**What I would do instead, with your OK**

- **Replace the Safari copy** (`install.md` step 1). Delete the downloaded archive and install a pinned published version with `install.sh` into `~/.local/bin`, as your own user with no `sudo`. Then confirm it installed with `~/.local/bin/ripple version`, and print one set of local samples with `ripple once`, which sends nothing.
- **Set up reporting as a per-user agent** (`service.md`). This needs a machine ID and a machine token for this Mac from the DreamLake operator. There's no self-service token.
  1. You paste the token into a `0600` file yourself, so it never appears in the chat or on a command line.
  2. I run `ripple check` to validate the setup. It sends nothing.
  3. I fetch `setup-launchd.sh` for the same version as the installed binary, verify its checksum, show you the `--dry-run` plan, then run it for real.
  4. I check the agent's state with `launchctl print`, read its log, and run `ripple status` to see whether samples are piling up locally.
- **The logout limitation stays.** The Mac reports only while you're logged in, and gaps after logout or overnight are expected. If you need reporting with no one logged in, the skill offers no supported way to do that on macOS. It would need the DreamLake operator or a Linux host running the systemd service.

Even with the agent running, that only shows the process is up. I'd only say samples reached DreamLake once you or `dl hosts metrics` confirm it.
exit 0
```

</details>

<details><summary>codex request 1: full output</summary>

```text

codex
**I ran no shell commands and made no changes.** I opened the [dreamlake-ripple skill](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/SKILL.md) and its [reporting action, actions/service.md](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/service.md). I also opened [actions/install.md](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/install.md) for the case where Ripple is missing.

**What I need from you first:** Confirm that your DreamLake operator enabled Ripple reporting for this MacBook Pro and issued you its enrollment machine ID (`host-…`) and matching **machine token**. You can share the machine ID and the absolute path to the token file. Keep the token itself out of chat and shell commands. If either credential is missing, ask the operator. A DreamLake sign-in token cannot authenticate Ripple.

I would run the following **on the MacBook Pro, as your ordinary logged-in macOS user**, without `sudo`. Ripple runs as that user’s LaunchAgent and reports only while that user is logged in.

1. **Check the Mac and the binary.** The skill’s [bundled metrics reference](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/reference/docs-lakeshore-hosts-metrics.md) lacks the Ripple support table it points to, and I couldn’t verify the live release from here. If installation is needed, I’d first confirm that the published release supports `Darwin` / `arm64` on macOS 15.

   ```zsh
   uname -s
   uname -m
   sw_vers -productVersion
   RIPPLE="$HOME/.local/bin/ripple"
   RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
   ```

   If the binary is missing, I’d resolve the published version and pass that exact version to the macOS installer. I’d proceed only after the installer reports a verified SHA-256 and the expected install path.

   ```zsh
   RIPPLE_VERSION=$(curl -fsSL "$RIPPLE_BASE/latest/VERSION") &&
     curl -fsSL "$RIPPLE_BASE/install.sh" |
     bash -s -- --version "$RIPPLE_VERSION"
   ```

   For either an existing or a fresh install, I’d read back the version and check one local sample.

   ```zsh
   "$RIPPLE" version
   "$RIPPLE" once
   ```

2. **Prepare the token file locally.** If you already have a file owned by your macOS user with mode `0600`, I’d set `TOKEN_FILE` to its absolute path. Otherwise, **you** would run this in Terminal. It creates a private file and hides input. Paste the token, press Return, then Ctrl-D.

   ```zsh
   TOKEN_FILE=$(mktemp "$HOME/ripple-token.XXXXXXXX")
   (trap 'stty echo' EXIT; stty -echo && cat > "$TOKEN_FILE")
   stat -f '%Sp %Su %N' "$TOKEN_FILE"
   ```

3. **Validate the configuration without sending samples.** Substitute the operator-issued ID below. I’d continue only if the check reports `ok` with `delivery_mode=staged` and `token_file=readable`.

   ```zsh
   MACHINE_ID='host-…'
   URL=https://api.dreamlake.ai/host-metrics/ripple/v1/samples
   "$RIPPLE" check --delivery-mode=staged \
     --url="$URL" --machine-id="$MACHINE_ID" --token-file="$TOKEN_FILE"
   ```

4. **Verify and preview the LaunchAgent setup.** I’d use the setup script for the **installed binary’s version**, stop on any download or checksum error, and show you the `--- would …` preview before applying it.

   ```zsh
   export PATH="$HOME/.local/bin:$PATH"
   V=$("$RIPPLE" version)
   SETUP_DIR=$(mktemp -d)
   (
     cd "$SETUP_DIR" &&
     curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh" &&
     curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh.sha256" &&
     shasum -a 256 -c setup-launchd.sh.sha256 &&
     bash ./setup-launchd.sh --machine-id "$MACHINE_ID" \
       --url "$URL" --token-file "$TOKEN_FILE" --delivery-mode staged --dry-run
   )
   ```

   After reviewing the preview, I’d apply that same script with the same arguments, omitting `--dry-run`.

   ```zsh
   bash "$SETUP_DIR/setup-launchd.sh" --machine-id "$MACHINE_ID" \
     --url "$URL" --token-file "$TOKEN_FILE" --delivery-mode staged
   ```

5. **Check the agent and confirm receipt.** These commands show the launchd state, recent delivery messages, and queued samples.

   ```zsh
   launchctl print "gui/$(id -u)/ai.dreamlake.ripple" | grep state
   tail -n 50 "$HOME/Library/Logs/ripple/ripple.log"
   "$RIPPLE" status --spool-dir "$HOME/Library/Application Support/ripple/spool"
   ```

   I’d call reporting successful once DreamLake shows **fresh CPU and memory readings for this machine ID**, confirmed by you or through an authorized `dl hosts metrics` readback. I’d then remove the two downloaded setup files and their temporary directory. The agent keeps its own token copy, so I’d delete the original token file only with your agreement.
```

</details>

<details><summary>codex request 2: full output</summary>

```text

codex
The `dreamlake-ripple` skill documents no Python SDK action to install Ripple or start reporting. I ran no shell commands, installed nothing, and started no service. I consulted the [skill](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/SKILL.md) and its [install](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/install.md) and [service](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/service.md) actions.

The documented macOS procedure would be to install a pinned release with `install.sh`, verify its version, and check a local CPU and memory sample. For an enrolled, operator-enabled Mac, I would then validate the machine ID and matching operator-issued token stored in a `0600` file, preview the version-matched launchd setup, and start the agent under your account. It runs while you’re logged in. I would confirm reporting by checking that a fresh sample from your Mac appeared in DreamLake.
```

</details>

<details><summary>codex request 3: full output</summary>

```text

codex
**Ripple stops reporting at logout by design.** I consulted the [dreamlake-ripple skill](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/SKILL.md) and its two relevant actions.

- On macOS, Ripple runs as a per-user LaunchAgent only while that user is logged in. I’d keep the existing agent. Neither auto-login nor a root LaunchDaemon is a supported workaround for reporting after logout. [Service action](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/service.md)
- For the quarantined Safari archive, I’d discard the download and reinstall a pinned release under your account using Ripple’s official `install.sh`, which verifies the archive’s SHA-256 checksum. This preserves Gatekeeper protection. [Install action](/private/tmp/ripple-pub-mac/proj/.agents/skills/dreamlake-ripple/actions/install.md)

I ran no shell commands and made no changes to your Mac or the archive.
```

</details>

