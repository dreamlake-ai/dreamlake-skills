# Blacksmith CI runner rollout

Compatible Ubuntu jobs select four-vCPU x64 Blacksmith runners when repository variable `CI_BLACKSMITH` is `true` (case-insensitive). Unset/false retains the original GitHub runner. This is a configuration rollback, not automatic provider failover. Original commands, actions, architecture-sensitive jobs, permissions, environments, dependencies, tests, assertions, timeouts and triggers are preserved.

Install the Blacksmith GitHub App for this repository and confirm provider runner availability/billing before activation:

```sh
gh variable set CI_BLACKSMITH --repo dreamlake-ai/dreamlake-skills --body true
# Roll back future jobs:
gh variable delete CI_BLACKSMITH --repo dreamlake-ai/dreamlake-skills
```

Registration on another repository does not establish access here. Do not dispatch release, deployment, provisioning or publication workflows merely for timing. Use ordinary authorized runs; existing queued jobs keep their original scheduling. Preserve publication OIDC and kernel/platform-specific contracts.

## Existing receipt baseline

| Workflow / receipt | Conclusion | Queue-inclusive wall minutes | Runner minutes |
| --- | --- | ---: | ---: |
| [Generated skills integrity](https://github.com/dreamlake-ai/dreamlake-skills/actions/runs/38308407300) | success | 0.23 | 0.17 |

Wall interval is run creation to terminal `updated_at`, a metadata proxy that may include later updates. Runner minutes sum completed, non-skipped job start-to-completion intervals, excluding queue and billing rounding. Failure timings remain failures. Different candidates/workloads prevent causal speed claims. After migration, retain exact commit, provider labels, run conclusion, job/step timestamps and coverage before comparing. Provider acceptance and post-migration timing are unverified.

## Preserved exceptions

Non-Ubuntu and matrix/platform jobs remain on their original runners pending architecture/OS and release-contract review.

Setup: https://docs.blacksmith.sh/introduction/quickstart
Runner types: https://docs.blacksmith.sh/blacksmith-runners/overview
