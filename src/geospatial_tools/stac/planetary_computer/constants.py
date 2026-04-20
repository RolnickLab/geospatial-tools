"""Constants for Planetary Computer Sentinel-2 STAC catalog."""

from enum import StrEnum


class PlanetaryComputerS2Collection(StrEnum):
    """Planetary Computer Sentinel-2 Collections."""

    L2A = "sentinel-2-l2a"


class PlanetaryComputerS2Property(StrEnum):
    """Planetary Computer Sentinel-2 STAC query properties."""

    CLOUD_COVER = "eo:cloud_cover"
    MGRS_TILE = "s2:mgrs_tile"
    NODATA_PIXEL_PERCENTAGE = "s2:nodata_pixel_percentage"

    @property
    def sortby_field(self) -> str:
        """Returns the full JSON path prefix required by the STAC API sortby object."""
        return f"properties.{self.value}"


class PlanetaryComputerS2Band(StrEnum):
    """
    Planetary Computer Sentinel-2 asset band keys.

    Planetary Computer uses plain base names (e.g., "B02") as asset keys, unlike Copernicus which appends resolution
    suffixes.
    """

    # Standard bands
    B01 = "B01"
    B02 = "B02"
    B03 = "B03"
    B04 = "B04"
    B05 = "B05"
    B06 = "B06"
    B07 = "B07"
    B08 = "B08"
    B8A = "B8A"
    B09 = "B09"
    B11 = "B11"
    B12 = "B12"
    SCL = "SCL"
    TCI = "TCI"
    AOT = "AOT"
    WVP = "WVP"

    # Common name aliases (alias members share values with standard bands above)
    COASTAL = "B01"
    BLUE = "B02"
    GREEN = "B03"
    RED = "B04"
    RED_EDGE_1 = "B05"
    RED_EDGE_2 = "B06"
    RED_EDGE_3 = "B07"
    NIR = "B08"
    NIR_NARROW = "B8A"
    SWIR_1 = "B11"
    SWIR_2 = "B12"
