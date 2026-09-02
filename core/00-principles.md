---
id: CORE-PRN-001
title: Principles
tier: core
status: active
version: 0.1
audience: [human, model]
load: always
related: [HYP-000]
---

# Principles

Every rule in Hyperion derives from one of these. If a rule cannot be traced to a
principle, delete the rule. If a principle stops being true, the rules under it are
suspect.

## P1 — Rigour follows reversibility

Ceremony is justified by the cost of unwinding a decision, not by the decision's
importance. LLM-generated implementation is cheap to regenerate; interfaces, data
schemas, and shared substrate are not. Spend process where the door is one-way.
Everything downstream inherits a baseline change, so the heaviest change must never be
the one made with the least ceremony: it is entered only under a recorded decision.

Consequence: [CORE-CHG-001](change-control/change-tiers.md), the BASELINE session type.

## P2 — Enforcement beats instruction

A rule that must be remembered will eventually not be followed, including by you, and
especially at 7pm. Prefer, in order: a compiler error, a failing test, a lint rule, a
CI check, a template that makes the right thing easiest, a written rule.

Consequence: boundary enforcement, design tokens, the lesson ladder.

## P3 — One fact, one place

Each fact lives in exactly one document. Others link to it by ID. Duplication is how
documentation starts lying.

## P4 — The contract is the promise

A consumer may depend on a module's contract and nothing else. Anything not in the
contract file or its conformance suite is not promised and may change without notice.
Widening a contract mid-slice is how a disciplined project quietly becomes an
undisciplined one; the session building the slice may not touch the contract.

Consequence: [CORE-CON-001](contracts/contract-definition.md).

## P5 — Attention is the scarce resource

Model capability is not uniform. Human attention goes where models are weakest and
where automated checks cannot reach — not spread evenly over the codebase, and never
on line-reading implementation.

Consequence: [CORE-REV-004](reviews/targeted-human-reads.md).

## P6 — Every artifact names its failure and its reader

Before creating any document, state which failure it prevents and who or what reads
it. An artifact that fails both tests is ceremony. An artifact read only once is a
liability, because it will drift from the code and then mislead.

## P7 — Verification and validation are different activities

Verification: does the implementation satisfy the contract. Validation: is the contract
the right one. A model asked to do both at once does neither. They are separate gates,
separate reviews, and separate agents.

## P8 — Tests are written against requirements, not against implementations

A model asked to write implementation and tests together writes tests that agree with
its own misreading. Contract-level tests are written from acceptance criteria, before
implementation, in a separate session. The contamination is invisible in the diff, so
context separation is the only control: a session that has designed an implementation
writes a suite shaped around it, and a session that can edit a failing test will make it
pass rather than read the contract.

Consequence: [CORE-SES-001](session-protocol.md).

## P9 — A lesson that cannot become a check is not a lesson

Recording is easy; retrieval is the hard part. Every lesson is promoted to the
strongest available enforcement or discarded. A reviewer that can fix things stops
reporting and starts patching, and the finding is never recorded to become a lesson.

Consequence: [CORE-LSN-001](lessons/lesson-ladder.md).

## P10 — The human owns the problem, the model owns the solution

Requirements, hazards, decomposition, interfaces, and acceptance criteria are human
work. Implementation is model work. The framework exists to keep that line intact
under time pressure. A model asked a question starts editing, because a fix looks more
helpful than an answer; a question is answered by naming the change, not making it.
