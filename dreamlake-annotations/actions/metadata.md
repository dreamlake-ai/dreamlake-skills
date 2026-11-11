# Change annotation metadata

```bash
dl annotation get "$ANNOTATION" --namespace "$NAMESPACE"
dl annotation update --help
dl annotation rename --help
```

Resolve the actual Annotation resource first. Read its current identity and
metadata, distinguish a display-title request from a URL request, and obtain the
intended spelling from the user or uniquely identified task context. Never rename
an Artifact or Memo just because it carries similar wording.

Use the installed metadata command or the documented SDK for an explicitly
requested integration. Follow the [canonical metadata contract](../reference/docs-annotations-reference.md#update-a-title-or-url-slug)
for rename guards, permissions, conflicts and old-link behavior. Preserve the
observed revision while the user reviews an edit. After a conflict or uncertain
write, read and reconcile; do not silently refresh the guards and retry.

Read the resource back through both its new and previous URL, verify the same
identity, title and access, and retain a concise receipt. If a related document
must change, identify it uniquely by title or link before editing; use the
appropriate document workflow and preserve unrelated content. Report the
capability release separately from the actual rename and document outcome.

Do not start data ingestion, replace annotation content, broaden sharing or launch
paid work to perform a metadata change. Unsupported installed commands or server
fields require a compatible release, not a guessed endpoint or delete/recreate.
