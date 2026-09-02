---
id: CORE-CON-001
title: Contract Definition
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [CONTRACT]
related: [CORE-PRN-001, CORE-CON-002, CORE-CON-003, CORE-CHG-001]
---

# Contract Definition

> **The contract is everything a consumer is permitted to depend on. Anything not in the
> contract file or its conformance suite is not promised.**

This single sentence is the load-bearing definition in Hyperion. It is what makes
Internal changes free.

## Location

One file per module: `modules/<name>/contract.*`. It is the module's **sole export
surface**. Consumers import from it and from nothing else, enforced mechanically
([CORE-CON-003](boundary-enforcement.md)).

## Contents

A contract has seven parts. Parts 1–3 are usually expressible in the type system; 4–7
usually are not, and are the parts people forget.

1. **Purpose** — one sentence. If it needs "and", the module may be wrong.
2. **Operations** — signatures, with parameter and return types.
3. **Data shapes** — types crossing the boundary. Units and reference frames stated
   explicitly, in the type name where the language allows it.
4. **Error conditions** — every way each operation can fail, and how failure is signalled.
   "Throws on invalid input" is not a contract; the specific conditions are.
5. **Behavioural promises** — ordering, idempotency, determinism, tolerance, null and
   empty semantics, concurrency safety, side effects.
6. **Performance envelope** — where it matters. Complexity, latency budget, memory bound.
7. **Requirement trace** — requirement and hazard IDs this contract satisfies.

## Units and frames

Any quantity crossing a module boundary carries its unit and, where relevant, its
reference frame — in the type, not in a comment. `metres_per_second`, `ecef_position`,
`body_rates_radps`. Comments do not survive refactoring; types do.

This is not pedantry. Unit and frame confusion at interfaces is among the highest-value
defect classes to design out, and it is invisible to a model reviewing one module in
isolation because each side is internally consistent.

## Tolerances

A tolerance is a correctness claim, not a constant. Every tolerance a contract states,
and every epsilon, threshold, or convergence criterion an implementation hard-codes,
carries a stated justification naming its basis: an analytical bound, a reference
dataset, a measurement, or a decision record. A number with no basis is a plausible
guess dressed as a promise, and the review that finds it cannot tell the two apart.

## What a contract is not

Not documentation of how the module works. A consumer reading the contract should learn
nothing about the implementation — if they can infer it, the contract is leaking, and
someone will eventually depend on the inference.

## Versioning

Contracts carry a version. Interface changes increment it. Where two consumers cannot
migrate together, run both versions side by side rather than blocking — that is
cheaper than a coordinated change and it is the modularity paying for itself.

Template: [templates/contract.md](../../templates/contract.md).
