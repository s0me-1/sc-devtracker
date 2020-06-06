#/usr/bin/env python
import codecs
import os
from setuptools import setup, find_packages


read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

pkgmeta = {
    '__title__': 'sc-devtracker',
    '__author__': 's0me-1',
    '__version__': '0.4',
    '__description__': "A Star Citizen RSS/Discord Webhook connector."
}


setup(
    name=pkgmeta['__title__'],
    description=pkgmeta['__description__'],
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.md')),
    version=pkgmeta['__version__'],
    author=pkgmeta['__author__'],
    url='https://github.com/s0me-1/sc-devtracker',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4', 'six', 'emoji', 'configparser', 'feedparser', 'requests'
    ],
)
