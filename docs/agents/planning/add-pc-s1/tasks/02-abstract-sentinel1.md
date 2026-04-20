# TASK-2: Implement AbstractSentinel1 Base Class

## 1. Goal

Create `AbstractSentinel1` in `sentinel_1.py` as a true ABC with SAR-typed kwargs, spatial filter
support, and one enforced abstract method — so direct instantiation raises `TypeError` and
subclasses are forced to implement `build_query()`.

## 2. Context & References

- **Source Plan**: `docs/agents/planning/add-pc-s1/add-pc-s1.md`

- **Relevant Specs**: `docs/agents/planning/add-pc-s1/add-pc-s1-spec.md`

- **Upstream task**: TASK-1 — all six S1 enums must be present in `constants.py` before
    implementing this class.

- **Key files**:

    - `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` — new file to create
    - `src/geospatial_tools/stac/planetary_computer/sentinel_2.py` — reference for `AbstractSentinel2`
        initialization pattern; do NOT copy `max_cloud_cover`, `max_no_data_value`,
        `successful_results`, `incomplete_results`, or `error_results`
    - `src/geospatial_tools/stac/core.py` — `StacSearch.search()` uses the same `bbox`/`intersects`
        types

- **Relevant skills**: `python`, `systemdesign`, `tdd`

- **Interface contract (complete, inline):**

    ```python
    import logging
    from abc import ABC, abstractmethod
    from typing import Any

    from geospatial_tools.stac.planetary_computer.constants import (
        PlanetaryComputerS1Collection,
        PlanetaryComputerS1InstrumentMode,
        PlanetaryComputerS1OrbitState,
        PlanetaryComputerS1Polarization,
    )
    from geospatial_tools.stac.utils import create_date_range_for_specific_period
    from geospatial_tools.utils import create_logger

    LOGGER = create_logger(__name__)


    class AbstractSentinel1(ABC):
        """Abstract base class for Sentinel-1 GRD STAC searches on Planetary Computer.

        Subclasses must implement `build_query()`. Direct instantiation raises TypeError.

        Args:
            collection: S1 collection identifier.
            date_ranges: List of date range strings. Set via `create_date_ranges()` or directly.
            instrument_mode: SAR instrument mode. Defaults to IW (Interferometric Wide swath).
            polarizations: List of polarizations to query. Defaults to None (caller must be
                explicit — no default dual-pol assumption).
            orbit_state: Orbit direction filter. None means no filter.
            bbox: Bounding box filter (min_lon, min_lat, max_lon, max_lat). None means no filter.
            intersects: GeoJSON geometry filter. None means no filter.
            logger: Logger instance.
        """

        def __init__(
            self,
            collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
            date_ranges: list[str] | None = None,
            instrument_mode: PlanetaryComputerS1InstrumentMode | str = PlanetaryComputerS1InstrumentMode.IW,
            polarizations: list[PlanetaryComputerS1Polarization] | None = None,
            orbit_state: PlanetaryComputerS1OrbitState | None = None,
            bbox: tuple[float, float, float, float] | None = None,
            intersects: dict[str, Any] | None = None,
            logger: logging.Logger = LOGGER,
        ) -> None:
            self.logger = logger
            self.collection = collection
            self._date_ranges = date_ranges
            self.instrument_mode = instrument_mode
            self.polarizations = polarizations
            self.orbit_state = orbit_state
            self.bbox = bbox
            self.intersects = intersects

        @abstractmethod
        def build_query(self) -> dict[str, Any]:
            """Build the STAC query dict for this search configuration."""
            ...

        @property
        def date_ranges(self) -> list[str] | None:
            """Date ranges used for the STAC search."""
            return self._date_ranges

        @date_ranges.setter
        def date_ranges(self, value: list[str]) -> None:
            self._date_ranges = value

        def create_date_ranges(
            self, start_year: int, end_year: int, start_month: int, end_month: int
        ) -> list[str] | None:
            """Create and store date ranges for the given year/month window.

            Args:
                start_year: First year of the range.
                end_year: Last year of the range (inclusive).
                start_month: Starting month of each period.
                end_month: Ending month of each period (inclusive).

            Returns:
                List of date range strings.
            """
            self.date_ranges = create_date_range_for_specific_period(
                start_year=start_year,
                end_year=end_year,
                start_month_range=start_month,
                end_month_range=end_month,
            )
            return self.date_ranges
    ```

    **What is NOT on this class** (do not add):
    `max_cloud_cover`, `max_no_data_value`, `successful_results`, `incomplete_results`,
    `error_results`. S1 has no tile-coverage workflow. Those belong to `AbstractSentinel2` only.

    **`polarizations` defaults to `None`**, not `["VV", "VH"]`. Callers must be explicit. This
    prevents silent dual-pol assumptions for single-pol products.

## 3. Subtasks

