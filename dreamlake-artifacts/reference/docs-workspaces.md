<!-- generated from https://docs.dreamlake.ai/workspaces.md at 0.1.102 757a8c39; do not edit -->

# Profiles and workspaces

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
public catalogs only. Projects, Notes, Annotations, Scenes and Artifacts support
public browsing in either layout. Private catalogs such as Sources, Connections
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
the live public note whose slug equals the namespace slug, for personal and
organization namespaces alike. There is no setting; publishing that note is the
whole mechanism. Everyone, including members, sees the same public
introduction, read-only and above recent projects. A private, deleted, empty or
differently slugged note shows nothing, and the area is simply absent when
there is no introduction. See [Notes](https://docs.dreamlake.ai/notes#profile-introduction). The global
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
existing DreamLake user by name, username or email. For someone without an
account yet, type their full email address and choose **Invite by email**,
optionally with a role and teams. The invitation appears in the members list as
*invited · not signed up yet*, under the **invited** filter, and only owners can
see it. The first time that person signs in to DreamLake with the invited email,
they join with the chosen role and teams and the row becomes a normal member.
Owners can revoke a pending invitation from its row.

Signing in is a separate gate. DreamLake uses Vuer accounts, and new accounts
may wait for approval before they can sign in at all. If the invited person sees
a waiting-list page, a Vuer auth administrator adds their email to DreamLake's
allowed emails. The organization invitation is kept until they get through.

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

Public resource lists and public Projects, Annotations, Scenes, Artifacts and Notes
details can be opened without signing in. Private-only pages require the
appropriate identity and permissions. The sidebar remains available while moving
between application lists and details, with the current owner's permitted links.
Loading or an error in the resource does not replace the navigation.

Project files inherit their containing project's visibility; separately filed
Notes, Artifacts and Annotations retain their own permissions. A public project
does not publish private resources filed inside it or their private counts.
An Env or Artifact share token can authorize an anonymous read. A private Note
share link requires sign-in because it creates a grant for that person. Invalid
or revoked links retain the server's not-found or access-denied behavior.

The detail header returns signed-out readers to
`/<namespace>/profile?tab=<resource-type>` and signed-in readers to
`/<namespace>/<resource-type>`. Embedded resources return to their containing
project first. Browser Back continues to follow actual history. There is no
extra sign-in strip above the detail.

The namespace list APIs for Notes, Projects and Annotations accept requests
without an Authorization header. Anonymous users and nonmembers receive only
live public rows; authenticated namespace members retain their existing access.
Pagination totals use the same visibility filter. Supplied invalid or expired
credentials return 401. Anonymous project summaries omit internal bindr/dataset
counts. Anonymous Notes searches do not activate or flush collaborative rooms.
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

The [Move note dialog](https://docs.dreamlake.ai/notes#moving-between-workspaces-development-preview)
uses this control for destination selection. It offers concrete workspaces and
writable projects, and requires an access preview before the move is confirmed.
Changing search scope alone never transfers a note or changes permissions.

## Project access management (development preview)

Project administrators can open **Manage access** from a project row. Add a
person by username or choose an active team in the project's organization, then
set **Read**, **Write**, or **Admin**. Saving the same recipient updates their
existing grant instead of adding duplicates. Existing grants can be changed or
removed; user rows report their current effective project role.

Workspace owners retain Admin access. Organization members retain baseline Read
access to organization projects, and public projects remain readable publicly.
The highest direct, team, or workspace role applies. Removing one grant does not
remove access obtained elsewhere. Private notes keep their own permissions;
granting project access does not publish them. This feature does not introduce
projects restricted to selected teams.

## Deleting a project

Project administrators can delete a project from its row or from the file
browser. Deleting removes the project, its Bindrs and everyone's access to it.
Notes and other resources filed in it are kept, as are their places in other
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

Your own Scenes and Notes catalogs include a separate **Recent in your
organizations** section. Each organization shows up to six recent resources and
a **View all** link. Personal results and Shared with me remain separate.
Visitors and organization catalogs do not show this personal aggregation.

Organizations load in batches of six, with at most three simultaneous catalog
requests. A failed organization can be retried without reloading your personal
resources. Notes requests are bounded by the existing API; Scenes currently reads
the organization's full catalog and displays the six most recent entries.
