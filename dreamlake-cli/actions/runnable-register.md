# Register UDF and agent definitions

Registration and editor commands require CLI 0.71.1; check installed help
first. Preview the explicit definition files before registering:

```bash
dreamlake runnable register .dreamrc --dry-run
dreamlake runnable register .dreamrc --namespace YOUR_NAMESPACE
dreamlake agents list --plain
dreamlake agents edit YOUR_AGENT --web
```

See [registration](../reference/cli-runnable-upload.md), [all `.dreamrc`
fields](../reference/cli-dreamrc.md) and [agent editing](../reference/cli-agents.md).
Registration and Save do not execute or publish an agent. Retain partial upload
receipts and inspect existing entries before retrying; differing declarations
are refused. Context is not an access grant.

Executing one registered UDF is [registered-udf](registered-udf.md); pushing a
workflow spec is [workflows](workflows.md).