- [ ] 1. Create `src/geospatial_tools/stac/planetary_computer/sentinel_1.py` with module
    docstring.
- [ ] 2. Write failing test: `pytest.raises(TypeError)` when calling `AbstractSentinel1()`
    directly (TDD Red).
- [ ] 3. Write failing test: define `ConcreteS1(AbstractSentinel1)` with `build_query()` returning
    `{}`, instantiate it with all kwargs, assert every attribute is stored correctly (TDD Red).
- [ ] 4. Write failing test: assert
    `AbstractSentinel1.__abstractmethods__ == frozenset({"build_query"})` (TDD Red).
- [ ] 5. Implement `AbstractSentinel1` with the exact signature above until all three tests pass
    (TDD Green).
- [ ] 6. Write failing test: assert `create_date_ranges()` sets `self.date_ranges` and returns the
    same list (TDD Red), then confirm it passes after step 5 (Green).
- [ ] 7. Run `ruff check` and `mypy src/geospatial_tools/stac/planetary_computer/sentinel_1.py`
    — fix any issues (Refactor).

## 4. Requirements & Constraints

- **Technical:** `AbstractSentinel1` must use `abc.ABC` and have exactly one `@abstractmethod`:
    `build_query()`. Any subclass that does not implement `build_query()` must also fail to
    instantiate.
- **No optical fields:** `max_cloud_cover`, `max_no_data_value`, `successful_results`,
    `incomplete_results`, and `error_results` must not appear anywhere in this file. S1 has no
    tile-coverage workflow.
- **`polarizations` defaults to `None`:** Callers are explicit. Document in docstring.
- **Typing:** All parameters and return types must be annotated. Use
    `list[PlanetaryComputerS1Polarization] | None`, not `list[str] | None`.
- **Out of scope:** `Sentinel1Search` and `sentinel_1_search()` — those are TASK-3.

## 5. Acceptance Criteria

- [ ] AC-1: `AbstractSentinel1.__abstractmethods__ == frozenset({"build_query"})`.
- [ ] AC-2: `AbstractSentinel1()` raises `TypeError` (direct instantiation blocked).
- [ ] AC-3: A subclass implementing `build_query()` initializes with all kwargs and stores them
    as instance attributes (`collection`, `date_ranges`, `instrument_mode`, `polarizations`,
    `orbit_state`, `bbox`, `intersects`).
- [ ] AC-4: `bbox` and `intersects` are stored as instance attributes (not discarded).
- [ ] AC-5: `polarizations` default is `None` — `ConcreteS1()` initialized without
    `polarizations` kwarg has `self.polarizations is None`.
- [ ] AC-6: `create_date_ranges(2023, 2023, 1, 3)` sets `self.date_ranges` to a non-empty list
    and returns it.
- [ ] AC-7: `sentinel_1.py` contains no reference to `max_cloud_cover`, `max_no_data_value`,
    `successful_results`, `incomplete_results`, or `error_results`.
- [ ] AC-8: All new code passes `ruff check` and `mypy` with zero errors.
- [ ] AC-9: `pytest tests/test_planetary_computer_sentinel1.py -x` passes with no regressions.

## 6. Testing & Validation

```bash
# Run targeted tests (new file)
pytest tests/test_planetary_computer_sentinel1.py -v

# Type-check
mypy src/geospatial_tools/stac/planetary_computer/sentinel_1.py

# Lint
ruff check src/geospatial_tools/stac/planetary_computer/sentinel_1.py

# Verify ABC enforcement
python -c "
from geospatial_tools.stac.planetary_computer.sentinel_1 import AbstractSentinel1
import pytest
assert AbstractSentinel1.__abstractmethods__ == frozenset({'build_query'})
try:
    AbstractSentinel1()
    raise AssertionError('should have raised TypeError')
except TypeError:
    pass
print('ABC enforcement ok')
"

# Verify no optical fields leaked
grep -n "max_cloud_cover\|max_no_data_value\|successful_results\|incomplete_results\|error_results" \
    src/geospatial_tools/stac/planetary_computer/sentinel_1.py
# Expected: no output (zero matches)
```

Expected: `pytest` green, `mypy`/`ruff` exit 0, ABC check prints `ABC enforcement ok`,
optical-field grep returns empty.

## 7. Completion Protocol

1. Verify every AC is checked off in Section 5.
2. Run all commands in Section 6 and confirm expected output.
3. Stage and commit:
    ```bash
    git add src/geospatial_tools/stac/planetary_computer/sentinel_1.py \
            tests/test_planetary_computer_sentinel1.py
    git commit -m "feat(stac-pc): implement AbstractSentinel1 base class — closes TASK-2"
    ```
4. Update this file: check off completed subtasks and ACs, note any deviations.
5. Notify the user with a concise summary and request approval before proceeding to TASK-3.
