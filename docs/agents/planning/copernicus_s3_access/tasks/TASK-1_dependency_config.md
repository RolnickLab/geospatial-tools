# TASK-1: Dependency and Configuration Updates

## Goal

Add `boto3` as a project dependency and update configuration templates to support S3 access for Copernicus Data Space Ecosystem (CDSE).

## Context & References

- **Source Plan**: `docs/agents/planning/refactor_copernicus_s3_access_PLAN.md`
- **Relevant Specs**: `docs/agents/planning/refactor_copernicus_s3_access_SPEC.md`
- **Existing Code**: `pyproject.toml`, `.env.example`

## Subtasks

1. [x] Add `boto3` to the `dependencies` section in `pyproject.toml`.
2. [x] Add `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `COPERNICUS_S3_ENDPOINT` to `.env.example`.
3. [x] Run `uv lock` (or the equivalent dependency resolution command) to update the lock file if required by the project setup.

## Requirements & Constraints

- Must not remove existing dependencies.
- `.env` template should clearly indicate these are for CDSE S3 access.

## Acceptance Criteria (AC)

- [x] `pyproject.toml` contains `boto3` in its dependencies.
- [x] `.env.example` contains the three new S3 environment variables.

## Testing & Validation

- **Command**: `uv pip compile pyproject.toml` or simply load a python shell and `import boto3` after installing.
- **Success State**: No dependency conflict errors.
- **Manual Verification**: Review the `.env.example` file to ensure the keys are present and clearly commented.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "build: task 1 - add boto3 dependency and update env template"`
6. [ ] Update this document: Mark as COMPLETE.
