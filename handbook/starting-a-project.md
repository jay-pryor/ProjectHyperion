---
id: HBK-006
title: Starting a Project
tier: handbook
status: active
audience: [human]
load: never
sessions: []
prevents: A project starting at the code, because nothing describes what the first days ask of the person before any code exists
reader: A person about to start a project under Hyperion, before they have read anything else
related: [HBK-000, HBK-001, HBK-002, HBK-004, HYP-000, CORE-PRN-001, CORE-LFC-001, CORE-SES-001, CORE-CHG-002]
---

# Starting a Project

Every framework document describes the work from its own side, and the reading order
([HBK-000](00-reading-order.md)) says what to read. Neither says what the first days ask
of the person: what you decide, in what order, and when the first line of code is allowed
to exist. Someone who cannot see that shape starts at the code, which is the one order
Hyperion does not permit. These are the stages of a beginning, in plain language, read by
a person about to start a project. They add no rules; each stage names the document that
owns it.

## The stages

| # | Stage | What it asks of you | Finished when |
|---|---|---|---|
| 1 | Describe the thing | Where it runs, who operates it, what it is connected to | You can say it in a paragraph a stranger understands |
| 2 | Set the project up | Which profiles, at which framework version | A session opens, declares its scope, and waits |
| 3 | G0 — what it must never do | Five failure questions, asked of every function | Statements of what must never happen, checkable by a non-programmer |
| 4 | G1 — what it must do | Each requirement, and how anyone would know it is right | Every requirement carries the way it will be judged |
| 5 | G2 — the parts | Where the seams go, and what will be expensive to change later | The parts and their dependencies are drawn and reviewed |
| 6 | G3 — the promises | What each part promises, and which piece of work runs first | Contracts exist, and their tests fail against empty code |

Then the first slice, which [HBK-004](one-slice-session-by-session.md) walks end to end.
Stages 3 to 6 are the four gates ([CORE-LFC-001](../core/lifecycle/00-gates-overview.md));
1 and 2 come before the framework has anything to check.

## 1 — Describe the thing

Before any gate: a paragraph saying what the software does, who operates it, what it is
attached to, and what else is nearby when it runs. It is not a document Hyperion checks.
It is the input the first gate works from, and the reason a model cannot start for you —
it can write code all day and still not know what the payload is bolted to.

## 2 — Set the project up

Someone runs one setup command, which is in the [README](../README.md) under *Consuming
Hyperion*. It copies nothing: the framework is pinned at a version inside the project, so
the rules the project follows can be named and upgraded deliberately. Two decisions are
yours. Which **profile** applies — the toolchain rules for a class of software, and none
is fine to begin with. And who the **reviewer** is at each gate: on a one-person project
that is you, recorded as yourself rather than left blank.

The stage is finished when a session opens with a declaration — what it is doing, what it
may change — and then waits for you ([CORE-SES-001](../core/session-protocol.md)). That
pause is the framework working, not a stall.

## 3 to 6 — the four gates

Each gate answers one question, and the answers are yours, not the model's
([P10](../core/00-principles.md)). What each gate produces, where it goes, and what checks
it, is one table in [HBK-001](artifact-map.md); who does which step is one table in
[HBK-002](who-does-what.md). Three things are worth knowing before you begin.

**No implementation until stage 6 is done.** Not as discipline, but because code written
against undecided interfaces has to be thrown away. Stage 6 itself writes tests — they
come before the thing they test, and failing is what they are supposed to do at first.

**A gate is passed when its artifacts exist and have been reviewed** — not when they are
finished to your satisfaction. The purpose is to stop the next thing from depending on
something undecided. Perfectionism at G1 is as costly as skipping it.

**Being wrong later is planned for.** A gate that turns out to have been wrong is handled
by a named procedure that re-opens the affected part, not by restarting the project
([CORE-CHG-002](../core/change-control/baseline-change-procedure.md)).

## The console: how to see where the project is

The state of a project is not in any document — it is in its records, and the **console**
is how a person reads them. It is a web page you generate from the project, showing the
gates, the hazards, the requirements and what verifies each of them, the findings, and the
handbook. It is what a reviewer reads, and it can be read without opening a source file.

Generate it from the project's own directory, then open `console/index.html` in a browser:

<!-- generated:commands-project -->
    python hyperion/tooling/check_traces.py                    # every trace/ record; --report prints the matrix
    python hyperion/tooling/build_console.py .                 # render console/index.html, the reviewer's artifact
    python hyperion/tooling/check_null_doubles.py .            # every suite must FAIL against its null double
    python hyperion/tooling/check_boundaries.py .              # the real import graph against modules/*/manifest.yaml
    python hyperion/tooling/check_units.py .                   # the type check runs clean and is proved to reject a unit confusion
    python hyperion/tooling/mutation_score.py --slice SL-nn .  # at acceptance; --write records the survivors, --check re-measures
    python hyperion/tooling/check_imperatives.py               # imperatives drifted from their source sections
    python hyperion/tooling/loadout.py --session <TYPE>        # the documents that session type loads
    python hyperion/tooling/init_project.py --upgrade .        # re-render generated blocks after a version bump
    python hyperion/tooling/check_commit.py <base>..HEAD       # paths must match the Session trailer
<!-- /generated -->

The console line is the `build_console.py` one. Regenerate it after anything changes a
record — a gate passing, a review, a slice being accepted — because the page is a
snapshot, not a live view. Everything else in that list is a check; run them before you
trust the page.

## What you do not need

A team, a ticketing system, or an existing hazard register. A single operator can work
every stage above, and the framework records that it was a single operator rather than
pretending otherwise. What you do need is to keep the questions in stages 3 and 4 yours:
they are the two the framework cannot delegate and cannot check for you.
