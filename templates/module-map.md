---
id: TPL-008
title: "Template — Module Map"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [GATE]
related: [CORE-LFC-004, CORE-CON-003]
---

# Template — Module Map

The G2 artifact ([CORE-LFC-004](../core/lifecycle/g2-architecture.md)). Prevents the
diagram drifting from the dependency manifests: the diagram is rendered from
`modules/*/manifest.yaml` by `init_project.py --upgrade`, so there is nothing to keep in
step. The table is hand-written; it says what the manifests cannot. Read at G2 and G3, and
by whoever plans a slice.

Copy to `docs/module-map.md`. `init_project.py` creates it if absent.

---

```markdown
# Module map

The diagram is generated from `modules/*/manifest.yaml`; edit a manifest, not the diagram.

<!-- generated:module-map -->
<!-- /generated -->

| Module | Responsibility | Requirements |
|---|---|---|
| <name> | <one sentence; if it needs "and", split it or justify it in a decision record> | REQ-nnn |
| baseline | <what every module inherits> | REQ-nnn |
```
