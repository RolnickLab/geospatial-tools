import abc
import logging
from pathlib import Path
from typing import Any

import pystac

from geospatial_tools.geotools_types import BBoxLike, DateLike, IntersectsLike
from geospatial_tools.stac.core import PLANETARY_COMPUTER, Asset, StacSearch
from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS1Band,
    PlanetaryComputerS1Collection,
    PlanetaryComputerS1InstrumentMode,
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS1Polarization,
)

LOGGER = logging.getLogger(__name__)


class AbstractSentinel1(abc.ABC):
    """Abstract base class for Planetary Computer Sentinel-1 STAC wrapper."""

    def __init__(
        self,
        collection: PlanetaryComputerS1Collection | str = PlanetaryComputerS1Collection.GRD,
        date_range: DateLike = None,
        bbox: BBoxLike | None = None,
        intersects: IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initialize AbstractSentinel1.

        Args:
            collection: The Sentinel-1 STAC collection (default: sentinel-1-grd).
            date_range: Temporal filter, native pystac DateLike.
            bbox: Spatial bounding box filter.
            intersects: Spatial GeoJSON geometry filter.
            logger: Custom logger instance.
        """
        self.collection = collection
        self.date_range = date_range
        self.bbox = bbox
        self.intersects = intersects
        self.logger = logger

        self.client: StacSearch = StacSearch(PLANETARY_COMPUTER)

        self.instrument_modes: list[PlanetaryComputerS1InstrumentMode] | None = None
        self.polarizations: list[PlanetaryComputerS1Polarization] | None = None
        self.orbit_states: list[PlanetaryComputerS1OrbitState] | None = None
        self.custom_query_params: dict[str, Any] = {}

        self.search_results: list[pystac.Item] | None = None
        self.downloaded_assets: list[Asset] | None = None

    def filter_by_instrument_mode(
        self, modes: list[PlanetaryComputerS1InstrumentMode] | PlanetaryComputerS1InstrumentMode
    ) -> "AbstractSentinel1":
        """Filter SAR products by instrument mode (e.g., IW, EW)."""
        if isinstance(modes, list):
            self.instrument_modes = modes
        else:
            self.instrument_modes = [modes]
        return self

    def filter_by_polarization(
        self, polarizations: list[PlanetaryComputerS1Polarization] | PlanetaryComputerS1Polarization
    ) -> "AbstractSentinel1":
        """Filter SAR products by polarization (e.g., VV, VH)."""
        if isinstance(polarizations, list):
            self.polarizations = polarizations
        else:
            self.polarizations = [polarizations]
        return self

    def filter_by_orbit_state(
        self, states: list[PlanetaryComputerS1OrbitState] | PlanetaryComputerS1OrbitState
    ) -> "AbstractSentinel1":
        """Filter SAR products by orbit state (ascending or descending)."""
        if isinstance(states, list):
            self.orbit_states = states
        else:
            self.orbit_states = [states]
        return self

    def with_custom_query(self, query_params: dict[str, Any]) -> "AbstractSentinel1":
        """Merge custom STAC query parameters."""
        self.custom_query_params.update(query_params)
        return self

    @abc.abstractmethod
    def search(self) -> list[pystac.Item]:
        """Execute the STAC search with the built query."""

    @abc.abstractmethod
    def download(self, bands: list[PlanetaryComputerS1Band | str], base_directory: str | Path) -> list[Asset]:
        """Download assets for the matched search results."""
