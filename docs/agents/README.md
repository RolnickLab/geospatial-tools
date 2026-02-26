# Agents

This folder is for everything concerning AI agents (such as Claude, Codex, Gemini, etc.) and related documentation.

These instructions are meant to be a first step into agent-based development. They are deliberately structured to help the user acquire deeper knowledge while still benefiting from agent assisted programming. Once you feel comfortable with these, please feel free to modify and extend them for your own projects and skill levels.

Yes, these instructions are more prescriptive than *current* best practices, but they are also configured to work better with lower end models that **do** require more guidance.

- [agent_instructions.md](agent_instructions.md): File containing strictly model-agnostic context (usable by Claude, Codex, Gemini, etc.) relating to the project. Reference this file as your primary context when using any AI agent with this repository.
- [planning](planning/): Folder that contains the planning and task tracking documents produced by agents. Create sub folders by PR and/or task.
- [instructions](instructions/): Folder to contain specific agent skills and reference document that are referenced by the `agent_intructions.md`.

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
