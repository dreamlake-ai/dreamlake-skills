# Integrate link files in an SDK client

Open [TypeScript](../reference/cli-links.md#typescript) and the Python guide
linked from [CLI and SDKs](../reference/docs-links.md#cli-and-sdks).

1. Use the SDK the user requested and its documented public client. Check the
   installed package against the released contract before writing an example.
2. Encode the saved URL as file contents, then use the ordinary file API at the
   chosen destination. Preserve its creation and revision checks. Use the legacy
   URL API only when recovering existing records, not for new file-list entries.
3. Exercise the example against a disposable destination: create, read, preview,
   edit, and clean up through the ordinary file operations. Preserve the path
   and revision when a response is uncertain; do not restart with a new path.
4. Report the tested package and service and any unverified operation. Do not
   silently replace an SDK-only request with CLI automation.

Unsupported destination crawling or permission changes are separate capabilities;
do not invent SDK methods for them.
