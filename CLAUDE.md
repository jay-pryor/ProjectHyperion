---
id: HYP-002
title: Framework Operating Instructions
tier: root
status: active
audience: [human, model]
load: always
prevents: A framework session that edits process documents without tracing, deduplicating, or regenerating what depends on them
reader: Every FRAMEWORK, REVIEW, and QUERY session in this repository, at declaration
related: [HYP-000, CORE-SES-001, CORE-PRN-001]
---

# Hyperion — Framework Operating Instructions

This repository **is the framework**, not a project built with it. Sessions here edit
process documents. For sessions building software under Hyperion, see
`templates/project-CLAUDE.md`.

## Open every session with (`/framework <scope>`, `/review`, `/query <question>` print it)

    SESSION: <FRAMEWORK | REVIEW | QUERY>
    SCOPE: <the one document or change this session will produce, or the question>
    MAY MODIFY: <explicit paths, or nothing>
    PRINCIPLE: <which of P1-P10 this change serves>

Then stop and wait; do not begin in the same turn. The types are defined in
`core/session-protocol.md` (CORE-SES-001); REVIEW and QUERY have no scope to confirm and do not wait.

## Rules for editing this repository

1. **Every rule traces to a principle.** If a proposed rule cannot be traced to P1–P10 in
   `core/00-principles.md`, either it is wrong or the principles are incomplete. Say which.
   Do not add unanchored rules.

2. **One fact, one place** (P3). Before adding content, search for where the fact already
   lives. Link by ID rather than restating. The single most likely way this framework
   degrades is the same rule appearing in three documents and drifting.

3. **Documents stay short**: 120 lines (160 for templates), checked by `build_registry.py --check`. Split rather than exceed.

4. **Every document declares its failure and its reader** (P6): the `prevents:` and `reader:` fields, checked by the same script.

5. **Prefer a mechanical check to a written rule** (P2). When adding process, first ask
   whether `tooling/` could enforce it instead. A rule that CI can check should be a check
   and a one-line note, not a section.

6. **Frontmatter is mandatory** and must match `tooling/doc-frontmatter-schema.md`. IDs are
   stable and never reused. Cross-references use IDs, not paths.

7. **Regenerate the registry and the operating layer** after any change (IMP-F1, IMP-F3):

       python tooling/build_registry.py && python tooling/build_layer.py

   Verify both with `--check` before finishing. Stale generated output fails CI. This
   repository's `.claude/`, `.hyperion/`, and `.devcontainer/` are outputs (CORE-HRN-001).

8. **Check the imperatives you may have invalidated.** Imperatives derive from sections
   of core; changing a section does not change the imperative derived from it.

       python tooling/check_imperatives.py

   If it flags one, re-read the source section, update the fragment or confirm it still
   holds, then clear with `--accept`. Clearing without re-reading defeats the check.
   Definition and rules: `core/imperatives.md` (CORE-IMP-001).

9. **A rule with no principle is a defect** (IMP-F2, CORE-PRN-001), in `CLAUDE.md` files as
   much as in core. If you cannot trace it, the principles are incomplete — say so — or the
   rule should not exist.

The imperatives this file carries, rendered from `imperatives/framework.yaml`:

<!-- generated:imperatives -->
| # | Imperative | Source |
|---|---|---|
| IMP-F1 | Regenerate the registry after any change to this repository. | TOOL-001#enforcement |
| IMP-F2 | Every rule added to core must trace to a principle. | CORE-PRN-001#principles |
| IMP-F3 | Regenerate the operating layer (`build_layer.py`) after changing any source it renders. | CORE-IMP-001#generated-blocks |
<!-- /generated -->

10. **Do not add a profile speculatively.** Profiles are written when a real project needs
   one, from what that project actually reached for. A profile written in advance encodes
   guesses as rules.

11. **`OPEN:` marks an unresolved decision.** Leave them. Do not resolve one by picking a
   plausible answer; open decisions belong to the human.

## Adding a lens agent

Write a lens only when a slice has needed it. Each agent file needs: the frontmatter
fields in TOOL-001, purpose, permitted inputs, **prohibited inputs**, the verbatim prompt
with the severity include, the output contract, and known weaknesses. The prompt must
state the adversarial framing, restrict to one failure mode, and require every finding
to carry a reproducing test. "Review this code" is not a lens.

## What this repository must not become

A style guide, a coding-standards document, or a software-engineering textbook. Hyperion
covers **process invariants and their enforcement**. Anything a competent engineer or model
already does by default does not belong here; it costs context and prevents nothing.

## Health checks

Run quarterly, with the lesson prune. The numbers a project's records can yield are on
the overview view of its console (`tooling/build_console.py`); read them there.

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
