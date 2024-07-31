import datetime
import pathlib
from typing import Union

import planetary_computer
import pystac_client

from geospatial_tools import types
from geospatial_tools.utils import create_logger, download_url

LOGGER = create_logger(__name__)
PLANETARY_COMPUTER = "planetary_cpu"
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


def catalog_generator(catalog_name, logger=LOGGER):
    catalog_dict = {PLANETARY_COMPUTER: create_planetary_computer_catalog}
    if catalog_name not in catalog_dict:
        logger.error(f"Unsupported catalog name: {catalog_name}")
        return None

    catalog = catalog_dict[catalog_name]()

    return catalog


class AssetSubItem:
    def __init__(self, asset, item_id, band, filename):
        self.asset = asset
        self.item_id = item_id
        self.band = band
        self.filename = filename


class Asset:
    def __init__(self, asset_id, asset_item_list: list[AssetSubItem] = None, logger=LOGGER):
        self.asset_id = asset_id
        self.list: list[AssetSubItem] = asset_item_list
        self.logger = logger

    def add_asset_item(self, asset):
        if not self.list:
            self.list = []
        self.list.append(asset)

    def show_asset_items(self):
        asset_list = []
        for asset_sub_item in self.list:
            asset_list.append(
                f"ID: [{asset_sub_item.item_id}], Band: [{asset_sub_item.band}], filename: [{asset_sub_item.filename}]"
            )
        self.logger.info(f"Asset list for asset [{self.asset_id }] : \n{asset_list}")


class StacSearch:
    def __init__(self, catalog_name, logger=LOGGER):
        self.catalog = catalog_generator(catalog_name=catalog_name)
        self.search_results = None
        self.cloud_cover_sorted_results = None
        self.downloaded_search_assets: list[Asset] = None
        self.downloaded_cloud_cover_sorted_assets: list[Asset] = None
        self.downloaded_best_sorted_asset = None
        self.logger = logger

    def stac_api_search_for_date_ranges(
        self,
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
            search = self.catalog.search(
                datetime=date_range,
                max_items=max_items,
                limit=limit,
                collections=collections,
                intersects=intersects,
                bbox=bbox,
                query=query,
                sortby=sortby,
            )
            for item in results:
                self.logger.info(f"{item.id}, {item.datetime}, {item.properties['eo:cloud_cover']}")
            results.extend(list(search.items()))
        self.search_results = results

        return results

    def sort_results_by_cloud_coverage(self):
        if self.search_results:
            self.logger.info("Sorting results by cloud cover (from least to most)")
            self.cloud_cover_sorted_results = self.cloud_cover_sorted_results = sorted(
                self.search_results, key=lambda item: item.properties.get("eo:cloud_cover", float("inf"))
            )
            return self.cloud_cover_sorted_results
        self.logger.warning("No results found: please run a search before trying to sort results")
        return None

    def download_assets(self, item, bands: list, base_directory: pathlib.Path):
        """

        Parameters
        ----------
        url
        filename

        Returns
        -------

        """
        image_id = item.id
        downloaded_files = Asset(asset_id=image_id)
        for band in bands:
            if band in item.assets:
                asset = item.assets[band]
                asset_url = asset.href
                print(f"Downloading {band} from {asset_url}")

                file_name = base_directory / f"{image_id}_{band}.tif"
                downloaded_file = download_url(asset_url, file_name)
                if downloaded_file:
                    asset_file = AssetSubItem(asset=item, item_id=image_id, band=band, filename=downloaded_file)
                    downloaded_files.add_asset_item(asset_file)
            else:
                print(f"Band {band} not available for {image_id}.")
        return downloaded_files

    def _download_results(self, results, bands, base_directory):
        downloaded_search_results = []
        if not isinstance(base_directory, pathlib.Path):
            base_directory = pathlib.Path(base_directory)
        if not base_directory.exists():
            base_directory.mkdir(parents=True, exist_ok=True)

        for item in results:
            self.logger.info(f"Downloading [{item.id}] ...")
            downloaded_item = self.download_assets(item=item, bands=bands, base_directory=base_directory)
            downloaded_search_results.append(downloaded_item)
        return downloaded_search_results

    def download_search_results(self, bands, base_directory):
        downloaded_search_results = self._download_results(
            results=self.search_results, bands=bands, base_directory=base_directory
        )
        self.downloaded_search_assets = downloaded_search_results
        return downloaded_search_results

    def download_sorted_by_cloud_cover_search_results(self, bands, base_directory, first_x_num_of_items=None):
        if self.cloud_cover_sorted_results is None:
            self.logger.info("Results are not sorted, sorting results...")
            self.sort_results_by_cloud_coverage()
        results = self.cloud_cover_sorted_results
        if first_x_num_of_items:
            results = results[:first_x_num_of_items]
        downloaded_search_results = self._download_results(results=results, bands=bands, base_directory=base_directory)
        self.downloaded_cloud_cover_sorted_assets = downloaded_search_results
        return downloaded_search_results

    def download_best_cloud_cover_results(self, bands, base_directory):
        if self.cloud_cover_sorted_results is None:
            self.logger.info("Results are not sorted, sorting results...")
            self.sort_results_by_cloud_coverage()

        best_result = self.cloud_cover_sorted_results[0]
        best_result = [best_result]

        if self.downloaded_cloud_cover_sorted_assets:
            self.logger.info(f"Asset [{best_result[0].id}] is already downloaded")
            self.downloaded_best_sorted_asset = self.downloaded_cloud_cover_sorted_assets[0]
            return self.downloaded_cloud_cover_sorted_assets[0]

        downloaded_search_results = self._download_results(
            results=best_result, bands=bands, base_directory=base_directory
        )
        self.downloaded_best_sorted_asset = downloaded_search_results[0]
        return downloaded_search_results[0]
