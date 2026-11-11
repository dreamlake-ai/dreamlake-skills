<!-- generated from https://docs.dreamlake.ai/ml-dash/reference/native-workload-credentials.md at 0.1.157 93913542; do not edit -->

# Native Experiment workload credentials

A workload credential names one writer, such as a training job, in one project.
It is the native form of an ml-dash managed writer. Projects whose
`GET .../status` lists the `workload-credentials` capability support it.

A credential is metadata only: an ID, its project, an optional bound run, a
generation and whether it is active. It contains no secret and there is no
token export. A writer authenticates with your DreamLake login, for example an
explicitly provided `DREAMLAKE_API_KEY` in CI, and receives a session that
lasts 60 seconds. Every request uses your current project role. If you lose
write access, the writer stops writing.

Only the person who created a credential can see or change it. Managing
credentials requires your DreamLake login and write access to the project;
a session cannot manage them.

## Sessions

`POST /native-experiments/ns/:namespace/projects/:project/session`:

| Body | Result |
| --- | --- |
| `{"mode": "read"}` or `{"mode": "write"}` | A project session, unchanged. |
| `{"mode": "write", "idempotencyKey": UUID}` | Creates the writer for this intent, or reuses the one it created. |
| `{"mode": "write", "idempotencyKey": UUID, "runId": ID}` | The same, bound to one live run. |
| `{"mode": "write", "workloadId": UUID}` | A session for an existing writer. Add `runId` to require its bound run. |

A writer response also contains `workloadId`, `generation` and, for a bound
writer, `runId`. Keep the same idempotency key for retries, then use
`workloadId` to renew. A retired writer returns
`403 NATIVE_CREDENTIAL_RETIRED`; neither key creates a replacement.

A writer session can read and write runs. A writer bound to a run reads and
writes only that run: other runs return `403 NATIVE_RUN_SCOPE_MISMATCH`, and
creating a run returns `403 NATIVE_RUN_CREATION_NOT_ALLOWED`. Moving a run to
the trash, restoring it and managing credentials require your login.

## Manage credentials

| Request | Result |
| --- | --- |
| `GET .../credentials?limit=50&cursor=ID` | `{credentials, hasMore, nextCursor}`; `limit` is 1–100. |
| `GET .../credentials/:credentialId` | `{credential}` |
| `POST .../credentials` `{"operation": "create", "idempotencyKey": UUID, "runId"?: ID}` | `{credential}` |
| `POST .../credentials` `{"operation": "rotate", "credentialId": UUID, "expectedGeneration": N}` | `{credential}` with generation `N + 1`. |
| `POST .../credentials` `{"operation": "retire", "credentialId": UUID, "expectedGeneration": N}` | `{credential}` with generation `N + 1`, inactive. |

A credential is
`{id, namespaceId, projectId, runId, generation, active, createdAt, updatedAt}`.
Its ID is the creating intent's UUID in lower case. Creating again with the same
intent and run returns the same credential. The same intent with another
project, person or run returns `409 NATIVE_CREDENTIAL_CONFLICT`.

Rotate and retire end every session of an older generation; the next write of
such a session returns `403 NATIVE_CREDENTIAL_RETIRED`. A write that started
before the change commits before it or is refused. Repeating a completed rotate
or retire returns the credential unchanged. Any other generation returns
`409 NATIVE_CREDENTIAL_CONFLICT`. A credential of another person, or an unknown
one, returns `404 NATIVE_CREDENTIAL_NOT_FOUND`. A malformed body returns
`400 NATIVE_INVALID_CREDENTIAL`.

Native credentials are separate from managed ml-dash credentials. A managed
credential does not work with native runs, and nothing is migrated.
