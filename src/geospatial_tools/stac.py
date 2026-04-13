"""This module contains functions that are related to STAC API."""

import logging
import time
from pathlib import Path
from typing import Any, FrozenSet, Iterator, overload

import pystac
import pystac_client
from planetary_computer import sign_inplace
from pystac_client.exceptions import APIError

from geospatial_tools import geotools_types, s3_utils
from geospatial_tools.auth import get_copernicus_token
from geospatial_tools.geotools_types import DateLike
from geospatial_tools.raster import (
    create_merged_raster_bands_metadata,
    get_total_band_count,
    merge_raster_bands,
    reproject_raster,
)
from geospatial_tools.s3_utils import download_url_s3
from geospatial_tools.utils import create_logger, download_url

LOGGER = create_logger(__name__)

# STAC catalog names
PLANETARY_COMPUTER = "planetary_computer"
COPERNICUS = "copernicus"

CATALOG_NAME_LIST = frozenset([PLANETARY_COMPUTER, COPERNICUS])

# STAC catalog API urls
PLANETARY_COMPUTER_API = "https://planetarycomputer.microsoft.com/api/stac/v1"
COPERNICUS_API = "https://stac.dataspace.copernicus.eu/v1/"


def create_planetary_computer_catalog(
    max_retries: int = 3, delay: int = 5, logger: logging.Logger = LOGGER
) -> pystac_client.Client | None:
    """
    Creates a Planetary Computer Catalog Client.

    Args:
      max_retries: The maximum number of retries for the API connection. (Default value = 3)
      delay: The delay between retry attempts in seconds. (Default value = 5)
      logger: The logger instance to use. (Default value = LOGGER)

    Returns:
        A pystac_client.Client instance if successful, else None.
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


def create_copernicus_catalog(
    max_retries: int = 3, delay: int = 5, logger: logging.Logger = LOGGER
) -> pystac_client.Client | None:
    """
    Creates a Copernicus Data Space Ecosystem Catalog Client.

    Args:
      max_retries: The maximum number of retries for the API connection. (Default value = 3)
      delay: The delay between retry attempts in seconds. (Default value = 5)
      logger: The logger instance to use. (Default value = LOGGER)

    Returns:
        A pystac_client.Client instance if successful, else None.
    """
    for attempt in range(1, max_retries + 1):
        try:
            client = pystac_client.Client.open(COPERNICUS_API)
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


def catalog_generator(catalog_name: str, logger: logging.Logger = LOGGER) -> pystac_client.Client | None:
    """
    Generates a STAC Client for the specified catalog.

    Args:
      catalog_name: The name of the catalog (e.g., 'planetary_computer', 'copernicus').
      logger: The logger instance to use.

    Returns:
        A pystac_client.Client instance for the requested catalog if supported, else None.
    """
    catalog_dict = {
        PLANETARY_COMPUTER: create_planetary_computer_catalog,
        COPERNICUS: create_copernicus_catalog,
    }
    if catalog_name not in catalog_dict:
        logger.error(f"Unsupported catalog name: {catalog_name}")
        return None

    catalog = catalog_dict[catalog_name]()

    return catalog


def list_available_catalogs(logger: logging.Logger = LOGGER) -> FrozenSet[str]:
    """
    Lists all available STAC catalogs.

    Args:
      logger: The logger instance to use.

    Returns:
        A frozenset of available catalog names.
    """
    logger.info("Available catalogs")
    return CATALOG_NAME_LIST


class AssetSubItem:
    """
    Class that represent a STAC asset sub item.

    Generally represents a single satellite image band.
    """

    def __init__(self, asset: pystac.Item, item_id: str, band: str, filename: str | Path) -> None:
        """
        Initializes an AssetSubItem.

        Args:
            asset: The pystac Item this asset belongs to.
            item_id: The ID of the item.
            band: The band name of this sub-item.
            filename: The local filename of the downloaded asset.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        self.asset = asset
        self.item_id: str = item_id
        self.band: str = band
        self.filename: Path = filename


