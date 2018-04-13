```
    ______           __               __       __             
   / ____/_  _____  / /      ______ _/ /______/ /_  ___  _____
  / /_  / / / / _ \/ / | /| / / __ `/ __/ ___/ __ \/ _ \/ ___/
 / __/ / /_/ /  __/ /| |/ |/ / /_/ / /_/ /__/ / / /  __/ /    
/_/    \__,_/\___/_/ |__/|__/\__,_/\__/\___/_/ /_/\___/_/     v 0.2.0
```

# Fuelwatcher

A simple python module that scrapes XML data from the government of Western Australia's FuelWatch initiative website making parsing a breeze.

>Fuelwatch.wa.gov.au provides information on fuel prices by fuel type, location, brand and region within Western Australia. 
> Fuelwatcher will parse the XML from the fuelwatch.wa.gov.au RSS feed giving the developer an easy way to manipulate the information.

## Installation

Requires `pip` to be installed or `pip3` dependant on system, or environment. 

**Python 3 only**

```sh
pip install fuelwatcher
```

## Usage example

### Basic Usage

```python
from fuelwatch import FuelWatch

api = FuelWatch()

api.query(product=2, region=25, day='yesterday')
# returns byte string of xml.
xml_query = api.get_xml
# iterates over each fuel station entry in the byte string
# and returns list of dictionaries in human readable text.

print(parsed_query)

>>>> [{'title': '138.5: Puma Bayswater', 'description': 'Address: 502 Guildford Rd, BAYSWATER, Phone: (08) 9379 1322, Open 24 hours', 'brand': 'Puma', 'date': '2018-04-05', 'price': '138.5', 'trading-name': 'Puma Bayswater', 'location': 'BAYSWATER', 'address': '502 Guildford Rd', 'phone': '(08) 9379 1322', 'latitude': '-31.919556', 'longitude': '115.929069', 'site-features': ', Open 24 hours'} ..snip.. ]
```

Fuelwatcher can also transform the XML into JSON format. It is as simple as calling the `get_json` method.

```python

api = FuelWatch()

api.query(region=1)

json_response = api.get_json

>>>> [
>>>>   {
>>>>       "title": "143.9: United Boulder Kalgoorlie",
>>>>       "description": "Address: Cnr Lane St & Davis St, BOULDER, Phone: (08) 9093 1543",
>>>>       "brand": "United",
>>>>       "date": "2018-04-13",
>>>>       "price": "143.9",
>>>>       ... snip ...
>>>>       "longitude": "121.433746",
>>>>       "site-features": "Unmanned Station, "
>>>>   }
>>>> ]
```

For most operations the `get_xml()` or `get_json()` method will be sufficient. If the developer wants to parse the raw RSS XML then the `get_raw()` method is available.

```python
get_raw = api.get_raw

print(get_raw)

>>>> (b'<?xml version="1.0" encoding="UTF-8"?>\r\n<rss version="2.0"><channel><title>FuelWatch Prices For North of River</title><ttl>720</ttl><link>http://www.fuelwatch.wa.gov.au</link><description>05/04/2018 - North of River</description><language>en-us</language><copyright>Copyright 2005 FuelWatch... snip...</item></channel></rss>\r\n')
```

The query method takes several keyword arguments. By defaults it will return every fuel station across Western Australia.

As guide query takes the following kwargs

```python
def query(self, product: int = None, suburb: str = None, region: int = None, 
            brand: int = None, surrounding: str = None, day: str = None):
```

Of importance if `suburb` is set, then `surrounding` can set to `no` or left as `None`; it defaults to `yes` at the API endpoint. Setting `region` with `suburb` and `surrounding` will have unexpected results and is best left to their default settings.

Simply put, if you want just one `suburb` then set `surrounding='no'` else leave the default. Only one `suburb` can be set per query. If a `region` is selected, do not set `surrounding` or `suburb`

Doesn't make sense? Try this table.

PARAMETERS | OPTION 1 | OPTION 2
-----------|----------|---------
suburb | Y | N
region | N | Y
surrounding | Y or N | N
product | Y | Y
brand | Y | Y
day | Y | Y

A list of valid suburbs, brands, regions and products (fuel types) can be found in [constants.py](https://github.com/danielmichaels/fuelwatcher/blob/master/fuelwatcher/constants.py) 

Fuelwatcher will run validation on the `query` method and throw AssertionError is an invalid integer or string is input

```python
api.query(product=20) # product=20 is invalid

>>> .... error snippet....
>>> AssertionError: Invalid Product Integer.
```

## Release History

* 0.2.0
    * __Braking Change!__
    * @property added raw, xml and json methods
    * json output now supported
* 0.1.1
    * Include correct packages in setup.py
* 0.1.0
    * First release live to PyPi
* 0.1.0rc2
    * Minor formatting fixes
* 0.1.0rc1
    * The first release candidate
* 0.0.1
    * Work in progress

## Meta

Daniel Michaels – https://www.danielms.site

Distributed under the MIT license. See ``LICENSE`` for more information.

## Contributing

All requests, ideas or improvements are welcomed!

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Inspired by..

A local python meetup group idea that turned into a PyPi package for anyone to use!

<!-- Markdown link & img dfn's -->