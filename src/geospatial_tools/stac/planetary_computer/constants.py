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


class PlanetaryComputerS1Collection(StrEnum):
    """Planetary Computer Sentinel-1 Collections."""

    GRD = "sentinel-1-grd"


class PlanetaryComputerS1Property(StrEnum):
    """Planetary Computer Sentinel-1 STAC query properties."""

    INSTRUMENT_MODE = "sar:instrument_mode"
    POLARIZATIONS = "sar:polarizations"
    ORBIT_STATE = "sat:orbit_state"


class PlanetaryComputerS1Band(StrEnum):
    """
    Planetary Computer Sentinel-1 asset band keys.

    Used to fetch assets from the STAC item.
    """

    VV = "vv"
    VH = "vh"


class PlanetaryComputerS1InstrumentMode(StrEnum):
    """
    Planetary Computer Sentinel-1 instrument modes.

    Used for STAC queries.
    """

    IW = "IW"
    EW = "EW"
    SM = "SM"
    WV = "WV"


class PlanetaryComputerS1Polarization(StrEnum):
    """
    Planetary Computer Sentinel-1 polarizations.

    Used for STAC queries.
    """

    VV = "VV"
    VH = "VH"
    HH = "HH"
    HV = "HV"


class PlanetaryComputerS1OrbitState(StrEnum):
    """
    Planetary Computer Sentinel-1 orbit states.

    Used for STAC queries.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


class PlanetaryComputerS3Collection(StrEnum):
    """Planetary Computer Sentinel-3 Collections."""

    OLCI_L1B = "sentinel-3-olci-l1b-efr"
    OLCI_WFR = "sentinel-3-olci-wfr-l2-netcdf"


class PlanetaryComputerS3Property(StrEnum):
    """Planetary Computer Sentinel-3 STAC query properties."""

    ORBIT_STATE = "sat:orbit_state"


class PlanetaryComputerS3OrbitState(StrEnum):
    """
    Planetary Computer Sentinel-3 orbit states.

    Used for STAC queries.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


class PlanetaryComputerS3Band(StrEnum):
    """Planetary Computer Sentinel-3 asset band keys."""

    OA16 = "oa16-radiance"
    OA17 = "oa17-radiance"
    OA18 = "oa18-radiance"
    OA19 = "oa19-radiance"
    OA20 = "oa20-radiance"
    OA21 = "oa21-radiance"

    # Common name aliases
    NIR_865 = "oa17-radiance"
    WATER_VAPOUR = "oa19-radiance"
