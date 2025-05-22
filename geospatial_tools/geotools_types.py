"""This module contains constants and functions pertaining to data types."""

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
IntersectsLike = Union[Point, Polygon, LineString, MultiPolygon, MultiPoint, MultiLineString, GeometryCollection]
