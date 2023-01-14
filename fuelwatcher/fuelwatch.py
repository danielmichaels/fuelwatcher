"""
    fuelwatcher - A python module for scraping XML data from the Western
    Australian governments Fuel Watch initiative.

    <https://www.fuelwatch.wa.gov.au>

        Copyright (C) 2018-2023, Daniel Michaels
"""
import json
import logging
import random
from xml.etree import ElementTree

import requests

from fuelwatcher import BRAND, PRODUCT, REGION, SUBURB

logging.basicConfig(level=logging.INFO)


class FuelWatch:
    """Client for FuelWatch RSS Feed."""

    def __init__(
        self,
        url="http://fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS",
        product=PRODUCT,
        region=REGION,
        brand=BRAND,
        suburb=SUBURB,
    ):
        self.url: str = url
        self._product: int = product
        self._region: int = region
        self._brand: int = brand
        self._suburb: str = suburb
        self._json = None
        self._xml = None
        self._raw = None

    @staticmethod
    def user_agent():
        """
        A static method which returns a random user agent for sending with each request.

        User agents taken from this regularly updated resource. Refer to this to update where
        required.
        https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
        ]
        agent = random.choice(user_agents)

        return agent

    def _validate_product(self, product: int) -> bool:
        if not product:
            return True
        else:
            assert product in self._product, "Invalid Product Integer."

    def _validate_region(self, region: int) -> bool:
        if not region:
            return True
        else:
            assert region in self._region, "Invalid Region Specified."

    def _validate_brand(self, brand: int) -> bool:
        if not brand:
            return True
        else:
            assert brand in self._brand, "Invalid Brand."

    def _validate_suburb(self, suburb: str) -> bool:
        if not suburb:
            return True
        else:
            assert suburb in self._suburb, "Invalid Suburb - Check Spelling"

    def query(
        self,
        product: int = None,
        suburb: str = None,
        region: int = None,
        brand: int = None,
        surrounding: str = None,
        day: str = None,
    ):
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

        self._validate_product(product)
        self._validate_brand(brand)
        self._validate_region(region)
        self._validate_suburb(suburb)

        payload = {
            "Product": product,
            "Suburb": suburb,
            "Region": region,
            "Brand": brand,
            "Surrounding": surrounding,
            "Day": day,
        }

        try:
            response = requests.get(
                self.url,
                timeout=30,
                params=payload,
                headers={"User-Agent": self.user_agent()},
            )
            if response.status_code == 200:
                self._raw = response.content
                return self._raw
            else:
                logging.log(
                    logging.WARN,
                    msg=f"Failed to get valid response from fuelwatcher website. Response: {response.status_code}",
                )
        except Exception as e:
            logging.log(
                logging.ERROR,
                msg="Failed to retrieve response from fuelwatcher website",
            )
            print(e)

    @property
    def get_raw(self):
        """
        Returns the full RSS response unparsed.

        :return: byte string full RSS XML response
        """
        return self._raw

    @property
    def get_xml(self):
        """
        Given page content parses through the RSS XML and returns only 'item'
        data which contains fuel station information.

        :return: a list of dictionaries from the XML content.
        """

        dom = ElementTree.fromstring(self._raw)
        items = dom.findall("channel/item")

        self._xml = []
        for elem in items:
            d = {
                "title": elem.find("title").text,
                "description": elem.find("description").text,
                "brand": elem.find("brand").text,
                "date": elem.find("date").text,
                "price": elem.find("price").text,
                "trading-name": elem.find("trading-name").text,
                "location": elem.find("location").text,
                "address": elem.find("address").text,
                "phone": elem.find("phone").text,
                "latitude": elem.find("latitude").text,
                "longitude": elem.find("longitude").text,
                "site-features": elem.find("site-features").text,
            }

            self._xml.append(d)

        return self._xml

    @property
    def get_json(self):
        """
        Convert the xml response into json.
        """
        xml = self.get_xml
        json_results = json.dumps(xml, indent=4, ensure_ascii=True)
        self._json = json_results

        return self._json
