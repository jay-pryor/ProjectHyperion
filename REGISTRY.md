---
id: HYP-001
title: Registry
tier: root
status: active
audience: [human, model]
load: reference
prevents: A hand-maintained index that rots and is trusted anyway
reader: Anyone locating a document by ID or tier; never loaded by a session
related: [HYP-000]
---

# Registry

<!-- GENERATED FILE — do not edit. Run: python tooling/build_registry.py -->

Hyperion 0.6.0 (from `VERSION`; history in `CHANGELOG.md`)

Generated 2026-09-02 · 56 documents

## Standing context loadout

Documents tagged `load: always`. Keep this list short — every entry costs
context budget in every session.

- `HYP-002` [Framework Operating Instructions](CLAUDE.md)
- `HYP-000` [Hyperion](README.md)
- `CORE-PRN-001` [Principles](core/00-principles.md)
- `CORE-CHG-001` [Change Tiers](core/change-control/change-tiers.md)
- `CORE-CON-003` [Boundary Enforcement](core/contracts/boundary-enforcement.md)
- `CORE-LFC-001` [Gate Overview](core/lifecycle/00-gates-overview.md)
- `CORE-LFC-006` [Slice Loop](core/lifecycle/slice-loop.md)
- `CORE-SES-001` [Session Protocol](core/session-protocol.md)
- `SIM-000` [Simulation Profile](profiles/simulation/PROFILE.md)
- `SIM-DET-001` [Determinism](profiles/simulation/determinism.md)

## root

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `HYP-003` | Changelog | active | reference |  | A framework whose version and what changed in it are recoverable only from commit archaeology | [CHANGELOG.md](CHANGELOG.md) |
| `HYP-002` | Framework Operating Instructions | active | always |  | A framework session that edits process documents without tracing, deduplicating, or regenerating what depends on them | [CLAUDE.md](CLAUDE.md) |
| `HYP-000` | Hyperion | active | always |  | A new reader or project starting without knowing what the framework is for, how it is laid out, or how to consume it at a pinned version | [README.md](README.md) |
| `HYP-001` | Registry | active | reference |  | A hand-maintained index that rots and is trusted anyway | [REGISTRY.md](REGISTRY.md) |

## handbook

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `HBK-000` | Reading Order | active | never |  | A new reader meeting the rules before the reason for them by reading the registry in path order | [handbook/00-reading-order.md](handbook/00-reading-order.md) |
| `HBK-001` | The Artifact Map | active | never |  | A reader unable to tell whether an artifact is a record, prose, or ceremony because the whole picture exists only in pieces | [handbook/artifact-map.md](handbook/artifact-map.md) |
| `HBK-005` | Glossary | active | never |  | Attention spent on words instead of the work by a systems engineer who already has a term for the thing | [handbook/glossary.md](handbook/glossary.md) |
| `HBK-004` | One Slice, Session by Session | active | never |  | A reader who has only the session table being unable to tell a stop from a failure | [handbook/one-slice-session-by-session.md](handbook/one-slice-session-by-session.md) |
| `HBK-003` | What Do I Do Now | active | never |  | A person who has just watched a test fail not knowing which session type comes next | [handbook/what-do-i-do-now.md](handbook/what-do-i-do-now.md) |
| `HBK-002` | Who Does What | active | never |  | The human-model line moving toward whoever is faster under time pressure | [handbook/who-does-what.md](handbook/who-does-what.md) |

