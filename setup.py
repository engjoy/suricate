#!/usr/bin/env python
# coding=utf-8

"""
Setuptools file.
"""

__author__ = 'tmetsch'

from distutils.core import setup

setup(name='suricate',
      version='1.0',
      description='Analytics Service',
      author='Thijs Metsch',
      author_email='tmetsch@engjoy.eu',
      url='http://www.engjoy.eu',
      packages=['suricate.ui', 'suricate.data', 'suricate.analytics'],
      # for prod also requires whatever you put in sdk.
      requires=['bottle', 'pymongo', 'matplotlib', 'pika', 'mox'])