#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright � 2017 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its
# subsidiaries. Other trademarks may be trademarks of their respective owners.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Vaideeswaran Ganesan
#
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omsdk',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.9.1010',

    description='Dell EMC OpenManage(tm) Python SDK',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/vaideesg/omsdk',

    # Author details
    author='Vaideeswaran Ganesan',
    author_email='vaideeswaran_ganesan@dell.com',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='dellemc, dellemcsdk, idrac, cmc, OpenManage, PowerEdge, Dell',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[
        'omsdk', 'omsdktest',
        'omsdk.version',
        'omsdk.catalog',
        'omsdk.http',
        'omsdk.lifecycle',
        'omsdk.listener',
        'omsdk.profiling',
        'omsdk.reflection',
        'omsdk.typemgr',
        'omsdk.omlogs',
        'omsdk.simulator',
        'omdrivers',
        'omdrivers.lifecycle',
        'omdrivers.lifecycle.iDRAC',
        'omdrivers.lifecycle.F10',
        'omdrivers.enums',
        'omdrivers.enums.iDRAC',
        'omdrivers.helpers',
        'omdrivers.helpers.iDRAC',
        'omdrivers.types',
        'omdrivers.types.iDRAC',
    ],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_dir= {
        'omdrivers' : 'omdrivers',
        'omsdk' : 'omsdk'
    },
    package_data={
        'omdrivers': [
                'iDRAC/*.Monitor',
                'iDRAC/Config/*',
                'CMC/*.Monitor',
        ],
        'omsdk': [
                'omlogs/config/*',
        ],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },
)
