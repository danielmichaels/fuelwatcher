```
    ______           __               __       __
   / ____/_  _____  / /      ______ _/ /______/ /_  ___  _____
  / /_  / / / / _ \/ / | /| / / __ `/ __/ ___/ __ \/ _ \/ ___/
 / __/ / /_/ /  __/ /| |/ |/ / /_/ / /_/ /__/ / / /  __/ /
/_/    \__,_/\___/_/ |__/|__/\__,_/\__/\___/_/ /_/\___/_/
```

# Fuelwatcher

A simple python module that scrapes XML data from the government of Western Australia's FuelWatch website that makes parsing a breeze.

> Fuelwatch.wa.gov.au provides information on fuel prices by fuel type, location, brand and region within Western Australia.
> Fuelwatcher will parse the XML from the fuelwatch.wa.gov.au RSS feed giving the developer an easy way to manipulate the information.

## Installation

Requires `pip` to be installed or `pip3` dependent on system, or environment.

```sh
pip install fuelwatcher
```

## Usage example

### Basic Usage (Recommended)

The recommended way to access fuel station data is via the typed `stations` property, which returns a list of `FuelStation` dataclass instances:

```python
from fuelwatcher import FuelWatch

api = FuelWatch()

# Query the API
api.query(product=2, region=25, day='yesterday')

# Access stations as typed dataclass instances
for station in api.stations:
    print(f"{station.trading_name}: ${station.price}")
    print(f"  Address: {station.address}")
    print(f"  Location: {station.latitude}, {station.longitude}")
```

The `FuelStation` dataclass provides IDE autocomplete and type safety:

```python
from fuelwatcher import FuelStation

# FuelStation fields:
# - title, description, brand, date, price
# - trading_name, location, address, phone
# - latitude, longitude, site_features
```

### Alternative Access Methods

**As list of dictionaries:**

```python
api = FuelWatch()
api.query(region=1)

# Access as list of dicts
stations = api.xml
print(stations[0]['title'])
>>> '143.9: United Boulder Kalgoorlie'
```

**As JSON string:**

```python
api = FuelWatch()
api.query(region=1)

json_response = api.json
>>> [
>>>   {
>>>       "title": "143.9: United Boulder Kalgoorlie",
>>>       "description": "Address: Cnr Lane St & Davis St, BOULDER...",
>>>       "brand": "United",
>>>       ...
>>>   }
>>> ]
```

**Raw XML bytes:**

```python
api = FuelWatch()
api.query(product=1)

raw_xml = api.raw
>>> b'<?xml version="1.0" encoding="UTF-8"?>...'
```

### Query Parameters

The `query` method takes several keyword arguments:

```python
def query(
    product: int = None,      # Fuel type ID
    suburb: str = None,       # WA suburb name
    region: int = None,       # Region ID
    brand: int = None,        # Brand ID
    surrounding: bool = None, # Include surrounding suburbs
    day: str = None,          # 'today', 'tomorrow', 'yesterday', or 'DD/MM/YYYY'
)
```

A query without any arguments returns *all* of today's Unleaded stations in Western Australia.

**Notes:**

- If `suburb` is set, `surrounding` defaults to `yes`. To get only the suburb, explicitly pass `surrounding=False`
- Don't mix `region` with `suburb` and `surrounding` together
- The `surrounding` parameter accepts both `bool` (`True`/`False`) and `str` (`'yes'`/`'no'`)

A list of valid suburbs, brands, regions and products (fuel types) can be found in [constants.py](https://github.com/danielmichaels/fuelwatcher/blob/master/fuelwatcher/constants.py)

### Error Handling

Fuelwatcher validates inputs and raises `FuelWatchError` for invalid parameters or failed requests:

```python
from fuelwatcher import FuelWatch, FuelWatchError

api = FuelWatch()

try:
    api.query(product=999)  # Invalid product ID
except FuelWatchError as e:
    print(f"Error: {e}")
>>> Error: Invalid product ID: 999. Valid options: 1: Unleaded Petrol, 2: Premium Unleaded...
```

### Backwards Compatibility

The previous `get_*` property names are still supported but deprecated:

```python
# Deprecated (still works, emits DeprecationWarning)
api.get_xml    # Use api.xml instead
api.get_json   # Use api.json instead
api.get_raw    # Use api.raw instead
```

**Migration guide:**

| Old (deprecated) | New |
|------------------|-----|
| `api.get_xml` | `api.xml` or `api.stations` |
| `api.get_json` | `api.json` |
| `api.get_raw` | `api.raw` |
| `AssertionError` | `FuelWatchError` |
| `surrounding='yes'` | `surrounding=True` |

## Meta

Daniel Michaels – https://danielms.site

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
