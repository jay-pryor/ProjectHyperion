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
    pip install pytest
    pytest -q                                                  # 27 passed
    pytest --collect-only -q | grep '::' > trace/tests.txt     # generated, never committed
    python ../../tooling/check_traces.py --strict              # chain intact
    python ../../tooling/check_traces.py --report              # the matrix
    ATMOSPHERE_IMPL=null pytest -q modules/atmosphere/conformance   # 4 failed, 4 passed

### What is ahead of the tooling

The current `check_traces.py` validates `requirements.yaml`, `hazards.yaml`, and
`slices.yaml`, and only the fields it knows. The example also carries fields and files
the checker does not yet read: `kind`, `verification_method`, `validation_class`,
`validated_by`, `status` on requirements; `register`, `failure_mode`, `likelihood` on
hazards; `contracts` on slices; and the `findings`, `reviews`, `needs`, `assumptions`,
`goals`, and `changes` records. They are the proposed record schema, written here first
so the checker has something real to grow into. Nothing in them is validated until it is.
