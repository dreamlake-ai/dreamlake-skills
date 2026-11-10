# Configure a run dashboard

Start with `dl experiments runs --help` and the [CLI experiment reference](../reference/cli-experiments.md).
Read [per-run configuration](../reference/docs-ml-dash-reference-native-charts.md#per-run-dashboard-configuration)
before writing a `.dashrc`.

Inspect the selected run's stored metric groups/fields and its current config.
Do not equate the number of overview tiles or header values with the amount of
stored data. When a field is missing on screen, distinguish a missing write,
an unavailable read and automatic selection before changing anything.

For an explicit dashboard, preserve existing user configuration and include the
fields/media they asked for. Use actual recorded keys and an appropriate x axis
for each group. For "all", include all value fields rather than only familiar
train/eval names, and size media grids for the matched files. The [complete RL example](../reference/docs-ml-dash-examples-rl-logging.md#dashboard-configuration)
provides a maintained starting point; do not duplicate its format here.

Write the configuration to the selected run, using the documented file operation,
then read the stored bytes back. Do not accidentally configure a project/folder
or create competing config files. Tell the reader to refresh after an out-of-page
write. Stored configuration and matched data are API evidence; claim rendered
acceptance only when the affected page was actually inspected.

A run-specific config does not change the app's default selection policy. Keep
those fixes separate, and do not rewrite or re-log experiment data to hide a
presentation problem.
