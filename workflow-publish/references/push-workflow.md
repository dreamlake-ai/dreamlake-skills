# Push Workflow

## Procedure

**1. Settle the target namespace before pushing.** With no `--namespace` the
push goes to the active login's PERSONAL namespace. That is rarely what someone
means when the work belongs to a team — and the mistake is silent: the push
succeeds, the URL looks right, and it is only noticed later by a colleague who
cannot find the workflow.

```bash
dreamlake profile     # personal namespace
dreamlake org list    # orgs you belong to
```

Creating an organisation also creates a namespace of the same slug, so an org
slug IS a namespace: `--namespace acme` publishes into that org.

If the caller named a namespace, use it. Otherwise inspect available orgs and
the active profile, state the destination clearly, and get the missing target
from the user before pushing when team ownership is plausible. Never silently
publish to personal namespace because `--namespace` was omitted.

**2. Push.** The CLI validates against the WorkflowSpec schema *and* the graph
rules before any network call. Invalid JSON or failed local validation leaves
remote state unchanged and consumes no version.

```bash
dreamlake workflow push <file.workflow.json> \
    [--namespace <slug>]
```

Success prints the version, shape, and canvas URL:

```
workflow:  <name> v1 · 5 stages · 8 nodes · 9 edges
✓ pushed <name> v1
  open:  https://dreamlake.ai/<namespace>/workflows/<name>
```

**3. Report to the user**: the version, the node/edge counts (so they can see
the shape matches what was described), and the URL as a clickable link. Tell
them the page has a **Run** button and that node states light up live on the
canvas while it executes.

## Project-derived access (under development)

The companion server change allows explicit Project READ to read attached
Workflow specs and WRITE/ADMIN to register supported spec updates. The public
Workflow catalog follows its independent metadata policy; public Project
visibility does not authorize private spec content. Project grants do not
authorize execution, host/secret access, catalog management or ownership transfer.
Do not infer permission to use Run from permission to publish a content version.
Project-only uploads require scoped temporary credentials; an unsafe broker mode
returns `DELEGATED_UPLOAD_UNSUPPORTED` (403).
See the [owning Workflow guide](https://docs.dreamlake.ai/workflows/).

For a new Project attachment, require independent resource sharing-management
authority and actual Project WRITE/ADMIN; ordinary organization-member READ or
public Project visibility is insufficient. Grouping an already-live attachment
into a Bindr of that same Project needs Project write authority and resource
readability, without sharing it again. Use the server's current `canBind` result,
not a role guessed from membership. See [Project choice and grouping](https://docs.dreamlake.ai/api/project-queries/).
