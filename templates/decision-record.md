---
id: TPL-002
title: "Template — Decision Record"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-DEC-001]
---

# Template — Decision Record

```markdown
# DEC-nnn: <title>
Date: YYYY-MM-DD
Status: proposed | accepted | superseded by DEC-nnn
Tier: internal | interface | baseline

## Context
<What forced a decision now. What would happen if it were deferred.>

## Decision
<What was chosen, stated plainly, in one paragraph.>

## Alternatives considered
### <Alternative A>
Rejected because: <specific reason, not "worse">

### <Alternative B>
Rejected because:

## Consequences
- Makes easy:
- Makes hard:
- Locks in:

## Reversal
Cost to undo: <hours | days | weeks | effectively permanent>
Would be triggered by: <what would make us revisit this>
```

The **Reversal** section is your [P1](../core/00-principles.md) classification recorded
at the moment you had the most context. Writing it forces the assessment that determines
how much ceremony the decision deserved.
