---
title: "Architecture Directory Governance and Contract"
tags: ["architecture", "governance", "up"]
created_at: "2026-11-13"
last_updated_at: "2026-11-13"
---

# Architecture Directory Governance and Contract

This directory serves as the authoritative Single Source of Truth (SSoT) for internal technical governance, requirements specifications, architectural trade-offs, and implementation blueprints for the `ed-fleet-client` project under the Unified Process (UP).

---

## 1. Dual-Root Partition

* **Maintainer / Engineering Plane (`architecture/`):** Reserved exclusively for internal engineering ledgers, formal requirements, design documents, and decision records.
* **Customer / Operator Plane (`docs/`):** Reserved exclusively for living, mutable user-facing manuals and runbooks governed by the Diátaxis framework.

---

## 2. Retained Architectural Document Types & Taxonomy

```text
architecture/
|-- README.md                      # Directory contract & governance index (this document)
|-- risk/                          # Project Management Discipline
|   \-- risk-list.md               # Barry Boehm Master Risk Register (RE = P * I)
|-- use-cases/                     # Requirements Discipline
|   |-- UC-01_...md                # RUP Use-Case Specifications (Cockburn Sea-Level)
|   \-- ...
|-- adr/                           # Analysis & Design Discipline
|   |-- README.md                  # Sequential index of all decisions
|   |-- 0001_high_level_architecture.md # Markdown Architectural Decision Records (MADR 3.0)
|   \-- ...
|-- designs/                       # Analysis & Design / Implementation
|   |-- 0001_subsystem_sdd.md      # IEEE 1016 Software Design Documents (SDD)
|   \-- ...
|-- rfcs/                          # Requirements & Architectural Consensus
|   |-- 0001_parent_proposal/      # Collaborative Engineering RFCs
|   \-- ...
\-- api/                           # Interface & Contract Specifications
    |-- openapi.yaml               # Boundary contracts & interface schemas
    \-- ...
```

---

## 3. Workflow & Boundary Invariants

1. **No Mixed Audience:** Never store end-user tutorials, CLI usage guides, or operational deployment runbooks in `architecture/`. Those belong strictly in `docs/` under the Diátaxis taxonomy.
2. **Immutable vs. Living Assets:**
   * **ADRs (`architecture/adr/`)** are **immutable historical snapshots**. Once accepted, they are never modified or rewritten. If an architectural decision changes, author a new ADR that explicitly supersedes the prior record.
   * **Use-Cases (`architecture/use-cases/`)**, **SDDs (`architecture/designs/`)**, and **API specs (`architecture/api/`)** are **living engineering baselines** maintained across active development phases.
3. **Traceability Invariant:** Every Software Design Document in `architecture/designs/` must declare explicit frontmatter traceability links to its parent ADRs in `architecture/adr/` and upstream requirements in `architecture/use-cases/` or `architecture/rfcs/`.
