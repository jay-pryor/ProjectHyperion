---
id: HBK-000
title: Reading Order
tier: handbook
status: active
version: 0.1
audience: [human]
load: never
sessions: []
related: [HYP-000, HYP-001, HBK-001, HBK-002, HBK-003, HBK-004, HBK-005, CORE-PRN-001, CORE-LFC-001]
---

# Reading Order

A framework of forty-odd short documents has no front door: a new reader opens the
registry, reads in path order, and meets the rules before the reason for them. This is
the front door. Read by a person joining a project built under Hyperion, or evaluating
the framework, who does not read code. No session loads any handbook document; the
project console renders them under its Handbook tab.

## What the handbook is

Five aids drawn from the framework as it stands and from the example project. They add
no rules. Where an aid and a core document disagree, the core document is right and the
aid has a defect; every aid cites the document it summarises so the disagreement can be
found.

| Aid | Question it answers | Document |
|---|---|---|
| Artifact map | What does each gate produce, where does it live, what checks it? | [HBK-001](artifact-map.md) |
| Who does what | Which of human, model, and check owns each step? | [HBK-002](who-does-what.md) |
| What do I do now | Something happened; which session type is next? | [HBK-003](what-do-i-do-now.md) |
| One slice, session by session | What does the loop look like when it runs? | [HBK-004](one-slice-session-by-session.md) |
| Glossary | Which systems-engineering term is this? | [HBK-005](glossary.md) |

## The order

The order the [README](../README.md) gives, with the aids placed where they help.

1. **The example first.** `examples/minimal/` is a complete, tiny project: two modules,
   six requirements, two hazards, one accepted slice, every record filled in
   ([examples/README.md](../examples/README.md)). Twenty minutes. Then
   [HBK-004](one-slice-session-by-session.md), which walks its first slice.
2. **Principles and gates.** [CORE-PRN-001](../core/00-principles.md), then
   [CORE-LFC-001](../core/lifecycle/00-gates-overview.md). Every rule in the framework
   traces to one of the ten principles; a rule that does not is a defect.
   [HBK-001](artifact-map.md) shows the gates and their outputs on one page.
3. **The line between human and model.** P10 in the principles, then
   [HBK-002](who-does-what.md), then [CORE-SES-001](../core/session-protocol.md),
   which is the mechanism that keeps the line under time pressure.
4. **The slice loop.** [CORE-LFC-006](../core/lifecycle/slice-loop.md) and
   [HBK-003](what-do-i-do-now.md). The loop's job is to answer "what next"; the tree
   answers it from the situation's side.
5. **The records.** [CORE-TRC-001](../core/traceability/traceability.md) for why,
   [CORE-TRC-002](../core/traceability/trace-records.md) and
   [CORE-TRC-003](../core/traceability/trace-logs.md) for the schemas. Everything the
   console shows comes from these.
6. **One profile at a time**, and only after the core. Start with its `PROFILE.md`
   ([SIM-000](../profiles/simulation/PROFILE.md) for simulation). Profile documents
   assume the core vocabulary.
7. **Reviews, findings, lessons, changes** as they arise:
   [CORE-REV-001](../core/reviews/00-review-taxonomy.md),
   [CORE-REV-005](../core/reviews/review-findings-handling.md),
   [CORE-LSN-001](../core/lessons/lesson-ladder.md),
   [CORE-CHG-001](../core/change-control/change-tiers.md).

Keep [HBK-005](glossary.md) open throughout.

## How to read a framework document

Every document opens with the failure it prevents and who reads it ([P6](../core/00-principles.md)).
If the first paragraph does not name a failure you recognise, skip the document until
it does. The frontmatter's `load` field says who consumes it: `always` documents cost
every session context and are deliberately few; `on-task` documents name their session
types; `reference` and `never` documents are for people. The
[registry](../REGISTRY.md) lists all of them by tier and is generated, so it is current.

## Where the state is

Not in any document. Gate passage, slice status, findings, and reviews are records in
`trace/`, and the console renders them. A `CLAUDE.md` that states the current gate is
stale by construction, which is why the template no longer has such a section.
