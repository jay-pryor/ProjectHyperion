---
id: CORE-SES-001
title: Session Protocol
tier: core
status: active
audience: [human, model]
load: always
prevents: A test, contract, or baseline written in a context that had already seen the thing it was meant to constrain
reader: Every session at declaration, and the tooling that enforces scope
related: [CORE-PRN-001, CORE-LFC-006, CORE-REV-001, CORE-CHG-001]
---

# Session Protocol

Prevents the failure no diff can show: a test, contract, or baseline written in a context
that had already seen the thing it was meant to constrain ([P8](00-principles.md)). Read
by every session at declaration and by the tooling that enforces scope.

## Session types

The block below is the single source; the template's session table, the scope hook, and
the commit checker are generated from it ([P3](00-principles.md)). A write is permitted
only if its path matches `may_modify` and nothing in `must_not_modify`; globs are
project-relative. `scope`: where the type is valid. `project_files`: what a session loads
from the project; the framework documents it loads are those whose `sessions:` names it (TOOL-001).

```yaml session-types
GATE:
  purpose: Produce or review G0-G3 artifacts and record gate passage
  scope: project
  may_modify: [docs/**, trace/**]
  must_not_modify: [modules/**, baseline/**, validation/**]
  project_files: [docs/decisions/**, trace/**]
CONTRACT:
  purpose: Author or change a contract and the acceptance criteria that depend on it
  scope: project
  may_modify: [modules/*/contract.*, modules/*/CONTRACT.md, docs/slices/**, docs/decisions/**, trace/**]
  must_not_modify: [modules/*/src/**, modules/*/conformance/**, modules/*/tests/**, baseline/**, validation/**]
  project_files: [modules/<module>/CONTRACT.md, docs/slices/<slice>.md]
CONFORMANCE:
  purpose: Write conformance suites and validation cases from human criteria
  scope: project
  may_modify: [modules/*/conformance/**, validation/**, "**/tolerance.yaml", trace/**]
  must_not_modify: [modules/*/src/**, modules/*/contract.*, modules/*/CONTRACT.md, modules/*/tests/**, baseline/**]
  project_files: [modules/<module>/CONTRACT.md, docs/slices/<slice>.md]
IMPLEMENT:
  purpose: Build a slice to contract
  scope: project
  may_modify: [modules/*/src/**, modules/*/tests/**, trace/**]
  must_not_modify: [modules/*/contract.*, modules/*/CONTRACT.md, modules/*/conformance/**, baseline/**, validation/**, fixtures/**]
  project_files: [modules/<module>/CONTRACT.md, modules/<module>/CLAUDE.md, docs/slices/<slice>.md]
REVIEW:
  purpose: Run one agent from agents/ and record its findings
  scope: both
  may_modify: [trace/findings.yaml]
  must_not_modify: [modules/**, baseline/**, validation/**, docs/**]
  note: append only
  loads: one agent file plus the inputs it permits, nothing else
INTEGRATE:
  purpose: Wire modules, run slices end to end, record fixture output
  scope: project
  may_modify: [integration/**, fixtures/**, trace/**]
  must_not_modify: [modules/*/contract.*, modules/*/CONTRACT.md, modules/*/conformance/**, "**/tolerance.yaml", baseline/**, validation/**]
  project_files: [modules/*/CONTRACT.md, docs/slices/<slice>.md]
LESSON:
  purpose: Promote findings to checks and complete the acceptance record
  scope: project
  may_modify: [lessons/**, lint/**, modules/*/CLAUDE.md, docs/slices/**, trace/**]
  must_not_modify: [modules/*/src/**, modules/*/contract.*, modules/*/conformance/**, baseline/**]
  project_files: [docs/slices/<slice>.md, lessons/**]
BASELINE:
  purpose: Change shared substrate under a decision record cited in the declaration
  scope: project
  may_modify: [baseline/**, docs/decisions/**, trace/**]
  must_not_modify: [modules/**, validation/**]
  project_files: [docs/decisions/<DEC-nnn>.md]
QUERY:
  purpose: Answer a question about the framework or the project
  scope: both
  may_modify: []
  must_not_modify: ["**"]
  project_files: ["**"]   # no ceiling; the question decides
FRAMEWORK:
  purpose: Change the framework itself
  scope: framework
  may_modify: [core/**, profiles/**, agents/**, templates/**, tooling/**, examples/**, handbook/**, imperatives/**, .github/**, .claude/**, .devcontainer/**, .hyperion/**, .gitignore, CLAUDE.md, README.md, REGISTRY.md]
  must_not_modify: []   # nothing by path; every change traces to a principle (HYP-002)
```

## The load-bearing prohibitions

- **CONFORMANCE must not implement** — [P8](00-principles.md).
- **IMPLEMENT must not touch `conformance/` or `contract.*`.** When a conformance test
  fails, read the **contract** to decide *which is wrong, the test or the code* (P8). If the
  slice needs a contract change, stop; an Interface change runs ([CORE-CHG-001](change-control/change-tiers.md)) — [P4](00-principles.md).
- **REVIEW appends findings and nothing else** — [P9](00-principles.md).
- **BASELINE is entered only with a decision record cited in the declaration**
  ([CORE-CHG-002](change-control/baseline-change-procedure.md)) — [P1](00-principles.md).
- **QUERY modifies nothing and may read anything**, human-only documents included. It
  ends by naming the session type that makes any change it uncovers — [P10](00-principles.md).

## Mechanical backstop

Session discipline is honour-based, but its main violation is visible in the diff.
`tooling/check_commit.py` reads the block above and rejects a commit whose paths fall outside
its `Session:` trailer's type, and the harness denies the write itself ([CORE-HRN-001](harness.md)):
not proof the sessions were separate, but the shortcut made inconvenient ([P2](00-principles.md)).

## Declaration, stop, and escalate

Every session opens with a declaration of type, scope, and permitted files, in the form
the project `CLAUDE.md` gives, so scope is committed to **before** anything is touched
and drift is visible against it. REVIEW and QUERY have no scope and do not wait.

A session that hits a stop condition ends with a written statement of the condition. It
does not work around it, and it does not ask permission to. Stop conditions are listed in
`CLAUDE.md`; they are the primary defence against architectural decisions made silently.
An ambiguity is a stop condition: a session that finds two defensible readings of a
criterion, a clause, or an instruction states both readings and ends. Picking one
silently is the model deciding what the problem is ([P10](00-principles.md)).
