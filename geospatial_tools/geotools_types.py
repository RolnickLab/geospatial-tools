"""This module contains constants and functions pertaining to data types."""

from datetime import datetime
from typing import Iterator, Union

from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

BBoxLike = tuple[float, float, float, float]
"""BBox like tuple structure used for type checking."""

IntersectsLike = Union[Point, Polygon, LineString, MultiPolygon, MultiPoint, MultiLineString, GeometryCollection]
"""Intersect-like union of types used for type checking."""

DateLike = Union[
    datetime,
    str,
    None,
    tuple[Union[datetime, str, None], Union[datetime, str, None]],
    list[Union[datetime, str, None]],
    Iterator[Union[datetime, str, None]],
]
"""Date-like union of types used for type checking."""
