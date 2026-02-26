# Formal Planning Protocol

\<primary_directive>
**MANDATE:** Ensure any generated plan adheres to the structure below.
\</primary_directive>

When the user explicitly asks for a "plan," "architecture," "design," or "proposal"—or when embarking on a multi-step/multi-domain implementation—you must use the **Formal Design Document** structure below, saving it to `docs/agents/planning/<TASK_DESCRIPTION>_PLAN.md`.

## 1. Scope & Context

*State briefly what you are solving and acknowledge any constraints. What are we doing right now?*

## 2. Architectural Approach (Trade-offs & Strategy)

*Explain the reasoning behind the proposed approach. Reference established principles (e.g., SOLID, Idempotency, Cloud-Optimized Geospatial Formats). Discuss trade-offs.*

## 3. Verification & Failure Modes (FMEA)

*How do we know this works, and how will it break? Outline the test strategy (pytest/nox) and known risks (potential bottlenecks, OOMs, or security considerations).*

## 4. Granular Implementation Steps

*Provide a structured, step-by-step list of the implementation process. Focus on one modular chunk at a time.*

## 5. Next Step

*End with a single, clear question asking for approval on Step 1 to maintain momentum.*
