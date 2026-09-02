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
| `validation/` | Analytical, convergence, envelope, and determinism cases, separate from the test suite |
| `trace/` | Every record the framework names: requirements, hazards, slices, findings (admitted and rejected), reviews (gates, targeted reads, an inspection), needs, assumptions, goals, changes |
| `docs/` | A slice definition with its acceptance record, a decision record with rejected alternatives, a module map |

### Run it

    cd examples/minimal
    pip install pytest pyyaml
    pytest -q                                      # 27 passed; writes trace/results.xml
    python ../../tooling/check_traces.py           # chain intact, every record validated
    python ../../tooling/check_traces.py --report  # the matrix; exits 1 over a broken chain
    python ../../tooling/check_null_doubles.py .   # both suites fail against their null double, per file
    pip install mutmut
    python ../../tooling/mutation_score.py --slice SL-01 .   # score and survivor rows, printed, not written

The null-double check and the mutation run write their own results elsewhere, so
`trace/results.xml` keeps the real run.

### What is ahead of the tooling

Nothing in `trace/`. Every record and every field here is validated by
`check_traces.py` against CORE-TRC-002 and CORE-TRC-003, including the results file,
the contract clauses, the fault point, and the gate-derived strictness. The generated
blocks in `CLAUDE.md` and the diagram in `docs/module-map.md` are rendered by
`init_project.py --upgrade` from the framework pinned in `.hyperion/version`, and
`build_layer.py --check` fails CI if they go stale. The acceptance-record fields
`mutation_score` and `survivors_triaged` are absent from SL-01 because its survivors
have not been triaged by a human; `mutation_score.py --write` fills them.
