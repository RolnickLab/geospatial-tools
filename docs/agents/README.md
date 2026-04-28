# Agents

This folder is for everything concerning AI agents (such as Claude, Codex, Gemini, etc.) and related documentation.

These instructions are meant to be a first step into agent-based development. They are deliberately structured to help the user acquire deeper knowledge while still benefiting from agent assisted programming. Once you feel comfortable with these, please feel free to modify and extend them for your own projects and skill levels.

Yes, these instructions are more prescriptive than *current* best practices, but they are also configured to work better with lower end models that **do** require more guidance.

- [agent_instructions.md](agent_instructions.md): File containing strictly model-agnostic context (usable by Claude, Codex, Gemini, etc.) relating to the project. Reference this file as your primary context when using any AI agent with this repository.
- [planning](planning/): Folder that contains the planning and task tracking documents produced by agents. Create sub folders by PR and/or task.
- [instructions](instructions/): Folder to contain specific agent skills and reference document that are referenced by the `agent_instructions.md`.

## Available Agent Skills

The `instructions/` folder contains specific skill files that guide the agent's behavior for particular tasks. Here is a summary of each skill, its purpose, and when to use it:

| Skill                    | Description                                                              | When to Use & Why                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `planning.md`            | Combined Planning, Specification (SDD), and Task Decomposition Protocol. | Use for any multi-step implementation to map out scope, define technical contracts (SDD), and break down work into atomic tasks.       |
| `software-dev.md`        | Unified Software Development, ML, Analytics & Infrastructure Protocol.   | Use for Python development, system design, ML/geospatial processing, data analysis, and infrastructure/environment management.         |
| `review.md`              | Harsh Security & Architecture Review Protocol.                           | Use to identify vulnerabilities (tokens, paths, SSL) and tear apart implementations for performance bottlenecks and architectural rot. |
| `root_cause_analysis.md` | Systematically diagnoses and permanently fixes software failures.        | Use when presented with a bug, traceback, or unexpected result to isolate the failure (MRE) and target the actual root cause.          |
| `KNOWLEDGE.md`           | A centralized repository for project-specific tribal knowledge.          | Use to document or consult specific findings, library quirks, or architectural decisions to avoid repeating past mistakes.             |

## How to use them

This template comes with CLAUDE.md and GEMINI.md files that essentially point to [agent_instructions.md](agent_instructions.md) and should, in theory, automatically take them into account.

In practice... it's not always the case. It is probably better to manually feed the instructions directly to the agent/tool as context in your prompt just to make sure:

```text
Using @docs/agents/agent_instructions.md, @docs/agents/instructions/software-dev.md, and @docs/agents/instructions/planning.md, create a plan for a new class that will ...
```

It's usually a good thing to clear/compress the context once in a while to ensure better results.

### Workflow example

First, define **what** you want to do, **how** and **why**. Go in as much detail as you can. Let's call this your *preliminary design document*.

You can also do this step through a chat interface with an LLM so you can brainstorm, ask questions, investigate starting points, development directions and library/tool selections.

Once you have your *preliminary design document*, you are ready to start using your agent.

- Activate `@docs/agents/instructions/planning.md`
    - **Create PLAN**
        - Ask agent to create a plan based on your *preliminary design document*
        - Manually revise plan document
    - **Create SPEC**
        - Ask agent to create a specification based on the plan
        - Manually revise the specification document
    - **Create TASKS**
        - Ask agent to create tasks based on the plan and specification created
        - Manually revise the tasks
    - **_CLEAR CONTEXT_**
- Activate `@docs/agents/instructions/code_review.md`
    - Ask the agent to review your planning documents
    - **_CLEAR CONTEXT_**
- Activate `@docs/agents/instructions/software_dev.md`
    - Ask agent to implement first task of the plan
    - Manual review
    - Commit work to git
    - **_COMPRESS CONTEXT_**
    - Repeat for subsequent tasks
