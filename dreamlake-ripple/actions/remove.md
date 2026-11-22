# Stop reporting or remove Ripple

Stop the service, then remove only what the user asks for. What each
platform leaves behind is in
[reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#stop-or-remove).

These steps remove a collector set up by hand with the `service` action. For
one set up by `dl hosts enroll`, there is no operator token to revoke; use only
what the enrollment reference documents for turning it off, and say so if it
documents nothing for the case.

## Steps

1. Show the backlog first; deleting the spool loses samples the API has not
   acknowledged:

   ```bash
   ripple status --spool-dir=/var/lib/lakeshore-host-metrics                 # Linux
   ripple status --spool-dir "$HOME/Library/Application Support/ripple/spool" # macOS
   ```

2. Stop the service:

   ```bash
   # Linux (root)
   systemctl disable --now ripple.service
   systemctl is-active ripple.service          # inactive
   # macOS (as the user; setup-launchd.sh of the installed version)
   bash setup-launchd.sh --uninstall --dry-run # review
   bash setup-launchd.sh --uninstall
   ```

3. Only if the user wants the files gone, list each remaining path from the
   reference and confirm before deleting it. Keep the spool if the backlog
   was not empty and reporting may resume.

4. Tell the user to ask the DreamLake operator to revoke the machine token;
   stopping does not revoke it.

A binary installed only for local samples has no service: delete the
binary.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `setup-launchd.sh` not at hand | Deleted after setup | Fetch and verify the installed version's copy as in [service.md](service.md) step 3 |
| `refusing to overwrite …: not created by this script` | The plist was not written by setup | Leave it; ask the user |
| Linux: `lakeshore-host-metrics.service` also exists | Pre-rename unit | Leave it unless the user asks to remove it too |