class Asset:
    """Represents a STAC asset, potentially composed of multiple bands/sub-items."""

    def __init__(
        self,
        asset_id: str,
        bands: list[str] | None = None,
        asset_item_list: list[AssetSubItem] | None = None,
        merged_asset_path: str | Path | None = None,
        reprojected_asset: str | Path | None = None,
        logger: logging.Logger = LOGGER,
    ) -> None:
        """
        Initializes an Asset object.

        Args:
            asset_id: Unique ID for the asset (usually the item ID).
            bands: List of bands this asset contains.
            asset_item_list: List of AssetSubItem objects belonging to this asset.
            merged_asset_path: Path to the merged multi-band raster file.
            reprojected_asset: Path to the reprojected raster file.
            logger: Logger instance.
        """
        self.asset_id = asset_id
        self.bands = bands
        self.merged_asset_path = Path(merged_asset_path) if isinstance(merged_asset_path, str) else merged_asset_path
        self.reprojected_asset_path = (
            Path(reprojected_asset) if isinstance(reprojected_asset, str) else reprojected_asset
        )
        self.logger = logger

        self._sub_items: list[AssetSubItem] = asset_item_list or []

    def __iter__(self) -> Iterator[AssetSubItem]:
        """Allows direct iteration: `for item in asset:`"""
        return iter(self._sub_items)

    def __len__(self) -> int:
        """Allows checking size: `len(asset)`"""
        return len(self._sub_items)

    def __contains__(self, band_name: str) -> bool:
        """Allows checking for band existence: `"B04" in asset`"""
        return any(item.band == band_name for item in self._sub_items)

    @overload
    def __getitem__(self, index: int) -> AssetSubItem: ...

    @overload
    def __getitem__(self, band_name: str) -> AssetSubItem: ...

    def __getitem__(self, key: int | str) -> AssetSubItem:
        """
        Allows indexing by position or band name:
        `asset[0]` or `asset["B04"]`
        """
        if isinstance(key, int):
            return self._sub_items[key]

        if isinstance(key, str):
            for item in self._sub_items:
                if item.band == key:
                    return item
            raise KeyError(f"Band '{key}' not found in asset '{self.asset_id}'.")

        raise TypeError(f"Invalid argument type: {type(key)}. Expected int or str.")

    def add_asset_item(self, asset: AssetSubItem) -> None:
        """
        Adds an AssetSubItem to the asset.

        Args:
          asset: The AssetSubItem to add.
        """
        self._sub_items.append(asset)
        if asset.band not in self.bands:
            self.bands.append(asset.band)

    def show_asset_items(self) -> None:
        """Show items that belong to this asset."""
        asset_list = [
            f"ID: [{item.item_id}], Band: [{item.band}], filename: [{item.filename}]" for item in self._sub_items
        ]
        self.logger.info(f"Asset list for asset [{self.asset_id}] :\n\t{asset_list}")

    def merge_asset(self, base_directory: str | Path | None = None, delete_sub_items: bool = False) -> Path | None:
        """
        Merges individual band rasters into a single multi-band raster file.

        Args:
          base_directory: Directory where the merged file will be saved.
          delete_sub_items: If True, delete individual band files after merging.

        Returns:
            The Path to the merged file if successful, else None.
        """
        if not base_directory:
            base_directory = Path("")
        if isinstance(base_directory, str):
            base_directory = Path(base_directory)

        merged_filename = base_directory / f"{self.asset_id}_merged.tif"

        if not self._sub_items:
            self.logger.error(f"No asset items to merge for asset [{self.asset_id}]")
            return None

        asset_filename_list = [asset.filename for asset in self._sub_items]

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
        base_directory: str | Path | None = None,
        delete_merged_asset: bool = False,
    ) -> Path | None:
        """
        Reprojects the merged multi-band raster to a target projection.

        Args:
          target_projection: The target CRS (EPSG code or string).
          base_directory: Directory where the reprojected file will be saved.
          delete_merged_asset: If True, delete the merged file after reprojection.

        Returns:
            The Path to the reprojected file if successful, else None.
        """
        if not base_directory:
            base_directory = Path("")
        if isinstance(base_directory, str):
            base_directory = Path(base_directory)
        target_path = base_directory / f"{self.asset_id}_reprojected.tif"
        self.logger.info(f"Reprojecting asset [{self.asset_id}] ...")

        if not self.merged_asset_path:
            self.logger.error(f"Merged asset path is missing for asset [{self.asset_id}]")
            return None

        reprojected_filename = reproject_raster(
            dataset_path=self.merged_asset_path,
            target_path=target_path,
            target_crs=target_projection,
            logger=self.logger,
        )
        if reprojected_filename and reprojected_filename.exists():
            self.logger.info(f"Asset location : [{reprojected_filename}]")
            self.reprojected_asset_path = reprojected_filename
            if delete_merged_asset:
                self.delete_merged_asset()
            return reprojected_filename
        self.logger.error(f"There was a problem reprojecting asset [{self.asset_id}]")
        return None

    def delete_asset_sub_items(self) -> None:
        """Delete all asset sub items that belong to this asset."""
        self.logger.info(f"Deleting asset sub items from asset [{self.asset_id}]")
        for item in self._sub_items:
            self.logger.info(f"Deleting [{item.filename}] ...")
            item.filename.unlink(missing_ok=True)

    def delete_merged_asset(self) -> None:
        """Delete merged asset."""
        if self.merged_asset_path:
            self.logger.info(f"Deleting merged asset file for [{self.merged_asset_path}]")
            self.merged_asset_path.unlink(missing_ok=True)

    def delete_reprojected_asset(self) -> None:
        """Delete reprojected asset."""
        if self.reprojected_asset_path:
            self.logger.info(f"Deleting reprojected asset file for [{self.reprojected_asset_path}]")
            self.reprojected_asset_path.unlink(missing_ok=True)

    def _create_merged_asset_metadata(self) -> dict[str, Any]:
        """
        Creates metadata for the merged asset from its sub-items.

        Returns:
            A dictionary containing the merged metadata.
        """
        self.logger.info("Creating merged asset metadata")
        if not self._sub_items:
            return {}
        file_list = [asset.filename for asset in self._sub_items]
        meta = create_merged_raster_bands_metadata(file_list)
        return meta

    def _get_asset_total_bands(self) -> int:
        """
        Calculates the total number of bands across all asset sub-items.

        Returns:
            The total count of bands.
        """
        if not self._sub_items:
            return 0
        downloaded_file_list = [asset.filename for asset in self._sub_items]
        total_band_count = get_total_band_count(downloaded_file_list)
        return total_band_count


