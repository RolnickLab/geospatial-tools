# Agents

This folder is for everything concerning AI agents (such as Claude, Codex, Gemini, etc.) and related documentation.

These instructions are meant to be a first step into agent-based development. They are deliberately structured to help the user acquire deeper knowledge while still benefiting from agent assisted programming. Once you feel comfortable with these, please feel free to modify and extend them for your own projects and skill levels.

Yes, these instructions are more prescriptive than *current* best practices, but they are also configured to work better with lower end models that **do** require more guidance.

- [agent_instructions.md](agent_instructions.md): File containing strictly model-agnostic context (usable by Claude, Codex, Gemini, etc.) relating to the project. Reference this file as your primary context when using any AI agent with this repository.
- [planning](planning/): Folder that contains the planning and task tracking documents produced by agents. Create sub folders by PR and/or task.
- [instructions](instructions/): Folder to contain specific agent skills and reference document that are referenced by the `agent_instructions.md`.

## Available Agent Skills

The `instructions/` folder contains specific skill files that guide the agent's behavior for particular tasks. Here is a summary of each skill, its purpose, and when to use it:

| Skill                    | Description                                                                      | When to Use & Why                                                                                                                          |
| ------------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `analytics.md`           | Extracts truth from experimental data with statistical rigor.                    | Use for Exploratory Data Analysis (EDA) and visualization to ensure reproducibility and prevent misleading claims.                         |
| `formal_planning.md`     | Enforces a structured planning protocol via a Formal Design Document.            | Use when explicitly asked for a plan, architecture, or proposal to map out scope, trade-offs, and steps before coding.                     |
| `infrastructure.md`      | Manages reproducible and resilient environments/pipelines as code.               | Use for containerization (Docker), HPC/SLURM cluster setup, or CI/CD tasks to ensure fault tolerance and exact dependency pinning.         |
| `KNOWLEDGE.md`           | A centralized repository for project-specific tribal knowledge.                  | Use to document or consult specific findings, library quirks, or architectural decisions to avoid repeating past mistakes.                 |
| `ml.md`                  | Builds state-of-the-art, reproducible, and reliable machine learning pipelines.  | Use for ML model training, evaluation, and experiment management to guarantee strict data isolation and deterministic execution.           |
| `orchestrator.md`        | Focuses on horizontal integration and strategic decomposition of goals.          | Use for multi-component tasks to define explicit contracts between modules and ensure end-to-end flows work correctly.                     |
| `plan_to_tasks.md`       | Decomposes high-level plans into modular, atomic, and verifiable tasks.          | Use when transitioning from planning to execution to ensure each step has clear context, acceptance criteria, and testing protocols.       |
| `python.md`              | Elevates Python scripts into robust, maintainable, and type-safe software.       | Use for all Python development and QA to enforce strict typing, SOLID principles, vectorization, and automated workflows.                  |
| `root_cause_analysis.md` | Systematically diagnoses and permanently fixes software failures.                | Use when presented with a bug, traceback, or unexpected result to isolate the failure (MRE) and target the actual root cause.              |
| `security.md`            | Identifies vulnerabilities, enforces defense-in-depth, and ensures data privacy. | Use for tasks involving authentication, untrusted input, or infrastructure to prevent injection attacks and hardcoded secrets.             |
| `specdrivendev.md`       | Implements lightweight Spec-Driven Development to define contracts first.        | Use when starting a new feature to define data structures, signatures, and docstrings before writing logic, preventing LLM hallucinations. |
| `systemdesign.md`        | Designs systems that are maintainable, evolvable, and robust.                    | Use for architectural decisions to enforce separation of concerns, configuration-first design, and proper dependency injection.            |

## How to use them

This template comes with CLAUDE.md and GEMINI.md files that essentially point to [agent_instructions.md](agent_instructions.md) and should, in theory, automatically take them into account.

In practice... it's not always the case. It is probably better to manually feed the instructions directly to the agent/tool as context in your prompt just to make sure:

```text
Using @docs/agents/agent_instructions.md, @docs/agents/instructions/python.md, and @docs/agents/instructions/systemdesign.md and @docs/agents/instructions/formal_planning.md, create a plan for a new class that will ...
```

When using models with smaller context windows, it will also be important to clear the context once in a while to ensure better results.

For example:

- Create plan
    - Manually revise plan document
- Clear context
- Ask agent to implement first step of the plan
- Clear context
- Repeat
