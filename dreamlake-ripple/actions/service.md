# Report an enrolled host to DreamLake as a service

Run Ripple as a service that sends CPU and memory samples for one enrolled
host: a systemd system service on Linux (as root) or a per-user launchd
agent on macOS (as the user, never root). Facts and file lists:
[reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#report-an-enrolled-host-to-dreamlake).

## Before you start

- The host is already enrolled in DreamLake
  ([reference](../reference/docs-lakeshore-hosts-enroll.md)); enrolling is
  not part of this skill.
- The user has, **from the DreamLake operator**, the enrollment's machine ID
  (`host-…`) and a machine token issued for that ID. If either is missing,
  stop and tell the user to ask the operator. There is no self-service
  token, nothing here creates one, and a user sign-in token does not work.
- The binary is installed (the `install` action): Linux `/usr/local/bin`,
  macOS `~/.local/bin`.
- Say which user you act as before running anything: root on Linux, the
  user to be measured on macOS.
- macOS: the agent runs only while that user is logged in. Tell the user;
  do not suggest auto-login or other login changes to work around it.

## Steps

1. Have the user put the token in a `0600` file themselves; it must not pass
   through a command line, shell history or this conversation:

   ```bash
   TOKEN_FILE=/root/ripple-token        # Linux; macOS: TOKEN_FILE="$HOME/ripple-token"
   (umask 077; cat > "$TOKEN_FILE")     # user pastes, then Ctrl-D
   ```

2. Validate (sends nothing). Expect `ok: … delivery_mode=staged token_file=readable`:

   ```bash
   MACHINE_ID=host-…                    # from the operator
   ripple check --delivery-mode=staged \
     --url=https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
     --machine-id="$MACHINE_ID" --token-file="$TOKEN_FILE"
   ```

3. Fetch the setup script of the **same version** as the installed binary,
   verify it, and preview:

   ```bash
   RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
   V=$(ripple version)
   # Linux
   curl -fsSLO "$RIPPLE_BASE/$V/setup-systemd.sh"
   curl -fsSL "$RIPPLE_BASE/$V/setup-systemd.sh.sha256" | sha256sum -c -
   SETUP=setup-systemd.sh
   # macOS
   curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh"
   curl -fsSLO "$RIPPLE_BASE/$V/setup-launchd.sh.sha256"
   shasum -a 256 -c setup-launchd.sh.sha256
   SETUP=setup-launchd.sh

   bash "$SETUP" --machine-id "$MACHINE_ID" \
     --url https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
     --token-file "$TOKEN_FILE" --delivery-mode staged --dry-run
   ```

   Show the user the `--- would …` plan, then run the same command without
   `--dry-run`. On Linux the preview does not check the token file's owner
   or mode, so the real run can still refuse.

4. Read back:

   ```bash
   # Linux
   systemctl is-active ripple.service
   journalctl -u ripple.service -n 50 --no-pager
   ripple status --spool-dir=/var/lib/lakeshore-host-metrics
   # macOS
   launchctl print "gui/$(id -u)/ai.dreamlake.ripple" | grep state
   tail -n 50 "$HOME/Library/Logs/ripple/ripple.log"
   ripple status --spool-dir "$HOME/Library/Application Support/ripple/spool"
   ```

   A running service only proves the process runs. Report what the log and
   the spool show; claim readings reached DreamLake only if the user (or
   `dl hosts metrics` from `dreamlake-lakeshore`) confirmed it.

5. If the user agrees, delete `$TOKEN_FILE`; the service keeps its own copy.

## Upgrade or rotate

- Upgrade: the `install` action with the new version, then restart: Linux
  rerun step 3 with that version's script; macOS
  `launchctl kickstart -k "gui/$(id -u)/ai.dreamlake.ripple"`.
- Rotate: the user gets a new token from the operator; repeat steps 1 and 3.

## Automatic updates (opt-in)

Only when the user explicitly asks; pinned manual upgrades above stay the
default. What opting in changes, which copy of the binary the service runs,
and when an update happens:
[reference](../reference/docs-lakeshore-hosts-metrics.md#automatic-updates).

1. Opt the host in. `ripple version` must be a stable v0.5.0 or later; an
   older binary has no updater, so upgrade it by hand first (the `install`
   action). Rerun step 3 with `--auto-update` added, as the same user (root
   on Linux, the measured user on macOS), `--dry-run` first. If the user no
   longer has the token file, pass the service's own copy as `--token-file`
   ([reference](../reference/docs-lakeshore-hosts-metrics.md#automatic-updates));
   never ask the operator for a new token just to opt in. To opt out, rerun
   it without `--auto-update`.
2. Set the target only if the user owns the Host and names the version.
   Use a version published on the release base (check
   `$RIPPLE_BASE/<version>/VERSION`), never `latest`, and only the one
   enrollment the user named: the GET/PUT in
   [Set the upgrade target](../reference/docs-lakeshore-hosts-metrics.md#set-the-upgrade-target),
   with `DREAMLAKE_TOKEN=$(dl auth token)` (never print it). Host and
   enrollment IDs: ask the user, or list them with the `dreamlake-lakeshore`
   skill. Read the target back with the GET. Clearing it
   (`{"targetVersion": null}`) stops further updates; it never rolls back.
3. Verify the **running process**, not the files:
   [Check which binary runs](../reference/docs-lakeshore-hosts-metrics.md#check-which-binary-runs).
   An update is proven only when the running process reports the new
   version; until then report what `ripple status --process` shows.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `401` / `invalid_machine_token` in the log | Token wrong, revoked, or for another machine ID | Ask the operator; never try other IDs or tokens |
| `--token-file must be an absolute path` | Relative path | Use an absolute path |
| `must not be accessible by group or others`, `must be owned by root` (Linux) or `owned by you` (macOS) | Token file mode or owner | Fix the owner, `chmod 600`, rerun |
| macOS: refuses to run as root | Agent is per-user | Rerun as the user to be measured |
| Refuses: file not created by this script, account or directory exists | Something else owns those paths | Stop and show the user; never delete or overwrite to proceed |
| Linux: refuses while `lakeshore-host-metrics.service` is enabled | Pre-rename unit in use | Stop; pass `--replace-legacy-unit` (see `--help`) only with explicit approval |
| `systemctl not found` | Not a systemd host, or a container | Stop; a container does not measure the host |
| macOS: readings stop overnight or after logout | Agent runs only while logged in | Expected; report it, no workaround |
| Backlog in `ripple status` keeps growing | Delivery failing | Read the log; report the error text |
| `--auto-update` refused: staged delivery, `https://` or a v0.5.0+ binary needed | Opt-in prerequisites | Meet them, then rerun setup (still as root on Linux) |
| `auto-update refuses to run as root` | `ripple run` started as root by hand | Use the setup script's service; never run `ripple run` as root or with `sudo` |
| `executable … is not owned by this account` | Service points at a root-owned binary | Rerun setup with `--auto-update`; never `chown` or loosen `/usr/local/bin` |
| Target GET/PUT: `403 forbidden` | No `lakeshore:use` in that namespace | Stop; tell the user. Do not switch namespaces or accounts |
| Target PUT: `404 host_not_found` | The user is not the Host's owner, or wrong IDs | Stop; only the owner sets it. Never try other hosts |
| Target PUT: `400 invalid_target_version` | Not a stable `vX.Y.Z` | Use a published stable version, never `latest` |
| Opted in, target set, nothing updates | Target not newer, not published, or set on another enrollment | Read back the target and `ripple status --process` (`last_result`); do not force an update |
| `auto-update failed …` in the log | Download or verification failed; still on the old version | Report the logged error; it retries by itself |
