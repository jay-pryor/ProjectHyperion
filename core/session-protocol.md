---
id: CORE-SES-001
title: Session Protocol
tier: core
status: active
version: 0.1
audience: [human, model]
load: always
related: [CORE-PRN-001, CORE-LFC-006, CORE-REV-001, CORE-CHG-001]
---

# Session Protocol

Prevents the failure no diff can show: a test, contract, or baseline written in a context
that had already seen the thing it was meant to constrain ([P8](00-principles.md)). Read
by every session at declaration and by the tooling that enforces scope.

## Session types

The block below is the single source; the project template's session table, the scope
hook, and the commit checker are generated from it ([P3](00-principles.md)). A write is
permitted only if its path matches `may_modify` and nothing in `must_not_modify`. Globs
are project-relative. `scope` says where the type is valid: a project, this repository, or both.

```yaml session-types
GATE:
  purpose: Produce or review G0-G3 artifacts and record gate passage
  scope: project
  may_modify: [docs/**, trace/**]
  must_not_modify: [modules/**, baseline/**, validation/**]
  loadout: [hyperion/core/lifecycle/g<n>-*.md]
CONTRACT:
  purpose: Author or change a contract and the acceptance criteria that depend on it
  scope: project
  may_modify: [modules/*/contract.*, modules/*/CONTRACT.md, docs/slices/**, docs/decisions/**, trace/**]
  must_not_modify: [modules/*/src/**, modules/*/conformance/**, modules/*/tests/**, baseline/**, validation/**]
  loadout: [CORE-CON-001, CORE-CON-002, TPL-001]
CONFORMANCE:
  purpose: Write conformance suites and validation cases from human criteria
  scope: project
  may_modify: [modules/*/conformance/**, validation/**, "**/tolerance.yaml", trace/**]
  must_not_modify: [modules/*/src/**, modules/*/contract.*, modules/*/CONTRACT.md, modules/*/tests/**, baseline/**]
  loadout: [CORE-CON-002, CORE-TST-001, modules/<module>/CONTRACT.md, docs/slices/<slice>.md]
IMPLEMENT:
  purpose: Build a slice to contract
  scope: project
  may_modify: [modules/*/src/**, modules/*/tests/**, trace/**]
  must_not_modify: [modules/*/contract.*, modules/*/CONTRACT.md, modules/*/conformance/**, baseline/**, validation/**, fixtures/**]
  loadout: [modules/<module>/CONTRACT.md, modules/<module>/CLAUDE.md, docs/slices/<slice>.md]
REVIEW:
  purpose: Run one agent from agents/ and record its findings
  scope: both
  may_modify: [trace/findings.yaml]   # append only
  must_not_modify: [modules/**, baseline/**, validation/**, docs/**]
  loadout: [hyperion/agents/<lens>.md]   # plus the inputs that file permits, nothing else
INTEGRATE:
  purpose: Wire modules, run slices end to end, record fixture output
  scope: project
  may_modify: [integration/**, fixtures/**, trace/**]
  must_not_modify: [modules/*/contract.*, modules/*/CONTRACT.md, modules/*/conformance/**, "**/tolerance.yaml", baseline/**, validation/**]
  loadout: [modules/*/CONTRACT.md, docs/slices/<slice>.md]
LESSON:
  purpose: Promote findings to checks and complete the acceptance record
  scope: project
  may_modify: [lessons/**, lint/**, modules/*/CLAUDE.md, docs/slices/**, trace/**]
  must_not_modify: [modules/*/src/**, modules/*/contract.*, modules/*/conformance/**, baseline/**]
  loadout: [CORE-LSN-001, TPL-003]
BASELINE:
  purpose: Change shared substrate under a decision record cited in the declaration
  scope: project
  may_modify: [baseline/**, docs/decisions/**, trace/**]
  must_not_modify: [modules/**, validation/**]
  loadout: [CORE-CHG-002, CORE-LFC-004, docs/decisions/<DEC-nnn>.md]
QUERY:
  purpose: Answer a question about the framework or the project
  scope: both
  may_modify: []
  must_not_modify: ["**"]
  loadout: ["**"]   # no ceiling; the question decides
FRAMEWORK:
  purpose: Change the framework itself
  scope: framework
  may_modify: [core/**, profiles/**, agents/**, templates/**, tooling/**, examples/**, .github/**, CLAUDE.md, README.md, REGISTRY.md]
  must_not_modify: []   # nothing by path; every change traces to a principle (HYP-002)
  loadout: [HYP-002, CORE-PRN-001, TOOL-001]
```

## The load-bearing prohibitions

Already in the block; restated because these are the ones argued with under time pressure.

- **CONFORMANCE must not implement** — [P8](00-principles.md).
- **IMPLEMENT must not touch `conformance/` or `contract.*`.** When a conformance test
  fails, read the **contract** to decide *which is wrong, the test or the code* (P8). If the
  slice needs a contract change, stop; an Interface change runs ([CORE-CHG-001](change-control/change-tiers.md)) — [P4](00-principles.md).
- **REVIEW appends findings and nothing else** — [P9](00-principles.md).
- **BASELINE is entered only with a decision record cited in the declaration**
  ([CORE-CHG-002](change-control/baseline-change-procedure.md)) — [P1](00-principles.md).
- **QUERY modifies nothing and may read anything**, human-only documents included. It ends
  by naming the session type that makes any change it uncovers — [P10](00-principles.md).

## Mechanical backstop

Session discipline is honour-based, but its main violation is visible in the diff. The
commit checker, generated from the block above, rejects a commit whose touched paths span
session types or fall outside the type in its `Session:` trailer. Until it exists, apply its
first two rules by hand: a commit touching both `src/**` and `conformance/**` fails, and so
does one touching `src/**` and `contract.*`. It does not prove the sessions were separate;
it makes the shortcut inconvenient ([P2](00-principles.md)).

## Declaration, stop, and escalate

Every session opens with a declaration of type, scope, and permitted files, in the form
the project `CLAUDE.md` gives, so that scope is committed to **before** anything is
touched and drift is visible against it. REVIEW and QUERY have no scope to confirm and do not wait.

A session that hits a stop condition ends with a written statement of the condition. It
does not work around it, and it does not ask permission to. Stop conditions are listed in
`CLAUDE.md`; they are the primary defence against architectural decisions made silently.
