"""Unit tests for Planetary Computer Sentinel-2 constants."""

import pytest

from geospatial_tools.stac.planetary_computer import (
    PlanetaryComputerS1Band,
    PlanetaryComputerS1Collection,
    PlanetaryComputerS1InstrumentMode,
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS1Polarization,
    PlanetaryComputerS1Property,
    PlanetaryComputerS2Band,
    PlanetaryComputerS2Collection,
    PlanetaryComputerS2Property,
    PlanetaryComputerS3Band,
    PlanetaryComputerS3Collection,
    PlanetaryComputerS3Property,
)


class TestPlanetaryComputerS2Collection:
    def test_l2a_value(self) -> None:
        assert PlanetaryComputerS2Collection.L2A == "sentinel-2-l2a"

    def test_is_str(self) -> None:
        assert isinstance(PlanetaryComputerS2Collection.L2A, str)

    def test_str_representation(self) -> None:
        assert str(PlanetaryComputerS2Collection.L2A) == "sentinel-2-l2a"


class TestPlanetaryComputerS2Property:
    def test_cloud_cover_value(self) -> None:
        assert PlanetaryComputerS2Property.CLOUD_COVER == "eo:cloud_cover"

    def test_mgrs_tile_value(self) -> None:
        assert PlanetaryComputerS2Property.MGRS_TILE == "s2:mgrs_tile"

    def test_nodata_pixel_percentage_value(self) -> None:
        assert PlanetaryComputerS2Property.NODATA_PIXEL_PERCENTAGE == "s2:nodata_pixel_percentage"

    def test_is_str(self) -> None:
        assert isinstance(PlanetaryComputerS2Property.CLOUD_COVER, str)

    def test_sortby_field_cloud_cover(self) -> None:
        assert PlanetaryComputerS2Property.CLOUD_COVER.sortby_field == "properties.eo:cloud_cover"

    def test_sortby_field_mgrs_tile(self) -> None:
        assert PlanetaryComputerS2Property.MGRS_TILE.sortby_field == "properties.s2:mgrs_tile"

    def test_sortby_field_nodata(self) -> None:
        assert (
            PlanetaryComputerS2Property.NODATA_PIXEL_PERCENTAGE.sortby_field == "properties.s2:nodata_pixel_percentage"
        )


class TestPlanetaryComputerS2Band:
    @pytest.mark.parametrize(
        "member, expected",
        [
            (PlanetaryComputerS2Band.B01, "B01"),
            (PlanetaryComputerS2Band.B02, "B02"),
            (PlanetaryComputerS2Band.B03, "B03"),
            (PlanetaryComputerS2Band.B04, "B04"),
            (PlanetaryComputerS2Band.B05, "B05"),
            (PlanetaryComputerS2Band.B06, "B06"),
            (PlanetaryComputerS2Band.B07, "B07"),
            (PlanetaryComputerS2Band.B08, "B08"),
            (PlanetaryComputerS2Band.B8A, "B8A"),
            (PlanetaryComputerS2Band.B09, "B09"),
            (PlanetaryComputerS2Band.B11, "B11"),
            (PlanetaryComputerS2Band.B12, "B12"),
            (PlanetaryComputerS2Band.SCL, "SCL"),
            (PlanetaryComputerS2Band.TCI, "TCI"),
            (PlanetaryComputerS2Band.AOT, "AOT"),
            (PlanetaryComputerS2Band.WVP, "WVP"),
        ],
    )
    def test_standard_band_values(self, member: PlanetaryComputerS2Band, expected: str) -> None:
        assert member == expected

    @pytest.mark.parametrize(
        "alias, expected_value",
        [
            (PlanetaryComputerS2Band.COASTAL, "B01"),
            (PlanetaryComputerS2Band.BLUE, "B02"),
            (PlanetaryComputerS2Band.GREEN, "B03"),
            (PlanetaryComputerS2Band.RED, "B04"),
            (PlanetaryComputerS2Band.RED_EDGE_1, "B05"),
            (PlanetaryComputerS2Band.RED_EDGE_2, "B06"),
            (PlanetaryComputerS2Band.RED_EDGE_3, "B07"),
            (PlanetaryComputerS2Band.NIR, "B08"),
            (PlanetaryComputerS2Band.NIR_NARROW, "B8A"),
            (PlanetaryComputerS2Band.SWIR_1, "B11"),
            (PlanetaryComputerS2Band.SWIR_2, "B12"),
        ],
    )
    def test_common_name_aliases(self, alias: PlanetaryComputerS2Band, expected_value: str) -> None:
        assert alias == expected_value

    def test_blue_alias_is_b02(self) -> None:
        assert PlanetaryComputerS2Band.BLUE == "B02"

    def test_is_str(self) -> None:
        assert isinstance(PlanetaryComputerS2Band.B02, str)


