"""
Data models and exceptions for FuelWatch.

Copyright (C) 2018-2025, Daniel Michaels
"""

from dataclasses import dataclass
from typing import Self


class FuelWatchError(Exception):
    """Raised when FuelWatch validation or request fails."""

    pass


@dataclass(frozen=True, slots=True)
class FuelStation:
    """Represents a single fuel station from FuelWatch.

    Attributes:
        title: Display title (e.g., "138.5: Puma Bayswater")
        description: Full description of the station
        brand: Fuel brand name
        date: Date of the price data
        price: Fuel price as string (e.g., "138.5")
        trading_name: Business trading name
        location: Suburb/location name
        address: Street address
        phone: Contact phone number (may be None)
        latitude: Geographic latitude
        longitude: Geographic longitude
        site_features: Available features at station (may be None)
    """

    title: str
    description: str
    brand: str
    date: str
    price: str
    trading_name: str
    location: str
    address: str
    phone: str | None
    latitude: str
    longitude: str
    site_features: str | None

    def to_dict(self) -> dict[str, str | None]:
        """Convert to dictionary with hyphenated keys for backwards compatibility.

        Returns:
            Dictionary with keys matching the original XML field names
            (e.g., 'trading-name' instead of 'trading_name').
        """
        return {
            "title": self.title,
            "description": self.description,
            "brand": self.brand,
            "date": self.date,
            "price": self.price,
            "trading-name": self.trading_name,
            "location": self.location,
            "address": self.address,
            "phone": self.phone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "site-features": self.site_features,
        }

    @classmethod
    def from_xml_dict(cls, data: dict[str, str | None]) -> Self:
        """Create a FuelStation from XML-style dictionary with hyphenated keys.

        Args:
            data: Dictionary with hyphenated keys (e.g., 'trading-name')

        Returns:
            FuelStation instance
        """
        return cls(
            title=data.get("title") or "",
            description=data.get("description") or "",
            brand=data.get("brand") or "",
            date=data.get("date") or "",
            price=data.get("price") or "",
            trading_name=data.get("trading-name") or "",
            location=data.get("location") or "",
            address=data.get("address") or "",
            phone=data.get("phone"),
            latitude=data.get("latitude") or "",
            longitude=data.get("longitude") or "",
            site_features=data.get("site-features"),
        )
