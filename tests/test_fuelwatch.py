"""Tests for FuelWatch API client."""

import warnings

import pytest

from fuelwatcher import FuelStation, FuelWatch, FuelWatchError


@pytest.fixture
def api() -> FuelWatch:
    """Create a FuelWatch instance."""
    return FuelWatch()


@pytest.fixture
def queried_api(api: FuelWatch) -> FuelWatch:
    """Create a FuelWatch instance with data loaded."""
    api.query()
    return api


def test_empty_query_returns_data(api: FuelWatch) -> None:
    """Query with no params returns data (defaults to Unleaded)."""
    result = api.query()
    assert result is not None
    assert isinstance(result, bytes)


def test_query_with_product(api: FuelWatch) -> None:
    """Query with product filter returns data."""
    result = api.query(product=1)  # Unleaded
    assert result is not None


def test_query_with_region(api: FuelWatch) -> None:
    """Query with region filter returns data."""
    result = api.query(region=25)  # Metro - South of River
    assert result is not None


def test_raw_property(queried_api: FuelWatch) -> None:
    """Raw property returns bytes."""
    assert queried_api.raw is not None
    assert isinstance(queried_api.raw, bytes)


def test_xml_property(queried_api: FuelWatch) -> None:
    """XML property returns list of dicts."""
    xml = queried_api.xml
    assert xml is not None
    assert isinstance(xml, list)
    if xml:  # May be empty if no stations
        assert isinstance(xml[0], dict)
        assert "title" in xml[0]
        assert "price" in xml[0]


def test_json_property(queried_api: FuelWatch) -> None:
    """JSON property returns string."""
    json_str = queried_api.json
    assert json_str is not None
    assert isinstance(json_str, str)
    assert json_str.startswith("[")  # JSON array


def test_stations_property(queried_api: FuelWatch) -> None:
    """Stations property returns list of FuelStation dataclasses."""
    stations = queried_api.stations
    assert stations is not None
    assert isinstance(stations, list)
    if stations:  # May be empty if no stations
        station = stations[0]
        assert isinstance(station, FuelStation)
        assert hasattr(station, "title")
        assert hasattr(station, "price")
        assert hasattr(station, "trading_name")  # Pythonic naming
        assert hasattr(station, "latitude")


def test_fuel_station_from_xml_dict() -> None:
    """FuelStation can be created from XML-style dict."""
    data = {
        "title": "138.5: Test Station",
        "description": "Test Description",
        "brand": "Shell",
        "date": "2024-01-01",
        "price": "138.5",
        "trading-name": "Test Shell",
        "location": "Perth",
        "address": "123 Test St",
        "phone": "08 1234 5678",
        "latitude": "-31.9505",
        "longitude": "115.8605",
        "site-features": "ATM",
    }
    station = FuelStation.from_xml_dict(data)

    assert station.title == "138.5: Test Station"
    assert station.price == "138.5"
    assert station.trading_name == "Test Shell"  # Converted from hyphenated
    assert station.site_features == "ATM"


def test_fuel_station_to_dict() -> None:
    """FuelStation.to_dict() returns hyphenated keys for backwards compat."""
    station = FuelStation(
        title="Test",
        description="Desc",
        brand="BP",
        date="2024-01-01",
        price="140.0",
        trading_name="Test BP",
        location="Perth",
        address="456 Test Ave",
        phone=None,
        latitude="-31.95",
        longitude="115.86",
        site_features=None,
    )
    d = station.to_dict()

    assert "trading-name" in d  # Hyphenated for backwards compat
    assert d["trading-name"] == "Test BP"
    assert "site-features" in d
    assert d["phone"] is None


def test_fuel_station_is_immutable() -> None:
    """FuelStation is frozen (immutable)."""
    station = FuelStation(
        title="Test",
        description="",
        brand="",
        date="",
        price="",
        trading_name="",
        location="",
        address="",
        phone=None,
        latitude="",
        longitude="",
        site_features=None,
    )
    with pytest.raises(AttributeError):
        station.price = "999"  # type: ignore[misc]


def test_invalid_product_raises_error(api: FuelWatch) -> None:
    """Invalid product ID raises FuelWatchError."""
    with pytest.raises(FuelWatchError, match="Invalid product ID"):
        api.query(product=999)


def test_invalid_region_raises_error(api: FuelWatch) -> None:
    """Invalid region ID raises FuelWatchError."""
    with pytest.raises(FuelWatchError, match="Invalid region ID"):
        api.query(region=999)


def test_invalid_brand_raises_error(api: FuelWatch) -> None:
    """Invalid brand ID raises FuelWatchError."""
    with pytest.raises(FuelWatchError, match="Invalid brand ID"):
        api.query(brand=999)


def test_invalid_suburb_raises_error(api: FuelWatch) -> None:
    """Invalid suburb raises FuelWatchError."""
    with pytest.raises(FuelWatchError, match="Invalid suburb"):
        api.query(suburb="NotARealSuburb")


def test_accessing_data_before_query_raises_error(api: FuelWatch) -> None:
    """Accessing xml/json/stations before query() raises FuelWatchError."""
    with pytest.raises(FuelWatchError, match="No data available"):
        _ = api.xml


def test_surrounding_accepts_bool_true(api: FuelWatch) -> None:
    """Surrounding parameter accepts True."""
    result = api.query(suburb="Perth", surrounding=True)
    assert result is not None


def test_surrounding_accepts_bool_false(api: FuelWatch) -> None:
    """Surrounding parameter accepts False."""
    result = api.query(suburb="Perth", surrounding=False)
    assert result is not None


def test_surrounding_accepts_string(api: FuelWatch) -> None:
    """Surrounding parameter still accepts string for backwards compat."""
    result = api.query(suburb="Perth", surrounding="yes")
    assert result is not None


def test_get_raw_deprecation_warning(queried_api: FuelWatch) -> None:
    """get_raw triggers deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = queried_api.get_raw
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_raw is deprecated" in str(w[0].message)


def test_get_xml_deprecation_warning(queried_api: FuelWatch) -> None:
    """get_xml triggers deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = queried_api.get_xml
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_xml is deprecated" in str(w[0].message)


def test_get_json_deprecation_warning(queried_api: FuelWatch) -> None:
    """get_json triggers deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = queried_api.get_json
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "get_json is deprecated" in str(w[0].message)


def test_deprecated_get_xml_still_works(queried_api: FuelWatch) -> None:
    """Deprecated get_xml still returns data for backwards compat."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        xml = queried_api.get_xml
        assert xml is not None
        assert isinstance(xml, list)
