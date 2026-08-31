---
id: CORE-SES-001
title: Session Protocol
tier: core
status: active
version: 0.1
audience: [human, model]
load: always
related: [CORE-PRN-001, CORE-LFC-006, CORE-REV-001]
---

# Session Protocol

The normative definition of session types. `CLAUDE.md` is the operational restatement of
this document; rationale lives here, imperatives live there.

## Why sessions are the enforcement mechanism

Several Hyperion rules cannot be enforced by CI because they are about **what a model
knew when it wrote something**, not about the artifact produced.

[P8](00-principles.md) is the clearest case: a conformance suite written in the same
session as the implementation is contaminated even if it looks identical to a clean one.
The contamination is invisible in the diff. The only available control is to keep the two
activities in separate sessions with separate contexts.

Session type is therefore a first-class concept, declared at the start of every session
and constraining what may be touched.

## The seven session types

| Type | Purpose | May modify | Must not modify |
|---|---|---|---|
| **GATE** | Produce or review G0–G3 artifacts | Gate artifacts, decision records | Any code |
| **CONTRACT** | Author or change a contract | `contract.*`, contract docs | `src/`, any conformance test |
| **CONFORMANCE** | Write conformance suites from acceptance criteria | `conformance/` | `src/`, `contract.*` |
| **IMPLEMENT** | Build a slice to contract | `src/`, `tests/` | `contract.*`, `conformance/`, `baseline/` |
| **REVIEW** | Run one agent from `agents/` | Nothing | Everything |
| **INTEGRATE** | Wire modules, run slices end to end | Integration code, fixtures | `contract.*`, `conformance/` |
| **LESSON** | Promote findings to checks | Lessons, lint rules, conformance | `src/` |

## The load-bearing prohibitions

**CONFORMANCE must not implement.** The suite is written from human acceptance criteria.
A session that has designed an implementation writes a suite shaped around it.

**IMPLEMENT must not touch `conformance/`.** This is the one that will be violated under
time pressure, because editing the test is always the fastest way to make it pass. When a
conformance test fails, the question is *which is wrong, the test or the code* — answered
by reading the **contract**, never by making the test green.

**IMPLEMENT must not touch `contract.*`.** Widening a contract mid-slice is how a
disciplined project quietly becomes an undisciplined one. If the slice cannot be built
within existing contracts, the session stops and an Interface gate runs
([CORE-CHG-001](change-control/change-tiers.md)).

**REVIEW modifies nothing.** A reviewer that can fix things stops reporting and starts
patching, and the finding is never recorded as a lesson.

## Mechanical backstop

Session discipline is honour-based within a session, but its main violation is visible in
the diff and can be caught:

```
CI: a commit touching both src/** and conformance/** fails.
CI: a commit touching both src/** and contract.* fails.
```

Split the work into two commits from two sessions. The check does not prove the sessions
were separate, but it makes the shortcut inconvenient, which is most of the benefit
([P2](00-principles.md)).

## Declaration

Every session opens with a declaration of type, scope, and permitted files. See the
project `CLAUDE.md`. The declaration exists so that scope is committed to **before**
anything is touched, and so that a drifting session is visible against its own stated
scope rather than against your memory of what you asked for.

## Stop and escalate

A session that hits a stop condition ends with a written statement of the condition. It
does not work around it, and it does not ask permission to work around it. Stop conditions
are listed in `CLAUDE.md` and are the primary defence against the failure mode this
framework exists to prevent: architectural decisions being made silently, one convenient
shortcut at a time.
