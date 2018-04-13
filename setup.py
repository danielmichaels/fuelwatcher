"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.p sdist
$ twine upload -r testpypi dist/*
    // ABOVE ONLY FOR TESTING
$ twine upload -r pypi dist/*
"""

from codecs import open
from setuptools import setup, find_packages
from os import path

NAME = 'fuelwatcher'
VERSION = '0.2.0'
DESCRIPTION = 'A simple XML scraper for FuelWatch.wa.gov.au fuel prices',
URL = 'https://github.com/danielmichaels/fuelwatcher'
DOWNLOAD_URL = (URL + '/tarball/' + VERSION)
AUTHOR = 'Daniel Michaels'
AUTHOR_EMAIL = 'dans.address@outlook.com'
REQUIRES_PYTHON = '>= Python 3.5'

# Include what dependancies it requires:
REQUIRED = [
    'requests'
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    packages=find_packages(exclude=('tests')),
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
