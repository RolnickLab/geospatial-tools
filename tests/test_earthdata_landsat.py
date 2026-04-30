"""Unit tests for AbstractLandsat, Landsat8/9Search, and AbstractStacWrapper catalog_name refactor."""

from unittest.mock import patch

import pytest

from geospatial_tools.stac.core import (
    EARTHDATA,
    PLANETARY_COMPUTER,
    AbstractStacWrapper,
    StacSearch,
)
from geospatial_tools.stac.earthdata import (
    AbstractLandsat,
    Landsat8Search,
    Landsat9Search,
)
from geospatial_tools.stac.earthdata.constants import (
    EarthdataLandsatCollection,
    EarthdataLandsatPlatform,
    EarthdataLandsatProperty,
)
from geospatial_tools.stac.planetary_computer.sentinel_2 import Sentinel2Search

# ---------------------------------------------------------------------------
# Minimal concrete subclasses for testing AbstractLandsat
# ---------------------------------------------------------------------------


class _Landsat8Stub(AbstractLandsat):
    _PLATFORM = EarthdataLandsatPlatform.LANDSAT_8


class _Landsat9Stub(AbstractLandsat):
    _PLATFORM = EarthdataLandsatPlatform.LANDSAT_9


# ---------------------------------------------------------------------------
# AbstractLandsat instantiation guard
# ---------------------------------------------------------------------------


def test_abstract_landsat_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        AbstractLandsat()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# AbstractLandsat targets EARTHDATA catalog
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_stub_catalog_name(_) -> None:
    stub = _Landsat8Stub()
    assert stub.client.catalog_name == EARTHDATA


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat9_stub_catalog_name(_) -> None:
    stub = _Landsat9Stub()
    assert stub.client.catalog_name == EARTHDATA


# ---------------------------------------------------------------------------
# Default collection
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_stub_default_collection(_) -> None:
    stub = _Landsat8Stub()
    assert stub.collection == EarthdataLandsatCollection.LEVEL_1_COLLECTION_2


# ---------------------------------------------------------------------------
# _build_collection_query injects correct platform filter
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_build_query(_) -> None:
    stub = _Landsat8Stub()
    query = stub._build_collection_query()
    assert query == {EarthdataLandsatProperty.PLATFORM.value: {"eq": "LANDSAT_8"}}


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat9_build_query(_) -> None:
    stub = _Landsat9Stub()
    query = stub._build_collection_query()
    assert query == {EarthdataLandsatProperty.PLATFORM.value: {"eq": "LANDSAT_9"}}


# ---------------------------------------------------------------------------
# StacSearch(EARTHDATA) does not initialise s3_client
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_stac_search_earthdata_no_s3_client(_) -> None:
    client = StacSearch(EARTHDATA)
    assert client.s3_client is None


# ---------------------------------------------------------------------------
# Regression: existing wrappers still default to PLANETARY_COMPUTER
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_abstract_stac_wrapper_default_catalog(_) -> None:
    """AbstractStacWrapper default catalog_name remains PLANETARY_COMPUTER."""

    class _ConcreteWrapper(AbstractStacWrapper):
        def _build_collection_query(self):
            return {}

    wrapper = _ConcreteWrapper()
    assert wrapper.client.catalog_name == PLANETARY_COMPUTER


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_sentinel2_search_catalog_name_regression(_) -> None:
    """Sentinel2Search still targets PLANETARY_COMPUTER after the refactor."""
    s2 = Sentinel2Search()
    assert s2.client.catalog_name == PLANETARY_COMPUTER


# ---------------------------------------------------------------------------
# Landsat8Search / Landsat9Search concrete classes
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_search_platform_query(_) -> None:
    l8 = Landsat8Search()
    assert l8._build_collection_query() == {"platform": {"eq": "LANDSAT_8"}}


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat9_search_platform_query(_) -> None:
    l9 = Landsat9Search()
    assert l9._build_collection_query() == {"platform": {"eq": "LANDSAT_9"}}


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_search_catalog_name(_) -> None:
    l8 = Landsat8Search()
    assert l8.client.catalog_name == EARTHDATA


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat9_search_catalog_name(_) -> None:
    l9 = Landsat9Search()
    assert l9.client.catalog_name == EARTHDATA


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_landsat8_search_default_collection(_) -> None:
    l8 = Landsat8Search()
    assert l8.collection == EarthdataLandsatCollection.LEVEL_1_COLLECTION_2


# ---------------------------------------------------------------------------
# filter_by_cloud_cover writes to custom_query_params
# ---------------------------------------------------------------------------


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_filter_by_cloud_cover_writes_custom_params(_) -> None:
    l8 = Landsat8Search()
    result = l8.filter_by_cloud_cover(20)
    assert result is l8  # fluent return
    assert l8.custom_query_params == {EarthdataLandsatProperty.CLOUD_COVER.value: {"lt": 20}}


@patch("geospatial_tools.stac.core.catalog_generator", return_value=None)
def test_filter_by_cloud_cover_invalidates_state(_) -> None:
    l9 = Landsat9Search()
    l9.client.search_results = []  # type: ignore[assignment]
    l9.filter_by_cloud_cover(10)
    assert l9.client.search_results is None


def test_landsat8_and_landsat9_importable() -> None:
    assert Landsat8Search is not None
    assert Landsat9Search is not None
