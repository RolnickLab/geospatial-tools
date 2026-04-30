"""Abstract base class for Earthdata USGS_EROS Landsat STAC wrappers."""

from __future__ import annotations

import abc
import logging
from typing import Any

from geospatial_tools.geotools_types import BBoxLike, DateLike, IntersectsLike
from geospatial_tools.stac.core import EARTHDATA, LOGGER, AbstractStacWrapper
from geospatial_tools.stac.earthdata.constants import (
    EarthdataLandsatCollection,
    EarthdataLandsatPlatform,
    EarthdataLandsatProperty,
)


class AbstractLandsat(AbstractStacWrapper):
    """
    Abstract base class for Landsat Level-1 Collection 2 STAC search wrappers.

    Targets the CMR Earthdata USGS_EROS catalog. Concrete subclasses must declare
    the ``_PLATFORM`` class attribute to select LANDSAT_8 or LANDSAT_9.
    """

    @property
    @abc.abstractmethod
    def _PLATFORM(self) -> EarthdataLandsatPlatform:  # noqa: N802
        """
        Platform constant identifying the Landsat satellite.

        Subclasses set this as a class attribute.
        """

    def __init__(
        self,
        collection: EarthdataLandsatCollection | str = EarthdataLandsatCollection.LEVEL_1_COLLECTION_2,
        date_range: DateLike = None,
        bbox: BBoxLike | None = None,
        intersects: IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initialize the Landsat STAC wrapper targeting the Earthdata catalog.

        Args:
            collection: Landsat collection ID. Defaults to Level-1 Collection 2.
            date_range: Temporal filter for the search.
            bbox: Spatial bounding box filter.
            intersects: Spatial GeoJSON geometry filter.
            logger: Logger instance.
        """
        super().__init__(
            catalog_name=EARTHDATA,
            collection=collection,
            date_range=date_range,
            bbox=bbox,
            intersects=intersects,
            logger=logger,
        )

    def _build_collection_query(self) -> dict[str, Any]:
        """
        Build the Landsat platform query.

        Returns:
            Query dict with a platform equality filter.
        """
        return {EarthdataLandsatProperty.PLATFORM.value: {"eq": self._PLATFORM.value}}
