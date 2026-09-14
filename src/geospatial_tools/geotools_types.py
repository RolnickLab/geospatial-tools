"""This module contains constants and functions pertaining to data types."""

from collections.abc import Iterator
from datetime import datetime
from typing import Union

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
    tuple[datetime | str | None, datetime | str | None],
    list[datetime | str | None],
    Iterator[datetime | str | None],
]
"""Date-like union of types used for type checking."""
