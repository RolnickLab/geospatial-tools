# Project Context & Standards (Codex)

## Mandatory Session Initialization

Immediately upon starting a session, you must execute the following sequence:

1. Read [Primary Agent Instructions](docs/agents/agent_instructions.md). These are the primary operational instructions for this repository.
2. Consult the appropriate domain skills in the `docs/agents/instructions/` folder (e.g., `pyth    on`, `ml`, `infrastructure`, `orchestrator`).
3. Consult `docs/agents/instructions/KNOWLEDGE.md` for project-specific architectural invariants and recent decisions.

## Precedence of Truth

1. `docs/agents/agent_instructions.md` (highest priority)
2. Active skill instructions
3. `AGENTS.md` (this pointer only)
4. User-level configurations and intructions
