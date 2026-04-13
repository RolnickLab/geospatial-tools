# Orchestrator Skill Instructions

\<primary_directive>
Your primary responsibility is the horizontal integration of all research components.
**MANDATE:** Apply the project-specific rules outlined below for all orchestration and integration tasks.
\</primary_directive>

<context>
In this repository, successful orchestration means tying together raw geospatial data fetching (STAC/Copernicus), pre-processing (Rasterio/Xarray), and output generation (COGs/Zarr).
</context>

<workflow>
For any task requiring more than a minor fix, you MUST enforce the following framework:

### 1. The Written Plan (Mandatory)

Before writing implementation code, you MUST create or update a `<TASK_DESCRIPTION>_PLAN.md` in `docs/agents/planning/` (or use the built-in planning tools like `enter_plan_mode` for Gemini or equivalent planning modes for Claude/Codex).

### 2. Contract Management

- **Define Boundaries:** Explicitly define the inputs and outputs between pipeline stages BEFORE either stage is implemented.
- **Geospatial Contracts:** When integrating geospatial modules, the contract MUST include the expected CRS and resolution.

### 3. Granular Execution

- Implement exactly ONE step from the plan at a time.
- After completing a step, you MUST STOP and ask the user to validate the output before moving to the next step.
    </workflow>

\<forbidden_patterns>

- ❌ **Vertical Myopia:** You MUST NOT focus entirely on optimizing one specific file while ignoring how it breaks integration with the rest of the project (e.g., changing a config structure without updating `geospatial_tools_ini.yaml.example`).
- ❌ **Implied Contracts:** You MUST NOT build components that pass raw, untyped dictionaries to each other. Always enforce explicit data contracts (e.g., Pydantic Models, Dataclasses).
- ❌ **Skipping E2E Testing:** You MUST NOT declare a complex integration "complete" without verifying that the data flows from start to finish via `nox` testing sessions or test notebooks.
    \</forbidden_patterns>
