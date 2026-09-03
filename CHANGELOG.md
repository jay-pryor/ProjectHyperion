---
id: HYP-003
title: Changelog
tier: root
status: active
audience: [human]
load: reference
prevents: A framework whose version and what changed in it are recoverable only from commit archaeology
reader: Anyone moving a project's vendored framework to a new tag, before running init_project.py --upgrade
related: [HYP-000]
---

# Changelog

One heading per release, newest first. The heading equals the content of `VERSION`, and CI
refuses a `v*` tag whose version has no heading here. Per-document history is `git log`.

## 0.7.0 — 2026-09-03

Single sources for the last two restated facts, and the release itself becomes a session.

- Every command a human runs is a row in `tooling/commands.yaml` carrying its context;
  README, the project template, and each project's `CLAUDE.md` render their command
  blocks from it, and `--check` fails CI when a rendered block drifts.
- The seven validation classes are the table in CORE-LFC-003 and nothing else; SIM-VAL-001
  says what each class means in simulation rather than listing eight of its own.
- Acceptance requires a recorded `targeted_read` review naming the slice. A targeted read
  that leaves no record was a statement of intent, not a control (CORE-REV-004).
- RELEASE is a session type (CORE-SES-001, IMP-F4): `VERSION` and `CHANGELOG.md` belong to
  it, not to the FRAMEWORK sessions it summarises. The tag job fails a release whose
  changelog entry is not the newest commit in the range.

## 0.6.0 — 2026-09-02

The consultant review's order of attack, steps 1 to 10, closing every MVP finding.

- Trace records have one schema (CORE-TRC-002, CORE-TRC-003) and `check_traces.py`
  resolves every reference against the thing itself; gate state is a review row.
- The session table is data in CORE-SES-001; the scope hook, the commit checker, and the
  template table read it. BASELINE, QUERY, and FRAMEWORK session types added.
- Imperatives are fragments sourced to sections; `build_layer.py` renders everything a
  session consumes, and `init_project.py` pins a project to a framework version.
- Tests are tested (CORE-TST-002): null doubles, mutation score, fault points.
- The Claude Code binding (CORE-HRN-001) is generated: skills, read-only lens agents,
  hooks, devcontainer. The console renders project state; nothing writes it.
- `examples/minimal` is the fixture; `tooling/tests` runs every script against it.
- P7 names verification, specification review, and validation; the agent that asks "is
  the contract right" is `specification-review` (ID unchanged). Local hazard register.
- Frontmatter gains `prevents` and `reader`, loses `version`; `VERSION` and this file
  are the version. Line limits, principle trace, and duplicate sentences are checks.

## 0.5 — 2026-08-31

Commit `fac99e6`. Documents carried `version: 0.1` individually; no changelog existed.
