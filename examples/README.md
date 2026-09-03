# Examples

Projects built **under** Hyperion, not documents **of** it. Files here carry no
frontmatter and are not in the registry. CI runs the framework tooling against them,
so each example is also a test fixture for `tooling/`.

## `minimal/`

A point-mass projectile with drag, under the Simulation profile. Small enough to read
in twenty minutes; complete enough to exercise every mechanism the framework names.

| Part | What it shows |
|---|---|
| `modules/atmosphere/`, `modules/trajectory/` | A contract with numbered clauses (`CONTRACT.md`), the code surface (`contract.py`), a conformance suite whose tests name their clauses, a private implementation, and a model-owned unit test that is never traced |
| `modules/*/null_double.py` | One per module: a deliberately trivial implementation the conformance suite **must fail against** (CORE-TST-002). Run the check and watch both fail |
| `baseline/` | Unit-carrying types, and a fault-point harness that lets a conformance test force a mid-operation failure |
| `validation/` | Analytical, determinism, and envelope cases, grouped by validation class and separate from the test suite |
| `trace/` | Every record the framework names: requirements, hazards, slices, findings (a mutation triage of 56, fixed and rejected, plus one still open), reviews (gates, targeted reads, an inspection), needs, assumptions, goals, changes |
| `docs/` | A slice definition with its acceptance record, a decision record with rejected alternatives, a module map |
| `.claude/`, `.devcontainer/` | The generated Claude Code binding (CORE-HRN-001): one skill per session type, the read-only lens agents, the scope hook, the plugin list, the container |

### Open a session

In Claude Code, from `examples/minimal/`, type the session's skill: `/implement SL-02 drag
in the integrator`, `/conformance SL-02 envelope cases`, `/review SL-01 verification
numerical-integrity`, `/query why is atmosphere a separate module`. The skill prints the
declaration, which the hook binds to that session id, and from then on the hook denies a
write outside that type's globs. `/review` runs the lenses as parallel subagents and appends
their findings; it fixes nothing.

### Run it

    cd examples/minimal
    pip install pytest pyyaml
    pytest -q                                      # 27 passed; writes trace/results.xml
    python ../../tooling/check_traces.py           # chain intact, every record validated
    python ../../tooling/check_traces.py --report  # the matrix; exits 1 over a broken chain
    python ../../tooling/build_console.py .        # console/index.html: open it in a browser
    python ../../tooling/check_null_doubles.py .   # both suites fail against their null double, per file
    pip install "mutmut>=3,<4"
    python ../../tooling/mutation_score.py --slice SL-01 --check .  # ~7 min; re-measures the recorded score

The null-double check and the mutation run write their own results elsewhere, so
`trace/results.xml` keeps the real run. The console is one self-contained page: the
overview, hazards, the requirement matrix, module map, plan, findings and reviews,
decisions and changes, and a handbook tab rendering the framework documents. It is
generated on every CI run and uploaded as a build artifact; `console/` is not committed.
Open console for the example repo with:

    cd examples/minimal
    python ../../tooling/build_console.py

### What is ahead of the tooling

Nothing in `trace/`. Every record and every field here is validated by
`check_traces.py` against CORE-TRC-002 and CORE-TRC-003, including the results file,
the contract clauses, the fault point, and the gate-derived strictness. The generated
blocks in `CLAUDE.md` and the diagram in `docs/module-map.md` are rendered by
`init_project.py --upgrade` from the framework pinned in `.hyperion/version`, and
`build_layer.py --check` fails CI if they go stale.

### What a finished rung 2 looks like

SL-01 records `mutation_score: 0.762` and `survivors_triaged: true`. The first run
scored 0.608 over 143 mutants and its 56 survivors are FND-004 to FND-059, which is the
part worth reading. Twenty-two were killed by three conformance tests, and one of those
tests exists only because the triage found the contract incomplete: nothing promised
anything about the sample arrays, so a reversed clock and a range read off the wrong
point both survived. C-108 was added under CHG-003 and FND-060 closed with it. The other
thirty-four are rejected, and their reasons carry the information: fifteen say only that
no promise SL-01 claims reaches the drag term, and those are raised again when SL-02
measures `trajectory` against the drag clause it will add; four say that C-101's
tolerance, not the suite, is what cannot see them, which is FND-061, open in the backlog.

Rung 2 runs on `trajectory` alone here. The score is an acceptance record, `atmosphere`
is reached only by SL-02, and SL-02 stays `in_progress` so the example also shows a slice
in flight. That is a choice, not an omission.
