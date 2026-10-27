# Record start, progress, end and done

These commands log the corresponding typed events. Times describe actual task
work, never PR creation or merge; keep unknown times null.

```bash
dreamlake tasks start vault/entries/write-recovery --at '2026-09-13T20:00:00Z' --event-id recovery-start-001 --if-match REV_BEFORE_START
dreamlake tasks progress vault/entries/write-recovery --mode discrete --completed 3 --total 5 --unit checks --at '2026-09-13T20:15:00Z' --event-id recovery-progress-003 --if-match REV_BEFORE_PROGRESS
dreamlake tasks progress vault/entries/write-recovery --mode discrete --completed 5 --total 5 --unit checks --at '2026-09-13T20:25:00Z' --event-id recovery-progress-005 --if-match REV_BEFORE_FINISH_PROGRESS
dreamlake tasks end vault/entries/write-recovery --at '2026-09-13T20:26:00Z' --event-id recovery-end-001 --if-match REV_BEFORE_END
dreamlake tasks status set vault/entries/write-recovery --status done --at '2026-09-13T20:27:00Z' --event-id recovery-done-001 --if-match REV_BEFORE_DONE
```

- `end` alone does not imply done; `done` does not imply acceptance. If the work
  ends unsuccessfully, log context and leave status `not_done`. End may be known
  with unknown start, and a known end cannot precede a known start.
- Progress is an absolute `{mode, completed, total?, unit}` snapshot. Omitting
  `--total` makes the total unknown, including when a previous total was known.
  Mode and unit stay fixed until reopen; use a separate task or an explicitly
  designed reset to change them. No mixed-unit or recursive numeric rollup is implied.
- Reuse an event ID only when replaying precisely the same update; each new
  snapshot gets a new ID. Timed events default to now and generate an ID when
  omitted; supply both when recording a known observation or retrying.
- Reopen clears current-cycle progress, start, end, review and acceptance while
  preserving history.

Continuous progress on an existing continuous-mode task:

```bash
dreamlake tasks progress vault/ingest --mode continuous --completed 0.375 --total 1 --unit fraction --at '2026-09-13T20:15:00Z' --event-id ingest-progress-003 --if-match INGEST_REVISION
```

See [start, progress, end and done](../reference/cli-tasks.md#start-discrete-progress-end-and-done)
and [floating-point progress](../reference/cli-tasks.md#floating-point-progress).
