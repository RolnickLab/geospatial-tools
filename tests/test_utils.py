from typing import Union

import pytest

from geospatial_tools.utils import create_crs, create_date_range_for_specific_period


@pytest.mark.parametrize(
    "code,expected",
    [
        pytest.param(5070, "EPSG:5070", id="From integer code"),
        pytest.param("5070", "EPSG:5070", id="From string code"),
        pytest.param("EPSG:5070", "EPSG:5070", id="From full code"),
        pytest.param(" EPSG:5070", "EPSG:5070", id="From full code starting with space"),
        pytest.param("EPSG:5070 ", "EPSG:5070", id="From full code ending with space"),
        pytest.param("epsg:5070", "EPSG:5070", id="From full code but lower case"),
        pytest.param("ESPGG:5070", "EPSG:5070", id="From full code but with typo in EPSG"),
    ],
)
def test_create_crs(code: Union[str, int], expected: str):
    crs = create_crs(code)
    assert crs == expected


@pytest.mark.parametrize(
    "start_year,end_year,start_month,end_month,expected_daterange",
    [
        pytest.param(2020, 2020, 1, 2, ["2020-01-01T00:00:00Z/2020-02-29T23:59:59Z"], id="One year"),
        pytest.param(
            2020,
            2021,
            2,
            3,
            ["2020-02-01T00:00:00Z/2020-03-31T23:59:59Z", "2021-02-01T00:00:00Z/2021-03-31T23:59:59Z"],
            id="Two years",
        ),
        pytest.param(
            2020,
            2024,
            3,
            4,
            [
                "2020-03-01T00:00:00Z/2020-04-30T23:59:59Z",
                "2021-03-01T00:00:00Z/2021-04-30T23:59:59Z",
                "2022-03-01T00:00:00Z/2022-04-30T23:59:59Z",
                "2023-03-01T00:00:00Z/2023-04-30T23:59:59Z",
                "2024-03-01T00:00:00Z/2024-04-30T23:59:59Z",
            ],
            id="Four years",
        ),
        pytest.param(
            2020,
            2023,
            11,
            1,
            [
                "2020-11-01T00:00:00Z/2021-01-31T23:59:59Z",
                "2021-11-01T00:00:00Z/2022-01-31T23:59:59Z",
                "2022-11-01T00:00:00Z/2023-01-31T23:59:59Z",
            ],
            id="Period crossing year boundary over 3 years",
        ),
        pytest.param(
            2020,
            2021,
            9,
            2,
            ["2020-09-01T00:00:00Z/2021-02-28T23:59:59Z"],
            id="Period crossing year boundary over 2 years",
        ),
    ],
)
def test_create_date_range_specific_period_per_year(start_year, end_year, start_month, end_month, expected_daterange):
    date_range = create_date_range_for_specific_period(start_year, end_year, start_month, end_month)
    assert date_range == expected_daterange
