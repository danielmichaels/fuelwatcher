"""
fuelwatcher - A python module for scraping XML data from the Western
Australian governments Fuel Watch initiative.

<https://www.fuelwatch.wa.gov.au>

    Copyright (C) 2018-2026, Daniel Michaels
"""

import json
import logging
import warnings
from collections.abc import Mapping
from xml.etree import ElementTree

import requests
from fake_useragent import UserAgent

from fuelwatcher import BRAND, PRODUCT, REGION, SUBURB
from fuelwatcher.models import FuelStation, FuelWatchError

logger = logging.getLogger(__name__)


class FuelWatch:
    """Client for FuelWatch RSS Feed.

    Example:
        >>> api = FuelWatch()
        >>> api.query(product=1, region=25)
        >>> for station in api.stations:
        ...     print(f"{station.trading_name}: ${station.price}")
    """

    def __init__(
        self,
        url: str = "https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS",
        product: Mapping[int, str] = PRODUCT,
        region: Mapping[int, str] = REGION,
        brand: Mapping[int, str] = BRAND,
        suburb: list[str] = SUBURB,
    ) -> None:
        """Initialize FuelWatch client.

        Args:
            url: FuelWatch RSS feed URL
            product: Valid product ID mapping (for validation)
            region: Valid region ID mapping (for validation)
            brand: Valid brand ID mapping (for validation)
            suburb: Valid suburb names list (for validation)
        """
        self.url: str = url
        self._product: Mapping[int, str] = product
        self._region: Mapping[int, str] = region
        self._brand: Mapping[int, str] = brand
        self._suburb: list[str] = suburb
        self._json: str | None = None
        self._xml: list[dict[str, str | None]] | None = None
        self._raw: bytes | None = None
        self._stations: list[FuelStation] | None = None
        self._ua = UserAgent()

    @staticmethod
    def user_agent() -> str:
        """Return a random user agent string.

        Returns:
            Random browser user agent string.
        """
        return UserAgent().random

    def _validate_product(self, product: int | None) -> None:
        """Validate product ID."""
        if product is not None and product not in self._product:
            valid = ", ".join(f"{k}: {v}" for k, v in self._product.items())
            raise FuelWatchError(
                f"Invalid product ID: {product}. Valid options: {valid}"
            )

    def _validate_region(self, region: int | None) -> None:
        """Validate region ID."""
        if region is not None and region not in self._region:
            raise FuelWatchError(f"Invalid region ID: {region}")

    def _validate_brand(self, brand: int | None) -> None:
        """Validate brand ID."""
        if brand is not None and brand not in self._brand:
            raise FuelWatchError(f"Invalid brand ID: {brand}")

    def _validate_suburb(self, suburb: str | None) -> None:
        """Validate suburb name."""
        if suburb is not None and suburb not in self._suburb:
            raise FuelWatchError(f"Invalid suburb: {suburb}")

    def query(
        self,
        product: int | None = None,
        suburb: str | None = None,
        region: int | None = None,
        brand: int | None = None,
        surrounding: bool | str | None = None,
        day: str | None = None,
    ) -> bytes:
        """Query FuelWatch for fuel price data.

        If all parameters are None, returns all stations with product
        set to Unleaded Petrol.

        Args:
            product: Fuel type ID:
                1 - Unleaded Petrol, 2 - Premium Unleaded,
                4 - Diesel, 5 - LPG, 6 - 98 RON,
                10 - E85, 11 - Brand diesel
            suburb: Western Australian suburb name
            region: FuelWatch region ID (see REGION constant)
            brand: Fuel brand ID (see BRAND constant)
            surrounding: Include surrounding suburbs. Accepts bool (True/False)
                or str ('yes'/'no'). Defaults to 'yes' when suburb is set.
            day: Date filter - 'today' (default), 'tomorrow' (after 2:30PM),
                'yesterday', or 'DD/MM/YYYY' (max 1 week old)

        Returns:
            Raw XML response as bytes

        Raises:
            FuelWatchError: If validation fails or request fails
        """
        self._validate_product(product)
        self._validate_brand(brand)
        self._validate_region(region)
        self._validate_suburb(suburb)

        # Reset cached data
        self._xml = None
        self._json = None
        self._stations = None

        # Handle bool surrounding parameter
        surrounding_str: str | None = None
        if isinstance(surrounding, bool):
            surrounding_str = "yes" if surrounding else "no"
        elif surrounding is not None:
            surrounding_str = surrounding

        payload = {
            "Product": product,
            "Suburb": suburb,
            "Region": region,
            "Brand": brand,
            "Surrounding": surrounding_str,
            "Day": day,
        }

        try:
            response = requests.get(
                self.url,
                timeout=30,
                params=payload,
                headers={"User-Agent": self._ua.random},
            )
            response.raise_for_status()
            self._raw = response.content
            return self._raw
        except requests.HTTPError as e:
            logger.warning(
                "Failed to get valid response from FuelWatch. Status: %s",
                e.response.status_code if e.response else "unknown",
            )
            raise FuelWatchError(
                f"HTTP error from FuelWatch: {e.response.status_code if e.response else 'unknown'}"
            ) from e
        except requests.RequestException as e:
            logger.exception("Failed to retrieve response from FuelWatch")
            raise FuelWatchError(f"Request failed: {e}") from e

    def _parse_xml(self) -> list[dict[str, str | None]]:
        """Parse raw XML response into list of dictionaries."""
        if self._raw is None:
            raise FuelWatchError("No data available. Call query() first.")

        dom = ElementTree.fromstring(self._raw)
        items = dom.findall("channel/item")

        result: list[dict[str, str | None]] = []
        for elem in items:
            d = {
                "title": elem.findtext("title"),
                "description": elem.findtext("description"),
                "brand": elem.findtext("brand"),
                "date": elem.findtext("date"),
                "price": elem.findtext("price"),
                "trading-name": elem.findtext("trading-name"),
                "location": elem.findtext("location"),
                "address": elem.findtext("address"),
                "phone": elem.findtext("phone"),
                "latitude": elem.findtext("latitude"),
                "longitude": elem.findtext("longitude"),
                "site-features": elem.findtext("site-features"),
            }
            result.append(d)

        return result

    @property
    def raw(self) -> bytes | None:
        """Raw RSS XML response as bytes."""
        return self._raw

    @property
    def xml(self) -> list[dict[str, str | None]]:
        """Parsed XML as list of dictionaries.

        Returns:
            List of station data dictionaries with hyphenated keys.

        Raises:
            FuelWatchError: If no data available (query() not called).
        """
        if self._xml is None:
            self._xml = self._parse_xml()
        return self._xml

    @property
    def json(self) -> str:
        """JSON string representation of the data.

        Returns:
            JSON-formatted string with 4-space indent.

        Raises:
            FuelWatchError: If no data available (query() not called).
        """
        if self._json is None:
            self._json = json.dumps(self.xml, indent=4, ensure_ascii=True)
        return self._json

    @property
    def stations(self) -> list[FuelStation]:
        """List of FuelStation instances.

        Provides typed access to station data with IDE autocomplete support.

        Returns:
            List of FuelStation instances.

        Raises:
            FuelWatchError: If no data available (query() not called).

        Example:
            >>> api = FuelWatch()
            >>> api.query(product=1)
            >>> for station in api.stations:
            ...     print(f"{station.trading_name}: ${station.price}")
        """
        if self._stations is None:
            self._stations = [FuelStation.from_xml_dict(d) for d in self.xml]
        return self._stations

    @property
    def get_raw(self) -> bytes | None:
        """Return raw RSS response.

        .. deprecated:: 1.0.0
            Use :attr:`raw` instead.
        """
        warnings.warn(
            "get_raw is deprecated, use 'raw' property instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.raw

    @property
    def get_xml(self) -> list[dict[str, str | None]]:
        """Parse RSS XML into list of dictionaries.

        .. deprecated:: 1.0.0
            Use :attr:`xml` or :attr:`stations` instead.
        """
        warnings.warn(
            "get_xml is deprecated, use 'xml' or 'stations' property instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.xml

    @property
    def get_json(self) -> str:
        """Convert XML response to JSON string.

        .. deprecated:: 1.0.0
            Use :attr:`json` instead.
        """
        warnings.warn(
            "get_json is deprecated, use 'json' property instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.json
