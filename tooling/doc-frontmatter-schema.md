---
id: TOOL-001
title: Document Frontmatter Schema
tier: tooling
status: active
audience: [human, model]
load: on-task
sessions: [FRAMEWORK]
prevents: Documents and tooling disagreeing about what a document is, so the registry, loadouts, and lens library render from guesses
reader: A FRAMEWORK session adding or re-tagging a document
related: [HYP-000, CORE-SES-001, CORE-IMP-001]
---

# Document Frontmatter Schema

Every Hyperion document carries YAML frontmatter. The registry, the loadout tables, the
lens library, the agent index, and the console's handbook are generated from it, so
frontmatter is the contract between documents and tooling. Read by FRAMEWORK sessions
adding or re-tagging a document.

```yaml
id: CORE-XXX-nnn      # stable, never reused, survives file moves
title: Human Title
tier: root | handbook | core | profile | agents | templates | tooling
status: draft | active | superseded
superseded_by: ID          # required when superseded, forbidden otherwise
audience: [human, model]   # who reads this
load: always | on-task | reference | never
sessions: [GATE, CONTRACT]   # on-task: which session types load it; never: []
prevents: <one sentence: the failure this document prevents>     # P6
reader: <who reads it, and when>                                 # P6
related: [ID, ID]
```

There is no per-document version: the framework's version is the root `VERSION` file,
its history `CHANGELOG.md`, and a document's history is `git log` (one fact, one place,
[P3](../core/00-principles.md)).

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

**`prevents`, `reader`** — [P6](../core/00-principles.md) as schema rather than advice. A
document whose author cannot fill these two fields specifically should not be written.
The registry and the console's handbook show them, so a reader can decide from the index
whether a document is for them.

**`audience`** — `[human]` means never load into a model context; it is human process
guidance and would only consume budget. `[model]` means the reverse. Most are both. An
imperative cannot derive from a human-only document ([CORE-IMP-001](../core/imperatives.md)).

**`load`** — the context budget control, and the most operationally useful field:

| Value | Meaning |
|---|---|
| `always` | In the standing loadout of every session on a project that uses this tier or profile |
| `on-task` | Loaded by the session types in `sessions:` |
| `reference` | Human lookup only; never loaded automatically |
| `never` | No session loads it: `tier: handbook` orientation for the person, rendered by the console. Requires `audience: [human]` and `sessions: []` |

**`sessions`** — required with `load: on-task`, `[]` with `load: never`, forbidden otherwise. Each entry is a type
from the `session-types` block in [CORE-SES-001](../core/session-protocol.md). This field is
the only definition of a session's loadout: `build_layer.py` renders the project
template's loadout table from it and `loadout.py --session <TYPE>` prints the file list.
`[]` on a human-only document says explicitly that no session loads it. `tier: root`
documents are the framework's own and never enter a project loadout; `tier: handbook`
documents ([HBK-000](../handbook/00-reading-order.md)) are read by people, in the console.

**`superseded_by`** — a superseded document points forward, as a decision record does
([CORE-DEC-001](../core/decisions/decision-log.md)). Superseded documents are listed in
their own registry section and excluded from every loadout.

**`model`** — a reviewer on the authoring model shares its blind spots
([CORE-REV-003](../core/reviews/lens-reviews.md)); the default is a different alias from the
one that writes code, and per-lens choice is calibration data, not a rule.

The `always` set must stay small. If it grows past roughly a dozen short documents,
something has been mis-tagged, and the model's effective attention on the actual task
degrades. Audit it quarterly alongside the lesson prune.

## Enforcement

`build_registry.py --check` fails CI if frontmatter is missing, malformed, carries a
`version` field, references an unknown ID in `related` or `superseded_by`, names a session
type that does not exist, omits `sessions` on an on-task document, omits or pads
`prevents` or `reader`, has `superseded_by` without `status: superseded` or the reverse,
gives an agent file an unknown `model` or `profile`, or if the registry is stale.

The same check enforces three rules about bodies, so they are not prose in `CLAUDE.md`
([P2](../core/00-principles.md)):

| Rule | Check |
|---|---|
| Documents stay short | core, profile, handbook, and agent documents: 120 lines; templates: 160 |
| Every rule traces to a principle | every core and profile body cites `P<n>`, or an ID whose document does, transitively |
| One fact, one place ([P3](../core/00-principles.md)) | no sentence of more than twelve words appears in two core or profile documents, outside generated and include blocks |

`build_layer.py --check` fails CI if anything rendered from frontmatter is stale.
