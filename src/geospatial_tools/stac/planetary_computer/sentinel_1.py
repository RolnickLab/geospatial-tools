import logging
from pathlib import Path
from typing import Any, Self

from geospatial_tools.geotools_types import BBoxLike, DateLike, IntersectsLike
from geospatial_tools.stac.core import AbstractStacWrapper, Asset
from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS1Band,
    PlanetaryComputerS1Collection,
    PlanetaryComputerS1InstrumentMode,
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS1Polarization,
    PlanetaryComputerS1Property,
)

LOGGER = logging.getLogger(__name__)


class Sentinel1Search(AbstractStacWrapper):
    """
    Executable wrapper for Sentinel-1 GRD data on Planetary Computer.

    Implements a fluent builder pattern to construct STAC queries for SAR data.
    Execution and result storage are delegated to an underlying `StacSearch` client
    via proxy properties.
    """

    def __init__(
        self,
        collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
        date_range: DateLike = None,
        bbox: BBoxLike | None = None,
        intersects: IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initialize Sentinel1Search.

        Args:
            collection: The Sentinel-1 STAC collection (default: sentinel-1-grd).
            date_range: Temporal filter, native pystac DateLike.
            bbox: Spatial bounding box filter.
            intersects: Spatial GeoJSON geometry filter.
            logger: Custom logger instance.
        """
        super().__init__(collection=collection, date_range=date_range, bbox=bbox, intersects=intersects, logger=logger)

        self.instrument_modes: list[PlanetaryComputerS1InstrumentMode] | None = None
        self.polarizations: list[PlanetaryComputerS1Polarization] | None = None
        self.orbit_states: list[PlanetaryComputerS1OrbitState] | None = None
        self.custom_query_params: dict[str, Any] = {}

    def filter_by_instrument_mode(
        self, modes: list[PlanetaryComputerS1InstrumentMode] | PlanetaryComputerS1InstrumentMode
    ) -> Self:
        """
        Filter SAR products by instrument mode (e.g., IW, EW).

        Invalidates current search results.

        Args:
            modes: Single mode or list of `PlanetaryComputerS1InstrumentMode`.

        Returns:
            The instance itself (Self) for fluent chaining.
        """
        self._invalidate_state()
        if isinstance(modes, list):
            self.instrument_modes = modes
        else:
            self.instrument_modes = [modes]
        return self

    def filter_by_polarization(
        self, polarizations: list[PlanetaryComputerS1Polarization] | PlanetaryComputerS1Polarization
    ) -> Self:
        """
        Filter SAR products by polarization (e.g., VV, VH).

        Invalidates current search results. Note: PC STAC requires an exact array match
        for `sar:polarizations`.

        Args:
            polarizations: Single polarization or list of `PlanetaryComputerS1Polarization`.

        Returns:
            The instance itself (Self) for fluent chaining.
        """
        self._invalidate_state()
        if isinstance(polarizations, list):
            self.polarizations = polarizations
        else:
            self.polarizations = [polarizations]
        return self

    def filter_by_orbit_state(
        self, states: list[PlanetaryComputerS1OrbitState] | PlanetaryComputerS1OrbitState
    ) -> Self:
        """
        Filter SAR products by orbit state (ascending or descending).

        Invalidates current search results.

        Args:
            states: Single state or list of `PlanetaryComputerS1OrbitState`.

        Returns:
            The instance itself (Self) for fluent chaining.
        """
        self._invalidate_state()
        if isinstance(states, list):
            self.orbit_states = states
        else:
            self.orbit_states = [states]
        return self

    def _build_collection_query(self) -> dict[str, Any]:
        """
        Build the Sentinel-1 specific STAC query.

        Uses `PlanetaryComputerS1Property` for property keys and appropriate
        operators (`eq`, `in`) based on filter state.
        """
        query: dict[str, Any] = {}

        if self.instrument_modes:
            modes_str = [m.value for m in self.instrument_modes]
            if len(modes_str) == 1:
                query[PlanetaryComputerS1Property.INSTRUMENT_MODE.value] = {"eq": modes_str[0]}
            else:
                query[PlanetaryComputerS1Property.INSTRUMENT_MODE.value] = {"in": modes_str}

        if self.orbit_states:
            states_str = [s.value for s in self.orbit_states]
            if len(states_str) == 1:
                query[PlanetaryComputerS1Property.ORBIT_STATE.value] = {"eq": states_str[0]}
            else:
                query[PlanetaryComputerS1Property.ORBIT_STATE.value] = {"in": states_str}

        if self.polarizations:
            # PC STAC requires exact array match for sar:polarizations, `contains` is unsupported
            pols_str = [p.value for p in self.polarizations]
            query[PlanetaryComputerS1Property.POLARIZATIONS.value] = {"eq": pols_str}

        query.update(self.custom_query_params)
        return query

    def download(self, bands: list[PlanetaryComputerS1Band | str], base_directory: str | Path) -> list[Asset] | None:
        """
        Download Sentinel-1 assets with lowercase band key normalization.

        Args:
            bands: List of bands to download.
            base_directory: Local directory where assets will be saved.

        Returns:
            List of downloaded Asset objects.
        """
        # Small specialized override for S1 casing requirements
        lower_bands = [str(b).lower() for b in bands]
        return super().download(bands=lower_bands, base_directory=base_directory)