## core

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `CORE-PRN-001` | Principles | active | always |  | Rules accumulating with no anchor, so that no one can say why a rule exists or when it should go | [core/00-principles.md](core/00-principles.md) |
| `CORE-CHG-002` | Baseline Change Procedure | active | on-task | BASELINE | A change every module inherits being made with less ceremony than a slice, or without a migration for data already in the old shape | [core/change-control/baseline-change-procedure.md](core/change-control/baseline-change-procedure.md) |
| `CORE-CHG-001` | Change Tiers | active | always |  | A behavioural interface change passing as an internal one, or a tier argued rather than classified by path | [core/change-control/change-tiers.md](core/change-control/change-tiers.md) |
| `CORE-CON-003` | Boundary Enforcement | active | always |  | A module reaching past another's contract because it is faster, after which the contract no longer describes what consumers depend on | [core/contracts/boundary-enforcement.md](core/contracts/boundary-enforcement.md) |
| `CORE-CON-002` | Conformance Suites | active | on-task | CONTRACT, CONFORMANCE | Behavioural promises a signature cannot express going unchecked, and a stub silently violating the contract it stands in for | [core/contracts/conformance-suites.md](core/contracts/conformance-suites.md) |
| `CORE-CON-001` | Contract Definition | active | on-task | CONTRACT | Consumers depending on behaviour that was never promised, which makes every internal change an interface change | [core/contracts/contract-definition.md](core/contracts/contract-definition.md) |
| `CORE-DEC-001` | Decision Log | active | on-task | GATE, CONTRACT, BASELINE | Relitigating a settled decision because the rejected alternatives and the reversal cost were never written down | [core/decisions/decision-log.md](core/decisions/decision-log.md) |
| `CORE-HRN-001` | Harness Binding | active | on-task | GATE, CONTRACT, CONFORMANCE, IMPLEMENT, REVIEW, INTEGRATE, LESSON, BASELINE, QUERY, FRAMEWORK | Session rules staying honour-based when the runtime could deny the write, pin the model, and withhold the tool | [core/harness.md](core/harness.md) |
| `CORE-IMP-001` | Imperatives | active | on-task | FRAMEWORK | A CLAUDE.md that summarises core instead of directing it, and an imperative whose source section moved on without it | [core/imperatives.md](core/imperatives.md) |
| `CORE-LSN-001` | Lesson Ladder | active | on-task | LESSON | Lessons recorded as prose that nothing retrieves, so the same defect recurs with a longer lessons file | [core/lessons/lesson-ladder.md](core/lessons/lesson-ladder.md) |
| `CORE-LFC-001` | Gate Overview | active | always |  | Code depending on things not yet decided, and gate state living in a human's head or a stale CLAUDE.md line | [core/lifecycle/00-gates-overview.md](core/lifecycle/00-gates-overview.md) |
| `CORE-LFC-002` | G0 — Hazard & Context | active | on-task | GATE | Hazards discovered after the architecture they should have driven exists, and silent wrong output never named as a hazard | [core/lifecycle/g0-hazard-context.md](core/lifecycle/g0-hazard-context.md) |
| `CORE-LFC-003` | G1 — Requirements & Validation Basis | active | on-task | GATE | Requirements that pass every test and are wrong, because no one wrote down how correctness would be known | [core/lifecycle/g1-requirements-validation-basis.md](core/lifecycle/g1-requirements-validation-basis.md) |
| `CORE-LFC-004` | G2 — Architecture | active | on-task | GATE | A decomposition where one requirement change touches three modules, and a dependency diagram that no longer matches the code | [core/lifecycle/g2-architecture.md](core/lifecycle/g2-architecture.md) |
| `CORE-LFC-005` | G3 — Contracts & Slice Plan | active | on-task | GATE | Code written before its contract and suite exist, and a first slice that validates nothing about the architecture | [core/lifecycle/g3-contracts.md](core/lifecycle/g3-contracts.md) |
| `CORE-LFC-006` | Slice Loop | active | always |  | Not knowing what to do next after G3, and a contract quietly widened mid-slice | [core/lifecycle/slice-loop.md](core/lifecycle/slice-loop.md) |
| `CORE-REV-001` | Review Taxonomy | active | on-task | REVIEW | One review asked to do two jobs answering neither, and lens reviews mistaken for a substitute for the human read | [core/reviews/00-review-taxonomy.md](core/reviews/00-review-taxonomy.md) |
| `CORE-REV-002` | Gate Reviews | active | on-task |  | Self-review degrading into rubber-stamping, and a gate passed with no record of who reviewed it and how | [core/reviews/gate-reviews.md](core/reviews/gate-reviews.md) |
| `CORE-REV-003` | Lens Reviews | active | on-task | GATE, REVIEW | A primed or general-purpose model review that manufactures confidence instead of findings | [core/reviews/lens-reviews.md](core/reviews/lens-reviews.md) |
| `CORE-REV-005` | Review Findings Handling | active | on-task | REVIEW, CONFORMANCE, LESSON | A backlog of plausible model output nobody can act on, and a failing test written by the session that then fixes it | [core/reviews/review-findings-handling.md](core/reviews/review-findings-handling.md) |
| `CORE-REV-004` | Targeted Human Reads | active | on-task |  | Human attention spread evenly over implementation code instead of concentrated where models are predictably weak | [core/reviews/targeted-human-reads.md](core/reviews/targeted-human-reads.md) |
| `CORE-SES-001` | Session Protocol | active | always |  | A test, contract, or baseline written in a context that had already seen the thing it was meant to constrain | [core/session-protocol.md](core/session-protocol.md) |
| `CORE-TST-001` | Test Strategy | active | on-task | CONFORMANCE | Tests that agree with the implementation's misreading, and coverage chased as a percentage instead of by clause | [core/testing/test-strategy.md](core/testing/test-strategy.md) |
| `CORE-TST-002` | Tests Are Tested | active | on-task | CONFORMANCE, IMPLEMENT, INTEGRATE | A conformance suite that checks shape, not behaviour, and so passes a wrong implementation as readily as a right one | [core/testing/tests-are-tested.md](core/testing/tests-are-tested.md) |
| `CORE-TRC-003` | Trace Records — Logs and Results | active | on-task | REVIEW, INTEGRATE, LESSON, BASELINE | Findings, reviews, and changes living in prose where they cannot be counted, filtered, or checked, so gate state ends up in a human's head | [core/traceability/trace-logs.md](core/traceability/trace-logs.md) |
| `CORE-TRC-002` | Trace Records — Registers | active | on-task | GATE, CONTRACT, CONFORMANCE | A requirement, hazard, or slice record validated by whoever last edited it, and a named artifact with no home | [core/traceability/trace-records.md](core/traceability/trace-records.md) |
| `CORE-TRC-001` | Traceability | active | on-task | GATE | Trace tables written as intentions that nothing checks, so a renamed test or a deleted requirement stays invisible | [core/traceability/traceability.md](core/traceability/traceability.md) |

