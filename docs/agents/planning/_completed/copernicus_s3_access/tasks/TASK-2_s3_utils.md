# TASK-2: Implement S3 Helper Module (s3_utils.py)

## Goal

Create a dedicated utility module to handle S3 client configuration and URL parsing for Copernicus data.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor_copernicus_s3_access_PLAN.md`
- **Relevant Specs**: `docs/agents/planning/refactor_copernicus_s3_access_SPEC.md`
- **Existing Code**: `src/geospatial_tools/`

## Subtasks

1. [x] Create `src/geospatial_tools/s3_utils.py`.
2. [x] Implement `get_s3_client(endpoint_url: str) -> boto3.client`. This should optionally load credentials from the environment via `python-dotenv` if not automatically handled by boto3.
3. [x] Implement `parse_s3_url(url: str) -> tuple[str, str]` to extract the bucket and key from a CDSE STAC href (or standard `s3://` URI).
4. [x] Create `tests/test_s3_utils.py` and write unit tests for the URL parser and client factory.

## Requirements & Constraints

- Strictly use the project's `logging` via `utils.create_logger` for logging any errors or connection details.
- Provide comprehensive type hints (`boto3.client` type, `str`, `tuple`).
- Ensure graceful error handling if parsing fails.

## Acceptance Criteria (AC)

- [x] `s3_utils.py` exists and implements `get_s3_client` and `parse_s3_url`.
- [x] `parse_s3_url` correctly handles expected CDSE STAC href formats (e.g., extracting bucket/key from an endpoint URL or a raw S3 path).
- [x] Unit tests pass for both valid and invalid S3 URIs.

## Testing & Validation

- **Command**: `pytest tests/test_s3_utils.py`
- **Success State**: All unit tests pass.
- **Manual Verification**: Review `s3_utils.py` to ensure SOLID principles (specifically single responsibility) are followed.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: task 2 - implement s3_utils for client config and url parsing"`
6. [ ] Update this document: Mark as COMPLETE.
