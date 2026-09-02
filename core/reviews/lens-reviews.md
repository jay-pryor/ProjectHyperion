---
id: CORE-REV-003
title: Lens Reviews
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-REV-001, CORE-REV-005]
---

# Lens Reviews

Machine review by a fresh model instance, one failure mode at a time.

## The five rules

**1. Fresh context, every time.** A model that wrote the code cannot review it; it will
defend its own reasoning. Start a new session with no history.

**2. No priming.** Give it the contract, the acceptance criteria, and the code. Do **not**
give it your suspicion, your reasoning, or where you think the bug is. A primed model
finds what you told it to find and reports it as an independent discovery, which is worse
than no review because it manufactures false confidence.

What a reviewer inevitably carries: the project `CLAUDE.md` loads into every session, so
a REVIEW session sees its imperatives and stop conditions. Those are rules about conduct,
not suspicions about the code, and are acceptable residue. Nothing else is: project state
is never restated in `CLAUDE.md` (gate and slice are records, rendered by the console),
and each lens runs as a generated read-only agent definition whose prompt is
self-contained and instructs it to disregard project operating instructions other than
the read-only restriction. The definitions are generated from `agents/` by the harness
binding, which is not yet written.

**3. One lens per session.** Named failure mode, nothing else. General review returns
generic advice.

**4. Every finding carries a reproducing test or a proposed clause.** Severity plus the
artifact; a finding with neither is rejected with a reason. Admission forms and the
rejected list: [CORE-REV-005](review-findings-handling.md).

**5. Adversarial framing.** "Review code from a contractor whose competence is unknown"
produces sharper output than "review our code". Stated in every agent prompt.

## The lens library

Core lenses, applicable to any profile:

| Lens | Looks for | Agent |
|---|---|---|
| Verification | Does implementation satisfy the contract | [verification-review](../../agents/verification-review.md) |
| Validation | Is the contract itself wrong | [validation-review](../../agents/validation-review.md) |
| Partial failure | States left inconsistent when an operation fails midway | [lens-partial-failure](../../agents/lens-partial-failure.md) |
| Error paths | Paths that are never exercised, swallowed errors, wrong recovery | *(to write)* |
| Boundary & input | Empty, null, min, max, malformed, adversarial input | *(to write)* |
| Resource exhaustion | Unbounded growth, leaks, allocation under load | *(to write)* |
| Concurrency | Races, reentrancy, shared mutable state | *(to write)* |
| Contract drift | Implementation has grown promises the contract does not make | *(to write)* |

Profile lenses extend this. Simulation adds
[numerical integrity](../../agents/lens-numerical-integrity.md) and
[determinism](../../agents/lens-determinism.md).

## Selecting lenses per slice

Not every lens on every slice. Select by what the slice touches:

- Touches persisted data → boundary, partial failure, migration
- Touches numerical core → numerical integrity, determinism
- Touches external system → partial failure, error paths, resource exhaustion
- Any slice → verification, plus validation on the contract it implements

Two to four lenses per slice is the working range.

## The two passes you will forget

Run **verification** and **validation** as separate sessions. Validation — *is the
contract wrong* — is the more valuable of the two and the one that gets skipped, because
by slice time the contract feels settled. It is not settled; it was written before
anything was built.

## Known limitation

Blind spots correlate between the writing model and the reviewing model, especially on
domain assumptions, unit and frame conventions, and requirement interpretation. Lens
reviews supplement [targeted human reads](targeted-human-reads.md); they do not replace
them. Running more lenses does not close a correlated gap.
