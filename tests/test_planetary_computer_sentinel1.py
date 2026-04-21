from pathlib import Path
from unittest.mock import patch

import pytest
from pystac import Item

from geospatial_tools.stac.core import Asset
from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS1Band,
    PlanetaryComputerS1Collection,
    PlanetaryComputerS1InstrumentMode,
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS1Polarization,
    PlanetaryComputerS1Property,
)
from geospatial_tools.stac.planetary_computer.sentinel_1 import (
    AbstractSentinel1,
    Sentinel1Search,
)


class Sentinel1Mock(AbstractSentinel1):
    def search(self) -> list[Item]:
        return []

    def download(self, bands: list[PlanetaryComputerS1Band | str], base_directory: str | Path) -> list[Asset]:
        return []


def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AbstractSentinel1()


def test_abstract_sentinel1_initialization():
    mock = Sentinel1Mock(
        collection=PlanetaryComputerS1Collection.GRD,
        date_range="2023-01-01/2023-01-31",
        bbox=(-74.0, 45.4, -73.5, 45.7),
    )
    assert mock.collection == PlanetaryComputerS1Collection.GRD
    assert mock.date_range == "2023-01-01/2023-01-31"
    assert mock.bbox == (-74.0, 45.4, -73.5, 45.7)
    assert mock.intersects is None
    assert mock.instrument_modes is None
    assert mock.polarizations is None
    assert mock.orbit_states is None
    assert mock.custom_query_params == {}
    assert mock.search_results is None
    assert mock.downloaded_assets is None
    assert mock.client is not None


def test_filter_by_instrument_mode():
    mock = Sentinel1Mock()
    result = mock.filter_by_instrument_mode(PlanetaryComputerS1InstrumentMode.IW)
    assert result is mock
    assert mock.instrument_modes == [PlanetaryComputerS1InstrumentMode.IW]

    result2 = mock.filter_by_instrument_mode(
        [PlanetaryComputerS1InstrumentMode.EW, PlanetaryComputerS1InstrumentMode.SM]
    )
    assert result2 is mock
    assert mock.instrument_modes == [PlanetaryComputerS1InstrumentMode.EW, PlanetaryComputerS1InstrumentMode.SM]


def test_filter_by_polarization():
    mock = Sentinel1Mock()
    result = mock.filter_by_polarization(PlanetaryComputerS1Polarization.VV)
    assert result is mock
    assert mock.polarizations == [PlanetaryComputerS1Polarization.VV]

    result2 = mock.filter_by_polarization([PlanetaryComputerS1Polarization.HH, PlanetaryComputerS1Polarization.HV])
    assert result2 is mock
    assert mock.polarizations == [PlanetaryComputerS1Polarization.HH, PlanetaryComputerS1Polarization.HV]


def test_filter_by_orbit_state():
    mock = Sentinel1Mock()
    result = mock.filter_by_orbit_state(PlanetaryComputerS1OrbitState.ASCENDING)
    assert result is mock
    assert mock.orbit_states == [PlanetaryComputerS1OrbitState.ASCENDING]

    result2 = mock.filter_by_orbit_state(
        [PlanetaryComputerS1OrbitState.DESCENDING, PlanetaryComputerS1OrbitState.ASCENDING]
    )
    assert result2 is mock
    assert mock.orbit_states == [PlanetaryComputerS1OrbitState.DESCENDING, PlanetaryComputerS1OrbitState.ASCENDING]


def test_with_custom_query():
    mock = Sentinel1Mock()
    result = mock.with_custom_query({"sar:resolution_range": {"eq": "high"}})
    assert result is mock
    assert mock.custom_query_params == {"sar:resolution_range": {"eq": "high"}}


@patch("geospatial_tools.stac.planetary_computer.sentinel_1.StacSearch")
def test_search_dynamic_query_building(mock_stac_search_class):
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []

    searcher = Sentinel1Search()
    searcher.filter_by_instrument_mode(PlanetaryComputerS1InstrumentMode.IW)
    searcher.filter_by_orbit_state([PlanetaryComputerS1OrbitState.ASCENDING, PlanetaryComputerS1OrbitState.DESCENDING])
    searcher.filter_by_polarization([PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH])
    searcher.with_custom_query({"custom_key": {"eq": "val"}})

    searcher.search()

    mock_client.search.assert_called_once()
    called_kwargs = mock_client.search.call_args.kwargs
    assert called_kwargs["query"] == {
        PlanetaryComputerS1Property.INSTRUMENT_MODE.value: {"eq": "IW"},
        PlanetaryComputerS1Property.ORBIT_STATE.value: {"in": ["ascending", "descending"]},
        PlanetaryComputerS1Property.POLARIZATIONS.value: {"eq": ["VV", "VH"]},
        "custom_key": {"eq": "val"},
    }


@patch("geospatial_tools.stac.planetary_computer.sentinel_1.StacSearch")
def test_download_triggers_search_if_none(mock_stac_search_class):
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []
    mock_client.download_search_results.return_value = []

    searcher = Sentinel1Search()
    searcher.download(bands=[PlanetaryComputerS1Band.VV], base_directory="test")

    mock_client.search.assert_called_once()
    mock_client.download_search_results.assert_called_once_with(bands=["vv"], base_directory=Path("test"))


@patch("geospatial_tools.stac.planetary_computer.sentinel_1.StacSearch")
def test_download_skips_search_if_already_populated(mock_stac_search_class):
    mock_client = mock_stac_search_class.return_value
    mock_client.download_search_results.return_value = []

    searcher = Sentinel1Search()
    searcher.search_results = []
    searcher.download(bands=[PlanetaryComputerS1Band.VH], base_directory="test")

    mock_client.search.assert_not_called()
    mock_client.download_search_results.assert_called_once()


@patch("geospatial_tools.stac.planetary_computer.sentinel_1.StacSearch")
def test_download_converts_bands_to_lowercase(mock_stac_search_class):
    mock_client = mock_stac_search_class.return_value
    mock_client.search.return_value = []

    searcher = Sentinel1Search()
    searcher.download(bands=["VV", PlanetaryComputerS1Band.VH], base_directory="test")

    called_kwargs = mock_client.download_search_results.call_args.kwargs
    assert called_kwargs["bands"] == ["vv", "vh"]


@pytest.mark.integration
def test_sentinel1_integration():
    searcher = Sentinel1Search(date_range="2023-01-01/2023-01-31", bbox=(-74.0, 45.4, -73.5, 45.7))
    searcher.filter_by_instrument_mode(PlanetaryComputerS1InstrumentMode.IW)
    searcher.filter_by_polarization([PlanetaryComputerS1Polarization.VV, PlanetaryComputerS1Polarization.VH])

    results = searcher.search()

    assert results is not None
    assert len(results) > 0
    for item in results:
        assert item.properties["sar:instrument_mode"] == "IW"
        assert "VV" in item.properties["sar:polarizations"]
