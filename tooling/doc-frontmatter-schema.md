---
id: TOOL-001
title: Document Frontmatter Schema
tier: tooling
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [FRAMEWORK]
related: [HYP-000, CORE-SES-001, CORE-IMP-001]
---

# Document Frontmatter Schema

Every Hyperion document carries YAML frontmatter. The registry, the loadout tables, the
lens library, and the agent index are generated from it, so frontmatter is the contract
between documents and tooling. Read by FRAMEWORK sessions adding or re-tagging a document.

```yaml
id: CORE-XXX-nnn      # stable, never reused, survives file moves
title: Human Title
tier: root | core | profile | agents | templates | tooling
status: draft | active | superseded
version: 0.1
audience: [human, model]   # who reads this
load: always | on-task | reference
sessions: [GATE, CONTRACT]   # on-task only: which session types load it
related: [ID, ID]
```

Agent files (`tier: agents`, other than the index) add:

```yaml
lens: partial-failure        # short name; the selection block in CORE-REV-003 uses it
question: "Can state be left inconsistent mid-operation?"
run_when: "Slices with multi-step operations or external systems"
model: sonnet                # Claude Code alias the binding pins: sonnet | opus | haiku
profile: simulation          # omit for a core lens
```

## Field notes

**`id`** — stable identity. Cross-references use IDs, so a file can move without breaking
references. Never reuse an ID. The ID prefix set is whatever is in use; the tooling
builds its citation pattern from the IDs it finds, so a new profile needs no script edit.

**`audience`** — `[human]` means never load into a model context; it is human process
guidance and would only consume budget. `[model]` means the reverse. Most are both. An
imperative cannot derive from a human-only document ([CORE-IMP-001](../core/imperatives.md)).

**`load`** — the context budget control, and the most operationally useful field:

| Value | Meaning |
|---|---|
| `always` | In the standing loadout of every session on a project that uses this tier or profile |
| `on-task` | Loaded by the session types in `sessions:` |
| `reference` | Human lookup only; never loaded automatically |

**`sessions`** — required with `load: on-task`, forbidden otherwise. Each entry is a type
from the `session-types` block in [CORE-SES-001](../core/session-protocol.md). This field is
the only definition of a session's loadout: `build_layer.py` renders the project
template's loadout table from it and `loadout.py --session <TYPE>` prints the file list.
`[]` on a human-only document says explicitly that no session loads it. `tier: root`
documents are the framework's own and never enter a project loadout.

**`model`** — a reviewer on the authoring model shares its blind spots
([CORE-REV-003](../core/reviews/lens-reviews.md)); the default is a different alias from the
one that writes code, and per-lens choice is calibration data, not a rule.

The `always` set must stay small. If it grows past roughly a dozen short documents,
something has been mis-tagged, and the model's effective attention on the actual task
degrades. Audit it quarterly alongside the lesson prune.

## Enforcement

`build_registry.py --check` fails CI if frontmatter is missing, malformed, references an
unknown ID in `related`, names a session type that does not exist, omits `sessions` on an
on-task document, gives an agent file an unknown `model` or `profile`, or if the registry
is stale. `build_layer.py --check` fails CI if anything rendered from frontmatter is stale.
