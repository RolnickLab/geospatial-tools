# pylint: disable=duplicate-code
"""UsgsLandsat USGS_EROS Landsat Level-1 Collection 2 STAC wrappers."""

from __future__ import annotations

import abc
import logging
from typing import Any, Self

from geospatial_tools.geotools_types import BBoxLike, DateLike, IntersectsLike
from geospatial_tools.stac.core import LOGGER, USGS_LANDSAT, AbstractStacWrapper
from geospatial_tools.stac.usgs_landsat.constants import (
    UsgsLandsatLandsatCollection,
    UsgsLandsatLandsatPlatform,
    UsgsLandsatLandsatProperty,
)


class AbstractLandsat(AbstractStacWrapper):
    """
    Abstract base class for Landsat Level-1 Collection 2 STAC search wrappers.

    Targets the CMR UsgsLandsat USGS_EROS catalog. Concrete subclasses must declare
    the ``_platform`` class attribute to select LANDSAT_8 or LANDSAT_9.
    """

    @property
    @abc.abstractmethod
    def _platform(self) -> UsgsLandsatLandsatPlatform:  # noqa: N802
        """
        Platform constant identifying the Landsat satellite.

        Subclasses set this as a class attribute.
        """

    def __init__(
        self,
        collection: UsgsLandsatLandsatCollection | str = UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2,
        date_range: DateLike = None,
        bbox: BBoxLike | None = None,
        intersects: IntersectsLike | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initialize the Landsat STAC wrapper targeting the UsgsLandsat catalog.

        Args:
            collection: Landsat collection ID. Defaults to Level-1 Collection 2.
            date_range: Temporal filter for the search.
            bbox: Spatial bounding box filter.
            intersects: Spatial GeoJSON geometry filter.
            logger: Logger instance.
        """
        super().__init__(
            catalog_name=USGS_LANDSAT,
            collection=collection,
            date_range=date_range,
            bbox=bbox,
            intersects=intersects,
            logger=logger,
        )

    def filter_by_cloud_cover(self, max_cloud_cover: int) -> Self:
        """
        Filter by maximum cloud cover percentage.

        Writes the cloud cover constraint into ``custom_query_params`` so it
        is merged into the STAC query by the base-class ``search()`` call.
        Invalidates cached results.

        Args:
            max_cloud_cover: Maximum allowed cloud cover percentage (exclusive upper bound).

        Returns:
            The instance itself for fluent chaining.
        """
        self._invalidate_state()
        self.custom_query_params[UsgsLandsatLandsatProperty.CLOUD_COVER.value] = {"lt": max_cloud_cover}
        return self

    def _build_collection_query(self) -> dict[str, Any]:
        """
        Build the Landsat platform query.

        Returns:
            Query dict with a platform equality filter.
        """
        return {UsgsLandsatLandsatProperty.PLATFORM.value: {"eq": self._platform.value}}


class Landsat8Search(AbstractLandsat):
    """Concrete STAC wrapper for Landsat 8 Level-1 Collection 2 on UsgsLandsat USGS_EROS."""

    _platform = UsgsLandsatLandsatPlatform.LANDSAT_8


class Landsat9Search(AbstractLandsat):
    """Concrete STAC wrapper for Landsat 9 Level-1 Collection 2 on UsgsLandsat USGS_EROS."""

    _platform = UsgsLandsatLandsatPlatform.LANDSAT_9
