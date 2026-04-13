# TASK-3: Refactor STAC Download Logic (stac.py)

## Goal

Refactor the STAC download logic to dispatch to either the new S3 downloader or the existing HTTP downloader based on the asset protocol or catalog source.

## Context & References

- **Source Plan**: `docs/agents/planning/refactor_copernicus_s3_access_PLAN.md`
- **Relevant Specs**: `docs/agents/planning/refactor_copernicus_s3_access_SPEC.md`
- **Existing Code**: `src/geospatial_tools/stac.py`

## Subtasks

1. [ ] Create a generic `download_asset(asset_url: str, destination: Path, method: str = "http")` function (or equivalent class method).
2. [ ] Implement the `s3` dispatcher branch using `s3_utils.get_s3_client` and `s3_utils.parse_s3_url`, utilizing `boto3`'s `download_file` method.
3. [ ] Refactor the existing `_download_assets` in `StacSearch` to delegate downloads to this new method.
4. [ ] Implement logic to automatically detect when a Copernicus Sentinel-2 STAC asset should use the `s3` method instead of `http`.
5. [ ] Add unit tests mocking `boto3` to ensure the correct download branch is hit without making actual network requests.

## Requirements & Constraints

- Must not break existing HTTP downloads (e.g., for Planetary Computer).
- Use `pathlib.Path` for all file destination handling.
- Ensure proper logging of the download progress or strategy chosen.

## Acceptance Criteria (AC)

- [ ] `stac.py` successfully dispatches downloads to `boto3` for Copernicus assets.
- [ ] `stac.py` falls back to `requests` for standard HTTP assets.
- [ ] Unit tests with mocked S3 clients pass.

## Testing & Validation

- **Command**: `pytest tests/test_stac.py` (or equivalent file where `stac.py` logic is tested).
- **Success State**: All unit tests pass, confirming the dispatcher routing logic works.
- **Manual Verification**: Review the refactored code to ensure it remains clean and does not become a God Object.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "refactor: task 3 - implement download dispatcher for s3 and http in stac.py"`
6. [ ] Update this document: Mark as COMPLETE.
