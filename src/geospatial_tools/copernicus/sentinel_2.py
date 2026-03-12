"""This module contains Enums for Sentinel-2 on Copernicus Data Space Ecosystem (CDSE)."""

from enum import Enum

# --- Constants & Mappings ---

# Sentinel-2 Level-2A native resolution mapping based on mission specifications.
# Centralized mapping to avoid magic numbers and facilitate maintainability.
# Reference: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
_S2_NATIVE_RESOLUTION_MAP: dict[str, int] = {
    "B02": 10,
    "B03": 10,
    "B04": 10,
    "B08": 10,
    "TCI": 10,
    "WVP": 10,
    "AOT": 10,
    "B05": 20,
    "B06": 20,
    "B07": 20,
    "B8A": 20,
    "B11": 20,
    "B12": 20,
    "SCL": 20,
    "CLD": 20,
    "SNW": 20,
    "B01": 60,
    "B09": 60,
}


class CopernicusS2Collection(str, Enum):
    """Copernicus Sentinel-2 Collections."""

    L2A = "sentinel-2-l2a"
    L1C = "sentinel-2-l1c"


class CopernicusS2Resolution(int, Enum):
    """Copernicus Sentinel-2 Resolutions in meters."""

    R10M = 10
    R20M = 20
    R60M = 60

    def __str__(self) -> str:
        """Returns the resolution as a string with 'm' suffix."""
        return f"{self.value}m"


class CopernicusS2Band(str, Enum):
    """
    Copernicus Sentinel-2 Bands for Level-2A.

    The value of each member corresponds to the asset key for the band. Base band names (e.g., 'B02') default to their
    native resolution. Explicit resolution members (e.g., 'B02_20m') are also provided.
    """

    # --- Native / Default Members ---

    # 10m Native
    B02 = "B02_10m"
    B03 = "B03_10m"
    B04 = "B04_10m"
    B08 = "B08_10m"
    TCI = "TCI_10m"
    WVP = "WVP_10m"
    AOT = "AOT_10m"

    # 20m Native
    B05 = "B05_20m"
    B06 = "B06_20m"
    B07 = "B07_20m"
    B8A = "B8A_20m"
    B11 = "B11_20m"
    B12 = "B12_20m"
    SCL = "SCL_20m"
    CLD = "CLD_20m"
    SNW = "SNW_20m"

    # 60m Native
    B01 = "B01_60m"
    B09 = "B09_60m"

    # --- Explicit Resolution Members ---

    # 10m
    B02_10m = "B02_10m"
    B03_10m = "B03_10m"
    B04_10m = "B04_10m"
    B08_10m = "B08_10m"
    TCI_10m = "TCI_10m"
    WVP_10m = "WVP_10m"
    AOT_10m = "AOT_10m"

    # 20m
    B01_20m = "B01_20m"
    B02_20m = "B02_20m"
    B03_20m = "B03_20m"
    B04_20m = "B04_20m"
    B05_20m = "B05_20m"
    B06_20m = "B06_20m"
    B07_20m = "B07_20m"
    B8A_20m = "B8A_20m"
    B11_20m = "B11_20m"
    B12_20m = "B12_20m"
    TCI_20m = "TCI_20m"
    WVP_20m = "WVP_20m"
    AOT_20m = "AOT_20m"
    SCL_20m = "SCL_20m"
    CLD_20m = "CLD_20m"
    SNW_20m = "SNW_20m"

    # 60m
    B01_60m = "B01_60m"
    B02_60m = "B02_60m"
    B03_60m = "B03_60m"
    B04_60m = "B04_60m"
    B05_60m = "B05_60m"
    B06_60m = "B06_60m"
    B07_60m = "B07_60m"
    B08_60m = "B08_60m"
    B09_60m = "B09_60m"
    B8A_60m = "B8A_60m"
    B11_60m = "B11_60m"
    B12_60m = "B12_60m"
    TCI_60m = "TCI_60m"
    WVP_60m = "WVP_60m"
    AOT_60m = "AOT_60m"
    SCL_60m = "SCL_60m"
    CLD_60m = "CLD_60m"
    SNW_60m = "SNW_60m"

    # --- Common Names ---
    COASTAL = "B01_60m"
    BLUE = "B02_10m"
    GREEN = "B03_10m"
    RED = "B04_10m"
    RED_EDGE_1 = "B05_20m"
    RED_EDGE_2 = "B06_20m"
    RED_EDGE_3 = "B07_20m"
    NIR = "B08_10m"
    NIR_NARROW = "B8A_20m"
    SWIR_1 = "B11_20m"
    SWIR_2 = "B12_20m"

    @property
    def base_name(self) -> str:
        """Returns the base name of the band (e.g., 'B02')."""
        return self.value.split("_")[0]

    @property
    def native_res(self) -> int:
        """
        Returns the native resolution of the band in meters.

        Defaults to 10m if band base name is not recognized.
        """
        return _S2_NATIVE_RESOLUTION_MAP.get(self.base_name, 10)

    def at_res(self, resolution: int | CopernicusS2Resolution) -> str:
        """
        Returns the asset key for this band at the specified resolution.

        Args:
            resolution: The resolution to get the key for (e.g., 20 or CopernicusS2Resolution.R20M).

        Returns:
            The asset key string (e.g., 'B02_20m').
        """
        res_val = resolution.value if isinstance(resolution, CopernicusS2Resolution) else resolution
        return f"{self.base_name}_{res_val}m"
