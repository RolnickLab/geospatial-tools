"""This module contains functions that are related to STAC API."""

import datetime
import pathlib
from typing import Union

import planetary_computer
import pystac_client
import rasterio

from geospatial_tools import types
from geospatial_tools.raster import reproject_raster
from geospatial_tools.utils import create_logger, download_url

LOGGER = create_logger(__name__)

# STAC catalog names
PLANETARY_COMPUTER = "planetary_computer"

CATALOG_NAME_LIST = frozenset(PLANETARY_COMPUTER)

# STAC catalog API urls
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


def list_available_catalogs(logger=LOGGER):
    logger.info("Available catalogs")
    return CATALOG_NAME_LIST


class AssetSubItem:
    def __init__(self, asset, item_id: str, band: str, filename: Union[str, pathlib.Path]):
        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        self.asset = asset
        self.item_id: str = item_id
        self.band: str = band
        self.filename: pathlib.Path = filename


class Asset:
    def __init__(
        self,
        asset_id,
        bands: list[str] = None,
        asset_item_list: list[AssetSubItem] = None,
        merged_asset_path: Union[str, pathlib.Path] = None,
        reprojected_asset: Union[str, pathlib.Path] = None,
        logger=LOGGER,
    ):
        self.asset_id: str = asset_id
        self.bands: list = bands
        self.list: list[AssetSubItem] = asset_item_list
        self.merged_asset_path: Union[str, pathlib.Path] = merged_asset_path
        self.reprojected_asset_path: Union[str, pathlib.Path] = reprojected_asset
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
        self.logger.info(f"Asset list for asset [{self.asset_id }] : \n\t{asset_list}")

    def merge_asset(self, base_directory: Union[str, pathlib.Path] = None, delete_sub_items=False):
        if not base_directory:
            base_directory = ""
        if isinstance(base_directory, str):
            base_directory = pathlib.Path(base_directory)

        merged_filename = base_directory / f"{self.asset_id}_merged.tif"

        total_band_count = self._get_asset_total_bands()

        self.logger.info(total_band_count)

        meta = self._create_merged_asset_metadata(total_band_count)

        merged_image_index = 1
        band_index = 0
        self.logger.info(f"Merging asset [{self.asset_id}] ...")
        with rasterio.open(merged_filename, "w", **meta) as merged_asset_image:
            for asset_sub_item in self.list:
                self.logger.info(f"Writing band image: {asset_sub_item.item_id}")
                with rasterio.open(asset_sub_item.filename) as asset_band_image:
                    num_of_bands = asset_band_image.count
                    for asset_band_image_index in range(1, num_of_bands + 1):
                        self.logger.info(f"writing asset sub item band {asset_band_image_index}")
                        self.logger.info(f"writing merged index band {merged_image_index}")
                        merged_asset_image.write_band(merged_image_index, asset_band_image.read(asset_band_image_index))
                        description = self.bands[band_index]
                        if num_of_bands > 1:
                            description = f"{description}-{asset_band_image_index}"
                        merged_asset_image.set_band_description(merged_image_index, description)
                        merged_asset_image.update_tags(
                            merged_image_index, **asset_band_image.tags(asset_band_image_index)
                        )
                        merged_image_index += 1
                    band_index += 1
        if merged_filename.exists():
            self.logger.info(f"Asset [{self.asset_id}] merged successfully")
            self.logger.info(f"Asset location : [{merged_filename}]")
            self.merged_asset_path = merged_filename
            if delete_sub_items:
                self.delete_asset_sub_items()
            return merged_filename
        self.logger.error(f"There was a problem merging asset [{self.asset_id}]")

    def reproject_merged_asset(
        self, target_projection, base_directory: Union[str, pathlib.Path] = None, delete_merged_asset=False
    ):
        if not base_directory:
            base_directory = ""
        if isinstance(base_directory, str):
            base_directory = pathlib.Path(base_directory)
        target_path = base_directory / f"{self.asset_id}_reprojected.tif"
        self.logger.info(f"Reprojecting asset [{self.asset_id}] ...")
        reprojected_filename = reproject_raster(
            dataset_path=self.merged_asset_path,
            target_path=target_path,
            target_crs=target_projection,
            logger=self.logger,
        )
        if reprojected_filename.exists():
            self.logger.info(f"Asset location : [{reprojected_filename}]")
            self.reprojected_asset_path = reprojected_filename
            if delete_merged_asset:
                self.delete_merged_asset()
            return reprojected_filename
        self.logger.error(f"There was a problem reprojecting asset [{self.asset_id}]")

    def delete_asset_sub_items(self):
        self.logger.info(f"Deleting asset sub items from asset [{self.asset_id}]")
        if self.list:
            for item in self.list:
                self.logger.info(f"Deleting [{item.filename}] ...")
                item.filename.unlink()

    def delete_merged_asset(self):
        self.logger.info(f"Deleting merged asset file for [{self.merged_asset_path}]")
        self.merged_asset_path.unlink()

    def delete_reprojected_asset(self):
        self.logger.info(f"Deleting reprojected asset file for [{self.reprojected_asset_path}]")
        self.reprojected_asset_path.unlink()

    def _create_merged_asset_metadata(self, total_band_count):
        self.logger.info("Creating merged asset metadata")
        with rasterio.open(self.list[0].filename) as meta_source:
            meta = meta_source.meta
            meta.update(count=total_band_count)
        return meta

    def _get_asset_total_bands(self):
        total_band_count = 0
        for download_file in self.list:
            with rasterio.open(download_file.filename, "r") as downloaded_image:
                total_band_count += downloaded_image.count
        self.logger.info(f"Calculated a total of [{total_band_count}] bands")
        return total_band_count


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

        intro_log = f"Initiating STAC API search for the following date ranges : [{date_ranges}"
        if query:
            intro_log = f"{intro_log} \n\tQuery : [{query}]"
        self.logger.info(intro_log)

        for date_range in date_ranges:
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
            items = search.items()

            base_log_message = f"for date range [{date_range}]"
            log_msg = f"Search successful {base_log_message}"
            if not items:
                log_msg = f"Search failed {base_log_message}"

            results.extend(list(items))
            self.logger.info(log_msg)
        if not results:
            self.logger.warning(f"Search for date ranges [{date_ranges}] found no results!")
            self.search_results = None

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
        downloaded_files = Asset(asset_id=image_id, bands=bands)
        for band in bands:
            if band in item.assets:
                asset = item.assets[band]
                asset_url = asset.href
                self.logger.info(f"Downloading {band} from {asset_url}")

                file_name = base_directory / f"{image_id}_{band}.tif"
                downloaded_file = download_url(asset_url, file_name)
                if downloaded_file:
                    asset_file = AssetSubItem(asset=item, item_id=image_id, band=band, filename=downloaded_file)
                    downloaded_files.add_asset_item(asset_file)
            else:
                self.logger.info(f"Band {band} not available for {image_id}.")
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
        if not self.cloud_cover_sorted_results:
            self.logger.info("Results are not sorted, sorting results...")
            self.sort_results_by_cloud_coverage()
        results = self.cloud_cover_sorted_results
        if first_x_num_of_items:
            results = results[:first_x_num_of_items]
        downloaded_search_results = self._download_results(results=results, bands=bands, base_directory=base_directory)
        self.downloaded_cloud_cover_sorted_assets = downloaded_search_results
        return downloaded_search_results

    def download_best_cloud_cover_results(self, bands, base_directory):
        if not self.cloud_cover_sorted_results:
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
