"""Unit tests for Planetary Computer Sentinel-3 wrapper."""

from unittest.mock import patch

from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS3Band,
    PlanetaryComputerS3Collection,
    PlanetaryComputerS3OrbitState,
    PlanetaryComputerS3Property,
)
from geospatial_tools.stac.planetary_computer.sentinel_3 import Sentinel3Search


def test_sentinel3_initialization() -> None:
    search = Sentinel3Search()
    assert search.collection == PlanetaryComputerS3Collection.OLCI_WFR
    assert search.orbit_states is None
    assert search.custom_query_params == {}


def test_initialization_with_collection() -> None:
    search = Sentinel3Search(collection=PlanetaryComputerS3Collection.OLCI_L1B)
    assert search.collection == PlanetaryComputerS3Collection.OLCI_L1B


def test_filter_by_orbit_state_single() -> None:
    search = Sentinel3Search()
    search.client.search_results = ["dummy"]  # type: ignore

    result = search.filter_by_orbit_state(PlanetaryComputerS3OrbitState.ASCENDING)

    assert result is search
    assert search.orbit_states == [PlanetaryComputerS3OrbitState.ASCENDING]
    assert search.client.search_results is None  # Invalidation test


def test_filter_by_orbit_state_multiple() -> None:
    search = Sentinel3Search()
    search.filter_by_orbit_state([PlanetaryComputerS3OrbitState.ASCENDING, PlanetaryComputerS3OrbitState.DESCENDING])
    assert search.orbit_states == [PlanetaryComputerS3OrbitState.ASCENDING, PlanetaryComputerS3OrbitState.DESCENDING]


@patch("geospatial_tools.stac.core.StacSearch")
def test_build_collection_query_dynamic(mock_stac_search_class) -> None:
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []

    searcher = Sentinel3Search()
    searcher.filter_by_orbit_state(PlanetaryComputerS3OrbitState.DESCENDING)
    searcher.with_custom_query({"custom_key": {"eq": "val"}})
    searcher.search()

    mock_client.search.assert_called_once()
    called_kwargs = mock_client.search.call_args.kwargs
    assert called_kwargs["query"] == {
        PlanetaryComputerS3Property.ORBIT_STATE.value: {"eq": "descending"},
        "custom_key": {"eq": "val"},
    }


@patch("geospatial_tools.stac.core.StacSearch")
def test_build_collection_query_multiple_orbits(mock_stac_search_class) -> None:
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []

    searcher = Sentinel3Search()
    searcher.filter_by_orbit_state([PlanetaryComputerS3OrbitState.ASCENDING, PlanetaryComputerS3OrbitState.DESCENDING])
    searcher.search()

    mock_client.search.assert_called_once()
    called_kwargs = mock_client.search.call_args.kwargs
    assert called_kwargs["query"] == {
        PlanetaryComputerS3Property.ORBIT_STATE.value: {"in": ["ascending", "descending"]}
    }


@patch("geospatial_tools.stac.core.StacSearch")
def test_download_lowercases_bands(mock_stac_search_class) -> None:
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []

    searcher = Sentinel3Search()
    searcher.download(bands=[PlanetaryComputerS3Band.OA17, "OA18-RADIANCE"], base_directory="test")

    called_kwargs = mock_client.download_search_results.call_args.kwargs
    assert called_kwargs["bands"] == ["oa17-radiance", "oa18-radiance"]
