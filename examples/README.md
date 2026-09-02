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
| `modules/atmosphere/null_double.py` | A deliberately trivial implementation the conformance suite **must fail against**. Run it and watch it fail |
| `baseline/` | Unit-carrying types, and a fault-point harness that lets a conformance test force a mid-operation failure |
| `validation/` | Analytical, convergence, envelope, and determinism cases, separate from the test suite |
| `trace/` | Every record the framework names: requirements, hazards, slices, findings (admitted and rejected), reviews (gates, targeted reads, an inspection), needs, assumptions, goals, changes |
| `docs/` | A slice definition with its acceptance record, a decision record with rejected alternatives, a module map |

### Run it

    cd examples/minimal
    pip install pytest pyyaml
    pytest -q                                      # 27 passed; writes trace/results.xml
    python ../../tooling/check_traces.py           # chain intact, every record validated
    python ../../tooling/check_traces.py --report  # the matrix; exits 1 over a broken chain
    ATMOSPHERE_IMPL=null pytest -q modules/atmosphere/conformance --junitxml=/tmp/nd.xml   # 4 failed, 4 passed

The checker runs the whole suite's results, so run `pytest -q` again after the null
double run if you did not redirect its results file.

### What is ahead of the tooling

Nothing in `trace/`. Every record and every field here is validated by
`check_traces.py` against CORE-TRC-002 and CORE-TRC-003, including the results file,
the contract clauses, the fault point, and the gate-derived strictness. What the example
carries that no tool yet reads: the placeholder generated blocks in `CLAUDE.md` (the
operating-layer generator, M1), the acceptance-record fields `mutation_score` and
`survivors_triaged` on a slice (the mutation run, M7, which no slice here has had), and
`docs/module-map.md`, whose diagram is hand-drawn from the manifests until the console
draws it (M8).
