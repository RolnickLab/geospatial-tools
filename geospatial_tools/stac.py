import datetime
from typing import Union

import planetary_computer
import pystac_client

from geospatial_tools import types
from geospatial_tools.utils import create_logger

LOGGER = create_logger(__name__)
PLANETARY_COMPUTER_API = "https://planetarycomputer.microsoft.com/api/stac/v1"


def create_planetary_computer_catalog():
    """
    Creates a Planetary Computer Catalog Client.

    Returns
    -------
    pystac_client.Client
        Planetary computer catalog client
    """
    return pystac_client.Client.open(PLANETARY_COMPUTER_API, modifier=planetary_computer.sign_inplace)


def stac_api_search_for_date_ranges(
    catalog: pystac_client.Client,
    date_ranges: list[datetime.datetime],
    max_items: int = None,
    limit: int = None,
    collections: str = None,
    bbox: types.BBoxLike = None,
    intersects: types.IntersectsLike | None = None,
    query: dict = None,
    sortby: Union[list, dict] = None,
) -> list:
    """
    STAC API search that will use search query and parameters for each date range in given list of `date_ranges`.

    Date ranges can be generated with the help of the `geospatial_tools.utils.create_date_range_for_specific_period`
    function for more complex ranges.

    Parameters
    ----------
    catalog : pystac_client.Client
        _description_
    date_ranges : list[datetime.datetime]
        _description_
    max_items : int, optional
        _description_, by default None
    limit : int, optional
        _description_, by default None
    collections : str, optional
        _description_, by default None
    bbox : types.BBoxLike, optional
        _description_, by default None
    intersects : types.IntersectsLike | None, optional
        _description_, by default None
    query : dict, optional
        _description_, by default None
    sortby : Union[list, dict], optional
        _description_, by default None

    Returns
    -------
    list
        _description_
    """
    results = []
    if isinstance(collections, str):
        collections = [collections]
    if isinstance(sortby, dict):
        sortby = [sortby]

    for date_range in date_ranges:
        print(date_range)
        search = catalog.search(
            datetime=date_range,
            max_items=max_items,
            limit=limit,
            collections=collections,
            intersects=intersects,
            bbox=bbox,
            query=query,
            sortby=sortby,
        )
        results.extend(list(search.items()))

    return results
