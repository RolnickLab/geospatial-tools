"""Unit tests for Planetary Computer Sentinel-2 constants."""

import pytest

from geospatial_tools.stac.planetary_computer import (
    PlanetaryComputerS2Band,
    PlanetaryComputerS2Collection,
    PlanetaryComputerS2Property,
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
