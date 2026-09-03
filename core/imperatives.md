---
id: CORE-IMP-001
title: Imperatives
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [FRAMEWORK]
prevents: A CLAUDE.md that summarises core instead of directing it, and an imperative whose source section moved on without it
reader: A FRAMEWORK session touching a fragment or a sourced section
related: [CORE-SES-001, CORE-PRN-001, HYP-002, TOOL-001]
---

# Imperatives

`CLAUDE.md` carries imperatives and pointers; everything else lives in core. That split
fails two ways: an imperative that is really a summary, and an imperative whose source
has moved on without it. This document defines the term and the mechanism that keeps
the layers in step. Read by FRAMEWORK sessions touching a fragment or a sourced section.

## Definition

> An **imperative** is a directive that changes what a session does at a decision point it
> will actually reach, stated so that compliance can be judged without loading any other
> document.

## The three tests

An imperative passes all three. Failing any one means it belongs in core with a pointer,
or nowhere.

**1. Actionable.** It names a decision point the session will reach and says what to do
there. Not a state of the world, not a goal.

**2. Self-sufficient.** Compliance is judgeable from the sentence alone. If the model must
read another document to know whether it complied, that document is the rule and
`CLAUDE.md` should carry only a pointer to it.

**3. Non-default.** A competent model would not already do this. This is the pruning test
and the one to apply hardest: an imperative restating ordinary good practice costs context
in every session and prevents nothing ([P6](00-principles.md)).

Grammatical form is not sufficient. *"Follow good design practice"* is grammatically
imperative and fails tests 2 and 3.

## What is not an imperative

Each of these belongs in core. Most yield an imperative as their **behavioural residue**,
the thing a session must do differently at a specific decision point.

| Kind | Example | Derived imperative |
|---|---|---|
| Principle | Rigour follows reversibility | none directly |
| Definition | The contract is everything a consumer may depend on | Import only from `contract.*` |
| Procedure | Baseline change: impact assessment, migration plan, decision record, re-entry at G2 | Stop if a change would touch `baseline/` |
| Rationale | Models write for the case where everything works | none; it justifies an imperative written elsewhere |
| Description | The registry is generated from frontmatter | Run `build_registry.py` after any change |
| Taxonomy | Three change tiers exist | Stop if the slice cannot be built within existing contracts |

A **procedure** yields a *trigger*, not a summary. `CLAUDE.md` says when to stop; core says
what happens next. Compressing the procedure into `CLAUDE.md` is how this layer bloats.

## Form

- One decision point each. If it contains "and", split it.
- Bounded, not aspirational. "Never edit a conformance test to make it pass" is checkable;
  "prefer clean interfaces" is not.
- **No rationale in the imperative.** The pointer carries the why.
- Every imperative names its source **section**: `CORE-CON-003#the-rule`, the slug of the
  heading the sentence sits under. A document-level source is too broad to check and too
  broad to read; a rule with no source is invented at the operating layer, which is a
  defect ([P3](00-principles.md)).

## Fragments are the source

Imperatives are hand-written in exactly one place: `imperatives/core.yaml` for every
project, `imperatives/framework.yaml` for this repository, and `profiles/<name>/fragment.yaml`
for what a profile adds (imperatives, stop conditions, tier rows, loadout entries,
targeted reads, plugins). Each row is `id, text, source, anchor`. The `anchor` words must
appear in the source section, so a row pointing at a section that does not contain its
rule fails the build instead of waiting to be noticed. A source whose audience excludes
the model is refused: an imperative cannot derive from a document its reader never loads.

## Generated blocks

`tooling/build_layer.py` renders everything a session consumes from these sources: the
imperative, session, stop-condition, loadout, and targeted-read blocks of the project
template; the lens library and agent index from agent frontmatter; the severity include in
every agent prompt; the command blocks of [HYP-000](../README.md) and the template from
`tooling/commands.yaml`; a project's module map from its manifests; and `imperatives.json`.
Rendered text sits between `<!-- generated:name -->` markers and is never edited by hand.
`build_layer.py --check` fails CI when any block is stale, which turns
[P3](00-principles.md) from a rule into a property of the build. Run it with the registry
after any change; both command lines are in the Commands section of HYP-000.

## Keeping the layers in sync

`imperatives.json` records, per imperative, its text, its source section, and a hash of
that section's body. `tooling/check_imperatives.py` has three failure modes:

| Failure | Meaning | Clear it by |
|---|---|---|
| source section changed | the sentence the imperative derives from moved | re-read the section; update the fragment or confirm; `--accept` |
| rendered table differs from the fragment | someone edited the carrying `CLAUDE.md` by hand | `build_layer.py`, or `init_project.py --upgrade` in a project |
| imperative on one side only | a row in the map with no table entry, or the reverse | same |

Hashes are over the section, not the document, so a change elsewhere in a long document
does not fire. `--accept` re-records a hash and is only honest after re-reading; it does
not prove the imperative is still correct, it forces someone to look.

**In a project.** `init_project.py` writes `.hyperion/imperatives.json`, whose hashes are
of the framework sections at the pinned version, beside `.hyperion/version`. The check
looks for that map first and compares it with the project's own `CLAUDE.md`, so a project
whose vendored framework moved on is told to run `init_project.py --upgrade`; `--accept`
is refused there because the map is generated, not confirmed.
