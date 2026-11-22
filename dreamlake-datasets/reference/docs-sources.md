<!-- generated from https://docs.dreamlake.ai/sources.md at 0.1.213 e321c4cd6; do not edit -->

{/* The FigSrc* tags come from the site-wide mdxComponents map in
    site.config.ts — no import needed. */}

# Visualize a source

  A **source** is where DreamLake finds your data. It can have an **external
  layer** — an S3 bucket or a Hugging Face repo connected to your namespace,
  read in place and never written to by DreamLake — and/or a **managed
  layer** of DreamLake-hosted files you upload with the CLI. Drop one
  `.dreamrc` file at a dataset's root and the app renders every episode in
  it: cameras, time series, timelines, 3D. Nothing is imported or converted
  to render — connected storage is read where it lives.

## Visibility and sharing

| Setting | Direct link | Public profile and source listings |
| --- | --- | --- |
| Private | Existing members and explicitly admitted collaborators | Hidden from visitors |
| Unlisted | Anyone with the link can read | Hidden from visitors |
| Public | Anyone can read | Listed for visitors |

Changing visibility requires Source settings permission. It does not change
signed-in share links, editors, or Project grants. Link readers cannot upload,
edit settings, or delete data. Sharing covers the whole Source, including its
external read layer; connection settings and credentials remain restricted.
Disabled Sources cannot be read by public or unlisted links. Previously
created Sources remain Private.

Read `GET /namespaces/:namespace/sources/:id` for visibility, capabilities, and
settingsRevision. Change visibility with
`PATCH /namespaces/:namespace/sources/:id/metadata`:

```json
{"visibility":"unlisted","expectedSettingsRevision":1}
```

Use the current returned revision, not the example value. A stale revision is
rejected. If the response is lost, read the Source again before retrying.
Creation and external import accept visibility; omission means private.
The namespace list accepts visibility=private|unlisted|public. For visitors,
filtering, pagination and counts include only active Public Sources. Signed-in
nonmembers request `visibility=public` for that catalog; their default namespace
listing retains its existing access-denied response so older clients can resolve
shared Sources directly by name. Anonymous catalog reads need no query flag.

