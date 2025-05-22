"""This module contains constants and functions pertaining to data types."""

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
IntersectsLike = Point | Polygon | LineString | MultiPolygon | MultiPoint | MultiLineString | GeometryCollection
