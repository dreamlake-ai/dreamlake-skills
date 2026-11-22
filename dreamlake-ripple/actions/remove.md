# Stop reporting or remove Ripple

Stop the service, then remove only what the user asks for. The released
version has no uninstaller; the list of what the installer and setup script
leave behind is in
[reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#stop-or-remove-linux).

## Steps (Linux, systemd)

1. Show the backlog first; samples still in the spool may not be delivered
   yet:

   ```bash
   ripple status --spool-dir=/var/lib/lakeshore-host-metrics
   ```

2. Stop and disable the service:

   ```bash
   systemctl disable --now ripple.service
   systemctl is-active ripple.service    # inactive
   ```

3. Only if the user wants the files gone, list each path from the reference
   and confirm before deleting it. Keep the spool if the backlog was not
   empty and the user may restart reporting.

4. Tell the user to ask the DreamLake operator to revoke the machine token.
   Stopping the service does not revoke it.

A user-only install (`$HOME/.local/bin/ripple`) has no service: delete the
binary.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `lakeshore-host-metrics.service` also exists | Pre-rename unit | Leave it unless the user asks to remove it too |
| Unit file without the "Managed by" marker | Not written by the setup script | Do not remove it; ask the user |
