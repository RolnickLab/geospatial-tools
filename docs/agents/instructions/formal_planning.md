# Formal Planning Protocol

When the user explicitly asks for a "plan," "architecture," "design," or "proposal"—or when embarking on a multi-step/multi-domain implementation—you must use the **Formal Design Document** structure below.

Do not deviate from these exact headers. Ensure the content underneath each header is concise and outcome-oriented.

## 1. Scope & Context

*State briefly what you are solving and acknowledge any constraints. What are we doing right now?*

## 2. Architectural Approach (Trade-offs & Strategy)

*Explain the reasoning behind the proposed approach. Reference established principles (e.g., SOLID, Idempotency). Discuss trade-offs (e.g., memory vs. speed).*

## 3. Verification & Failure Modes (FMEA)

*How do we know this works, and how will it break? Outline the test strategy and known risks (potential bottlenecks, edge cases, or security considerations).*

## 4. Granular Implementation Steps

*Provide a structured, step-by-step list of the implementation process. Focus on one modular chunk at a time.*

## 5. Next Step

*End with a single, clear question asking for approval on Step 1 to maintain momentum.*
