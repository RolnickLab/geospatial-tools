# TASK-4: Integration Testing and Validation

## Goal

Verify the end-to-end functionality of downloading Copernicus STAC assets via S3 using real credentials against the live API.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor_copernicus_s3_access_PLAN.md`
- **Relevant Specs**: `docs/agents/planning/refactor_copernicus_s3_access_SPEC.md`
- **Existing Code**: `tests/test_copernicus.py`

## Subtasks

1. [ ] Update or create an integration test in `tests/test_copernicus.py` that searches for a STAC item and triggers a download.
2. [ ] Ensure this test is marked with `@pytest.mark.online`.
3. [ ] Create a local `.env` file (or ensure environment variables are present) with valid CDSE credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `COPERNICUS_S3_ENDPOINT`).
4. [ ] Run the integration test and verify that the file is successfully downloaded and saved to the local file system.

## Requirements & Constraints

- The test must not run by default without the `--run-online` flag (or standard pytest custom marker configuration).
- Ensure the downloaded file is a valid file (e.g., check file size or existence after download).

## Acceptance Criteria (AC)

- [ ] Integration test successfully downloads a file from Copernicus S3.
- [ ] The test correctly loads credentials via `python-dotenv`.
- [ ] Existing Planetary Computer integration tests still pass, proving no regressions.

## Testing & Validation

- **Command**: `pytest tests/test_copernicus.py -m online`
- **Success State**: Integration tests pass successfully.
- **Manual Verification**: Inspect the test download directory to confirm the asset was downloaded.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "test: task 4 - add end-to-end integration test for copernicus s3 downloads"`
6. [ ] Update this document: Mark as COMPLETE.
