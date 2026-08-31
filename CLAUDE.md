---
id: HYP-002
title: Framework Operating Instructions
tier: root
status: active
version: 0.1
audience: [human, model]
load: always
related: [HYP-000, CORE-SES-001, CORE-PRN-001]
---

# Hyperion — Framework Operating Instructions

This repository **is the framework**, not a project built with it. Sessions here edit
process documents. For sessions building software under Hyperion, see
`templates/project-CLAUDE.md`.

## Open every session with

    SESSION: FRAMEWORK
    SCOPE: <the one document or change this session will produce>
    MAY MODIFY: <explicit paths>
    PRINCIPLE: <which of P1-P10 this change serves>

Then stop and wait. Do not begin in the same turn.

## Rules for editing this repository

1. **Every rule traces to a principle.** If a proposed rule cannot be traced to P1–P10 in
   `core/00-principles.md`, either it is wrong or the principles are incomplete. Say which.
   Do not add unanchored rules.

2. **One fact, one place** (P3). Before adding content, search for where the fact already
   lives. Link by ID rather than restating. The single most likely way this framework
   degrades is the same rule appearing in three documents and drifting.

3. **Documents stay short.** Target under 120 lines. A document that needs more is usually
   two documents. Splitting is cheap because references are by ID.

4. **Every document declares its failure and its reader** (P6). If you cannot name the
   failure a document prevents, do not write it.

5. **Prefer a mechanical check to a written rule** (P2). When adding process, first ask
   whether `tooling/` could enforce it instead. A rule that CI can check should be a check
   and a one-line note, not a section.

6. **Frontmatter is mandatory** and must match `tooling/doc-frontmatter-schema.md`. IDs are
   stable and never reused. Cross-references use IDs, not paths.

7. **Regenerate the registry** after any change (IMP-13, TOOL-001):

       python tooling/build_registry.py

   Verify with `--check` before finishing. A stale registry fails CI.

8. **Check the imperatives you may have invalidated.** `CLAUDE.md` files carry imperatives
   derived from core documents. Changing a core document does not automatically change the
   imperative derived from it, and a session obeying a stale imperative has no way to know.

       python tooling/check_imperatives.py

   If it flags an imperative, re-read the source, update the imperative or confirm it
   still holds, then clear with `--accept`. Clearing without re-reading defeats the check.
   Definition and rules: `core/imperatives.md` (CORE-IMP-001).

9. **A rule with no principle is a defect** (IMP-14, CORE-PRN-001). Applies to imperatives
   in `CLAUDE.md` files as much as to rules in core. If you write an imperative you cannot
   trace, either the principles are incomplete — say so — or the rule should not exist.

10. **Do not add a profile speculatively.** Profiles are written when a real project needs
   one, from what that project actually reached for. A profile written in advance encodes
   guesses as rules.

11. **`OPEN:` marks an unresolved decision.** Leave them. Do not resolve one by picking a
   plausible answer; open decisions belong to the human.

## Adding a lens agent

Write a lens only when a slice has needed it. Each agent file needs: purpose, permitted
inputs, **prohibited inputs**, the verbatim prompt, the output contract, and known
weaknesses.

The prompt must state the adversarial framing, restrict to one failure mode, and require
every finding to carry a reproducing test. A prompt that says "review this code" is not a
lens and should not be added.

## What this repository must not become

A style guide, a coding-standards document, or a general software-engineering textbook.
Hyperion covers **process invariants and their enforcement**. Anything a competent
engineer or a competent model already does by default does not belong here — it costs
context in every session and prevents nothing.

## Health checks

Run quarterly, with the lesson prune:

- **Standing loadout size.** `load: always` should be roughly a dozen short documents.
  Growth means something is mis-tagged and every session's attention is being diluted.
- **Baseline change rate** in projects using the framework. Trending to zero after the
  first month means the gates are calibrated. Staying high means G2 and G3 are not doing
  their job and the framework needs changing, not more discipline.
- **Lens yield.** Lenses producing no admitted findings across several slices should be
  retired or rewritten. A review that never finds anything is a habit, not a control.
- **Rejected-findings list.** Rejected findings that later turned out to be real are
  calibration data for the agent prompts.
- **Imperative drift rate.** Frequent `check_imperatives.py` failures that turn out to need
  no change mean the imperative is sourced to the wrong document — usually a broad one when
  a narrow section is what it actually derives from. Re-source it rather than tolerating the
  noise.
