# Read status and show the waterfall

```bash
dreamlake tasks status vault --recursive --to-json
dreamlake tasks show vault/entries/write-recovery --to-json
```

`status` returns the task, immediate child summaries and an explicitly labelled
immediate-child status rollup; deprecated children are excluded from the done
denominator. The UI opens the selected task or folder in an outline and
waterfall, and its detail panel shows note links and event history. A task with
a start and no end shows a striped open bar to the present and does not acquire
an `endedAt`; unknown start or end is never fabricated. Refresh reads the
current projection. Reading changes nothing. See
[read status](../reference/cli-tasks.md#read-status-and-show-the-waterfall).
