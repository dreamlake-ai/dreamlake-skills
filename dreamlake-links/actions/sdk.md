# Integrate Links in an SDK client

Open [TypeScript](../reference/cli-links.md#typescript) and the Python guide
linked from [CLI and SDKs](../reference/docs-links.md#cli-and-sdks).

1. Use the SDK the user requested and its documented public client. Check the
   installed package against the released contract before writing an example.
2. Keep resource identity and URL content separate. Retain the creation identity
   and the last observed version in the caller's state so recovery survives a
   process interruption.
3. Exercise the example against a disposable resource: save, read, edit, page
   and remove the example record. Preserve the failing operation and identity
   when a response is uncertain; do not automatically restart the whole example.
4. Report the tested package and service, and any unverified operation. Do not
   silently replace an SDK-only request with CLI automation.

Use [the API contract](../reference/docs-links.md#api) for validation, pagination
and recovery. Unsupported destination crawling or permission changes must be
reported as separate capabilities, without invented methods.
