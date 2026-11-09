# Inspect and exercise an open scene

**Candidate procedure, unreleased.** First check the deployed tool inventory and
read the [browser scene tool contract](https://docs.dreamlake.ai/agents/scene-tools).
Do not infer availability from this action or a local checkout. Use the contract
for schemas, limits, capabilities and version requirements.

1. Establish the execution surface before planning mutations. For an SDK-only,
   CLI-only or headless request, verify a documented equivalent exists; otherwise
   report the runtime gap and offer the existing local [compose](compose.md) and
   [validate](validate.md) workflows. Do not invent a browser-runtime SDK method.
2. For an asset-selection request, first search accessible libraries and inspect
   the selected asset card and an actual image. Retain the library, asset ID,
   revision and selection rationale. A thumbnail is not a physics check. If the
   asset still needs packaging, composition or publication, complete the normal
   scene workflow before attempting runtime inspection.
3. Identify the exact published scene version mounted in the current browser
   agent turn. Call `dreamlake_scene_inspect`; retain its instance and revision,
   address metadata, actuator limits and reported capabilities. Stop if the
   intended model or necessary capability is absent.
4. Call `dreamlake_scene_pause` and use its returned revision. Reset only when
   restoring the initial state is part of the request. Derive actuator targets
   from the observed model; never guess actuator IDs or treat controls as poses.
5. Submit a small target update with `dreamlake_scene_set_actuator_targets`, then
   a bounded `dreamlake_scene_step`. Carry the returned revision into each next
   operation. After a timeout, missing acknowledgement or user interference,
   inspect again before deciding whether another mutation is needed.
6. Call `dreamlake_scene_render` with an explicit camera. Inspect the actual model
   image and record the scene identity, controls, completed steps, resulting
   revision and observation. Keep receipts and image evidence together.

## Evidence and fallback

Separate the native Python composer result, browser engine result and observed
image in the report. Do not use one as proof that the other ran. Check capabilities
before promising contacts, scene creation, layer composition or robot-task
completion. If the request needs an unavailable capability, state that gap and
route to the appropriate local scene action; do not silently substitute a
rendered pose for a successful physical interaction.

For example, “inspect this pinned robot scene, pause it, apply the observed
actuator target, step and show the result” follows this action. “Build a new
warehouse from these library assets” starts with [source-assets](source-assets.md)
and [compose](compose.md), then returns here only after publication and mounting.
