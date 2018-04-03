"""
fuelwatch wa - add description

include copyright

include license
"""
from pprint import pprint

import requests
import requests_cache
import logging
from xml.etree import ElementTree

logging.basicConfig(level=logging.INFO)


class FuelWatch:

    def __init__(self,
                 url='http://fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS'):
        self.url = url

    def query(self, product=None, suburb=None, region=None, brand=None,
              surrounding=None, day=None):
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

        payload = dict()
        payload['Product'] = product
        payload['Suburb'] = suburb
        payload['Region'] = region
        payload['Brand'] = brand
        payload['Surrounding'] = surrounding
        payload['Day'] = day
        logging.info(payload)

        try:
            resp = requests.get(self.url, timeout=30, params=payload)
            requests_cache.install_cache()
            logging.info(resp)
            logging.info(resp.url)
            if resp.status_code == 200:
                return resp.content
                # print('should go to self.parse now')
                # results = resp.content
                # return self.parse(results)
        except Exception as e:
            print(e)

    def get_raw_xml(self, result):
        """
        Returns the full RSS response. Must be manually called.

        :param result:
        :return:
        """
        print(result)
        print('R\nA\nW\n')
        pass

    def parse(self, result):
        """
        Given page content parses through the RSS XML and returns only 'item'
        data which contains fuel station information.

        :param result: url response.content from FuelWatch.query()

        :return: a list of dictionaries from the XML content.
        """

        logging.info(result)
        dom = ElementTree.fromstring(result)
        logging.info(f'DOM: {dom}')
        items = dom.findall('channel/item')
        logging.info(f'Items: {items}')

        parsed_results = []
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
            parsed_results.append(dic)

        logging.info(f'Here is the results: \n {parsed_results}')

        return parsed_results


api = FuelWatch()
query = api.query()
api.get_raw_xml(query)
# query = api.query(product=1, region=5)
# pprint(query)
# a = next((item for item in query if float(item['price']) < 140))
# print(a)
# print(f'Total: {len(query)}'
#       f'Total < 140c: {len(a)}')
# resp = apr.parse(query)
