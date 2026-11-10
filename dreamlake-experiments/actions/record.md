# Record an experiment

Start with `dl --version`. Use the setup action of `dreamlake-cli` if installation
or login is needed, then read the [runnable RL example](../reference/docs-ml-dash-examples-rl-logging.md#run-the-example).

Choose the user's namespace/project, a fresh run name, and local or remote
recording before writing. Keep the requested SDK integration: do not substitute
an old managed backend or a resource-upload command for instrumentation. Follow
[the login and project-creation entry](../reference/docs-ml-dash-examples-rl-logging.md#existing-login-and-project-creation)
when testing automatic project creation; do not manually pre-create the project
and then claim the SDK created it.

For a mock fixture, adapt the maintained example and dashboard from the docs.
Keep mock provenance in its parameters, tags and artifacts, distinguish virtual
steps from actual training, and do not launch a simulator, GPU or worker just to
produce logging data. For an existing platform job, consult [workload credentials](../reference/docs-ml-dash-reference-native-workload-credentials.md)
before changing its connection; preserve its supplied run binding.

After the writer finishes, read back the run status and representative data from
the categories the user requested. A successful process exit alone does not prove
that requested labels or artifacts were persisted. Consult the [file Bindr limitation](../reference/docs-ml-dash-examples-rl-logging.md#sdk-file-bindr-limitation)
when membership matters; report an explicit data repair separately from a fix to
the SDK itself.

If charts look incomplete, continue with [the dashboard action](dashboard.md),
not a replay of successful logging. Retain a user-requested UI fixture and return
its run link; clean up disposable rehearsal data and staging files when done.
