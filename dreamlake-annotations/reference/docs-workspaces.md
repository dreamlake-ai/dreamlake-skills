<!-- generated from https://docs.dreamlake.ai/workspaces.md at 0.1.193 4d8f60536; do not edit -->

# Profiles and workspaces

See [Folder and Bindr visibility](https://docs.dreamlake.ai/workspaces/folder-visibility) for Private,
Unlisted and Public organization within projects.

## One namespace, two layouts

`/<namespace>/profile?tab=<resource-type>` and
`/<namespace>/<resource-type>` show the same resource catalog with the same
permissions. Profile has an identity and avatar rail; the workspace has a resource
sidebar. Projects is the first resource after Overview and the default workspace
destination. Existing namespace-root links continue to open Profile.

Your own profile and profiles of organizations you belong to expose the resources
and actions available to you. Creation, editing, deletion and organization
administration remain subject to the existing resource and role permissions;
being able to browse a catalog does not grant permission to modify every item.

Signed-out visitors and signed-in visitors browsing someone else's namespace see
public catalogs only. Projects, Memos, Annotations, Scenes and Artifacts support
public browsing in either layout. Sources expose public entries to visitors. Private catalogs such as Connections
and Vault are not advertised to visitors. A directly shared resource can still be
opened according to its existing server permissions; a share does not turn its
owner's private catalog into a public list.

Public views omit private counts, trash, Shared with me, organization updates and
creation/editing controls. All/Public filters are omitted when every result is
public; meaningful filters such as artifact kind remain. The member views retain
useful catalog filters and permitted management actions. List/grid, search,
sorting and resource cards are shared across the two layouts.

Overview keeps recent projects and annotations and its list/grid preference.
It does not fetch every resource catalog merely to display counts.

The profile Overview opens with the namespace's introduction when it has one:
the live public memo whose slug equals the namespace slug, for personal and
organization namespaces alike. There is no setting; publishing that memo is the
whole mechanism. Everyone, including members, sees the same public
introduction, read-only and above recent projects. A private, deleted, empty or
differently slugged memo shows nothing, and the area is simply absent when
there is no introduction. See [Memos](https://docs.dreamlake.ai/notes/browsing#profile-introduction). The global
**Cmd+Shift+D** (or **Ctrl+Shift+D**) developer switch controls discovery of
experimental features, not access rights. Turning it on never grants access to
private resources.

### Following a profile

The profile rail shows **Follow** below the @handle on every profile except your
own. Signed out, **Follow** points to **Sign In** at the top right: it is
briefly highlighted, with a hint such as "Sign in to follow Tom Tao" for a few
seconds. Choosing that **Sign In** while the hint shows returns you to the same
profile and completes that one follow. Once the hint expires or is dismissed,
or if you choose **Sign Up** or leave the profile, signing in does not follow
anyone. The follow is not repeated, and it is not created by opening the
profile link or by signing in some other way. Once you follow, the button reads
**Following**; unfollowing is a separate **Unfollow** choice in its menu.

Below the button, every visitor sees the profile's counts, for example
`12 followers · 8 following`. Followers counts the accounts that follow this
namespace. Following counts the live namespaces its personal owner follows;
organizations cannot follow, so their profiles show followers only. Counts are
public. The list of who follows whom is not shown.

## Resource owner and signed-in account

The sidebar separates your signed-in account, global navigation and the namespace
you are browsing. Above the DreamLake brand, a plain username and chevron open your
account menu; the sidebar collapse control shares that row. Dashboard opens your
own recent work from any namespace. Gallery opens the same public gallery for
everyone in a new browser tab.

In your own personal namespace, a plain **Workspace** heading folds and unfolds
the resource navigation, just like Bindrs. It scrolls with the list. Other
namespaces instead show an avatar, display name and **Workspace @namespace**
heading. This heading stays at the top of the scrolling sidebar; clicking the
avatar/name area folds its resource links. The plus/minus indicator appears on
hover. The separate **@namespace** link opens that owner's Profile in the current
tab. A collapsed sidebar shows only the owner avatar and resource icons, and
restores the previous resource-fold state when expanded. Folding Workspace does
not hide Pinned or Bindrs. When available, **+New** sits above the Workspace group.

Resource links and permitted Settings, Members and Teams entries belong to the
URL's namespace. Your signed-in identity above the brand does not turn into an
organization when you browse one.

The account menu lists your personal namespace and organizations, then **My
Profile**, **My Dashboard**, **New organization** and **Sign out**. Both personal
destinations remain available on every signed-in surface: My Profile opens your
own profile, and My Dashboard opens `/dashboard`, in the current browser tab.
Profile has no separate Enter workspace button or Dashboard shortcut beside the
account menu.

Choosing a namespace normally opens its corresponding resource list. From a
detail it returns to the list without carrying the previous resource ID;
unavailable destinations fall back to Projects. From Profile it retains that
layout and an available tab. From the personal Dashboard, choosing an organization
opens its Projects list.

Browser history and refresh follow the URL's namespace. There is no remembered
workspace overriding the owner shown in navigation. Membership loss removes
member-only navigation and content without changing the owner of the page.

Signed-out visitors see a brief sign-in invitation between the brand and Gallery,
with a primary **Sign in** button and a **New to DreamLake? Sign up** link. Gallery
and public workspace navigation remain available, while Dashboard is hidden.
A collapsed sidebar keeps a sign-in icon accessible. While authentication is
being checked, a neutral placeholder reserves the account area instead of
flashing sign-in buttons. Profile retains its landing-style authentication
buttons. Explicit sign-in return addresses preserve the pathname, query and fragment.

The footer pairs a small **Theme** label with the light/system/dark segmented
control. The label is hidden and the control turns vertical when the sidebar is
collapsed. Profile keeps its existing horizontal theme control.

Profile owners can edit their identity through the existing pencil/avatar dialogs;
organization identity editing remains restricted to its owners. Organization
profiles show member avatars and directory views to members. The member and
team directory is members-only: signed-out visitors and nonmembers see the
organization's public identity and catalogs, and its Members and Teams tabs say
the directory is visible to members. Governance remains permission-controlled.

### Inviting members

Organization owners add people from **Members → + invite**. Search finds an
existing DreamLake user by name, username or email; choosing that account adds
them immediately. Otherwise type a full email address and choose **Invite by
email**, optionally with a role and teams. An email invitation never adds anyone
immediately, even when the address belongs to an existing account: it appears in
the members list as *invited · pending sign-in*, under the **invited** filter, and
only owners can see it. The person joins with the invitation's role and teams the
next time they sign in to DreamLake, when that sign-in's identity provider
confirms the exact invited email as verified; the row then becomes a normal
member. Being signed in already is not enough: someone with an open session joins
after signing out and back in, or an owner adds their account directly. Until a
verified sign-in, the invitation stays pending.
Owners can revoke a pending invitation from its row. Inviting a pending email
again updates its role and teams; when the invitation is accepted it uses its most
current role and teams, skipping teams deleted in the meantime. An invitation
counts only while the owner who sent it is still an owner: demoting or removing
that owner, or that owner leaving, revokes their pending invitations at once.

Signing in is a separate gate. DreamLake uses Vuer accounts, and new accounts
may wait for approval before they can sign in at all. If the invited person sees
a waiting-list page, a Vuer auth administrator adds their email to DreamLake's
allowed emails. The organization invitation is kept until they get through.

### Teams

Teams group people, for example to grant a Project or share a machine with them.
Only organization owners create teams; the creator becomes the team's first
**owner**. A team slug is 3–40 lowercase letters, digits and hyphens, cannot
start or end with a hyphen, and is unique in the organization.

| Role | Can |
| --- | --- |
| Organization owner | Everything below on every team of the organization, whether or not they are in it; add a DreamLake user who is not yet an organization member to a team, which also makes them an organization **member** |
| Team owner | Edit, rename, archive, restore and delete the team; grant, change and remove every team role |
| Team admin | Edit and rename the team; add **existing organization members** as members; remove members and guests; invite and revoke guests |
| Team maintainer | Older role. In a team without any owner it acts as an owner, as it always did. Once the team has an owner it acts as an admin. |
| Team member | See the team (as any member sees visible teams) and leave it |
| Guest | See this one team, its members (without their email addresses) and the Projects granted to the team, and leave it. Nothing else of the organization. |

Managing a team always needs current organization membership: someone who leaves
the organization loses all team authority. Admins cannot grant, change or remove
owner, admin or maintainer roles. A team admin cannot bring someone new into the
organization: ask an owner to add them or invite them by email first. To add
someone outside the organization to only this team, invite them as a guest.

**Leaving and removal.** Anyone can leave a team except its last owner, who must
first make another member an owner. In a team without owners, the last maintainer
must first make another member an owner or maintainer. Leaving or being removed
from the organization removes every team membership in it and the Project grants
that person issued in the organization's Projects. Direct Project grants **to** a
removed person are kept by default, so deliberate external-collaborator access
survives; an owner can opt in to deleting them as part of the removal (see
[Project access](https://docs.dreamlake.ai/workspaces/project-access)). A removed or departed person
immediately stops receiving access through the team's Project grants and machine
grants; connections they opened through a team machine grant are closed
(best effort, usually within seconds).

**Guests.** A team owner, admin or maintainer, or an organization owner, invites
a guest by email from the team page. DreamLake does not send the email: copy the
invitation link (`/teams/invitations/<id>`) and send it yourself. The person signs
in with an identity provider that verifies that email address. If they are
already signed in, they sign out and back in. The invitation then shows up for
them and they **accept** or **decline** it; nobody else can use the link. An
invitation expires after 14 days and can be revoked while pending.

Accepting always makes the person a **guest** of that team, never an
organization member. This holds even if they are already in the organization or
join it before accepting. A guest:

- reaches the Projects granted to the team, with the grant's role, and nothing
  else in the organization's Projects;
- never gets machine access (SSH, the browser terminal or machine lists) through
  the team's machine grants. This holds even if they later join the organization
  while still a guest. Access granted to them some other way is unaffected: a
  direct machine grant, their own machines, or another team where they are not a
  guest.
- cannot see the organization's members, its other teams or its settings.

To give a guest the regular member role, first add them to the organization,
then change their team role. Guests cannot be added any other way, and nobody
can be changed into a guest.

**Renaming.** Owners and admins can change the slug of an active team. The old
slug stays reserved for that team: no other team can use any current, earlier or
deleted team's slug, so an old link never leads to a different team. The team
can take back one of its own earlier slugs. Members, grants and invitations
follow the team, not its slug. The slug cannot change while the team holds Vault
state, because Vault entry names include it.

**Archiving.** An owner can archive a team and restore it later. While it is
archived, the team keeps its members, grants and invitations but gives no access.
Nobody receives anything through its Project grants or machine grants, and
connections opened through a team machine grant are closed. It accepts no
changes and no new members. Guest invitations to it cannot be accepted, and its
guests lose sight of it. It is left out of team lists, except the organization's
**Archived** list. Members can leave an archived team, and an owner can still
delete it.

**Nesting.** A team can be created inside a parent team of the same organization.
Nesting is organizational only: members, Project grants and machine access are
never inherited between parent and child teams. A team's parent cannot be changed
after creation, and a team with child teams cannot be deleted until its child
teams are deleted.

**Deleting a team** needs a team owner or an organization owner. It removes the
team's memberships, its Project grants and its place in pending invitations,
revokes its pending guest invitations and its machine grants, and keeps its slug
reserved. A team that still holds Vault state (secrets, including retired ones
awaiting purge, access keys, Host credential bindings or pending transfers) is
refused until that state is cleared.

## Your Dashboard

`/dashboard` is the signed-in user's personal home, with the application sidebar.
It combines recent projects and annotations in your own namespace with your
recently visited projects across namespaces. Visit history stays private to your
account and each project links to its real owner. Other people and organizations
are browsed through Profile and their resource lists, not public Dashboards.

The global Dashboard entry stays reachable while browsing someone else's
namespace. On Dashboard, the Workspace section offers your own namespace's
resource shortcuts. Profile exposes My Dashboard in the account menu; Gallery retains its signed-in
Dashboard shortcut.

Signing in without an explicit return destination opens `/dashboard`; a preserved
resource destination still takes priority. Legacy `/<namespace>/dashboard` links
redirect to `/dashboard`, which requires authentication and always resolves the
signed-in user's own data rather than the namespace in the old address.

## Resource lists and shared links

Public resource lists and public Projects, Annotations, Scenes, Artifacts and Memos
details can be opened without signing in. Private-only pages require the
appropriate identity and permissions. The sidebar remains available while moving
between application lists and details, with the current owner's permitted links.
Loading or an error in the resource does not replace the navigation.

Project files inherit their containing project's visibility; separately filed
Memos, Artifacts and Annotations retain their own permissions. A public project
does not publish private resources filed inside it or their private counts.
An Env or Artifact share token can authorize an anonymous read. A private Memo
share link requires sign-in because it creates a grant for that person. Invalid
or revoked links retain the server's not-found or access-denied behavior.

The detail header returns signed-out readers to
`/<namespace>/profile?tab=<resource-type>` and signed-in readers to
`/<namespace>/<resource-type>`. Embedded resources return to their containing
project first. Browser Back continues to follow actual history. There is no
extra sign-in strip above the detail.

The namespace list APIs for Memos, Projects and Annotations accept requests
without an Authorization header. Anonymous users and nonmembers receive only
live public rows; authenticated namespace members retain their existing access.
Pagination totals use the same visibility filter. Supplied invalid or expired
credentials return 401. Anonymous project summaries omit internal bindr/dataset
counts. Anonymous Memos searches do not activate or flush collaborative rooms.
Creating, modifying, sharing and deleting remain authenticated operations.

## Project workspace search (development preview)

On member project lists, the **Projects** eyebrow and `@workspace /` search
prefix identify the catalog being searched. Click the prefix or press Backspace
with an empty project query to choose your personal workspace, an organization
you belong to, or **All workspaces**. Typing while choosing filters workspaces;
Arrow keys and Enter select, and Escape restores the project search. On narrow
screens, the workspace prefix sits above the search input.

Scope changes keep your signed-in identity and the surrounding page context.
Every project row identifies its owner, and opening it goes to that workspace.
**All workspaces** combines permitted results with bounded concurrent requests
and complete pagination. A failed workspace is shown as an error with retry;
successful workspaces remain available. Public visitor lists keep their existing
namespace-only behavior. Creation requires one concrete workspace.

The [Move memo dialog](https://docs.dreamlake.ai/notes/sharing#moving-between-workspaces-development-preview)
uses this control for destination selection. It offers concrete workspaces and
writable projects, and requires an access preview before the move is confirmed.
Changing search scope alone never transfers a memo or changes permissions.

## Project access management (development preview)

Project administrators can open **Manage access** from a project row. Add a
person by username or choose an active team in the project's organization, then
set **Read**, **Write**, or **Admin**. Saving the same recipient updates their
existing grant instead of adding duplicates. Existing grants can be changed or
removed; user rows report their current effective project role.

Project access has two modes in the implementation update: **Workspace** keeps
the existing organization-member Read and public visibility baselines;
**Restricted** removes those baselines and admits current explicit user/team
grants plus namespace-owner recovery access. Legacy projects remain Workspace.
There is no namespace-global default setting or automatic change to existing
projects. See [Project access](https://docs.dreamlake.ai/workspaces/project-access) for policy APIs,
atomic restricted creation, client examples and deployment status.

The highest applicable direct/team role applies; workspace owners retain Admin.
Removing one grant does not remove access obtained elsewhere. Restricted mode
hides project discovery and its tree from ungranted members; it does not revoke
independent Memo/resource membership, accepted shares or other Project grants.
A public project must be explicitly made private in the same policy request
before it becomes Restricted. No silent visibility change is performed.

## Deleting a project

Project administrators can delete a project from its row or from the file
browser. Deleting removes the project, its Bindrs and everyone's access to it.
Memos and other resources filed in it are kept, as are their places in other
projects; the project's files stay stored but can no longer be opened. The
project's address (its URL slug) becomes free, so a new project can use it; an
old link that names only the address then opens the new project, never the
deleted one's files. A project cannot be deleted while a job submitted to it
is still queued, running or being cancelled. There is no restore in the
dashboard. See the [API reference](https://docs.dreamlake.ai/api#namespaces--projects) for the matching
endpoint.

Once the server release with the issue #1343 fix is out (not yet released),
deleting a workflow, artifact, annotation or scene also removes it from every
project that holds it, along with its Bindr tags there. Moving it to the Trash
counts. Restoring it from the Trash does not put it back in those projects;
add it to a project again. A new resource with the same name can be added
where the old one was.

## Organization updates

Your own Scenes and Memos catalogs include a separate **Recent in your
organizations** section. Each organization shows up to six recent resources and
a **View all** link. Personal results and Shared with me remain separate.
Visitors and organization catalogs do not show this personal aggregation.

Organizations load in batches of six, with at most three simultaneous catalog
requests. A failed organization can be retried without reloading your personal
resources. Memos requests are bounded by the existing API; Scenes currently reads
the organization's full catalog and displays the six most recent entries.

## Project addresses

[Project names and addresses](https://docs.dreamlake.ai/workspaces/project-addresses) explains automatic
slugs, separate custom settings, preserved old links, and rename conflicts.
