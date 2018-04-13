"""
    fuelwatcher - A python module for scraping XML data from the Western
    Australian governments Fuel Watch initiative.

    <https://www.fuelwatch.wa.gov.au>

        Copyright (C) 2018, Daniel Michaels
"""
from .constants import PRODUCT, REGION, BRAND, SUBURB
from xml.etree import ElementTree

import logging
import json
import requests

logging.basicConfig(level=logging.INFO)


class FuelWatch:
    """Client for FuelWatch RSS Feed. """

    def __init__(self,
                 url='http://fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS',
                 product=PRODUCT, region=REGION, brand=BRAND, suburb=SUBURB):
        self.url = url
        self._product = product
        self._region = region
        self._brand = brand
        self._suburb = suburb
        self._json = None
        self._xml = None
        self._raw = None

    def validate_product(self, product: int) -> bool:
        if not product:
            return True
        else:
            assert product in self._product, "Invalid Product Integer."

    def validate_region(self, region: int) -> bool:
        if not region:
            return True
        else:
            assert region in self._region, "Invalid Region Specified."

    def validate_brand(self, brand: int) -> bool:
        if not brand:
            return True
        else:
            assert brand in self._brand, "Invalid Brand."

    def validate_suburb(self, suburb: str) -> bool:
        if not suburb:
            return True
        else:
            assert suburb in self._suburb, "Invalid Suburb - Check Spelling"

    def query(self, product: int = None, suburb: str = None,
              region: int = None, brand: int = None, surrounding: str = None,
              day: str = None):
        """
        Returns FuelWatch data based on query parameters

        If all parameters are None it will return all stations with
        product set to Unleaded Petrol.

        :param product: Takes in a integer from the following table.
        1 - Unleaded Petrol     2 - Premium Unleaded
        4 - Diesel              5 - LPG
        6 - 98 RON              10 - E85
        11 - Brand diesel

        :param suburb: Takes a valid Western Australian suburb.

        Full list found in utils.suburbs

        :param region: FuelWatch seperates WA into regions that take an

        integer. Refer to utils.region for a listing.

        :param brand: Takes in any valid registered WA fuel station. Refer to
        utils.brand for the full list.

        :param surrounding: boolean 'yes/no' that will return surrounding
        suburbs when used in conjuction with the suburb parameter. Must be set
        to 'no' explicitly, otherwise returns True.

        :param day: Capable of four argument types:
            - today (this is the default)
            - tomorrow (only available after 2:30PM)
            - yesterday
            - DD/MM/YYYY (only prices for the last week, e.g. 23/08/2016)

            returns today if not set.

        :return: byte-string content of url
        """

        self.validate_product(product)
        self.validate_brand(brand)
        self.validate_region(region)
        self.validate_suburb(suburb)

        payload = dict()
        payload['Product'] = product
        payload['Suburb'] = suburb
        payload['Region'] = region
        payload['Brand'] = brand
        payload['Surrounding'] = surrounding
        payload['Day'] = day

        try:
            response = requests.get(self.url, timeout=30, params=payload)
            if response.status_code == 200:
                self._raw = response.content
                # return self._raw
                return self._raw
        except Exception as e:
            print(e)

    @property
    def get_raw(self):
        """
        Returns the full RSS response unparsed.

        :param result: url response.content from FuelWatch.query()

        :return: byte string full RSS XML response
        """
        return self._raw

    @property
    def get_xml(self):
        """
        Given page content parses through the RSS XML and returns only 'item'
        data which contains fuel station information.

        :param result: url response.content from FuelWatch.query()

        :return: a list of dictionaries from the XML content.
        """

        dom = ElementTree.fromstring(self._raw)
        items = dom.findall('channel/item')

        self._xml = []
        for elem in items:
            dic = dict()

            dic['title'] = elem.find('title').text
            dic['description'] = elem.find('description').text
            dic['brand'] = elem.find('brand').text
            dic['date'] = elem.find('date').text
            dic['price'] = elem.find('price').text
            dic['trading-name'] = elem.find('trading-name').text
            dic['location'] = elem.find('location').text
            dic['address'] = elem.find('address').text
            dic['phone'] = elem.find('phone').text
            dic['latitude'] = elem.find('latitude').text
            dic['longitude'] = elem.find('longitude').text
            dic['site-features'] = elem.find('site-features').text
            self._xml.append(dic)

        return self._xml

    @property
    def get_json(self):
        xml = self.get_xml
        json_results = json.dumps(xml, indent=4, ensure_ascii=True)
        self._json = json_results

        return self._json