class TestPlanetaryComputerS1Collection:
    def test_grd_value(self) -> None:
        assert PlanetaryComputerS1Collection.GRD == "sentinel-1-grd"


class TestPlanetaryComputerS1Property:
    def test_property_values(self) -> None:
        assert PlanetaryComputerS1Property.INSTRUMENT_MODE == "sar:instrument_mode"
        assert PlanetaryComputerS1Property.POLARIZATIONS == "sar:polarizations"
        assert PlanetaryComputerS1Property.ORBIT_STATE == "sat:orbit_state"


class TestPlanetaryComputerS1Band:
    def test_band_values(self) -> None:
        assert PlanetaryComputerS1Band.VV == "vv"
        assert PlanetaryComputerS1Band.VH == "vh"


class TestPlanetaryComputerS1InstrumentMode:
    def test_instrument_mode_values(self) -> None:
        assert PlanetaryComputerS1InstrumentMode.IW == "IW"
        assert PlanetaryComputerS1InstrumentMode.EW == "EW"
        assert PlanetaryComputerS1InstrumentMode.SM == "SM"
        assert PlanetaryComputerS1InstrumentMode.WV == "WV"


class TestPlanetaryComputerS1Polarization:
    def test_polarization_values(self) -> None:
        assert PlanetaryComputerS1Polarization.VV == "VV"
        assert PlanetaryComputerS1Polarization.VH == "VH"
        assert PlanetaryComputerS1Polarization.HH == "HH"
        assert PlanetaryComputerS1Polarization.HV == "HV"

    def test_invariant_uppercase_property_vs_lowercase_asset(self) -> None:
        assert PlanetaryComputerS1Polarization.VV != PlanetaryComputerS1Band.VV
        assert PlanetaryComputerS1Polarization.VV == "VV"
        assert PlanetaryComputerS1Band.VV == "vv"


class TestPlanetaryComputerS1OrbitState:
    def test_orbit_state_values(self) -> None:
        assert PlanetaryComputerS1OrbitState.ASCENDING == "ascending"
        assert PlanetaryComputerS1OrbitState.DESCENDING == "descending"


class TestPlanetaryComputerS3Collection:
    def test_collection_values(self) -> None:
        assert PlanetaryComputerS3Collection.OLCI_L1B == "sentinel-3-olci-l1b-efr"
        assert PlanetaryComputerS3Collection.OLCI_WFR == "sentinel-3-olci-wfr-l2-netcdf"


class TestPlanetaryComputerS3Property:
    def test_property_values(self) -> None:
        assert PlanetaryComputerS3Property.ORBIT_STATE == "sat:orbit_state"


class TestPlanetaryComputerS3Band:
    def test_band_values(self) -> None:
        assert PlanetaryComputerS3Band.OA16 == "oa16-radiance"
        assert PlanetaryComputerS3Band.OA17 == "oa17-radiance"
        assert PlanetaryComputerS3Band.OA18 == "oa18-radiance"
        assert PlanetaryComputerS3Band.OA19 == "oa19-radiance"
        assert PlanetaryComputerS3Band.OA20 == "oa20-radiance"
        assert PlanetaryComputerS3Band.OA21 == "oa21-radiance"

    def test_band_aliases(self) -> None:
        assert PlanetaryComputerS3Band.NIR_865 == PlanetaryComputerS3Band.OA17
        assert PlanetaryComputerS3Band.WATER_VAPOUR == PlanetaryComputerS3Band.OA19
        assert PlanetaryComputerS3Band.NIR_865 == "oa17-radiance"
