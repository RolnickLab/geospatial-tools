---
name: planning
description: Combined Planning, Specification, and Task Decomposition Protocol
---
# Planning, Spec & Task Decomposition Protocol

## Primary Directive
**MANDATE:** Follow this protocol for any multi-step implementation, architectural change, or high-level request. Ensure every plan is specified and decomposed into modular, atomic, and verifiable tasks.

## Phase 1: Formal Design
When embarking on a multi-step implementation, create a **Formal Design Document** at `docs/agents/planning/<TASK_DESCRIPTION>_PLAN.md`.

### Structure:
1.  **Scope & Context**: Briefly state problem and constraints.
2.  **Architectural Approach**: Explain reasoning, trade-offs, and principles (SOLID, Idempotency, Cloud-Optimized formats).
3.  **Verification & Failure Modes (FMEA)**: Outline test strategy (pytest/nox) and known risks (bottlenecks, OOM, security).
4.  **Granular Implementation Steps**: Structured, step-by-step list of the process.
5.  **Next Step**: Single question for approval on Step 1.

## Phase 2: Technical Specification (SDD)
Before creating tasks or writing logic, define the technical contract. Create `docs/agents/planning/<TASK_DESCRIPTION>_SPEC.md`.

### Workflow:
1.  **Define Nouns (Dataclasses)**: Use `dataclasses` or Pydantic. Geospatial structures MUST contain metadata (CRS, Affine transform).
2.  **Write Contract**: Function signatures with strict type hints (`numpy.typing`, `xarray.DataArray`). Google Style docstrings for inputs, outputs, and spatial projections/shapes.
3.  **Stub & Validate**: Use `raise NotImplementedError()`. Present stubs for validation BEFORE implementation logic.

### SDD Forbidden Patterns:
- ❌ **`Any` Escape Hatch**: Use specific types (e.g., `xarray.Dataset`, `geopandas.GeoDataFrame`).
- ❌ **Logic Before Contract**: Signature and docstring first.

## Phase 3: Plan to Tasks
Decompose the approved plan and spec into modular, atomic tasks in `docs/agents/planning/<TASK_DESCRIPTION>/tasks/`.

### Task Structure Requirements:
Every task document MUST include:
- **Goal**: Clear, outcome-oriented objective.
- **Context & References**: Links to docs, specs, and existing code.
- **Subtasks**: Granular, atomic implementation steps.
- **Requirements & Constraints**: Technical or business rules.
- **Acceptance Criteria (AC)**: Measurable pass/fail states.
- **Testing & Validation**: Commands and steps to verify implementation.
- **Completion Protocol**: Mandatory steps: verify ACs, run tests, commit work, update task doc.

## Implementation Principles
- **Vertical Slices (TDD)**: Deliver full slices (One test → One implementation).
- **Contract-First**: Define interfaces/protocols (Phase 2) before implementation.
- **Outcome-Orientation**: Every subtask must be tied to a verifiable outcome.
- **Fail Fast**: Include specific test commands for immediate feedback.
- **Evolvability**: Ensure tasks are decoupled and follow SOLID.
