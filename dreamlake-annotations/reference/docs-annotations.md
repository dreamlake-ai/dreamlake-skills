<!-- generated from https://docs.dreamlake.ai/annotations.md at 0.1.106 513428f0; do not edit -->

{/* The Fig tags come from the site-wide mdxComponents map in
    site.config.ts — no import needed. Beyond the install commands,
    this page carries no code: every SDK call it describes is written
    out in /annotations/reference. */}

# Annotations

  An annotation is where your **labeled data** lives — your workflow does the labeling, the
  annotation stores its output. One episode is one raw video plus any number of annotation layers:
  anything you can pin to that video's clock. Layers are independent and open-ended — send what you
  have, add the rest later.

## Public catalog reads

`GET /namespaces/:slug/annotations` accepts requests without an Authorization
header. Anonymous callers and authenticated nonmembers receive only live public
annotation rows; namespace members retain access to their private rows. A supplied
invalid or expired token returns 401.

Public annotation details (`GET /namespaces/:slug/annotations/:name`) and
content reads (`POST /namespaces/:slug/annotations/:name/presign-read`) also accept
anonymous requests. Both check the annotation's current visibility. Private,
missing and deleted annotations return 404 to callers without access; namespace
members can still read their private annotations. Presigned reads retain the
existing path validation and expiry limits. Upload credentials, creation,
editing and deletion still require authentication and membership.

## Browsing in the app

`/<namespace>/profile?tab=annotations` and `/<namespace>/annotations` share the
same catalog. Personal owners and organization members see the resources and
operations permitted to them; anonymous visitors and visitors to someone else's
namespace see public annotations only. Profile has an identity rail, while the
application has resource navigation for the URL's namespace.

Public details open without a sign-in redirect and retain the namespace sidebar.
The detail header returns anonymous readers to the Profile annotations tab and
signed-in readers to `/<namespace>/annotations`. Embedded viewers return to their
containing project. See [Profiles and workspaces](docs-workspaces.md).