The built-in resource API tools discover these schemas through
`dreamlake_resource_api_discover` (family sources). The repository's source-only
[local MCP adapter](https://docs.dreamlake.ai/lakeshore/agents/mcp#source-visibility) exposes `source_get`
and `source_visibility_set`; pass the settings revision from `source_get`.
Use a checkout containing those tools and a backend supporting this contract.
There is no hosted MCP endpoint or published adapter package.

## Connect your data

Linking takes two steps: a [Connection](https://docs.dreamlake.ai/connections) holds the credential,
and a Source reads through it. Create the Connection in the web app
(**Connections**, `/<namespace>/connections`), with `dl connection create`, from
the Python or TypeScript SDK, or by asking the assistant, which hands secret
entry to the web form. Then import the Source in **Sources**
(`/source/<namespace>`) or with `dl source import --connection <id>`.
Credentials stay server-side, encrypted — never in files or URLs.

| Storage | Connect with | Get bytes in today |
| --- | --- | --- |
| S3 bucket | Connection: access key or role | `aws s3 cp --recursive ./my-dataset s3://bucket/prefix` |
| Hugging Face repo | Connection: OAuth, token or public | `hf upload you/dataset ./my-dataset --repo-type dataset` |
| Any source (managed files) | `dl source create` (namespace owner) | `dl source upload ./my-dataset -r --source <name> --to <prefix>` |

Uploads land in the source's managed layer, never in your bucket or repo. An
uploaded file at a path that also exists in the connected storage takes
precedence in the source view, and uploading to an existing managed path
replaces it silently — use a fresh prefix. Limits, permissions and overwrite
rules: the [CLI sources guide](https://cli.dreamlake.ai/sources/).

Then verify from a shell (CLI 0.45.3+) that the source holds what you think:

```bash
dl source list                                    # sources you can reach
dl source browse [path] --source <name>           # one level; -r to recurse, --files for files only
dl source stat <path> --source <name>             # one path, which layer it resolves from
dl source download <path> --source <name> -o ./out # spot-check a file
```

Public GitHub repository support is an [implementation preview](./github/),
with commit-pinned reads and explicit pilot limits.

## Namespace, audience, and storage

A Source belongs to one namespace and can be referenced by multiple Projects.
Projects organize Sources; a Source can outlive a Project. An ordinary Source
uses `accessMode: "namespace"`: active namespace members can read it, and
Editors can write. `visibility: "private"` does not hide it from those members.

Deployments advertising `owner_admin` in the Sources list's
`capabilities.supportedAccessModes` also accept it when creating an empty
Source. This immutable audience admits only the active Source creator and
namespace administrators. The creator must remain a member. The current
organization role model gives administrator authority to organization owners.
Share links, public visibility, team Editor grants, and Project grants cannot
expand this audience. Restricted Sources must remain private. Project and
Bindr references are shown only to people who can access the Source. Moving a
Project with a restricted Source requires detaching that Source first;
restricted Source namespace transfers are not supported.

Source creation still requires namespace administrator authority. The create
API accepts, for example:

```json
{"name":"session-archives","accessMode":"owner_admin","visibility":"private"}
```

Managed Sources share platform storage, with a separate server-controlled
prefix for each Source ID. There is no per-folder or arbitrary prefix ACL
inside a Source: use separate Sources for different audiences. Upload and
read capabilities target objects within the selected Source; they do not
expose bucket credentials. A Project reference does not relocate stored bytes.

Operator-configured, namespace-allowlisted storage profiles can select a
managed bucket when a Source is created. Importing an external S3 connection
adds a read layer; it does not change the managed upload destination. An
organization-admin storage binding screen is a separate capability. Session
archives use the consent-gated service described below, rather than generic
Source upload permissions.

## Session archive sources

Source setup requires an `Idempotency-Key` that pins the exact candidate and
storage choice. Reusing it with a different request returns a conflict. An
unchanged retry checks current access and returns the current configuration;
it does not restart a stopped Source or create upload consent.

The session archive API binds an explicitly reported machine, provider root and
account to one namespace and restricted storage Source. A working directory or
Project never changes the destination. Each root/account currently has one
binding; directory routing across multiple namespaces is not yet supported.

`GET /namespaces/:namespace/session-archive-source-candidates` returns the caller's
reported roots. `GET /namespaces/:namespace/session-archive-sources` returns
configurations, permitted storage choices and creation capabilities. Creating a
configuration with `{candidateId,storageSourceId:null}` provisions a dedicated
creator-and-admin Source in shared platform storage when
`capabilities.createDefaultStorage` is true. An explicit eligible Source ID uses
that existing binding instead. Any current human namespace member may use this
archive-only default. The server fixes its canonical name, owner, private
`owner_admin` audience and shared-storage location; retries reuse the same
owner/namespace binding. General Source creation and external storage setup
retain their existing administrator requirements. Leaving the namespace removes
access, and administrators cannot configure another person's root through this
path. Creating a configuration does not approve uploads.

An authenticated observation records a native session identity and a frozen byte
boundary without transcript text, titles or working directories. A user approves
that exact observation and representation before the enrolled machine can request
short-lived, exact-object grants. Namespace administrators can read permitted
archives; that authority cannot approve another user's local uploads. Each grant
pins the checksum, length and immutable object, expires within two minutes, and
requires a current-authority commit before the bytes become readable. Interrupted
uploads recover through status and commit; a successful PUT is not a commit.

The upload path supports explicit native JSONL snapshots and gzip/zstd snapshots
preserved as encoded bytes. Compressed snapshots require an explicit
`native-compressed` source policy and consent; they are not decompressed on the
device or presented as a decoded conversation. Automatic session and source-wide
upload capabilities remain false. Upload consent never
authorizes remote execution. Local signed requests reuse the existing enrolled
machine key authority; DreamLake owns source, consent and archive permissions.
Current signing-key verification still depends on Lakeshore rotation/revocation
state, and work notifications use its existing connection. Independent DreamLake
device pairing and disconnected transport recovery are not yet available.

S3 holds immutable content. The application database owns identity, permissions,
consent and committed manifests; a durable outbox publishes namespace-scoped
manifest indexes to DreamDB. Index delay never grants access. Archive objects use
a private storage area outside generic Source browsing; only committed manifests
allow reads. Uncommitted expired objects remain private and are reclaimed after a one-hour
safety window by a bounded server worker with retry backoff. Committed objects
are excluded. Versioned storage needs a separately configured version-purge
policy; a delete marker is never reported as a payload purge. Generic deletion
of a Source bound to archival is refused.

A source owner or namespace administrator can stop future uploads with
`POST /namespaces/:namespace/session-archive-sources/:sourceId/disable`; only the
owner can re-enable with `/enable`. Both commands require an `Idempotency-Key`
and `{expectedSourceRevision,expectedPolicyRevision}`. Stopping clears current
consents and pending uploads, while preserving access to committed archives.
Re-enabling never restores previous consent. Disabled configurations remain listed.
Stopping uploads preserves configured metadata discovery, observations, and inventory
reporting under the current source revision. Configuration delivery still refreshes
the device binding and schedules metadata observation; upload grants remain blocked.

`GET` on the same source's `/policy` returns the current epochs, permitted
representations, `managedBy: null`, and the hard 4 MiB per-chunk limit.
`POST /policy` accepts the two expected revisions and `allowedRepresentations`
(`native-jsonl`, `native-compressed`, or an empty list to permit neither).
Owner/admin policy changes invalidate existing consents; they do not approve
another person's local upload. These controls are not enterprise forced-upload
policy: managed-root enrollment is a separate requirement.

The read-only message projection accepts Codex event-message JSONL (legacy
user/agent events and completed `UserMessage`/`AgentMessage` text items), Claude
user/assistant JSONL, explicit DeepSeek role/content JSONL exports, and DreamLake
schema-version-1 messages. Duplicate Codex response items, developer context,
tool output and reasoning are omitted. Unknown or
malformed records produce an incomplete preview, never a fabricated transcript.
Each page returns at most 200 messages, reads at most 8 MiB of native chunks and
uses an actor-bound cursor. A complete native snapshot does not imply complete
decoded coverage. Cross-namespace session links are optional and disappear when
the viewer cannot read either side.

### Configuration delivery and the private catalog

Configuration creation queues a durable, enrollment-bound notification. The
machine fetches configuration from DreamLake using its existing signed identity;
the notification carries no paths, credentials or upload permission. Installation
requires an explicitly configured local root/account, owner identity and an
independent destination allowlist. The browser exposes `deviceConfiguration` as
`pending`, `applied`, or `blocked`; server configuration alone is not proof that a
machine applied it. Stop and policy changes create a new configuration revision.

`GET /namespaces/:namespace/session-archive-sources/:sourceId/sessions` returns
source-authorized metadata with `query` (literal native-ID or normalized explicit-provider-title prefix), `limit`
(default 50, maximum 100), and an opaque `cursor`. It does not search transcript
text. Each entry identifies its machine, native session, observation, format and
explicit archive binding. An origin-session link is returned only within the
same namespace when separately readable. Stopped sources remain readable.

### Explicit historical import

`GET` on a source's `/history` returns bounded, resumable lists of previews and
grants plus `capabilities.createPreview`. The owner creates a preview through
`POST /history/previews` with expected source/policy revisions and permitted
representations. The server freezes the latest observed snapshot per session at
its cutoff, builds metadata in bounded pages, and returns counts, encoded bytes,
exclusions, expiry and a manifest SHA-256. Zero-byte or disallowed observations
are excluded. This step neither reads local content nor approves upload.

A preview may include a frozen, revision-matched `inventory` summary reported by
the configured device. It separately lists recognized native session IDs,
physical variants, stat-known encoded bytes, excluded files/bytes and safe reason
codes. An incomplete or missing scan is explicit. Unclassified child components
are not assigned fabricated session IDs. These device-reported counts do not
prove all files were registered or uploaded; server eligible snapshot counts
remain a separate denominator. Signed reports use
`POST /daemon/session-archive-sources/:sourceId/inventory`; source-authorized
readers can inspect the latest revision-matched report at the browser source's
`/inventory` route. Reports contain no paths, filenames or transcript text.

After inspecting a ready preview, the owner approves its exact hash and revisions
through `POST /history/previews/:id/approve`. Grants expire after 48 hours and
cannot silently extend. Historical approval does not enable future sessions.
The server dispatches at most one active snapshot per enrollment, rechecks each
frozen observation, and retains existing automatic-session approval instead of
overwriting it. Changed observations are blocked. Completed counts mean verified,
committed native bytes, not complete decoded transcripts.

`GET /history/grants/:id` reports progress; an owner or namespace administrator
can stop the import with `POST /history/grants/:id/revoke` and `expectedRevision`.
All history writes require `Idempotency-Key`. Revocation is checked again by
already-issued child upload grants and commits. Pauses and reconnects recover
through durable work leases and bounded retries; a notification acknowledgment
alone never marks an archive complete.

### Claude subagent components

Servers advertising `history.capabilities.includeComponents` accept version 2
previews that explicitly include Claude child logs. Preview creation and approval
have different request bodies. Both require an `Idempotency-Key` header; use a
separate key for each action and retain it when retrying that same request.

Create the preview with `POST /history/previews`. Replace the revision
placeholders with the source's current revisions:

```json
{
  "apiVersion": 2,
  "includeComponents": true,
  "expectedSourceRevision": "<current source revision>",
  "expectedPolicyRevision": "<current policy revision>",
  "allowedRepresentations": ["native-jsonl"]
}
```

Read `GET /history/previews/:previewId`. Once it is ready, inspect its frozen
entries, counts and byte total. Approve that exact preview with
`POST /history/previews/:previewId/approve`, using its returned revisions and
manifest SHA-256:

```json
{
  "apiVersion": 2,
  "expectedSourceRevision": "<preview.sourceRevision>",
  "expectedPolicyRevision": "<preview.policyRevision>",
  "manifestSha256": "<preview.manifestSha256>"
}
```

`includeComponents` and `allowedRepresentations` belong only to preview creation.
Do not send them in approval: the approval endpoint rejects extra fields and
uses the already frozen preview to determine which files and representations are
approved. For root-only version 1 imports, omit both `apiVersion` and
`includeComponents` from preview creation, and omit `apiVersion` from approval.
An older preview or parent snapshot approval never includes child logs.

Each child retains the real parent's native session ID, an explicit
`claude-subagent` component ID, and its own observation, generation, consent and
immutable archive chain. The initial classifier accepts IDs matching
`a[0-9a-f]{16}` only after bounded canonical-directory and native-header checks
against an existing parent. Ambiguous or unsupported children stay excluded.

Version 2 counts distinguish root sessions from components. `entryCount` is
`sessionCount + componentCount`; `totalBytes` includes both, with `componentBytes`
as a subset. Completed and blocked component counts remain separate from root
session counts. A nonempty component-only preview can be approved. Signed v2
inventory reports add a separate `components` count block; existing root-file
counts keep their meaning, and recognized children no longer count as exclusions.

Root catalogs remain lists of native sessions. The authorized parent's
`/components` endpoint lists child metadata without fetching transcripts.
Selecting a child uses an explicitly versioned passive reader tied to that parent
and component. Device dispatch requires `session_archive_components: 1` and v2
work negotiation; older claims receive a retry without acquiring a lease. These
contracts do not grant remote execution or enable future automatic uploads.

Component admission is enabled after the compatibility deployment
[`44750784681`](https://github.com/dreamlake-ai/dreamlake-workspace/actions/runs/44750784681)
and independent API/history-worker and search drain verification on November 20,
2026. Rollback must retain reader floor `dc36ef830a5758c7c0a9774e79ca5b455d5cb498`
or newer: older builders would incorrectly include children in legacy previews.
Each device's component opt-in remains off until its compatible producer and the
activated fleet are verified. Existing root-only approvals never include children.

## Shape the dataset

Most robot-learning exports work **as-is** — a published dataset renders
unmodified, with one file added:

| Your dataset root holds | `format` | Anything to do first? |
| --- | --- | --- |
| `meta/info.json` (LeRobot v2.x / v3.0) | `lerobot` | no |
| `*.zarr.zip` or a `.zarr/` directory (UMI) | `umi` | no |
| `*.mcap` files — Foxglove schemas or plain ROS&nbsp;1 / ROS&nbsp;2 bags | `mcap` | no |
| `model/` + `episodes/*/frames.parquet` + `episode.json` | `folder` | no — a DreamLake sim-playback dataset renders as-is |
| anything else — videos, images, CSV, parquet | `folder` | one folder per episode |

Layout details and shape rules:
[prepare your data](https://viz.dreamlake.ai/dataset-viz/requirements).

## Make it render

The `.dreamrc` names which fields feed which **views** — that's the whole
job. Open the source in the app and the dataset renders:

```yaml file=".dreamrc"
version: 1
dataset:
  format: lerobot # lerobot | umi | mcap | folder
  episodes: auto
views:
  - view: videoStack
    cameras: ['observation.images.*']
  - view: lineChart
    series: [{ field: [action, '*'] }]
```

The full authoring workflow — reading the field inventory, every view and
its options, a live gallery of finished files —
[starts here](https://viz.dreamlake.ai/dataset-viz/start).

## Single MCAP files

In **Visualize**, a root `.dreamrc` with `format: mcap` and `episodes: auto`
lists each root MCAP as an episode. In **Files**, selecting a recording
reuses the configured panels and pins the dataset to that one file for the
preview. This leaves the saved configuration and episode list intact.
The **Views** menu switches Source panels. The `views:` entries in a
`.dreamrc` describe what to draw inside an episode.

DreamLake chooses the first applicable layout in this order:

1. **`<filename>.dreamrc`** beside the file — `test.mcap` looks for
   `test.mcap.dreamrc`. A config written *for this file*: its views render
   with the selected file as the one episode.
2. **The folder's `.dreamrc`**, when its `dataset.format` is `mcap` — the
   unified config for a folder of recordings, applied to just this file.
3. **The source root's `.dreamrc`**, same condition.
4. **No config at all** — the file still renders: a default view generated
   from its [Foxglove or ROS well-known schemas](https://viz.dreamlake.ai/dataset-viz/reference#the-default-mcap-view).
   Camera topics become a frame stack, point clouds a 3D pane, tf a moving
   robot or skeleton (below), numeric channels charts. The header marks it
   as generated, and **copy .dreamrc** hands you the exact YAML — save it
   as `<filename>.dreamrc` (step 1) and the layout is yours to edit.

The file preview reads indexed, chunked MCAP over HTTP Range. A recording can
exceed the generic 50 MiB Source file-preview limit. The reader bounds
individual transfers and decoded chunks, and cancels a whole-object response.
See the [MCAP reader reference](https://viz.dreamlake.ai/dataset-viz/reference#mcap)
for limits, supported video codecs and repeated numeric fields.

The more standard the recording, the more the no-config default shows;
channels outside the Foxglove / JSON / ROS schema set fall back to the
metadata table with the reason stated.

## Show an annotation as an Output Source

A Source can present a published annotation instead of describing files. Give
its root `.dreamrc` exactly one key:

```yaml file=".dreamrc"
annotation: dreamlake://<namespace>/<annotation-name>
```

**Visualize** then opens that annotation in the annotation viewer: its
episodes, video and labelled timeline, plus [semantic search](https://docs.dreamlake.ai/annotations#search-it)
when the annotation stores search vectors.

- **Private reads:** reads go through the annotation's own private access under
  the reader's session. A reader who may open the Source but not the annotation
  sees the annotation's refusal, not its data.
- **Strict format:** the file must contain only the `annotation` key, with a
  `dreamlake://<namespace>/<name>` value. Any other `.dreamrc` is read as a
  dataset config, exactly as above.

## ROS bags and robots

Plain ROS bags need no conversion — ROS&nbsp;2 (rosbag2's own MCAP
output) and ROS&nbsp;1 alike. Images, point clouds and poses land in the
same views as their Foxglove twins, and the `/tf` tree renders in 3D with
Foxglove semantics: transforms compose down the declared parent chain, so
a tf-only recording plays as a **moving skeleton** — joints, bones, no
model required.

When the names a recording publishes — tf frame ids, or the joint names on a
`/joint_states` topic — carry a known robot's own naming, the default view
goes further and renders **the robot itself**: a Unitree&nbsp;G1 recording
opens as the G1, a DROID episode as a Franka Panda with its Robotiq gripper,
meshes streamed from the
[robot preset registry](https://huggingface.co/datasets/live9080/dreamlake-robots).
Unknown structures keep the honest skeleton — nothing is guessed. To put a
robot on a recording yourself, name its URDF in the 3D view:

```yaml file="<filename>.dreamrc"
- view: recon3d
  up: z
  tracks: [{ field: '/tf::*', as: transform3d }]
  models:
    - https://huggingface.co/datasets/live9080/dreamlake-robots/resolve/main/g1/g1_29dof.urdf
```

The viewer reads URDF directly — meshes resolve relative to the file (or
through a `packages:` map for `package://` references), each link drives from
its `/tf::<link>` track by name, and links the recording never publishes ride
their nearest tracked parent.

A bag that logs only **joint angles** and no per-link poses — very common,
since the angles are the state and the poses are derivable — is 3D too: bind
the topic with `joints:` beside a URDF and the viewer runs the forward
kinematics itself, gripper linkages included. Full detail:
[ROS bags & robot models](https://viz.dreamlake.ai/dataset-viz/robots).

## Sim recordings (MuJoCo & URDF)

A teleop recorder that runs MuJoCo can write a DreamLake **sim-playback
dataset** directly — one folder per episode, plus the exact model the
session ran snapshotted into `model/`. Each `frames.parquet` stores **named
channels** — one column per joint, seven per free body, keyed to MJCF names
by `episode.json` — so the data survives model recompilation and outlives
any single scene version. The `mujoco` view loads the snapshot and plays the
channels back **kinematically**: qpos in, forward kinematics out, never
stepping physics — scrubbing the shared timeline is random access,
frame-exact in either direction. Because channels are name-keyed, an `env:`
override plays the same data on a scene-only [env](https://docs.dreamlake.ai/scenes): hand channels
with no match there are skipped and listed, while objects and fixtures
replay on their own. `ctrl.*` columns carry the action stream for a
`lineChart`. The recorder drops this `.dreamrc` at the root:

```yaml file=".dreamrc"
version: 1
name: sharpa-teleop
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - view: mujoco
    qpos: [frames]          # named channel columns
    meta: [episode]         # episode.json — channels map + model ref
    height: 420
    # env: ns/laundry       # optional: play on a scene-only env
  - view: timeline           # shared clock + playback bar
  - view: lineChart
    series: [{ field: [frames, 'ctrl.*'] }]
```

The same contract has a **URDF flavor** for motion that isn't an MJCF scene —
a retargeted mocap clip, a policy rollout, anything that is "a robot
description plus per-frame joint values". `episode.json` says `sim: "urdf"`,
`model.path` names the dataset's URDF (with `model.files` listing every
mesh), and channels bind **URDF joints by name** — one column per
revolute/continuous/prismatic joint — plus one `freejoint` channel naming
the **root link** with seven columns (x, y, z, qw, qx, qy, qz — quaternion
**w-first**, meters, Z-up world) for the floating base. The `urdf` view
drives `setJointValue` and the base pose directly; joints the robot lacks
are listed, not fatal, and the same `env:` override plays the data on a
pushed URDF env:

```yaml file=".dreamrc"
version: 1
name: g1-dance
dataset:
  format: folder
  episodes: "episodes/*/"
views:
  - view: urdf
    joints: [frames]        # URDF joint columns, keyed by joint name
    meta: [episode]         # episode.json — sim "urdf", model + channels
    height: 480
  - view: timeline
  - view: lineChart
    series: [{ field: [frames, left_knee_joint] }]
```

Playback lives here, in sources; the envs you curate stay untouched —
pushing and versioning scenes is the [envs guide](https://docs.dreamlake.ai/scenes).

## Let Claude do it

Install the [datasets skill](https://github.com/dreamlake-ai/dreamlake-skills),
point at a folder, and say *"visualize this dataset in DreamLake"*:

| Step | Does |
| --- | --- |
| connect | inspects the data, preps the layout, gets it linked, verifies the source |
| `.dreamrc` | writes and debugs the `.dreamrc` — bindings, validation, iteration |

```bash
dl init                             # once: pick your agent and scope
dl skill install dreamlake-datasets
```

One skill does both — it gets the bytes connected, then makes them render.
Without the CLI, download `skills.tar.gz` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
and copy `dreamlake-datasets/` and `dreamlake-cli/` into your agent's skills
directory.

## Next steps

    The five-step authoring workflow, every view, and the .dreamrc gallery.

    A separate kind — structured collections with schemas, pushed with the
    Python SDK.

## Browse a Source in a Project

In the Project column, select a row marked **Source** to browse its directories
and preview files in a tab on the right. Selecting the same Source again brings
its existing tab forward, with the selected directory and file still open.
Projects with a top-level folder named `sources` also show their bound Sources
inside that folder. These rows represent Project-wide bindings.

## Project reference access

A Source reference attaches the **whole Source**, using its existing reference
`ProjectSourceBinding` relation and existing Bindr references. This release does
not migrate Source mounts or create another association table. Unifying them
with ordinary resource Nodes is a separate future optimization. Explicit user/team
Project READ grants Source USE; WRITE and ADMIN grant Source EDIT for supported managed content on namespace-mode Sources. Restricted `owner_admin` Sources keep their independent audience and receive no Project-derived access. These grants do not confer
Source ADMIN, settings/sharing management, Source deletion, or Connection/Vault
credentials, and do not bypass Source lifecycle restrictions.

Public Project visibility alone gives visitors no access to an otherwise
private Source. Independent Source sharing remains effective at its canonical
address. Existing and later references follow current grants dynamically;
detaching or revoking removes only that Project's contribution.

The Project-sharing backend and Web update are released. CLI Project commands
require 0.62.0 or later; Python Project support requires SDK 0.29.0 or later. See the
[Project resource access contract](https://docs.dreamlake.ai/dev/notes/project-resource-sharing).

The released [whole-Project and owned-Notes transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
supports Project, ordinary Project files/images/videos, owned Memos, and owned
Artifact and Env attachments (Artifact/Env members need the matching released
clients). In the
deployed service, a Source mount/reference blocks the entire transfer rather
than silently excluding it. The Source's existing independent sharing and
released Project-derived content access remain available.

> **Unreleased — intended design contract, not deployed behavior.** A planned
> expansion of the same whole-Project transfer adds **purely managed, eligible
> Sources** as manifest members (`source`, alongside `project`, `note`,
> `artifact`, `env` and `annotation`). It is whole-Project only: no standalone
> Source move, conversion or migration procedure is added. Server-side
> blockers — readiness, lifecycle state, storage and active operations —
> decide each Source's eligibility; external or mixed-layer Sources and
> Sources carrying a Connection/credential remain unsupported and continue to
> block the entire operation. No file payload is copied, moved or relocated:
> the Source ID, its physical storage under the existing bucket/prefix and its
> in-Project binding IDs stay stable, and the moved Project keeps its original
> `ProjectSourceBinding` and `BindrSourceReference` rows. Bindings, references and
> catalog placements from **outside** the moved Project detach; the Memo-only
> `preserveExternalFilings` option does not retain them, and no generic
> Source-relationship migration is introduced. The Source becomes private at
> the destination; preserving a direct share is conditional on the server's
> eligibility policies and blockers, and signed capability URLs already issued
> keep their existing bounded expiry — there is no immediate-invalidation
> promise. No released backend or client version supports this yet; the
> [whole-Project contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer) is authoritative
> for scope and current blockers.

## USD scene previews

Selecting a `.usd`, `.usda`, `.usdc` or `.usdz` file opens the shared Libraries
USD viewer in the file preview. Project files use the same renderer. Scene
layers and textures load on demand through authorized reads; relative
references must remain within the Project or Source. USDZ embedded assets
remain inside the package. Source preview permissions still apply. USD previews
have a 256 MiB file ceiling, enforced again while reading layers in the worker; texture and
package expansion limits are also enforced.

For a collection, place a `.dreamrc` at its root using the
[USD collection configuration](https://viz.dreamlake.ai/dataset-viz/spec#usd-scene-collections).
Visualize provides a searchable scene catalog and one active 3D viewport,
so browsing a large collection does not load all scenes. Orbit and zoom use
the same controls, lighting and theme as Libraries. Previews show static
geometry, not physics execution; inspect viewer warnings for unsupported
content or missing dependencies.

## Portable USD previews and collections

USD rendering is owned by `@dreamlake/viz/dataset-viz`. Libraries, Project file
previews and Source file previews share this renderer. DreamLake supplies
Project/Source authorization through `UsdResourceProvider`; independent hosts
can use the same component with public HTTP resources or their own resolver.
See the [view parameters and live example](https://viz.dreamlake.ai/dataset-viz/views#usd)
and [resource API](https://viz.dreamlake.ai/dataset-viz/reference#usd-resources).

Collection search belongs to `DatasetBrowser`, not to `view: usd`. Opt in
explicitly in `.dreamrc`:

```yaml
browser: { mode: collection, groupBy: directory, pageSize: 50 }
```

This presentation works with any dataset format and view. It searches only the
enumerated names, paths and task metadata, and renders one selected episode.
Task counts, filename details and selection state remain visible while filtering;
filters do not silently change the current scene. The Source Visualize tab retains the native file-navigation column and its
resize controls; changing views does not automatically hide that column.
Collections open as a responsive thumbnail grid without loading a USD scene.
Scrolling near the bottom automatically reveals another page until all matching
items are shown; `pageSize` is the append size, not a total scene limit.
A displayed/total count and an end-of-list message make progress explicit.
Search and task filters apply to the complete indexed catalog, including items
not yet displayed. Thumbnails stay lazy and offscreen images are released.
Selecting an item narrows the grid alongside the preview while retaining multiple
columns of thumbnail cards.
Close preview restores the grid, search filters and scroll position, and releases
the renderer. When the available preview panel is narrow, the visible two-column
grid sits above the selected preview. Native mobile List/Detail navigation remains
available through the existing application layout.

For tabletop robotics, `framing: workbench` offers a closer default view; Reset
view and Show full scene remain available. Large scenes are loaded on demand in
an abortable worker and render on demand. Unsupported materials and primitives
remain documented preview limitations, not simulation support.

For collections with preview images, use the documented
[indexed USD catalog](https://viz.dreamlake.ai/dataset-viz/spec#indexed-usd-catalogs-and-thumbnails).
The Source can hold the index and JPEG thumbnails in its managed layer while
original USD files remain in external storage. The list reads only metadata and
nearby thumbnails; selecting an entry starts the USD download. Indexes are
snapshots and must be refreshed when the underlying scene collection changes.

## Custom applications

For a visualization that needs its own UI and interaction, publish a static
application under `.dreamlake/visualization/` and select it in `.dreamrc`.
[Custom Source visualization](docs-sources-custom-visualization.md) covers publishing,
the read-only Source bridge, permissions and SDK examples.

The archive pilot admits only the configured shared `SOURCE_ASSETS_BUCKET`, whose versioning must remain disabled. Recheck this deployment assumption before release. Arbitrary or versioned archive bindings remain unavailable until lifecycle deletion and Terraform-managed IAM support them. Cleanup refuses versioned objects rather than claiming they were purged.

Explicit provider titles can be refreshed independently of uploaded conversation bytes.
New daemons negotiate `metadataProtocolVersion: 1` in the signed Source configuration
request and send title changes only when `capabilities.providerTitleMetadata` is true.
Older empty configuration requests retain their existing response shape.

The signed `POST /daemon/session-archive-sources/:sourceId/sessions/:sessionId/metadata`
request contains `sourceRevision`, the exact provider/native-session/root `occurrence`,
and `providerTitle: { value, observedAt }`. Titles are limited to 128 Unicode codepoints
without control characters; timestamps use UTC ISO milliseconds and cannot be more
than five minutes ahead of the server. Only a newer timestamp replaces a provider title.
The response reports `applied` and the current title, so delayed requests cannot revert it.
Catalog title search uses an indexed, Unicode-normalized, case-insensitive prefix;
native-ID matching remains literal. Search never reads transcript bytes. An unfiltered
root catalog can request `order=newest` to show newly registered sessions first,
ordered by archive registration time and ID. This opt-in order uses its own
actor/Source-bound cursor and cannot be combined with a search prefix or a
component listing; omitting it preserves native-ID ordering. Each page remains
bounded to 100 entries. Refresh the newest page for recent registrations and
retain pagination for older entries; a first-page refresh alone does not certify
that every session in a larger burst has been loaded.
This endpoint accepts explicit provider title metadata, not conversation or terminal
output. It preserves byte observations, upload consent, capture boundaries, namespace
ownership, and manually assigned session names. Current Source permissions govern
both updates and title reads. A newer retained provider title also refreshes an exact
reciprocally linked terminal's proven automatic name, after current execution-namespace,
host and enrollment checks. Manual names, unknown legacy naming provenance and newer
terminal titles remain unchanged. The first private registration may apply its provider
title while establishing that reciprocal link. An identical metadata replay or bounded
authorized identity backfill can repair missed propagation without reading or uploading
conversation bytes. An inaccessible terminal does not prevent the Source title update.
Provider-title support requires a compatible daemon; publication of the
backend alone does not update installed devices.
Authorized registered-session responses expose `nameIsAutomatic`. A UI may prefer a newer
provider title only for an exact authorized archive binding whose flag is true; false
or absent preserves the manually assigned name. Previous automatic names remain private.

Older session archive registrations are repaired lazily when their Source catalog is read.
Each request examines at most 25 rows and materializes the native ID only when the
current stored observation matches the existing session and configured provider/root.
This repair does not upload bytes, change consent, or move a session between namespaces.

Historical archive jobs yield between bounded device work quanta. Only a new verified commit since the current claim receives a short scheduling retry; zero-progress resource pressure and transport failures retain exponential backoff. The server continues to admit at most one archive upload job per enrolled machine.
### Captured new activity (admission disabled)

The separate capture protocol records only bytes after an explicitly inspected local boundary. It does not include the earlier prefix, certify the current file, or reuse snapshot approval. Each approval has a new capture ID, consent ID, and consent revision; device application is acknowledged separately. Replacement, truncation, or uncertain local journals pause the capture. Stopping upload permission preserves prior captured history under current Source read authorization.

Captured ranges use their own immutable revision chain and read routes. The decoder never joins an excluded prefix or another stream epoch. Reads are bounded to eight chunks and 8 MiB per page, with signed actor-bound cursors and explicit partial coverage. The default-off application gate keeps preparation, new approval, grants, and commits unavailable until compatible device production and fleet verification pass. Readers, revocation, and cancellation remain available after admission is disabled. Legacy automatic-session and automatic-source capabilities remain false.

A signed capture observation may attest that the inspected offset starts a native record by checking the preceding byte on the same owned file handle. This evidence is pinned to the capture and its manifests. Without it, decoding conservatively omits the initial partial record; retained raw bytes always start at the exact approved offset. This boundary evidence does not establish historical file continuity.

An enrolled device reconciles a lost start acknowledgment through signed
`POST /daemon/session-archive-sources/:sourceId/captures/:captureId/status` with
an empty payload. The response includes the current Source and policy revisions,
original approval timestamp and capture summary. It rechecks current enrollment
and Source access, remains readable for stopped captures, and never mints an upload grant.

Local session rows can open their existing Source consent and archive view even
when an automatic observation has no saved terminal-record association. The
server requires a single matching native session under the same owner,
enrollment and provider, with the occurrence root matching the explicitly
configured Source. Child components and ambiguous destinations are excluded.
Both the terminal row and Source must remain readable. The Source namespace
stays explicit; working-directory names never select it. This association
neither starts a terminal nor grants upload permission.

### Registering an observed native session for explicit terminal access

This additive protocol requires a compatible API and daemon; its deployment does
not retroactively turn existing catalog rows into executable sessions. The daemon
negotiates `{ "metadataProtocolVersion": 2 }` in signed Source configuration and
calls the registration endpoint only when `capabilities.nativeSessionRegistration`
is true. Empty and version-1 configuration requests keep their prior shapes.

`POST /daemon/session-archive-sources/:sourceId/sessions/:sessionId/registration`
accepts a signed metadata payload with `apiVersion: 1`, `idempotencyKey`, current
`sourceRevision`, `accountFingerprint`, logical `occurrence`
(`provider`, `nativeSessionId`, `localRootId`), `launch` (`cwd`, `providerRoot`),
and `metadata` (`name`, `observedAt`, `titleKind: "provider" | "fallback"`,
optional provider-derived `lastActivityAt`).
Only root Codex and Claude sessions are supported. The daemon must obtain the
canonical provider root from its exact applied local Source pin and the working
directory from explicit provider metadata. An archive path never supplies a
launch directory. Names are limited to 128 Unicode characters; observations may
be at most five minutes ahead of server time.

The server derives the namespace, owner, host, account and enrollment. It checks
current Source and execution eligibility even on a replay, pins the provider
root, and associates one exact private terminal descriptor with the root archive.
The namespace remains part of terminal identity: an existing descriptor in a
different namespace is left untouched. Ambiguous or conflicting bindings fail
with `ARCHIVE_REGISTRATION_CONFLICT`; unsupported providers return
`ARCHIVE_REGISTRATION_UNSUPPORTED`. Neither error changes archive upload consent.

The receipt echoes the complete Source identity, current revision, enrollment,
machine, Unix user, account, logical occurrence and immutable launch binding,
plus `terminalSessionId`, `archiveSessionId`, `archiveBinding` and `bindingDigest`.
The digest is lower-case SHA-256 over the UTF-8 JSON array of, in order:
`"archive-native-registration-v1"`, Source ID, archive ID, namespace ID, owner ID,
enrollment ID, machine ID, Unix user, provider, native ID, local root ID, account
fingerprint, working directory, provider root and terminal ID. Display names and
append-changing byte generations are excluded from that stable binding.

Registration starts no process and grants no upload permission. Uploads may be
stopped while metadata registration remains authorized. Subsequent explicit
provider titles update only a proven automatic name, in timestamp order; manual
aliases and launch bindings remain fixed. Provider activity advances monotonically;
collection time never substitutes for unknown activity in a Source-registered
descriptor. Daemons may coalesce activity-only registration updates by provider
activity minute; an unchanged activity report causes no idle request.
The catalog exposes the registered ID
through its existing `originSessionId` field only when both sides are readable
and the reciprocal mapping still agrees. That link is not execution authority:
an explicit terminal action must resolve and authorize the exact descriptor.

### Reconciling a lost snapshot grant response

An enrolled daemon that retained its original grant request but lost the response
can send the same descriptor and `idempotencyKey` to
`POST /daemon/session-archive-sources/:sourceId/uploads/by-request/status`.
The signed request returns `{ apiVersion: 1, idempotencyKey, descriptor, status }`
only when the stored descriptor matches exactly and the enrollment and Source
owner still have access. `status` is the existing upload status or committed
receipt. The response contains no storage URL and neither renews nor cancels an
upload. Upload-consent revocation does not prevent this restricted reconciliation;
current Source and enrollment access are still required.

A missing request returns `404`, and a reused key with a different descriptor
returns `409`. Neither response authorizes a replacement upload. An expired or
cancelled result identifies only that original attempt; any later upload still
requires fresh status, current consent and a new authorized grant.

### Retrying an unchanged historical snapshot

A history owner can inspect
`GET /namespaces/:ns/session-archive-sources/:sourceId/history/grants/:grantId/recovery`.
It returns at most 25 blocked entries with an archive-ID
`nextCursor`. This read schedules nothing. `canRecover` is advisory: current
Source, enrollment, storage, consent, frozen generation and competing work are
checked again when requesting and dispatching a retry.

The first supported recovery is a terminal `transport-unavailable` failure.
`policy-denied` entries remain unavailable because a purged upload does not, by
itself, prove whether expiration or cancellation caused its cleanup. A changed
local generation, revoked or expired grant, or changed consent cannot be widened
into a new approval by recovery.

An owner sends one entry to
`POST /namespaces/:ns/session-archive-sources/:sourceId/history/grants/:grantId/entries/:sessionId/recover`
with an `Idempotency-Key` and these exact body fields:

```json
{
  "expectedGrantRevision": "reviewed-grant-revision",
  "expectedSourceRevision": "reviewed-source-revision",
  "expectedPolicyRevision": "reviewed-policy-revision",
  "entrySha256": "reviewed-64-character-entry-hash",
  "expectedWorkId": "reviewed-terminal-work-id",
  "consentId": "existing-snapshot-consent-id",
  "consentRevision": "existing-snapshot-consent-revision"
}
```

Acceptance atomically creates one ordinary pending snapshot work item and
reports `queued`, only while no other snapshot work is active on that enrollment.
This excludes retry-delayed and leased snapshots, but makes no claim that the
machine has no other workloads. The new work reuses the original immutable
snapshot payload, child consent and grant expiration. Existing dispatch and
claim paths recheck current authority before device execution. The old terminal work and device block remain
unchanged. Repeating the same request returns the same receipt after current
authority checks; a different key cannot create a second pending successor.
At most three explicit recoveries are accepted per entry.

`retainedSnapshotBytes` reports previously verified committed bytes, separately
from `frozenSnapshotBytes`. Neither is newly transferred by the recovery command,
and `localFileVerified: false` explicitly means the device must still validate
its current root and frozen file before transfer. Recovery starts no terminal,
extends no grant, and changes no upload approval.

### Canonical session metadata

A daemon may separately opt into observed session metadata with the signed configuration
request `{ "metadataProtocolVersion": 2, "sessionMetadataProtocolVersion": 1 }`. Only this
request receives `capabilities.sessionMetadata`; existing protocol 1/2 configuration
responses and native-registration bodies remain unchanged. When supported, use signed
`POST /daemon/session-archive-sources/:sourceId/sessions/:archiveSessionId/session-metadata`.

The strict payload contains `apiVersion: 1`, a persisted UUID `idempotencyKey`, current
`sourceRevision` and `accountFingerprint`, exact logical `occurrence`, and `metadata`.
Metadata contains `kind`, `parentArchiveSessionId`, `observedAt`, `workingDirectories`,
`primaryWorkingDirectory`, `directoryCoverage`, and optional `lastActivityAt`. Root kind
is `session`; the initial child implementation accepts only persisted Claude subagents
with their exact same-Source parent and component identity. Unsupported Codex children
and sidecars are not relabeled as roots. Ownership, namespace and enrollment come from
current server authority, never from the body.

Each directory has a normalized absolute POSIX `path`, `firstObservedAt` and
`lastObservedAt`. At most16 paths,4096 UTF-8 bytes per path, and80KiB of serialized JSON
(including escapes) are accepted per report. UTC timestamps include milliseconds, are
ordered first≤last≤observed, and observation time is at most five minutes ahead. The
primary path must appear in that report. `unknown` carries no paths or primary. The
server unions directories retained during verified reciprocal joins with later reports,
retains at most32 recently observed paths, keeps the current primary, and marks
overflow permanently `truncated`. `observed` never claims complete historical coverage.
Paths are metadata, not filesystem, launch or upload authority. Immutable launch cwd is
unchanged.

The receipt binds source, archive and canonical session IDs, Source revision, exact
occurrence, original key and request observation time. `metadataObservedAt` is the
durable high-water time; `disposition` is `applied`, `replayed` or `stale`. An older report
cannot overwrite newer metadata; contradictory values at the same timestamp conflict.
A newer unchanged report still advances the durable fence. A receipt may clear only its
exact queued request, not a newer desired value. The canonical ID always names the
deterministic retained archive address, even if a later verified reciprocal registration
redirects it to a terminal representative. Both addresses require current access checks.
The existing command receipt is retained for 24 hours. Within that window an exact replay
returns it unchanged; after expiry the response may report current disposition and
high-water, but its request tuple and canonical address remain stable.

This metadata updates the additive canonical Session identity store, physically stored
in `CanonicalSession` so the retained legacy experiment `Session` collection and its
constraints remain untouched. Byte observations,
frozen snapshots, consent, upload state, provider-title metadata and manual aliases are
not changed. Legacy IDs and records are retained during migration; this endpoint does
not itself switch existing list or open routes. Source observations, provider-title
updates and native registration also synchronize their canonical identity within the
original authority transaction. A joined provider title reaches the representative only
after current reciprocal, owner, enrollment, host and execution-namespace checks; manual
labels remain authoritative. An inaccessible terminal does not authorize following its
redirect or changing its label.

### First-user fallback title negotiation

New daemons may request `{ "metadataProtocolVersion": 2, "titleMetadataProtocolVersion": 1 }`
in signed Source configuration, optionally alongside `sessionMetadataProtocolVersion: 1`.
Only this opt-in adds `capabilities.firstUserPromptTitleMetadata`; unchanged clients retain
their existing response shape. After that capability is present, the existing registration
request may use `metadata.titleKind: "first-user-prompt"`. Its receipt, exact Source/profile
binding and current execution authorization are unchanged. First-user text is not sent to
the explicit provider-title endpoint and does not grant archive upload or execution rights.

The receiver records automatic title quality separately from observation time and binds it
to the exact name hash. Explicit provider titles take precedence over a first-user fallback,
which takes precedence over a proven generated fallback. Updates within the same quality
remain monotonic; a higher-quality promotion does not regress the collection timestamp.
Manual names and automatic legacy names with unknown quality remain protected. Old writers
that change a name cannot leave usable quality evidence for the previous name. A generic-looking
name alone is never proof of generated provenance. Legacy quality may be established only with the optional `priorFallbackRegistration`
proof: the exact original nonrecursive fallback registration, at most 16 KiB, whose
successful unexpired server-ledger hash and receipt still match the current binding.
The automatic name and its metadata timestamp must still equal that original request.
The receiver records proven fallback quality and promotes the new first-user title in
one authorized transaction. If unknown legacy quality needs to be established, supplied
proof with missing, expired or contradictory retained evidence returns
`ARCHIVE_TITLE_PROVENANCE_UNAVAILABLE` without changing the label. Omitting proof leaves
unknown quality unchanged. Already proven quality follows its existing precedence rules;
manual names remain unchanged, and neither path needs to revalidate unused prior proof.
The total registration
payload is bounded to 30 KiB (32 KiB signed HTTP envelope). This never infers provenance
from a generic-looking name or re-reads historical transcripts.
