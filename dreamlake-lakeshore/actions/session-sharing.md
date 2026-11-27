# Share saved session history with one person

Inspect `dl sessions share --help` before making a grant. Resolve the owner,
the session's saved ID and namespace, and the recipient's exact personal
DreamLake username. Use the active owner's login. Confirm the title with
`dl sessions show` when more than one saved row could match.

Use the grant command in [Share saved session history](../reference/cli-sessions.md#share-saved-session-history).
Inspect access with `dl sessions shares --help`. To remove one grant, use the
account ID from that list with `dl sessions unshare --help`. Read the list
again after a grant or removal. If a response is lost, inspect the list
before repeating the change.

Use this action when the user wants a named person to read a saved
conversation. If the user asks for interactive terminal access, follow the
separate [team session procedure](../reference/docs-lakeshore-hosts-browser-terminal.md#share-a-session-with-a-team).
A session link identifies the session. Grant access first and send the link
only when the user authorizes sending it.

If the command is missing, report the installed CLI capability. Keep the
existing visibility and check the product documentation for the matching app
flow. When access is denied, inspect the exact owner, recipient and namespace
in the server receipt.
