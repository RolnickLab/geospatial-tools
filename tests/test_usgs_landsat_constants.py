"""Unit tests for CMR UsgsLandsat USGS_EROS Landsat constants."""

import pytest

from geospatial_tools.stac.usgs_landsat import (
    UsgsLandsatLandsatBand,
    UsgsLandsatLandsatCollection,
    UsgsLandsatLandsatPlatform,
    UsgsLandsatLandsatProperty,
)


class TestUsgsLandsatLandsatCollection:
    def test_level_1_collection_2_value(self) -> None:
        assert UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2 == "landsat-c2l1"

    def test_collection_id_contains_landsat_level_1(self) -> None:
        assert "landsat-c2l1" in UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2

    def test_is_str(self) -> None:
        assert isinstance(UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2, str)

    def test_str_representation(self) -> None:
        assert str(UsgsLandsatLandsatCollection.LEVEL_1_COLLECTION_2) == "landsat-c2l1"


class TestUsgsLandsatLandsatProperty:
    def test_platform_value(self) -> None:
        assert UsgsLandsatLandsatProperty.PLATFORM == "platform"

    def test_cloud_cover_value(self) -> None:
        assert UsgsLandsatLandsatProperty.CLOUD_COVER == "eo:cloud_cover"

    def test_is_str(self) -> None:
        assert isinstance(UsgsLandsatLandsatProperty.PLATFORM, str)

    def test_sortby_field_platform(self) -> None:
        assert UsgsLandsatLandsatProperty.PLATFORM.sortby_field == "properties.platform"

    def test_sortby_field_cloud_cover(self) -> None:
        assert UsgsLandsatLandsatProperty.CLOUD_COVER.sortby_field == "properties.eo:cloud_cover"


class TestUsgsLandsatLandsatPlatform:
    def test_landsat_8_value(self) -> None:
        assert UsgsLandsatLandsatPlatform.LANDSAT_8 == "LANDSAT_8"

    def test_landsat_9_value(self) -> None:
        assert UsgsLandsatLandsatPlatform.LANDSAT_9 == "LANDSAT_9"

    def test_is_str(self) -> None:
        assert isinstance(UsgsLandsatLandsatPlatform.LANDSAT_8, str)


class TestUsgsLandsatLandsatBand:
    @pytest.mark.parametrize(
        "member, expected",
        [
            (UsgsLandsatLandsatBand.COASTAL, "coastal"),
            (UsgsLandsatLandsatBand.BLUE, "blue"),
            (UsgsLandsatLandsatBand.GREEN, "green"),
            (UsgsLandsatLandsatBand.RED, "red"),
            (UsgsLandsatLandsatBand.NIR08, "nir08"),
            (UsgsLandsatLandsatBand.SWIR16, "swir16"),
            (UsgsLandsatLandsatBand.SWIR22, "swir22"),
            (UsgsLandsatLandsatBand.PAN, "pan"),
            (UsgsLandsatLandsatBand.CIRRUS, "cirrus"),
            (UsgsLandsatLandsatBand.LWIR11, "lwir11"),
            (UsgsLandsatLandsatBand.LWIR12, "lwir12"),
            (UsgsLandsatLandsatBand.QA_PIXEL, "qa_pixel"),
            (UsgsLandsatLandsatBand.QA_RADSAT, "qa_radsat"),
            (UsgsLandsatLandsatBand.SAA, "SAA"),
            (UsgsLandsatLandsatBand.SZA, "SZA"),
            (UsgsLandsatLandsatBand.VAA, "VAA"),
            (UsgsLandsatLandsatBand.VZA, "VZA"),
            (UsgsLandsatLandsatBand.ANG_TXT, "ANG.txt"),
            (UsgsLandsatLandsatBand.MTL_JSON, "MTL.json"),
            (UsgsLandsatLandsatBand.MTL_TXT, "MTL.txt"),
            (UsgsLandsatLandsatBand.MTL_XML, "MTL.xml"),
            (UsgsLandsatLandsatBand.THUMBNAIL, "thumbnail"),
            (UsgsLandsatLandsatBand.REDUCED_RESOLUTION_BROWSE, "reduced_resolution_browse"),
            (UsgsLandsatLandsatBand.INDEX, "index"),
        ],
    )
    def test_standard_band_values(self, member: UsgsLandsatLandsatBand, expected: str) -> None:
        assert member == expected

    @pytest.mark.parametrize(
        "alias, expected_value",
        [
            (UsgsLandsatLandsatBand.NIR, "nir08"),
            (UsgsLandsatLandsatBand.SWIR_1, "swir16"),
            (UsgsLandsatLandsatBand.SWIR_2, "swir22"),
            (UsgsLandsatLandsatBand.THERMAL_1, "lwir11"),
            (UsgsLandsatLandsatBand.THERMAL_2, "lwir12"),
        ],
    )
    def test_common_name_aliases(self, alias: UsgsLandsatLandsatBand, expected_value: str) -> None:
        assert alias == expected_value

    def test_nir_alias_equals_nir08(self) -> None:
        assert UsgsLandsatLandsatBand.NIR == UsgsLandsatLandsatBand.NIR08

    def test_swir_1_alias_equals_swir16(self) -> None:
        assert UsgsLandsatLandsatBand.SWIR_1 == UsgsLandsatLandsatBand.SWIR16

    def test_swir_2_alias_equals_swir22(self) -> None:
        assert UsgsLandsatLandsatBand.SWIR_2 == UsgsLandsatLandsatBand.SWIR22

    def test_thermal_1_alias_equals_lwir11(self) -> None:
        assert UsgsLandsatLandsatBand.THERMAL_1 == UsgsLandsatLandsatBand.LWIR11

    def test_thermal_2_alias_equals_lwir12(self) -> None:
        assert UsgsLandsatLandsatBand.THERMAL_2 == UsgsLandsatLandsatBand.LWIR12

    def test_is_str(self) -> None:
        assert isinstance(UsgsLandsatLandsatBand.BLUE, str)
