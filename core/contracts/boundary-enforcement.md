---
id: CORE-CON-003
title: Boundary Enforcement
tier: core
status: active
version: 0.1
audience: [human, model]
load: always
related: [CORE-CON-001, CORE-PRN-001]
---

# Boundary Enforcement

Without mechanical enforcement, module boundaries are fiction within a month
([P2](../00-principles.md)). Someone reaches past a contract because it is faster, and
after that the contract no longer describes what consumers depend on.

## The rule

> No module may import another module's internals. Only `modules/<name>/contract.*` is
> importable from outside the module.

## Enforcement mechanisms by language

| Language | Mechanism |
|---|---|
| TypeScript / JS | `dependency-cruiser`, or ESLint `no-restricted-imports` with path patterns |
| Python | `import-linter` contracts; `__init__.py` exposing only the contract surface |
| Rust | Module privacy plus `pub(crate)`; the compiler does most of it |
| C / C++ | Header discipline plus a CI grep; weakest of the four, compensate with review |

The check runs in CI and **fails the build**. Not a warning. A warning is a rule that
must be remembered.

## Dependency manifest

Each module declares its permitted imports. CI validates the actual import graph against
the manifest, which means the [G2 architecture diagram](../lifecycle/g2-architecture.md)
cannot drift from reality — the usual death of architecture documentation.

```yaml
module: trajectory
allowed_imports:
  - baseline/types
  - baseline/logging
  - modules/atmosphere/contract
```

An import not on the list fails CI. Adding one is an Interface-tier decision that leaves
a visible diff.

## Circular dependencies

Rejected by CI. A cycle means the decomposition is wrong; fix the decomposition rather
than the check.

## Escape hatch

There isn't one. If a module genuinely needs something not exposed by a contract, the
contract is wrong — change it through the Interface gate, which takes minutes. The cost
of the gate is deliberately lower than the cost of arguing for an exception.
