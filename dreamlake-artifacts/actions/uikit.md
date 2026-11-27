# Use UIKit for internal team interfaces

Use DreamLake UIKit components, tokens and standard examples for internal team
artifact interfaces. Keep content and application-specific actions in the artifact;
improve missing reusable behavior in UIKit rather than copying a component fork.
Preserve an existing artifact's design and the user's requested deliverable format.

1. Read the public [UIKit setup](https://uikit.dreamlake.ai/index.md), then use
   the [component index](https://uikit.dreamlake.ai/llms.txt) to load only the
   needed component and style guides. Private repository access is not a prerequisite.
2. Install from the public npm registry in the application build. Inspect the
   installed package version, exports and peer dependencies before using an
   example: live docs can describe components newer than the npm release.
   Use a compatible published version; report a missing export rather than
   inventing a prop or silently switching to a private workspace dependency.
3. Follow the installed package README for its CSS build and dependency scan;
   importing tokens alone is not a styling check. Bundle UIKit with the application
   and publish the built client directory through [static builds](publish.md#static-builds).
   Do not paste package imports into the single-file React template or rely on
   browser CDN imports. For an explicitly requested self-contained file,
   bundle its dependencies and styles into that output and check the sandbox.
4. Check the rendered components and their interaction in DreamLake at the
   intended panel size, including theme and keyboard behavior. Group related
   panels as tabs, keep width stable and preserve inactive work. Follow the
   shared component examples for tab alignment and contextual actions.

The public [UIKit agent skill](https://uikit.dreamlake.ai/llm-readable.md#import-it-as-a-skill)
is optional; these public docs are sufficient. Reusing UIKit does not make an
artifact or its data public. Retain its existing access settings.
