from pathlib import Path

import pytest
from pystac import Item

from geospatial_tools.stac.core import Asset
from geospatial_tools.stac.planetary_computer.constants import (
    PlanetaryComputerS1Band,
    PlanetaryComputerS1Collection,
    PlanetaryComputerS1InstrumentMode,
    PlanetaryComputerS1OrbitState,
    PlanetaryComputerS1Polarization,
)
from geospatial_tools.stac.planetary_computer.sentinel_1 import AbstractSentinel1


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
