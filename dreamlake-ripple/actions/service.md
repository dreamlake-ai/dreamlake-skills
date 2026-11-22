# Report an enrolled host to DreamLake as a service

Run Ripple as a system service that sends CPU and memory samples for one
enrolled host. Today the released service setup is systemd on Linux; check the
service-manager row of the support table in
[reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#ripple-collector)
before anything else. If the user's platform has no released service setup,
stop and say so.

## Before you start

- The host is already enrolled in DreamLake
  ([reference/docs-lakeshore-hosts-enroll.md](../reference/docs-lakeshore-hosts-enroll.md)).
  Enrolling is not part of this skill.
- The user has, **from the DreamLake operator**, the enrollment's machine ID
  (`host-…`) and a machine token issued for that ID. If either is missing,
  stop and tell the user to ask the operator; there is no self-service token
  and no command in this skill creates one. A user sign-in token does not
  work.
- The binary is installed system-wide (`/usr/local/bin/ripple`) by the
  `install` action of this skill.
- You are acting as root on the host to be measured (systemd system scope).
  Say so to the user before running anything as root.

## Steps (Linux, systemd)

1. Put the token in a root-owned `0600` file without it passing through the
   command line, shell history or this conversation. Ask the user to paste it
   into the terminal themselves:

   ```bash
   install -m 0600 /dev/stdin /root/ripple-token   # user pastes, then Ctrl-D
   ```

2. Validate the configuration. This sends nothing:

   ```bash
   ripple check --delivery-mode=staged \
     --url=https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
     --machine-id="$MACHINE_ID" --token-file=/root/ripple-token \
     --spool-dir=/var/lib/lakeshore-host-metrics
   ```

   Expect `ok: endpoint=… machine_id=… delivery_mode=staged token_file=readable`.

3. Fetch the setup script of the **same version** as the installed binary,
   verify it, preview, then apply:

   ```bash
   RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
   V=$(ripple version)
   curl -fsSLo setup-systemd.sh "$RIPPLE_BASE/$V/setup-systemd.sh"
   curl -fsSL "$RIPPLE_BASE/$V/setup-systemd.sh.sha256" | sha256sum -c -
   bash setup-systemd.sh --machine-id "$MACHINE_ID" \
     --url https://api.dreamlake.ai/host-metrics/ripple/v1/samples \
     --token-file /root/ripple-token --delivery-mode staged --dry-run
   ```

   Show the user the `--- would …` lines, then run the same command without
   `--dry-run`. The preview does not check the token file's owner or mode;
   the real run can still refuse. What the script writes, refuses and
   reruns: [reference](../reference/docs-lakeshore-hosts-metrics.md#run-as-a-systemd-service-linux).

4. Read back:

   ```bash
   systemctl is-active ripple.service
   journalctl -u ripple.service -n 50 --no-pager
   ripple status --spool-dir=/var/lib/lakeshore-host-metrics
   ```

   `active` means the process runs. Delivery is shown only by the journal and
   the spool: samples stay in the spool until the API confirms they are
   archived (meaning of `202`/`204`:
   [reference](../reference/docs-lakeshore-hosts-metrics.md#report-an-enrolled-host-to-dreamlake)).
   Report what you saw; do not claim the readings appear in DreamLake unless
   the user (or `dl hosts metrics` from the `dreamlake-lakeshore` skill)
   confirmed it.

5. Delete the source token file once setup succeeded if the user agrees; the
   service uses its own copy.

## Upgrade or rotate

- Upgrade: the `install` action with the new version, then rerun step 3 with
  that version's `setup-systemd.sh`.
- Rotate the token: the user gets a new token from the operator; repeat
  steps 1 and 3. Reruns are idempotent.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `401` / `invalid_machine_token` in the journal | Token wrong, revoked, or not issued for this machine ID | Ask the operator; do not try other IDs or tokens |
| Samples refused for the machine ID | Label differs from the enrollment the token is bound to | Use the exact `host-…` ID from the operator |
| `--token-file must be an absolute path` | Relative path | Use `/root/ripple-token` |
| `must not be accessible by group or others` or `must be owned by root` | Token file mode or owner | `chown root: …; chmod 600 …` and rerun |
| Refuses: file lacks the marker, account or state directory exists | Something else owns those paths | Stop and show the user; never delete or overwrite them to proceed |
| Refuses while `lakeshore-host-metrics.service` is enabled | Pre-rename unit still in use | Stop and show the user; pass `--replace-legacy-unit` (listed by `bash setup-systemd.sh --help`) only with their explicit approval |
| `systemctl not found` | Not a systemd host, or inside a container | Stop; a container does not measure the host |
| Backlog in `ripple status` keeps growing | Delivery failing | Read the journal; report the error text |
