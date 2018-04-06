"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    // ABOVE ONLY FOR TESTING
$ twine upload dist/*
"""

from codecs import open
from setuptools import setup
from os import path

__VERSION__ = '0.1.0rc3'
__URL__ = 'https://github.com/danielmichaels/fuelwatcher'
__DOWNLOAD_URL__ = (__URL__ + '/tarball/' + __VERSION__)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fuelwatcher',
    packages=['fuelwatcher'],
    version=__VERSION__,
    description='A simple XML scraper for FuelWatch.wa.gov.au fuel prices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Daniel Michaels',
    author_email='dans.address@outlook.com',
    url=__URL__,
    download_url=__DOWNLOAD_URL__,
    keywords=['fuelwatch', 'western australia', 'fuel watch rss'],
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6', ]
)
