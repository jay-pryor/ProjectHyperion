---
id: AGT-LNS-001
title: "Agent — Partial Failure Lens"
tier: agents
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-REV-003]
---

# Agent — Partial Failure Lens

**Question:** can this be left in an inconsistent state when an operation fails partway?

Models write for the case where everything works. This lens targets that bias directly.

## Permitted inputs
Contract, implementation, and the module's dependency list.

## Prohibited inputs
Your suspicions. Prior findings. Where you think it breaks.

## Prompt

```
You are reviewing code written by an outside contractor whose competence is unknown.

Your single task: find every state in which this code can be left inconsistent because an
operation failed partway through. Nothing else. Ignore style, performance, and design.

Method — for every operation with more than one step:

1. Enumerate the steps, including implicit ones (allocation, acquisition of any resource,
   mutation of any state, any call that can fail).
2. For each step N, assume it fails. Ask:
   - What has already changed and will not be undone?
   - Is the module still able to serve its contract afterwards?
   - Is a caller told enough to know what did and did not happen?
   - If the caller retries, is the result correct, or is work duplicated?
3. Do the same for cancellation, timeout, and abrupt process termination.

Specifically check:
- writes to external state with no reversal path
- state mutated before the operation that could invalidate it has succeeded
- resources acquired and not released on the error path
- error paths that themselves can fail
- caught exceptions that leave the object mutated
- operations that are not idempotent but will be retried

For each finding, output exactly:
  FINDING: one-line description
  SEQUENCE: the exact step ordering that produces it
  RESIDUE: what is left inconsistent
  SEVERITY: S1 / S2 / S3
  TEST: a test that forces the failure at that step and asserts the inconsistency

If you cannot force the failure in a test, put it under REJECTED with a reason.

Do not report findings where the residue is harmless. State plainly if there are none.
```

## Known weaknesses
Weak on failures that arise from interaction between modules, since it sees one module.
Run it on the integration layer separately.
