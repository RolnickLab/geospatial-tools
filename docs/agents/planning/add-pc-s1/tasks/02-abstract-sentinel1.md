# TASK-2: Implement AbstractSentinel1 Base Class

## Goal

Create the `AbstractSentinel1` base class that manages state and default parameters for Sentinel-1 GRD searches, avoiding optical assumptions like cloud cover.

## Context & References

- **Source Plan**: docs/agents/planning/add-pc-s1/add-pc-s1.md
- **Relevant Specs**: docs/agents/planning/add-pc-s1/add-pc-s1-spec.md
- **Existing Code**: src/geospatial_tools/stac/planetary_computer/sentinel_2.py (for architectural inspiration, NOT for optical domain logic)

## Subtasks

1. [ ] Create new file `src/geospatial_tools/stac/planetary_computer/sentinel_1.py`.
2. [ ] Implement `AbstractSentinel1` class (using `abc.ABC`).
3. [ ] Implement `__init__` with SAR-specific kwargs: `collection` (default `sentinel-1-grd`), `date_ranges`, `instrument_mode` (default `IW`), `polarizations` (default `["VV", "VH"]`), and `orbit_state` (optional).
4. [ ] Add `create_date_ranges` method (identical to `AbstractSentinel2` implementation) using `create_date_range_for_specific_period`.
5. [ ] Add unit tests verifying `AbstractSentinel1` raises `TypeError` if instantiated directly and correctly sets/gets SAR attributes when subclassed.

## Requirements & Constraints

- Must NOT include `max_cloud_cover` or optical equivalent parameters. S1 penetrates clouds.
- Default `instrument_mode` should be `IW` (Interferometric Wide swath).
- Maintain property getters/setters for standard attributes like `date_ranges`.

## Acceptance Criteria (AC)

- [ ] `AbstractSentinel1` cannot be instantiated directly.
- [ ] A mock subclass correctly initializes with `instrument_mode="IW"` and `polarizations=["VV", "VH"]`.
- [ ] The class explicitly lacks any `max_cloud_cover` state.
- [ ] `create_date_ranges` correctly sets the `date_ranges` property.

## Testing & Validation

- **Command**: `pytest tests/test_planetary_computer_sentinel1.py` (new test file)
- **Success State**: Subclass initializes correctly, property assignments work, instantiation of the ABC fails.
- **Manual Verification**: Review `sentinel_1.py` to guarantee no S2/optical logic was blindly copy-pasted.

## Completion Protocol

1. [ ] All ACs are met.
2. [ ] Tests pass without regressions.
3. [ ] All new code passes the project's formating, linting and type-checking tools with zero errors.
4. [ ] Documentation updated (if applicable).
5. [ ] Commit work: `git commit -m "feat: implement AbstractSentinel1 base class"`
6. [ ] Update this document: Mark as COMPLETE.
