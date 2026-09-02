---
id: CORE-LSN-001
title: Lesson Ladder
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [LESSON]
related: [CORE-REV-005, CORE-PRN-001, CORE-CHG-001]
---

# Lesson Ladder

Recording lessons is easy. Retrieval is the hard part — after a year you have 200
entries, and a model that reads them all at session start has spent its context budget on
mostly-irrelevant history.

The answer is promotion: every lesson climbs to the strongest available enforcement, and
the prose entry is the last resort rather than the default ([P9](../00-principles.md)).

## The ladder

| Rung | Enforcement | Why it is better than the rung below | Cost |
|---|---|---|---|
| 1 | **Type / compiler constraint** | Cannot be ignored; fails before running | Sometimes impossible |
| 2 | **Test** (conformance or property) | Runs automatically, cannot be forgotten | Low |
| 3 | **Lint or CI rule** | Runs automatically, applies repo-wide | Medium; false positives |
| 4 | **Template or scaffold change** | Makes the right thing the easy thing | Low |
| 5 | **Module convention note** | Loaded only with that module's context | Low value |
| 6 | **Global lessons file** | Read by everything, costs context every session | Last resort |

Always ask: *can this go one rung higher?* Most lessons that feel like rung 6 are
actually rung 2. A rung-2 conformance test needs a contract clause to cite first: a
CONTRACT session adds the under-specified promise and a CONFORMANCE session encodes it,
in the Interface sequence ([CORE-CHG-001](../change-control/change-tiers.md)), so the
test derives from the clause rather than from the defect ([P8](../00-principles.md)).

> If a lesson cannot be converted into any check at all, it is usually a war story rather
> than a lesson. It belongs in your head, not in the model's context.

## Scoring

Each lesson carries a **catch count**: the number of times the check it produced has
actually failed on real code.

Score by catches, not by references or by how memorable the incident was. A lesson that
has never fired is a lesson that is either already designed out or was never a real
pattern.

```yaml
id: LSN-014
date: 2026-03-11
defect: Frame conversion applied twice when input already in body frame
rung: 2
check: modules/attitude/conformance/invariants.py::test_frame_idempotent
catches: 3
last_catch: 2026-05-02
status: active
```

## Pruning

Reviewed quarterly.

- **Rung 5–6 with zero catches after two quarters** → archive.
- **Rung 5–6 with catches** → attempt promotion; the catches prove it is a real pattern.
- **Rung 1–3 with zero catches** → keep. A check that never fires is cheap and may be
  preventing the defect rather than failing to find it.

The asymmetry is deliberate: prose costs context every session, automated checks cost
nothing after they are written.

## Context loadout

Only rung 5–6 lessons ever enter a prompt, and only the ones relevant to the module in
hand. Rungs 1–4 are already in the build and need no context at all — which is the whole
point of promoting them.
