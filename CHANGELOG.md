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

## 0.8.0 — 2026-09-03

Four assertions the framework made but nothing verified become checks, and a session's
declared scope is bound to the session rather than to the working tree.

- `check_boundaries.py` validates the real import graph against `modules/*/manifest.yaml`
  in four fatal rules — surface, declared, drawn, acyclic (CORE-CON-003). *Drawn* is new:
  a manifest entry nothing imports is an edge on the G2 diagram that is not in the code,
  and `build_layer.py` draws that diagram from the manifest. IMP-01 gains its one real
  exception — a module's conformance suite is importable from test code.
- `check_units.py` runs the project's type check and then proves that run rejects a
  deliberate unit confusion built from the unit definitions themselves (CORE-CON-001).
  A checker that matched no files passes the first half and fails the second.
- `mutation_score` is a score per module, required at acceptance and ratcheted against the
  highest that module has reached in an accepted slice (CORE-TST-002, CORE-TRC-002). A run
  finding no mutants is an error, not a zero; an unread toolchain major version is refused.
  Survivor severity comes from the hazard register — S2 where a `mitigation_contract` rides
  on the module, S3 elsewhere, which is also when `survivors_triaged` is required.
- The scope hook binds a declaration to the runtime session id under `.hyperion/sessions/`,
  written by the hook and never by the session — a session that could restate its type
  could widen it. Keying it to the working tree failed in the permissive direction two ways
  (CORE-HRN-001). The hook no longer parses paths out of shell commands, which no parse
  makes sound, and denies `Bash` whenever it can write; `check_commit.py` over each commit's
  real paths is the layer that sees the rest, and runs on pushes, not only pull requests.
- HBK-006 *Starting a Project*: the stages of a beginning in plain language, for the person
  who has decided to use Hyperion and has not been told what the first days ask of them.

Upgrading: `mutation_score` on an accepted slice must become a per-module map, so a
`trace/slices.yaml` written under 0.7.0 needs editing before `check_traces.py` passes.

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