## profile

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `SIM-000` | Simulation Profile | draft | always |  | Simulation software that produces plausible wrong numbers being treated as correct because it runs and its tests pass | [profiles/simulation/PROFILE.md](profiles/simulation/PROFILE.md) |
| `SIM-DET-001` | Determinism | draft | always |  | A regression diff that cannot distinguish a real change from run-to-run variation | [profiles/simulation/determinism.md](profiles/simulation/determinism.md) |
| `SIM-RDS-001` | Targeted Human Reads — Simulation | draft | on-task |  | Unit, frame, initialisation, and tolerance defects that are consistent on each side of a boundary and invisible to a model reviewing one module | [profiles/simulation/targeted-reads.md](profiles/simulation/targeted-reads.md) |
| `SIM-VAL-001` | Validation Basis | draft | on-task | GATE, CONFORMANCE | A simulation result presented with more confidence than its evidence supports, or run outside the envelope it was validated for | [profiles/simulation/validation-basis.md](profiles/simulation/validation-basis.md) |

## agents

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `AGT-000` | Agent Index | active | on-task | REVIEW | A lens run with the wrong inputs, on the wrong slice, or with a primed prompt because no one place lists the lenses and their rules | [agents/00-agent-index.md](agents/00-agent-index.md) |
| `AGT-LNS-003` | Agent — Determinism Lens | draft | on-task | REVIEW | Two runs with identical config and seed differing, undetected until a regression diff cannot be trusted | [agents/lens-determinism.md](agents/lens-determinism.md) |
| `AGT-LNS-002` | Agent — Numerical Integrity Lens | draft | on-task | REVIEW | Plausible-looking wrong numbers from unit, frame, initialisation, integration, or floating-point defects passing review | [agents/lens-numerical-integrity.md](agents/lens-numerical-integrity.md) |
| `AGT-LNS-001` | Agent — Partial Failure Lens | active | on-task | REVIEW | State left inconsistent when an operation fails partway, in code written for the case where everything works | [agents/lens-partial-failure.md](agents/lens-partial-failure.md) |
| `AGT-VAL-001` | Agent — Specification Review | active | on-task | REVIEW | A contract that, implemented perfectly, would still not satisfy its requirement, found only after code depends on it | [agents/specification-review.md](agents/specification-review.md) |
| `AGT-VER-001` | Agent — Verification Review | active | on-task | REVIEW | An implementation that does not satisfy a contract clause passing because the suite did not cover the clause | [agents/verification-review.md](agents/verification-review.md) |

## templates

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `TPL-001` | Template — Module Contract | active | on-task | CONTRACT | A contract that states signatures and omits the error conditions, promises, and tolerances people forget | [templates/contract.md](templates/contract.md) |
| `TPL-002` | Template — Decision Record | active | on-task | GATE, CONTRACT, BASELINE | A decision recorded without its rejected alternatives or its reversal cost | [templates/decision-record.md](templates/decision-record.md) |
| `TPL-004` | Template — Hazard Trace Entry | active | on-task | GATE | A hazard record whose never-statement a non-programmer cannot check, or whose mitigation points at nothing | [templates/hazard-entry.md](templates/hazard-entry.md) |
| `TPL-003` | Template — Lesson | active | on-task | LESSON | A lesson with no check, scored by how memorable it was rather than by what it caught | [templates/lesson.md](templates/lesson.md) |
| `TPL-007` | Template — Module CLAUDE.md | active | on-task | LESSON | Module-specific detail loaded into every session, or a module file growing into a second contract | [templates/module-CLAUDE.md](templates/module-CLAUDE.md) |
| `TPL-008` | Template — Module Map | active | on-task | GATE | A dependency diagram that drifts from the manifests it is supposed to depict | [templates/module-map.md](templates/module-map.md) |
| `TPL-006` | Template — Project CLAUDE.md | active | on-task | FRAMEWORK | A project operating layer that restates core in its own words and drifts from it | [templates/project-CLAUDE.md](templates/project-CLAUDE.md) |
| `TPL-005` | Template — Slice Definition | active | on-task | GATE, CONTRACT | A slice without observable acceptance criteria, or one that grows past what can be reviewed in one sitting | [templates/slice-definition.md](templates/slice-definition.md) |

## tooling

| ID | Title | Status | Load | Sessions | Prevents | Path |
|---|---|---|---|---|---|---|
| `TOOL-001` | Document Frontmatter Schema | active | on-task | FRAMEWORK | Documents and tooling disagreeing about what a document is, so the registry, loadouts, and lens library render from guesses | [tooling/doc-frontmatter-schema.md](tooling/doc-frontmatter-schema.md) |

## Draft documents

- `SIM-000` Simulation Profile
- `SIM-DET-001` Determinism
- `SIM-RDS-001` Targeted Human Reads — Simulation
- `SIM-VAL-001` Validation Basis
- `AGT-LNS-003` Agent — Determinism Lens
- `AGT-LNS-002` Agent — Numerical Integrity Lens