## Prerequisites

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash   # the dreamlake CLI
pip install dreamlake dreamdb   # SDK + storage engine
brew install ffmpeg             # transcoding (any install method works)
dreamlake login                 # browser sign-in; CI uses DREAMLAKE_API_KEY
```

Windows, what the installer puts where, release channels, and auto-update:
[Install](https://docs.dreamlake.ai/#install).

## Upload it

One call. The video is transcoded for the browser, each layer is stored
against its clock, and adding a layer later just means passing one more
argument. Give the episode an id you'll recognise — that's the handle for
coming back.

## Keep adding

Open an annotation by name on any day and add to it. Revisions never overwrite —
newest wins, history stays.

| Later, you can                    | Effect                                         |
| --------------------------------- | ---------------------------------------------- |
| add another episode               | the annotation grows                           |
| revise a layer                    | newest wins, old versions kept                 |
| add a layer you skipped           | it shows up on an episode you already uploaded |
| add a layer type that ships later | same thing — just another revision             |
| add a camera angle                | views share one clock; video is add-only       |
| make it public                    | anyone can open it, no login                   |

Nothing you upload today has to be re-uploaded to benefit from what ships
tomorrow.

## Watch it

Open the web app → **Annotations** → your annotation → your episode.

How a layer is drawn follows from how it's pinned — which is why the list can
grow without the picture changing:

| A layer pinned to | Is drawn                                       | Shipping today                     |
| ----------------- | ---------------------------------------------- | ---------------------------------- |
| a frame           | on the picture, tracking playback              | joint skeletons, 3D reconstruction |
| an interval       | as labeled bars on the timeline; click to seek | action segments                    |
| the whole episode | as episode metadata                            | task labels                        |

Each is optional. The player shows what you have and skips what you don't —
a bare video simply streams.

## When there's no overlay yet

Every annotation page has two views, and the second one always works.

**Preset view** is what the last section showed: the annotation's type label
matches a preset, and you get the player with its overlays.

**Raw tracks view** ignores presets and lists every track straight off the
manifest — name, kind, values along the timeline. Label, JSON, embedding,
video; it doesn't matter.

| If your data        | You get                                           |
| ------------------- | ------------------------------------------------- |
| matches a preset    | the rendered view, overlays and all               |
| doesn't, or not yet | the raw track view — nothing hidden, nothing lost |
| gets a preset later | the rendered view, with no re-upload              |

So a new kind of data is **useful the day you upload it**.

## Bring your own schema

The same machinery with the lid off: declare any columns you like — sensor
readings, JSON, images, embeddings — anchored to timestamps, or to row
numbers when your data has no clock. It's also the escape hatch when the
layer you need doesn't exist yet.

| Rule                    | What it means for you                                 |
| ----------------------- | ----------------------------------------------------- |
| append-only, write-once | a value at a given time and column is never rewritten |
| one commit per write    | send batches, not one point at a time                 |
| one writer at a time    | parallel writers to the same annotation will clash    |

Custom annotations appear in the catalog under their own type label; today
you read them back through the SDK.

## Share it

Annotations are **private** by default.

|                        | Who can view                      |
| ---------------------- | --------------------------------- |
| 🔒 private _(default)_ | you and members of your namespace |
| 🌐 public              | anyone, no login                  |

Names can be scoped to a team, too: a bare name is yours, an organisation
prefix targets that org, and membership is checked per request.

## Let Claude do it

Install the [annotations skill](https://github.com/dreamlake-ai/dreamlake-skills)
(`dreamlake init` once, then `dreamlake skill install dreamlake-annotations`;
or copy `dreamlake-annotations/` from the latest
[release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest) tarball
into your agent's skills directory) and skip the SDK — describe what you
want, it makes the calls:

| You say                                                          | It does                                     |
| ---------------------------------------------------------------- | ------------------------------------------- |
| _"upload this clip with its hand skeletons and action segments"_ | creates the annotation, uploads the episode |
| _"add the 3D reconstruction to ep-001"_                          | fills in the missing layer                  |
| _"add a wrist camera to ep-001"_                                 | attaches the second view                    |
| _"make this annotation public"_                                  | flips visibility                            |

## Next steps

    The manual — every method, argument and data shape, with the code this page leaves out.

    Every layer's exact fields, including 3D reconstruction.

## Project attachment access

Explicit user/team Project READ grants content reads for its live Annotation
attachments; WRITE/ADMIN permit supported content uploads. Public Project
visibility does not open a private Annotation. Independent resource policy
remains valid, and detaching or revoking removes only inherited access.

Attaching requires Project content creation and independent sharing-management
authority. Project grants do not grant catalog/schema management, resource
deletion, ownership transfer or infrastructure credentials. Delegated uploads
require resource-scoped temporary credentials; static custom-S3 credentials and
unscoped STS fallback are refused with `DELEGATED_UPLOAD_UNSUPPORTED` (403).
An annotation owned by another namespace attaches only through its owner's
[cross-namespace mount grant](https://docs.dreamlake.ai/api/external-mounts).

The Project-sharing backend and Web update are released. CLI Project commands
require 0.62.0 or later; Python Project support requires SDK 0.29.0 or later. See the
[Project resource access contract](docs-dev-notes-project-resource-sharing.md).

The released [whole-Project and owned-Notes transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
supports Project, ordinary Project files/images/videos, owned Notes, and owned
Artifact and Env attachments (Artifact/Env members need the matching released
clients). In the
deployed service, an Annotation attachment blocks the entire transfer rather
than silently excluding it. The Annotation's existing independent sharing and
released Project-derived content access remain available.

> **Unreleased — intended design contract, not deployed behavior.** A planned
> expansion of the same whole-Project transfer carries the Project's live
> Annotation attachments as manifest members (`annotation`, alongside
> `project`, `note`, `artifact`, `env` and `source`). It is whole-Project
> only: no standalone Annotation transfer is added. Annotation IDs, storage
> bindings and pinned catalog identity stay stable; episode, layer and
> revision payloads retain their existing storage — nothing is copied, moved
> or re-uploaded — and schemas, versions and raw tracks stay stable, while
> ownership metadata changes. Catalog placements outside the moved Project
> detach; the Note-only `preserveExternalFilings` option does not retain them.
> The Annotation becomes private at the destination; preserving a direct share
> is conditional on the server's eligibility policies and blockers, and signed
> URLs already issued keep their existing bounded expiry — there is no
> immediate-invalidation promise. Standalone label datasets have no Project
> relationship and are not moved by this feature. No released backend or
> client version supports this yet; the
> [whole-Project contract](https://docs.dreamlake.ai/dev/notes/project-note-transfer) is authoritative
> for scope and current blockers.
