"""This module contains functions that are related to STAC API."""

import logging
import time
from pathlib import Path

import pystac
import pystac_client
from planetary_computer import sign_inplace
from pystac_client.exceptions import APIError

from geospatial_tools import geotools_types
from geospatial_tools.geotools_types import DateLike
from geospatial_tools.raster import (
    create_merged_raster_bands_metadata,
    get_total_band_count,
    merge_raster_bands,
    reproject_raster,
)
from geospatial_tools.utils import create_logger, download_url

LOGGER = create_logger(__name__)

# STAC catalog names
PLANETARY_COMPUTER = "planetary_computer"

CATALOG_NAME_LIST = frozenset(PLANETARY_COMPUTER)

# STAC catalog API urls
PLANETARY_COMPUTER_API = "https://planetarycomputer.microsoft.com/api/stac/v1"


def create_planetary_computer_catalog(max_retries: int = 3, delay=5, logger=LOGGER) -> pystac_client.Client | None:
    """
    Creates a Planetary Computer Catalog Client.

    Args:
      max_retries:  (Default value = 3)
      delay:  (Default value = 5)
      logger:  (Default value = LOGGER)

    Returns:
    """
    for attempt in range(1, max_retries + 1):
        try:
            client = pystac_client.Client.open(PLANETARY_COMPUTER_API, modifier=sign_inplace)
            logger.debug("Successfully connected to the API.")
            return client
        except Exception as e:  # pylint: disable=W0718
            logger.error(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                logger.error(e)
                raise e
    return None


def catalog_generator(catalog_name, logger=LOGGER) -> pystac_client.Client | None:
    """

    Args:
      catalog_name:
      logger:

    Returns:
        STAC Client
    """
    catalog_dict = {PLANETARY_COMPUTER: create_planetary_computer_catalog}
    if catalog_name not in catalog_dict:
        logger.error(f"Unsupported catalog name: {catalog_name}")
        return None

    catalog = catalog_dict[catalog_name]()

    return catalog


def list_available_catalogs(logger: logging.Logger = LOGGER) -> frozenset[str]:
    """

    Args:
      logger:

    Returns:


    """
    logger.info("Available catalogs")
    return CATALOG_NAME_LIST


class AssetSubItem:
    """
    Class that represent a STAC asset sub item.

    Generally represents a single satellite image band.
    """

    def __init__(self, asset, item_id: str, band: str, filename: str | Path):
        """

        Args:
            asset:
            item_id:
            band:
            filename:
        """
        if isinstance(filename, str):
            filename = Path(filename)
        self.asset = asset
        self.item_id: str = item_id
        self.band: str = band
        self.filename: Path = filename


class Asset:
    """Represents a STAC asset."""

    def __init__(
        self,
        asset_id: str,
        bands: list[str] | None = None,
        asset_item_list: list[AssetSubItem] | None = None,
        merged_asset_path: str | Path | None = None,
        reprojected_asset: str | Path | None = None,
        logger: logging.Logger = LOGGER,
    ):
        """

        Args:
            asset_id:
            bands:
            asset_item_list:
            merged_asset_path:
            reprojected_asset:
            logger:
        """
        self.asset_id = asset_id
        self.bands = bands
        self.list = asset_item_list
        self.merged_asset_path = merged_asset_path
        self.reprojected_asset_path = reprojected_asset
        self.logger = logger

    def add_asset_item(self, asset: AssetSubItem):
        """

        Args:
          asset: AssetSubItem:

        Returns:


        """
        if not self.list:
            self.list = []
        self.list.append(asset)

    def show_asset_items(self):
        """Show items that belong to this asset."""
        asset_list = []
        for asset_sub_item in self.list:
            asset_list.append(
                f"ID: [{asset_sub_item.item_id}], Band: [{asset_sub_item.band}], filename: [{asset_sub_item.filename}]"
            )
        self.logger.info(f"Asset list for asset [{self.asset_id}] : \n\t{asset_list}")

    def merge_asset(self, base_directory: str | Path | None = None, delete_sub_items: bool = False) -> Path | None:
        """

        Args:
          base_directory:
          delete_sub_items:

        Returns:


        """
        if not base_directory:
            base_directory = ""
        if isinstance(base_directory, str):
            base_directory = Path(base_directory)

        merged_filename = base_directory / f"{self.asset_id}_merged.tif"

        asset_filename_list = [asset.filename for asset in self.list]

        meta = self._create_merged_asset_metadata()

        merge_raster_bands(
            merged_filename=merged_filename,
            raster_file_list=asset_filename_list,
            merged_metadata=meta,
            merged_band_names=self.bands,
        )

        if merged_filename.exists():
            self.logger.info(f"Asset [{self.asset_id}] merged successfully")
            self.logger.info(f"Asset location : [{merged_filename}]")
            self.merged_asset_path = merged_filename
            if delete_sub_items:
                self.delete_asset_sub_items()
            return merged_filename
        self.logger.error(f"There was a problem merging asset [{self.asset_id}]")
        return None

    def reproject_merged_asset(
        self,
        target_projection: str | int,
        base_directory: str | Path = None,
        delete_merged_asset: bool = False,
    ):
        """

        Args:
          target_projection:
          base_directory:
          delete_merged_asset:

        Returns:


        """
        if not base_directory:
            base_directory = ""
        if isinstance(base_directory, str):
            base_directory = Path(base_directory)
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
        return None

    def delete_asset_sub_items(self):
        """Delete all asset sub items that belong to this asset."""
        self.logger.info(f"Deleting asset sub items from asset [{self.asset_id}]")
        if self.list:
            for item in self.list:
                self.logger.info(f"Deleting [{item.filename}] ...")
                item.filename.unlink()

    def delete_merged_asset(self):
        """Delete merged asset."""
        self.logger.info(f"Deleting merged asset file for [{self.merged_asset_path}]")
        self.merged_asset_path.unlink()

    def delete_reprojected_asset(self):
        """Delete reprojected asset."""
        self.logger.info(f"Deleting reprojected asset file for [{self.reprojected_asset_path}]")
        self.reprojected_asset_path.unlink()

    def _create_merged_asset_metadata(self):
        self.logger.info("Creating merged asset metadata")
        file_list = [asset.filename for asset in self.list]
        meta = create_merged_raster_bands_metadata(file_list)
        return meta

    def _get_asset_total_bands(self):
        downloaded_file_list = [asset.filename for asset in self.list]
        total_band_count = get_total_band_count(downloaded_file_list)
        return total_band_count


class StacSearch:
    """Utility class to help facilitate and automate STAC API searches through the use of `pystac_client.Client`."""

    def __init__(self, catalog_name, logger=LOGGER):
        """

        Args:
            catalog_name:
            logger:
        """
        self.catalog: pystac_client.Client = catalog_generator(catalog_name=catalog_name)
        self.search_results: list[pystac.Item] | None = None
        self.cloud_cover_sorted_results: list[pystac.Item] | None = None
        self.filtered_results: list[pystac.Item] | None = None
        self.downloaded_search_assets: list[Asset] | None = None
        self.downloaded_cloud_cover_sorted_assets: list[Asset] | None = None
        self.downloaded_best_sorted_asset = None
        self.logger = logger

    def search(
        self,
        date_range: DateLike = None,
        max_items: int | None = None,
        limit: int | None = None,
        ids: list | None = None,
        collections: str | list | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict | None = None,
        sortby: list | dict | None = None,
        max_retries: int = 3,
        delay=5,
    ) -> list:
        """
        STAC API search that will use search query and parameters. Essentially a wrapper on `pystac_client.Client`.

        Parameter descriptions taken from pystac docs.

        Args:
          date_range: Either a single datetime or datetime range used to filter results.
                You may express a single datetime using a :class:`datetime.datetime`
                instance, a `RFC 3339-compliant <https://tools.ietf.org/html/rfc3339>`__
                timestamp, or a simple date string (see below). Instances of
                :class:`datetime.datetime` may be either
                timezone aware or unaware. Timezone aware instances will be converted to
                a UTC timestamp before being passed
                to the endpoint. Timezone unaware instances are assumed to represent UTC
                timestamps. You may represent a
                datetime range using a ``"/"`` separated string as described in the
                spec, or a list, tuple, or iterator
                of 2 timestamps or datetime instances. For open-ended ranges, use either
                ``".."`` (``'2020-01-01:00:00:00Z/..'``,
                ``['2020-01-01:00:00:00Z', '..']``) or a value of ``None``
                (``['2020-01-01:00:00:00Z', None]``).
                If using a simple date string, the datetime can be specified in
                ``YYYY-mm-dd`` format, optionally truncating
                to ``YYYY-mm`` or just ``YYYY``. Simple date strings will be expanded to
                include the entire time period, for example: ``2017`` expands to
                ``2017-01-01T00:00:00Z/2017-12-31T23:59:59Z`` and ``2017-06`` expands
                to ``2017-06-01T00:00:00Z/2017-06-30T23:59:59Z``
                If used in a range, the end of the range expands to the end of that
                day/month/year, for example: ``2017-06-10/2017-06-11`` expands to
                  ``2017-06-10T00:00:00Z/2017-06-11T23:59:59Z`` (Default value = None)
          max_items: The maximum number of items to return from the search, even if there are
            more matching results.
          limit: A recommendation to the service as to the number of items to return per
            page of results.
          ids: List of one or more Item ids to filter on.
          collections: List of one or more Collection IDs or pystac. Collection instances. Only Items in one of the
            provided Collections will be searched
          bbox: A list, tuple, or iterator representing a bounding box of 2D or 3D coordinates. Results will be filtered
            to only those intersecting the bounding box.
          intersects: A string or dictionary representing a GeoJSON geometry, or an object that implements a
            __geo_interface__ property, as supported by several libraries including Shapely, ArcPy, PySAL, and geojson.
            Results filtered to only those intersecting the geometry.
          query: List or JSON of query parameters as per the STAC API query extension.
          sortby: A single field or list of fields to sort the response by
          max_retries:
          delay:

        Returns:
        """
        if isinstance(collections, str):
            collections = [collections]
        if isinstance(sortby, dict):
            sortby = [sortby]

        intro_log = "Initiating STAC API search"
        if query:
            intro_log = f"{intro_log} \n\tQuery : [{query}]"
        self.logger.info(intro_log)
        items = []
        for attempt in range(1, max_retries + 1):
            try:
                items = self._base_catalog_search(
                    date_range=date_range,
                    max_items=max_items,
                    limit=limit,
                    ids=ids,
                    collections=collections,
                    bbox=bbox,
                    intersects=intersects,
                    query=query,
                    sortby=sortby,
                )
            except APIError as e:  # pylint: disable=W0718
                self.logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                else:
                    raise e

        if not items:
            self.search_results = None

        self.search_results = items
        return items

    def search_for_date_ranges(
        self,
        date_ranges: list[DateLike],
        max_items: int | None = None,
        limit: int | None = None,
        collections: str | list | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict | None = None,
        sortby: list | dict | None = None,
        max_retries: int = 3,
        delay=5,
    ) -> list:
        """
        STAC API search that will use search query and parameters for each date range in given list of `date_ranges`.

        Date ranges can be generated with the help of the `geospatial_tools.utils.create_date_range_for_specific_period`
        function for more complex ranges.

        Parameter descriptions taken from pystac docs.

        Args:
          date_ranges: List containing datetime date ranges
          max_items: The maximum number of items to return from the search, even if there are more matching results
          limit: A recommendation to the service as to the number of items to return per page of results.
          collections: List of one or more Collection IDs or pystac. Collection instances. Only Items in one of the
            provided Collections will be searched
          bbox: A list, tuple, or iterator representing a bounding box of 2D or 3D coordinates. Results will be
            filtered to only those intersecting the bounding box.
          intersects: A string or dictionary representing a GeoJSON geometry, or an object that implements
            a __geo_interface__ property, as supported by several libraries including Shapely, ArcPy, PySAL, and
            geojson. Results filtered to only those intersecting the geometry.
          query: List or JSON of query parameters as per the STAC API query extension.
          sortby: A single field or list of fields to sort the response by
          max_retries:
          delay:

        Returns:
        """
        results = []
        if isinstance(collections, str):
            collections = [collections]
        if isinstance(sortby, dict):
            sortby = [sortby]

        intro_log = f"Running STAC API search for the following parameters: \n\tDate ranges : {date_ranges}"
        if query:
            intro_log = f"{intro_log} \n\tQuery : {query}"
        self.logger.info(intro_log)

        for attempt in range(1, max_retries + 1):
            try:
                for date_range in date_ranges:
                    items = self._base_catalog_search(
                        date_range=date_range,
                        max_items=max_items,
                        limit=limit,
                        collections=collections,
                        bbox=bbox,
                        intersects=intersects,
                        query=query,
                        sortby=sortby,
                    )
                    results.extend(items)
            except APIError as e:  # pylint: disable=W0718
                self.logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                else:
                    raise e

        if not results:
            self.logger.warning(f"Search for date ranges [{date_ranges}] found no results!")
            self.search_results = None

        self.search_results = results
        return results

    def _base_catalog_search(
        self,
        date_range: DateLike,
        max_items: int | None = None,
        limit: int | None = None,
        ids: list | None = None,
        collections: str | list | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict | None = None,
        sortby: list | dict | None = None,
    ):
        """

        Args:
          date_range:
          max_items:
          limit:
          ids:
          collections:
          bbox:
          intersects:
          query:
          sortby:

        Returns:


        """
        search = self.catalog.search(
            datetime=date_range,
            max_items=max_items,
            limit=limit,
            ids=ids,
            collections=collections,
            intersects=intersects,
            bbox=bbox,
            query=query,
            sortby=sortby,
        )
        items = search.items()
        base_log_message = f"for date range [{date_range} ]"
        log_msg = f"Search successful {base_log_message}"
        log_state = self.logger.debug
        if not items:
            log_msg = f"Search failed {base_log_message}"
            log_state = self.logger.warning
        log_state(log_msg)
        return list(items)

    def sort_results_by_cloud_coverage(self) -> list | None:
        """Sort results by cloud coverage."""
        if self.search_results:
            self.logger.debug("Sorting results by cloud cover (from least to most)")
            self.cloud_cover_sorted_results = sorted(
                self.search_results, key=lambda item: item.properties.get("eo:cloud_cover", float("inf"))
            )
            return self.cloud_cover_sorted_results
        self.logger.warning("No results found: please run a search before trying to sort results")
        return None

    def filter_no_data(self, property_name: str, max_no_data_value: int = 5) -> list[pystac.Item] | None:
        """
        Filter results and sorted results that are above a nodata value threshold.

        Args:
          property_name: str:
          max_no_data_value: int:  (Default value = 5)

        Returns:
        """
        sorted_results = self.cloud_cover_sorted_results
        if not sorted_results:
            sorted_results = self.sort_results_by_cloud_coverage()
        if not sorted_results:
            return None

        filtered_results = []
        for item in sorted_results:
            if item.properties[property_name] < max_no_data_value:
                filtered_results.append(item)
        self.filtered_results = filtered_results

        return filtered_results

    def _download_assets(self, item: pystac.Item, bands: list, base_directory: Path) -> Asset:
        """

        Args:
          item: Search result item
          bands: List of bands to download from asset
          base_directory: Base directory where assets will be downloaded

        Returns:


        """
        image_id = item.id
        downloaded_files = Asset(asset_id=image_id, bands=bands)
        for band in bands:
            if band not in item.assets:
                self.logger.info(f"Band {band} not available for {image_id}.")
                continue

            asset = item.assets[band]
            asset_url = asset.href
            self.logger.info(f"Downloading {band} from {asset_url}")
            file_name = base_directory / f"{image_id}_{band}.tif"
            downloaded_file = download_url(asset_url, file_name)

            if downloaded_file:
                asset_file = AssetSubItem(asset=item, item_id=image_id, band=band, filename=downloaded_file)
                downloaded_files.add_asset_item(asset_file)

        return downloaded_files

    def _download_results(
        self, results: list[pystac.Item] | None, bands: list, base_directory: str | Path
    ) -> list[Asset]:
        """

        Args:
          results:
          bands:
          base_directory:

        Returns:


        """
        if not results:
            return []
        downloaded_search_results = []
        if not isinstance(base_directory, Path):
            base_directory = Path(base_directory)
        if not base_directory.exists():
            base_directory.mkdir(parents=True, exist_ok=True)

        for item in results:
            self.logger.info(f"Downloading [{item.id}] ...")
            downloaded_item = self._download_assets(item=item, bands=bands, base_directory=base_directory)
            downloaded_search_results.append(downloaded_item)
        return downloaded_search_results

    def download_search_results(self, bands: list, base_directory: str | Path) -> list[Asset]:
        """

        Args:
          bands: List of bands to download from asset
          base_directory: Base directory where assets will be downloaded

        Returns:


        """
        downloaded_search_results = self._download_results(
            results=self.search_results, bands=bands, base_directory=base_directory
        )
        self.downloaded_search_assets = downloaded_search_results
        return downloaded_search_results

    def _generate_best_results(self):
        """"""
        results = []
        if self.filtered_results:
            results = self.filtered_results
            return results
        if not self.cloud_cover_sorted_results:
            self.logger.info("Results are not sorted, sorting results...")
            self.sort_results_by_cloud_coverage()
        if self.cloud_cover_sorted_results:
            results = self.cloud_cover_sorted_results
            return results
        return results

    def download_sorted_by_cloud_cover_search_results(
        self, bands: list, base_directory: str | Path, first_x_num_of_items: int | None = None
    ) -> list[Asset]:
        """

        Args:
          bands: List of bands to download from asset
          base_directory: Base directory where assets will be downloaded
          first_x_num_of_items: Number of items to download from the results

        Returns:


        """
        results = self._generate_best_results()
        if not results:
            return []
        if first_x_num_of_items:
            results = results[:first_x_num_of_items]
        downloaded_search_results = self._download_results(results=results, bands=bands, base_directory=base_directory)
        self.downloaded_cloud_cover_sorted_assets = downloaded_search_results
        return downloaded_search_results

    def download_best_cloud_cover_result(self, bands: list, base_directory: str | Path) -> Asset | None:
        """

        Args:
          bands: List of bands to download from asset
          base_directory: Base directory where assets will be downloaded

        Returns:


        """
        results = self._generate_best_results()
        best_result = results[0]
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
