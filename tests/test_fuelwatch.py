import pytest

from fuelwatcher import FuelWatch


@pytest.fixture
def empty_query():
    api = FuelWatch()
    return api.query()


@pytest.fixture
def get_xml():
    api = FuelWatch()
    api.query()
    return api.get_xml


def test_empty_query_return_data(empty_query):
    assert empty_query is not None


def test_xml_returns_data(get_xml):
    assert get_xml is not None
