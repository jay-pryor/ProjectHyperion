---
id: TOOL-001
title: Document Frontmatter Schema
tier: tooling
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [HYP-000]
---

# Document Frontmatter Schema

Every Hyperion document carries YAML frontmatter. The registry is generated from it, so
frontmatter is the contract between documents and tooling.

```yaml
id: CORE-XXX-nnn      # stable, never reused, survives file moves
title: Human Title
tier: root | core | profile | agents | templates | tooling
status: draft | active | superseded
version: 0.1
audience: [human, model]   # who reads this
load: always | on-task | reference
related: [ID, ID]
```

## Field notes

**`id`** — stable identity. Cross-references use IDs, so a file can move without breaking
references. Never reuse an ID.

**`audience`** — `[human]` means never load into a model context; it is human process
guidance and would only consume budget. `[model]` means the reverse. Most are both.

**`load`** — the context budget control, and the most operationally useful field:

| Value | Meaning |
|---|---|
| `always` | In the standing context loadout for every session on this project |
| `on-task` | Loaded when working the relevant gate, review, or artifact |
| `reference` | Human lookup only; never loaded automatically |

The `always` set must stay small. If it grows past roughly a dozen short documents,
something has been mis-tagged, and the model's effective attention on the actual task
degrades. Audit it quarterly alongside the lesson prune.

## Enforcement

`build_registry.py --check` fails CI if frontmatter is missing, malformed, references an
unknown ID in `related`, or if the registry is stale.
