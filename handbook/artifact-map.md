---
id: HBK-001
title: The Artifact Map
tier: handbook
status: active
audience: [human]
load: never
sessions: []
prevents: A reader unable to tell whether an artifact is a record, prose, or ceremony because the whole picture exists only in pieces
reader: A person orienting in a project, in the console's handbook tab
related: [HBK-000, CORE-LFC-001, CORE-TRC-001, CORE-TRC-002, CORE-TRC-003, CORE-CON-003, CORE-TST-002]
---

# The Artifact Map

The five gate documents each carry an Outputs table and the traceability documents say
which check reads what, so the whole picture exists only in pieces. A reader who cannot
see it whole cannot tell whether an artifact is a record, prose, or ceremony. Read by a
person orienting in a project; the console's views follow this map.

## The picture

```mermaid
flowchart LR
    subgraph gates["Gates and loop"]
        direction TB
        G0["G0 hazards and context"] --> G1["G1 requirements and validation basis"] --> G2["G2 architecture"] --> G3["G3 contracts and slice plan"] --> SL["Slice loop"] --> G4["G4 release"]
    end
    subgraph records["trace/ records (checked)"]
        direction TB
        HZ["hazards.yaml"]
        NE["needs, assumptions, goals"]
        RQ["requirements.yaml"]
        SLC["slices.yaml"]
        FN["findings.yaml"]
        RV["reviews.yaml"]
        CH["changes.yaml"]
        RS["results.xml (generated)"]
    end
    subgraph prose["Prose and code (templated)"]
        direction TB
        MM["docs/module-map.md"]
        DC["docs/decisions/DEC-nnn.md"]
        SD["docs/slices/SL-nn.md"]
        CT["modules/*/CONTRACT.md + contract.*"]
        CF["modules/*/conformance/"]
        VL["validation/"]
    end
    subgraph checks["Checks"]
        direction TB
        TR["check_traces.py"]
        CC["check_commit.py"]
        NM["null double + mutation"]
        CS["build_console.py"]
    end
    G0 -->|writes| HZ
    G1 -->|writes| RQ
    G1 -->|writes| NE
    G2 -->|writes| MM
    G2 -->|writes| DC
    G3 -->|writes| CT
    G3 -->|writes| CF
    G3 -->|writes| SD
    G3 -->|writes| SLC
    SL -->|appends| FN
    SL -->|appends| RV
    SL -->|appends| CH
    SL -->|writes| VL
    SL -->|test run emits| RS
    HZ --> TR
    RQ --> TR
    SLC --> TR
    FN --> TR
    RV -->|gate state| TR
    RS -->|pass or fail| TR
    CT --> CC
    CF --> CC
    CF --> NM
    TR -->|verdict| CS
    RV --> CS
    MM --> CS
    CS -->|evidence bundle| G4
```

Every gate writes records or templated prose. Every record is read by the trace
checker, which reads gate state from the review log and pass or fail from the test
results. The console renders all of it and is what the release gate receives.

## The table

| Gate | Question | Artifact | Lives in | Checked by |
|---|---|---|---|---|
| G0 | What must it never do? | Hazard records with never-statements | `trace/hazards.yaml` | `check_traces.py`: link to requirement, contract clause, test ([CORE-TRC-002](../core/traceability/trace-records.md)) |
| G1 | What must it do, and how would we know? | Requirements with verification method and validation class; needs, assumptions, goals | `trace/requirements.yaml` and siblings | `check_traces.py`: allocation, verification, validation, source |
| G2 | What are the parts? | Module map, dependency manifests, decision records, baseline list | `docs/module-map.md`, `modules/*/manifest.yaml`, `docs/decisions/` | Boundary lint against the manifests ([CORE-CON-003](../core/contracts/boundary-enforcement.md)); the diagram is generated from the manifests |
| G3 | What does each part promise? | Contracts with clause IDs, conformance suites, slice plan | `modules/*/CONTRACT.md`, `conformance/`, `docs/slices/`, `trace/slices.yaml` | Suites fail against an empty implementation and against the null double ([CORE-TST-002](../core/testing/tests-are-tested.md)); `check_commit.py` |
| Slice loop | What do I do next? | Findings, reviews, changes, validation cases, acceptance records | `trace/findings.yaml`, `reviews.yaml`, `changes.yaml`, `validation/` | `check_traces.py` with `results.xml`; mutation score; console |
| G4 | Can this be released? | Evidence bundle | The console, built from everything above | The checker over a chain with every gate row passed and every claim verified |

Where an artifact lives is decided once, in the table of
[CORE-TRC-002](../core/traceability/trace-records.md); this map only draws it.
