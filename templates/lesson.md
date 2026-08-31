---
id: TPL-003
title: "Template — Lesson"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-LSN-001]
---

# Template — Lesson

One YAML entry per lesson, in `lessons/`.

```yaml
id: LSN-nnn
date: YYYY-MM-DD
defect: <what actually went wrong, one line>
found_by: <lens review | targeted read | validation | use | field>
root_cause: <why it was possible, not just what happened>

rung: <1-6>
check: <path to the test, lint rule, or type that now prevents it>
promotion_attempted: <higher rungs considered and why they were not possible>

catches: 0
last_catch: null
status: active | archived
```

## Rules

- `check` is mandatory. A lesson with no check is not a lesson
  ([P9](../core/00-principles.md)) — either promote it or discard it.
- `promotion_attempted` exists to stop rung 6 becoming the default. State why a test or
  type constraint was not possible.
- `catches` increments only when the check **fails on real code**. Not when the lesson is
  read or referenced.
- Rung 5–6 entries with zero catches after two quarters are archived.
