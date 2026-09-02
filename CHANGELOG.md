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
