---
name: plan_to_tasks
description: Plan To Tasks
---
# Plan To Tasks

## Primary Directive
**MANDATE:** Decompose a plan into modular, atomic tasks, each documented in its own file (or a structured document) with all the context needed for implementation and verification.

## Core Workflow

1. **Analyze the Plan**: Review the existing implementation plan (e.g., `PLAN.md` or `SPEC.md`) or a high-level request.
2. **Identify Boundaries**: Break the plan into modular, atomic tasks based on logical boundaries (modules, features, or architectural layers).
3. **Generate Task Documents**: For each task, create a file using the task structure below.
4. **Enforce Quality Standards**: Integrate principles from `orchestrator`, `spec-driven-development`, `systemdesign`, and `formal-planning` into each task.

## Task Structure Requirements

Every task document MUST include:

- **Goal**: A clear, outcome-oriented objective.
- **Context & References**: Links to relevant documentation, specs, and existing code.
- **Subtasks**: Granular, atomic steps for implementation.
- **Requirements & Constraints**: Specific technical or business rules to follow.
- **Acceptance Criteria (AC)**: Measurable pass/fail states that define "done".
- **Testing & Validation**: Concrete commands and steps to verify the implementation.
- **Completion Protocol**: Mandatory steps to verify ACs, run tests, commit work to git, and update the task document.

## Implementation Principles

- **Vertical Slices (TDD/Tracer Bullets)**: Prefer tasks that deliver a full slice of functionality (One test → One implementation) over horizontal technical layers.
- **Contract-First (Orchestrator)**: Define interfaces and shared protocols before starting implementation subtasks.
- **Outcome-Orientation (Formal Planning)**: Every subtask must be tied to a verifiable outcome.
- **Fail Fast (QA)**: Include specific test commands that provide immediate feedback.
- **Evolvability (System Design)**: Ensure tasks are decoupled and follow SOLID principles.

## Next Steps

- Use the Task Structure Requirements to bootstrap each new task.
