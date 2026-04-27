# pylint: disable=duplicate-code
import logging
from pathlib import Path
from typing import Any, Self

from geospatial_tools.geotools_types import BBoxLike, DateLike, IntersectsLike
from geospatial_tools.stac.core import AbstractStacWrapper, Asset
from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS3Band,
    PlanetaryComputerS3Collection,
    PlanetaryComputerS3Property,
)

LOGGER = logging.getLogger(__name__)


class Sentinel3Search(AbstractStacWrapper):
    """
    Executable wrapper for Sentinel-3 OLCI data on Planetary Computer.

    Implements a fluent builder pattern to construct STAC queries.
    Execution and result storage are delegated to an underlying `StacSearch` client
    via proxy properties.
    """

    def __init__(
        self,
        collection: PlanetaryComputerS3Collection | str = PlanetaryComputerS3Collection.OLCI_WFR,
        date_range: DateLike = None,
        bbox: BBoxLike | None = None,
        intersects: IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initialize Sentinel3Search.

        Args:
            collection: The Sentinel-3 STAC collection (default: sentinel-3-olci-wfr-l2-netcdf).
            date_range: Temporal filter, native pystac DateLike.
            bbox: Spatial bounding box filter.
            intersects: Spatial GeoJSON geometry filter.
            logger: Custom logger instance.
        """
        super().__init__(collection=collection, date_range=date_range, bbox=bbox, intersects=intersects, logger=logger)

        self.orbit_states: list[PlanetaryComputerS1OrbitState] | None = None
        self.custom_query_params: dict[str, Any] = {}

    def filter_by_orbit_state(
        self, states: list[PlanetaryComputerS1OrbitState] | PlanetaryComputerS1OrbitState
    ) -> Self:
        """
        Filter products by orbit state (ascending or descending).

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
        Build the Sentinel-3 specific STAC query.

        Uses `PlanetaryComputerS3Property` for property keys and appropriate
        operators (`eq`, `in`) based on filter state.
        """
        query: dict[str, Any] = {}

        if self.orbit_states:
            states_str = [s.value for s in self.orbit_states]
            if len(states_str) == 1:
                query[PlanetaryComputerS3Property.ORBIT_STATE.value] = {"eq": states_str[0]}
            else:
                query[PlanetaryComputerS3Property.ORBIT_STATE.value] = {"in": states_str}

        query.update(self.custom_query_params)
        return query

    def download(self, bands: list[PlanetaryComputerS3Band | str], base_directory: str | Path) -> list[Asset] | None:
        """
        Download Sentinel-3 assets with lowercase band key normalization.

        Args:
            bands: List of bands to download.
            base_directory: Local directory where assets will be saved.

        Returns:
            List of downloaded Asset objects.
        """
        lower_bands = [str(b).lower() for b in bands]
        return super().download(bands=lower_bands, base_directory=base_directory)
