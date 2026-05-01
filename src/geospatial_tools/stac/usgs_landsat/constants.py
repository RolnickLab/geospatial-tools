"""Constants for CMR UsgsLandsat USGS_EROS Landsat STAC catalog."""

from enum import StrEnum


class UsgsLandsatLandsatCollection(StrEnum):
    """
    CMR UsgsLandsat USGS_EROS Landsat collections.

    Collection IDs verified against https://landsatlook.usgs.gov/stac-servercollections
    on 2026-04-30.
    """

    LEVEL_1_COLLECTION_2 = "landsat-c2l1"


class UsgsLandsatLandsatProperty(StrEnum):
    """CMR UsgsLandsat USGS_EROS Landsat STAC query properties."""

    PLATFORM = "platform"
    CLOUD_COVER = "eo:cloud_cover"

    @property
    def sortby_field(self) -> str:
        """Returns the full JSON path prefix required by the STAC API sortby object."""
        return f"properties.{self.value}"


class UsgsLandsatLandsatPlatform(StrEnum):
    """Landsat platform query values as returned by the USGS_EROS STAC catalog."""

    LANDSAT_8 = "LANDSAT_8"
    LANDSAT_9 = "LANDSAT_9"


class UsgsLandsatLandsatBand(StrEnum):
    """
    Landsat Collection 2 Level-1 asset keys.

    Asset keys are verbatim strings as returned by the USGS LandsatLook STAC catalog
    (https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l1).
    Reconnaissance item: LC09_L1GT_042206_20260430_20260430_02_T2 (LANDSAT_9).
    Identical keys observed for LANDSAT_8 items.

    Note: CMR USGS_EROS STAC search (https://landsatlook.usgs.gov/stac-serversearch)
    returned 0 items during reconnaissance (2026-04-30) despite a valid collection ID.
    Keys were sourced from the USGS LandsatLook STAC, which is the operational USGS
    Landsat Collection 2 STAC endpoint and uses the same asset key schema.
    """

    # Spectral bands
    COASTAL = "coastal"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    NIR08 = "nir08"
    SWIR16 = "swir16"
    SWIR22 = "swir22"
    PAN = "pan"
    CIRRUS = "cirrus"
    LWIR11 = "lwir11"
    LWIR12 = "lwir12"

    # QA bands
    QA_PIXEL = "qa_pixel"
    QA_RADSAT = "qa_radsat"

    # Angle bands
    SAA = "SAA"
    SZA = "SZA"
    VAA = "VAA"
    VZA = "VZA"

    # Metadata files
    ANG_TXT = "ANG.txt"
    MTL_JSON = "MTL.json"
    MTL_TXT = "MTL.txt"
    MTL_XML = "MTL.xml"

    # Visualization assets
    THUMBNAIL = "thumbnail"
    REDUCED_RESOLUTION_BROWSE = "reduced_resolution_browse"
    INDEX = "index"

    # Common-name aliases (share values with backing standard bands above)
    NIR = "nir08"
    SWIR_1 = "swir16"
    SWIR_2 = "swir22"
    THERMAL_1 = "lwir11"
    THERMAL_2 = "lwir12"
