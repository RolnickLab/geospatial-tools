# Root Cause Analysis (RCA) Skill Instructions

\<primary_directive>
Your objective is to systematically diagnose and permanently fix software failures.
**MANDATE:** Apply the project-specific rules outlined below for all debugging and root cause analysis tasks.
\</primary_directive>

<context>
Geospatial errors are often opaque (e.g., `rasterio.errors.RasterioIOError`, mismatched CRSs, out-of-bounds bounding boxes). Slapping a `try/except` block over an error without understanding it creates brittle systems that fail silently later.
</context>

<workflow>
When presented with a traceback or unexpected result, you MUST follow this workflow:

### Step 1: Evidence Gathering

- Request or extract the exact error message and traceback. Identify the exact file and line number.
- For geospatial errors, gather state: What is the shape of the array? What is the CRS? What are the bounds of the bounding box? Are there `NaN` or nodata values present?

### Step 2: Failure Isolation (Reproduction)

- Help the user create a Minimal, Reproducible Example (MRE), potentially using synthetic data or a single tiny raster tile.

### Step 3: Hypothesize & Explain (The "Why")

- **STOP.** Before writing a fix, explicitly state your hypothesis to the user. Explain the root cause.

### Step 4: Surgical Remediation & Verification

- Propose the smallest, most targeted code change required. Prove the fix works via `pytest`.
- Document the finding in `docs/agents/instructions/KNOWLEDGE.md` if it represents a systemic quirk (e.g., a specific STAC catalog behavior).
    </workflow>

\<forbidden_patterns>

- ❌ **Guesswork:** You MUST NOT propose random fixes (e.g., "try reprojecting it again") without a coherent hypothesis based on the traceback and data state.
- ❌ **Patching Symptoms:** You MUST NEVER suppress an error (e.g., using a bare `except: pass`) without fixing the foundational logic flaw that caused it.
- ❌ **Fixing Without Explaining:** You MUST NOT provide a corrected block of code without first explaining the root cause of the bug to the researcher.
    \</forbidden_patterns>
