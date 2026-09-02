---
id: TPL-007
title: "Template — Module CLAUDE.md"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [LESSON]
related: [TPL-006, CORE-LSN-001]
---

# Template — Module CLAUDE.md

Copy to `modules/<name>/CLAUDE.md`. Loaded only when working inside that module, which is
what keeps module-specific detail out of every other session's context budget.

Keep it under 40 lines. If it grows past that, the content probably belongs in the
contract or has failed to be promoted up the [lesson ladder](../core/lessons/lesson-ladder.md).

---

```markdown
# Module: <name>

Purpose: <one sentence, copied from the contract — do not restate it differently>
Contract: `contract.<ext>` · Version <n>

## Allowed imports

<Copied from the dependency manifest. Anything else fails CI.>

- baseline/<...>
- modules/<other>/contract

## Conventions specific to this module

<Only what differs from project-wide conventions. If it applies project-wide, it belongs
in the root CLAUDE.md, not here.>

- <e.g. all angles in radians internally; degrees only at the contract boundary>
- <e.g. state is immutable; step() returns a new state rather than mutating>

## Rung-5 lessons

<Lessons that could not be promoted to a type, test, lint rule, or template. Each must
name why promotion failed. Prune anything with zero catches after two quarters.>

- LSN-nnn: <one line> — promotion blocked because <reason>

## Known sharp edges

<Things that have bitten before and are not yet checkable. This section should shrink
over time. If it is growing, checks are not being written.>
```
