from typing import Tuple, Union

from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

BBoxLike = Tuple[float, float, float, float]
IntersectsLike = Union[Point, Polygon, LineString, MultiPolygon, MultiPoint, MultiLineString, GeometryCollection]
