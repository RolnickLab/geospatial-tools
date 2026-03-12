from geospatial_tools.copernicus.sentinel_2 import (
    CopernicusS2Band,
    CopernicusS2Collection,
    CopernicusS2Resolution,
)


def test_copernicus_s2_collection():
    assert CopernicusS2Collection.L2A == "sentinel-2-l2a"
    assert CopernicusS2Collection.L1C == "sentinel-2-l1c"


def test_copernicus_s2_resolution():
    assert CopernicusS2Resolution.R10M == 10
    assert CopernicusS2Resolution.R20M == 20
    assert CopernicusS2Resolution.R60M == 60
    assert str(CopernicusS2Resolution.R10M) == "10m"


def test_copernicus_s2_band_native_keys():
    # 10m native
    assert CopernicusS2Band.B02 == "B02_10m"
    assert CopernicusS2Band.BLUE == "B02_10m"
    assert CopernicusS2Band.B08 == "B08_10m"
    assert CopernicusS2Band.NIR == "B08_10m"
    assert CopernicusS2Band.TCI == "TCI_10m"

    # 20m native
    assert CopernicusS2Band.B05 == "B05_20m"
    assert CopernicusS2Band.RED_EDGE_1 == "B05_20m"
    assert CopernicusS2Band.B11 == "B11_20m"
    assert CopernicusS2Band.SWIR_1 == "B11_20m"

    # 60m native
    assert CopernicusS2Band.B01 == "B01_60m"
    assert CopernicusS2Band.COASTAL == "B01_60m"
    assert CopernicusS2Band.B09 == "B09_60m"


def test_copernicus_s2_band_explicit_keys():
    # Verify some explicit resolution members
    assert CopernicusS2Band.B04_10m == "B04_10m"
    assert CopernicusS2Band.B04_20m == "B04_20m"
    assert CopernicusS2Band.B04_60m == "B04_60m"

    assert CopernicusS2Band.B01_20m == "B01_20m"
    assert CopernicusS2Band.B01_60m == "B01_60m"

    assert CopernicusS2Band.SCL_20m == "SCL_20m"
    assert CopernicusS2Band.SCL_60m == "SCL_60m"


def test_copernicus_s2_band_at_res():
    # B02 native 10m -> 20m
    assert CopernicusS2Band.B02.at_res(20) == "B02_20m"
    assert CopernicusS2Band.BLUE.at_res(60) == "B02_60m"

    # B05 native 20m -> 60m
    assert CopernicusS2Band.B05.at_res(CopernicusS2Resolution.R60M) == "B05_60m"

    # B01 native 60m -> 20m
    assert CopernicusS2Band.COASTAL.at_res(20) == "B01_20m"


def test_copernicus_s2_band_properties():
    assert CopernicusS2Band.B02.base_name == "B02"
    assert CopernicusS2Band.BLUE.base_name == "B02"
    assert CopernicusS2Band.B02.native_res == 10

    assert CopernicusS2Band.B01.base_name == "B01"
    assert CopernicusS2Band.B01.native_res == 60

    assert CopernicusS2Band.B05.base_name == "B05"
    assert CopernicusS2Band.B05.native_res == 20