def download_stac_asset(
    asset_url: str,
    destination: Path,
    method: str = "http",
    headers: dict[str, str] | None = None,
    s3_client: Any | None = None,
    logger: logging.Logger = LOGGER,
) -> Path | None:
    """
    Generic dispatcher for downloading STAC assets via HTTP or S3.

    Args:
        asset_url: URL/HREF of the asset to download.
        destination: Path where the file will be saved.
        method: Download method ('http' or 's3').
        headers: Headers for HTTP request.
        s3_client: Boto3 S3 client (required for 's3' method).
        logger: Logger instance.

    Returns:
        The Path to the downloaded file if successful, else None.
    """
    if method == "s3":
        file_path = download_url_s3(asset_url=asset_url, destination=destination, s3_client=s3_client, logger=logger)
    else:
        # Default to HTTP
        file_path = download_url(url=asset_url, filename=destination, headers=headers, logger=logger)

    return file_path


class StacSearch:
    """Utility class to help facilitate and automate STAC API searches through the use of `pystac_client.Client`."""

    def __init__(self, catalog_name: str, logger: logging.Logger = LOGGER) -> None:
        """
        Initializes a StacSearch instance.

        Args:
            catalog_name: Name of the STAC catalog (e.g., 'planetary_computer', 'copernicus').
            logger: Logger instance.
        """
        self.catalog_name = catalog_name
        self.catalog: pystac_client.Client | None = catalog_generator(catalog_name=catalog_name)
        self.search_results: list[pystac.Item] | None = None
        self.cloud_cover_sorted_results: list[pystac.Item] | None = None
        self.filtered_results: list[pystac.Item] | None = None
        self.downloaded_search_assets: list[Asset] | None = None
        self.downloaded_cloud_cover_sorted_assets: list[Asset] | None = None
        self.downloaded_best_sorted_asset: Asset | None = None
        self.logger = logger
        self.s3_client: Any | None = None
        if catalog_name == COPERNICUS:
            self.s3_client = s3_utils.get_s3_client()

    def search(
        self,
        date_range: DateLike = None,
        max_items: int | None = None,
        limit: int | None = None,
        ids: list[str] | None = None,
        collections: str | list[str] | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict[str, Any] | None = None,
        sortby: list[dict[str, Any]] | dict[str, Any] | None = None,
        max_retries: int = 3,
        delay: int = 5,
    ) -> list[pystac.Item]:
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
            A list of pystac.Item objects matching the search criteria.
        """
        if isinstance(collections, str):
            collections = [collections]
        if isinstance(sortby, dict):
            sortby = [sortby]

        if not self.catalog:
            self.logger.error("STAC client is not initialized.")
            return []

        intro_log = "Initiating STAC API search"
        if query:
            intro_log = f"{intro_log} \n\tQuery : [{query}]"
        self.logger.info(intro_log)
        items: list[pystac.Item] = []
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
                break
            except APIError as e:  # pylint: disable=W0718
                self.logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                else:
                    raise e

        self.search_results = items
        return items

    def search_for_date_ranges(
        self,
        date_ranges: list[DateLike],
        max_items: int | None = None,
        limit: int | None = None,
        collections: str | list[str] | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict[str, Any] | None = None,
        sortby: list[dict[str, Any]] | dict[str, Any] | None = None,
        max_retries: int = 3,
        delay: int = 5,
    ) -> list[pystac.Item]:
        """
        STAC API search that will use search query and parameters for each date range in given list of `date_ranges`.

        Date ranges can be generated with the help of the `geospatial_tools.utils.create_date_range_for_specific_period`
        function for more complex ranges.

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
            A list of pystac.Item objects.
        """
        results: list[pystac.Item] = []
        if isinstance(collections, str):
            collections = [collections]
        if isinstance(sortby, dict):
            sortby = [sortby]

        if not self.catalog:
            self.logger.error("STAC client is not initialized.")
            return []

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
                break
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
        ids: list[str] | None = None,
        collections: str | list[str] | None = None,
        bbox: geotools_types.BBoxLike | None = None,
        intersects: geotools_types.IntersectsLike | None = None,
        query: dict[str, Any] | None = None,
        sortby: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> list[pystac.Item]:
        """
        Performs a basic search on the catalog.

        Args:
            date_range: The date range for the search.
            max_items: The maximum number of items to return.
            limit: The number of items to return per page.
            ids: List of item IDs to filter on.
            collections: List of collection IDs to search.
            bbox: Bounding box to filter results.
            intersects: Geometry to filter results.
            query: Query parameters for the STAC API query extension.
            sortby: Sort parameters for the response.

        Returns:
            A list of pystac.Item objects found.
        """
        if not self.catalog:
            return []

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
        items = list(search.items())
        base_log_message = f"for date range [{date_range} ]"
        log_msg = f"Search successful {base_log_message}"
        log_state = self.logger.debug
        if not items:
            log_msg = f"Search failed {base_log_message}"
            log_state = self.logger.warning
        log_state(log_msg)
        return items

    def sort_results_by_cloud_coverage(self) -> list[pystac.Item] | None:
        """
        Sorts the search results by cloud coverage (ascending).

        Returns:
            A list of sorted pystac.Item objects, or None if no results exist.
        """
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
        Filter results that are above a nodata value threshold.

        Args:
          property_name: Name of the property containing nodata percentage.
          max_no_data_value: Max allowed percentage of nodata. (Default value = 5)

        Returns:
            Filtered list of pystac.Item objects.
        """
        sorted_results = self.cloud_cover_sorted_results
        if not sorted_results:
            sorted_results = self.sort_results_by_cloud_coverage()
        if not sorted_results:
            return None

        filtered_results = []
        for item in sorted_results:
            if item.properties.get(property_name, 0) < max_no_data_value:
                filtered_results.append(item)
        self.filtered_results = filtered_results

        return filtered_results

    def _download_assets(self, item: pystac.Item, bands: list[str], base_directory: Path) -> Asset:
        """
        Downloads specific bands for a single STAC item.

        Args:
            item: The STAC item to download assets for.
            bands: List of band names to download.
            base_directory: The directory where files will be saved.

        Returns:
            An Asset object containing the downloaded files.
        """
        image_id = item.id
        downloaded_files = Asset(asset_id=image_id, bands=bands)

        headers: dict[str, str] | None = None
        method = "http"
        if self.catalog_name == COPERNICUS:
            method = "s3"
            token = get_copernicus_token(self.logger)
            if token:
                headers = {"Authorization": f"Bearer {token}"}
            else:
                self.logger.error("Failed to obtain Copernicus token. Download may fail.")

        for band in bands:
            if band not in item.assets:
                self.logger.info(f"Band {band} not available for {image_id}.")
                continue

            asset = item.assets[band]
            asset_url = asset.href
            self.logger.info(f"Downloading {band} from {asset_url} using method [{method}]")
            file_name = base_directory / f"{image_id}_{band}.tif"

            downloaded_file = download_stac_asset(
                asset_url=asset_url,
                destination=file_name,
                method=method,
                headers=headers,
                s3_client=self.s3_client,
                logger=self.logger,
            )

            if downloaded_file:
                asset_file = AssetSubItem(asset=item, item_id=image_id, band=band, filename=downloaded_file)
                downloaded_files.add_asset_item(asset_file)

        return downloaded_files

    def _download_results(
        self, results: list[pystac.Item] | None, bands: list[str], base_directory: str | Path
    ) -> list[Asset]:
        """
        Downloads assets for multiple results.

        Args:
            results: List of STAC items to download.
            bands: List of bands to download for each item.
            base_directory: The base directory for downloads.

        Returns:
            A list of Asset objects corresponding to the downloaded items.
        """
        if not results:
            return []
        downloaded_search_results: list[Asset] = []
        if not isinstance(base_directory, Path):
            base_directory = Path(base_directory)
        if not base_directory.exists():
            base_directory.mkdir(parents=True, exist_ok=True)

        for item in results:
            self.logger.info(f"Downloading [{item.id}] ...")
            downloaded_item = self._download_assets(item=item, bands=bands, base_directory=base_directory)
            downloaded_search_results.append(downloaded_item)
        return downloaded_search_results

    def download_search_results(self, bands: list[str], base_directory: str | Path) -> list[Asset]:
        """
        Downloads assets for all search results.

        Args:
            bands: List of bands to download.
            base_directory: The base directory for downloads.

        Returns:
            A list of Asset objects for the downloaded search results.
        """
        downloaded_search_results = self._download_results(
            results=self.search_results, bands=bands, base_directory=base_directory
        )
        self.downloaded_search_assets = downloaded_search_results
        return downloaded_search_results

    def _generate_best_results(self) -> list[pystac.Item]:
        """
        Selects the best results (filtered or sorted).

        Returns:
            A list of pystac.Item objects representing the best results.
        """
        if self.filtered_results:
            return self.filtered_results
        if not self.cloud_cover_sorted_results:
            self.logger.info("Results are not sorted, sorting results...")
            self.sort_results_by_cloud_coverage()
        if self.cloud_cover_sorted_results:
            return self.cloud_cover_sorted_results
        return []

    def download_sorted_by_cloud_cover_search_results(
        self, bands: list[str], base_directory: str | Path, first_x_num_of_items: int | None = None
    ) -> list[Asset]:
        """
        Downloads sorted results.

        Args:
            bands: List of bands to download.
            base_directory: The base directory for downloads.
            first_x_num_of_items: Optional number of top items to download.

        Returns:
            A list of Asset objects for the downloaded items.
        """
        results = self._generate_best_results()
        if not results:
            return []
        if first_x_num_of_items:
            results = results[:first_x_num_of_items]
        downloaded_search_results = self._download_results(results=results, bands=bands, base_directory=base_directory)
        self.downloaded_cloud_cover_sorted_assets = downloaded_search_results
        return downloaded_search_results

    def download_best_cloud_cover_result(self, bands: list[str], base_directory: str | Path) -> Asset | None:
        """
        Downloads the single best result based on cloud cover.

        Args:
            bands: List of bands to download.
            base_directory: The base directory for downloads.

        Returns:
            The Asset object for the best result, or None if no results available.
        """
        results = self._generate_best_results()
        if not results:
            return None
        best_result = [results[0]]

        if self.downloaded_cloud_cover_sorted_assets:
            self.logger.info(f"Asset [{best_result[0].id}] is already downloaded")
            self.downloaded_best_sorted_asset = self.downloaded_cloud_cover_sorted_assets[0]
            return self.downloaded_cloud_cover_sorted_assets[0]

        downloaded_search_results = self._download_results(
            results=best_result, bands=bands, base_directory=base_directory
        )
        if downloaded_search_results:
            self.downloaded_best_sorted_asset = downloaded_search_results[0]
            return downloaded_search_results[0]
        return None
