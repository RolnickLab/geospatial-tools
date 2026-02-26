# Project Context & Standards (Gemini CLI)

## Mandatory Session Initialization

**Immediately upon starting a session, you MUST execute the following sequence:**

1. **READ** the [Primary Agent Instructions](docs/agents/agent_instructions.md). These are your absolute operational truth for this repository.
2. **CONSULT** the appropriate domain skills in the `docs/agents/instructions/` folder (e.g., `python`, `ml`, `infrastructure`, `orchestrator`).
3. **CONSULT** `docs/agents/instructions/KNOWLEDGE.md` for project-specific architectural invariants and recent decisions.

## Precedence of Truth

1. `docs/agents/agent_instructions.md` (Highest Priority)
2. Activated Skill Instructions
3. `GEMINI.md` (This pointer only)
4. User-level configurations and instructions
