---
id: CORE-CON-003
title: Boundary Enforcement
tier: core
status: active
audience: [human, model]
load: always
prevents: A module reaching past another's contract because it is faster, after which the contract no longer describes what consumers depend on
reader: Every session, standing; whoever configures the import lint for a profile's language
related: [CORE-CON-001, CORE-PRN-001]
---

# Boundary Enforcement

Without mechanical enforcement, module boundaries are fiction within a month
([P2](../00-principles.md)). Someone reaches past a contract because it is faster, and
after that the contract no longer describes what consumers depend on.

## The rule

> No module may import another module's internals. Only `modules/<name>/contract.*` is
> importable from outside the module — and, from test code alone, that module's
> conformance suite, which is the other half of what is promised
> ([CORE-CON-001](contract-definition.md)).

## Dependency manifest

Each module declares its permitted imports, and `check_boundaries.py` validates the real
import graph against that declaration. The manifest is therefore the one place the graph
is stated: `build_layer.py` draws the [G2 architecture
diagram](../lifecycle/g2-architecture.md) from it, and the check makes the drawing true.
Without the check the manifest is a picture, and the picture drifts — the usual death of
architecture documentation.

```yaml
module: trajectory
allowed_imports:
  - baseline/types
  - baseline/logging
  - modules/atmosphere/contract
```

Four rules, each **failing the build**. Not a warning; a warning is a rule that must be
remembered.

| Rule | Fails when |
|---|---|
| surface | A file outside the module imports anything but `modules/<m>/contract*`, or reaches its `conformance/**` from production code |
| declared | A module imports a `baseline/` or `modules/` path its manifest does not list |
| drawn | A manifest lists a path no file in the module imports — an edge on the map that is not in the code |
| acyclic | Modules form a cycle, or `baseline/` imports a module |

Adding an entry is an Interface-tier decision that leaves a visible diff. Dropping the
last import of one is a change of the same size, which is why *drawn* is a rule rather
than housekeeping.

## Circular dependencies

Rejected by *acyclic*, on the real graph rather than the declared one. A cycle means the
decomposition is wrong; fix the decomposition rather than the check. `baseline/` is the
substrate every module inherits, so a baseline importing a module is the same defect one
layer down.

## Enforcement in other languages

`check_boundaries.py` reads Python imports. A profile whose language is not Python
configures the equivalent below and runs it in the same CI position; the manifest stays
the declaration, and the four rules stay the rules.

| Language | Mechanism |
|---|---|
| TypeScript / JS | `dependency-cruiser`, or ESLint `no-restricted-imports` with path patterns |
| Rust | Module privacy plus `pub(crate)`; the compiler does most of it |
| C / C++ | Header discipline plus a CI grep; weakest of the three, compensate with review |

## Escape hatch

There isn't one. If a module genuinely needs something not exposed by a contract, the
contract is wrong — change it through the Interface gate, which takes minutes. The cost
of the gate is deliberately lower than the cost of arguing for an exception.
