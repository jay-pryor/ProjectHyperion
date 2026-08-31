---
id: HYP-000
title: Hyperion
tier: root
status: active
version: 0.1
audience: [human, model]
load: always
related: [CORE-PRN-001, CORE-LFC-001]
---

# Hyperion

A systems-engineering framework for building software with LLM assistance, where the
human works at architectural level and the models work at implementation level.

## What problem this solves

Unstructured LLM-assisted development fails in three specific ways:

| Symptom | Cause | Hyperion's answer |
|---|---|---|
| Whack-a-mole bugs | No regression net | [CORE-TST-001](core/testing/test-strategy.md), [CORE-LSN-001](core/lessons/lesson-ladder.md) |
| Architecture needing rework mid-build | Contracts and schemas not settled before code depended on them | [CORE-LFC-004](core/lifecycle/g2-architecture.md), [CORE-LFC-005](core/lifecycle/g3-contracts.md) |
| Not knowing what to do next | No ordered backlog with acceptance criteria | [CORE-LFC-006](core/lifecycle/slice-loop.md) |

## Structure

Hyperion is **core + profiles**.

- **`core/`** — process invariants. Domain-independent. Applies to every project.
- **`profiles/`** — toolchain, test harness, and gate artifacts for a class of software.
  A project may instantiate more than one (see [Profile composition](profiles/simulation/PROFILE.md)).
- **`agents/`** — ready-to-use prompts for machine reviews. One file per review type.
- **`templates/`** — scaffolds for the artifacts the gates produce.
- **`tooling/`** — mechanical enforcement: registry generation, CI checks.
- **`CLAUDE.md`** — operating instructions for sessions editing *this repository*.
  Projects get their own, from [templates/project-CLAUDE.md](templates/project-CLAUDE.md).

## Navigation

[REGISTRY.md](REGISTRY.md) is the index. It is **generated**, not hand-maintained —
run `python tooling/build_registry.py` after any change. CI fails if it is stale.

## Starting a new project

1. Read [CORE-PRN-001 Principles](core/00-principles.md) and
   [CORE-LFC-001 Gate overview](core/lifecycle/00-gates-overview.md).
2. Read the relevant profile's `PROFILE.md`.
3. Copy [templates/project-CLAUDE.md](templates/project-CLAUDE.md) to the project root as
   `CLAUDE.md` and fill it in. Nothing else is loaded automatically; that file is the
   entry point for every session.
4. Work the gates in order. Add `modules/<name>/CLAUDE.md` per module as modules appear.

## Reading order for a new person

Core first, one profile at a time. Do not attempt to learn a profile before the core;
the profile documents assume the core vocabulary.

## Status

Version 0.1. Core is drafted, including the [session protocol](core/session-protocol.md)
and the CLAUDE.md operating layer. The simulation profile is partial and contains open
decisions marked `OPEN:`. Web, Embedded, and Mobile profiles are not written, by design —
profiles are written when a real project needs one.
