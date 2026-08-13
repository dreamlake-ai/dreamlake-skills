# FilePreview

The composed preview layer is the one most apps will mount directly.
Each component pairs a loader with the matching view, owns its
`useLoader` call, and dispatches ``
into the body slot while the data is in flight.

All composed previews follow the same prop contract:
`{ src, metadata?, onSave? }`. Hand them a URL (signed HTTP, `blob:`,
or `data:`) and they handle the rest.
