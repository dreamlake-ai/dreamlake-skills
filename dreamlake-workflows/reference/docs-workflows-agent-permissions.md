<!-- generated from https://docs.dreamlake.ai/workflows/agent-permissions.md at 0.1.102 757a8c39; do not edit -->

# Agent Permissions

  Every user-defined agent (uda node) declares what it may touch. Grants are
  flat, auditable strings in the IAM style — <code>domain.resource.verb</code> —
  validated when a workflow version is saved.

> **Status**: permission grants are **defined, stored, and validated for
> well-formedness**. Runtime enforcement ships with the execution engine.

> **Note:** Grants govern **resources** — datasets, nodes, queues. They do not govern
>   **tools and files**; that is Claude's `allow` / `ask` / `deny` rule syntax,
>   documented on [Agents](https://docs.dreamlake.ai/lakeshore/agents#permissions--what-it-may-touch). A
>   `uda` node and a declared agent both carry a `tools` list and a permission
>   block, and in both cases the two lists are validated independently.

## Grant grammar

```
grant   := domain "." resource "." verb (":" scope)?
domain  := lowercase identifier        e.g.  dreamlake, lakeshore
resource:= lowercase identifier        e.g.  datasets, providers, queues
verb    := read | create | update | delete | <registered custom verb>
scope   := resource qualifier          e.g.  @acme/robotics/grasp-v2, gpu-a10g
```

The format follows Google Cloud IAM (`service.resource.verb`, as in
`storage.objects.get`). The verb set follows the Kubernetes/IAM CRUD
convention, with `get`/`list` collapsed to **`read`** (we do not enforce
them differently). Domain actions that are not CRUD — like publishing a
dataset version — are **registered custom verbs on a specific resource**
(the way Kubernetes registers `impersonate` or `bind`), never a global verb.

## Registry

| Grant | Meaning |
| --- | --- |
| `dreamlake.datasets.read` | read datasets and dataset versions |
| `dreamlake.datasets.create` | create datasets / write new data |
| `dreamlake.datasets.update` | modify dataset metadata / annotations |
| `dreamlake.datasets.delete` | soft-delete datasets |
| `dreamlake.datasets.release` | **custom verb** — publish an immutable dataset version |
| `dreamlake.nodes.read` / `.create` / `.update` / `.delete` | the Node tree: episodes, folders, files |
| `dreamlake.artifacts.read` / `.create` / `.update` / `.delete` | renderable artifacts |
| `dreamlake.providers.read` / `.create` / `.update` / `.delete` | provider administration |
| `dreamlake.workflows.read` / `.create` / `.update` / `.delete` | workflow definitions and versions |
| `dreamlake.workflows.run` | **custom verb** — launch a workflow run |
| `lakeshore.queues.submit:<queue>` | **custom verb, scope required** — submit work to a queue |
| `lakeshore.queues.consume:<queue>` | **custom verb, scope required** — consume work from a queue |

Unknown domains, unknown resources under a known domain, and unknown verbs
are validation **errors** — the registry is closed, and grows by
registration, not convention drift.

## Scoped grants

A `:scope` suffix narrows a grant to a resource path:

```
dreamlake.datasets.read:@acme/robotics/grasp-v2
lakeshore.queues.submit:gpu-a10g
```

Unscoped grants apply namespace-wide. Queue verbs always require a scope.

## Tools are not permissions

Tool access is declared in the uda node's own **`tools`** field
(`tools: ["Read", "Bash"]`), following Claude's agent spec — the same field
name, the same semantics, and the same "omit to inherit everything" default.
Permission strings govern **data and resources**; the tools list governs
**capabilities**. The two lists are validated independently.

Which *files* a tool may touch, and which *commands* Bash may run, is a third
thing again — Claude's `Read(…)` / `Edit(…)` / `Bash(…:*)` rule syntax. A `uda`
node does not carry one today; a declared agent does. See
[Agents → Rule syntax](https://docs.dreamlake.ai/lakeshore/agents#rule-syntax).

```json
{
  "kind": "uda",
  "title": "vlm_annotator",
  "uda": {
    "instructions": "Label task, sub-task and active hand for each clip",
    "model": "qwen-vl-72b",
    "tools": ["Read"],
    "permissions": [
      "dreamlake.datasets.read",
      "dreamlake.datasets.create",
      "lakeshore.queues.submit:gpu-a10g"
    ],
    "queue": "gpu-a10g"
  }
}
```

## Why not `edit`, `remove`, or `ToolUse.*`?

- **`edit` → `update`, `remove` → `delete`**: no major permission system
  (IAM, Kubernetes RBAC, GitHub fine-grained) uses `edit` or `remove` as
  verbs; `update`/`delete` map 1:1 to REST methods and to both IAM and
  RBAC.
- **`ToolUse.Bash` → `tools: ["Bash"]`**: tool grants as permission
  strings would duplicate a concept every agent runtime already models as
  a first-class field, and would leave the runtime with two sources of
  truth for the same capability.
