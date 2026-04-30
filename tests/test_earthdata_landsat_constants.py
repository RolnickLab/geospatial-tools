"""Unit tests for CMR Earthdata USGS_EROS Landsat constants."""

import pytest

from geospatial_tools.stac.earthdata import (
    EarthdataLandsatBand,
    EarthdataLandsatCollection,
    EarthdataLandsatPlatform,
    EarthdataLandsatProperty,
)


class TestEarthdataLandsatCollection:
    def test_level_1_collection_2_value(self) -> None:
        assert EarthdataLandsatCollection.LEVEL_1_COLLECTION_2 == "Landsat Level-1 Collection 2_Collection 2"

    def test_collection_id_contains_landsat_level_1(self) -> None:
        assert "Landsat Level-1 Collection 2" in EarthdataLandsatCollection.LEVEL_1_COLLECTION_2

    def test_is_str(self) -> None:
        assert isinstance(EarthdataLandsatCollection.LEVEL_1_COLLECTION_2, str)

    def test_str_representation(self) -> None:
        assert str(EarthdataLandsatCollection.LEVEL_1_COLLECTION_2) == "Landsat Level-1 Collection 2_Collection 2"


class TestEarthdataLandsatProperty:
    def test_platform_value(self) -> None:
        assert EarthdataLandsatProperty.PLATFORM == "platform"

    def test_cloud_cover_value(self) -> None:
        assert EarthdataLandsatProperty.CLOUD_COVER == "eo:cloud_cover"

    def test_is_str(self) -> None:
        assert isinstance(EarthdataLandsatProperty.PLATFORM, str)

    def test_sortby_field_platform(self) -> None:
        assert EarthdataLandsatProperty.PLATFORM.sortby_field == "properties.platform"

    def test_sortby_field_cloud_cover(self) -> None:
        assert EarthdataLandsatProperty.CLOUD_COVER.sortby_field == "properties.eo:cloud_cover"


class TestEarthdataLandsatPlatform:
    def test_landsat_8_value(self) -> None:
        assert EarthdataLandsatPlatform.LANDSAT_8 == "LANDSAT_8"

    def test_landsat_9_value(self) -> None:
        assert EarthdataLandsatPlatform.LANDSAT_9 == "LANDSAT_9"

    def test_is_str(self) -> None:
        assert isinstance(EarthdataLandsatPlatform.LANDSAT_8, str)


class TestEarthdataLandsatBand:
    @pytest.mark.parametrize(
        "member, expected",
        [
            (EarthdataLandsatBand.COASTAL, "coastal"),
            (EarthdataLandsatBand.BLUE, "blue"),
            (EarthdataLandsatBand.GREEN, "green"),
            (EarthdataLandsatBand.RED, "red"),
            (EarthdataLandsatBand.NIR08, "nir08"),
            (EarthdataLandsatBand.SWIR16, "swir16"),
            (EarthdataLandsatBand.SWIR22, "swir22"),
            (EarthdataLandsatBand.PAN, "pan"),
            (EarthdataLandsatBand.CIRRUS, "cirrus"),
            (EarthdataLandsatBand.LWIR11, "lwir11"),
            (EarthdataLandsatBand.LWIR12, "lwir12"),
            (EarthdataLandsatBand.QA_PIXEL, "qa_pixel"),
            (EarthdataLandsatBand.QA_RADSAT, "qa_radsat"),
            (EarthdataLandsatBand.SAA, "SAA"),
            (EarthdataLandsatBand.SZA, "SZA"),
            (EarthdataLandsatBand.VAA, "VAA"),
            (EarthdataLandsatBand.VZA, "VZA"),
            (EarthdataLandsatBand.ANG_TXT, "ANG.txt"),
            (EarthdataLandsatBand.MTL_JSON, "MTL.json"),
            (EarthdataLandsatBand.MTL_TXT, "MTL.txt"),
            (EarthdataLandsatBand.MTL_XML, "MTL.xml"),
            (EarthdataLandsatBand.THUMBNAIL, "thumbnail"),
            (EarthdataLandsatBand.REDUCED_RESOLUTION_BROWSE, "reduced_resolution_browse"),
            (EarthdataLandsatBand.INDEX, "index"),
        ],
    )
    def test_standard_band_values(self, member: EarthdataLandsatBand, expected: str) -> None:
        assert member == expected

    @pytest.mark.parametrize(
        "alias, expected_value",
        [
            (EarthdataLandsatBand.NIR, "nir08"),
            (EarthdataLandsatBand.SWIR_1, "swir16"),
            (EarthdataLandsatBand.SWIR_2, "swir22"),
            (EarthdataLandsatBand.THERMAL_1, "lwir11"),
            (EarthdataLandsatBand.THERMAL_2, "lwir12"),
        ],
    )
    def test_common_name_aliases(self, alias: EarthdataLandsatBand, expected_value: str) -> None:
        assert alias == expected_value

    def test_nir_alias_equals_nir08(self) -> None:
        assert EarthdataLandsatBand.NIR == EarthdataLandsatBand.NIR08

    def test_swir_1_alias_equals_swir16(self) -> None:
        assert EarthdataLandsatBand.SWIR_1 == EarthdataLandsatBand.SWIR16

    def test_swir_2_alias_equals_swir22(self) -> None:
        assert EarthdataLandsatBand.SWIR_2 == EarthdataLandsatBand.SWIR22

    def test_thermal_1_alias_equals_lwir11(self) -> None:
        assert EarthdataLandsatBand.THERMAL_1 == EarthdataLandsatBand.LWIR11

    def test_thermal_2_alias_equals_lwir12(self) -> None:
        assert EarthdataLandsatBand.THERMAL_2 == EarthdataLandsatBand.LWIR12

    def test_is_str(self) -> None:
        assert isinstance(EarthdataLandsatBand.BLUE, str)
