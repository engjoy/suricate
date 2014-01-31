#!/usr/bin/env python

# coding=utf-8

"""
Runs an execution node.
"""

import sys

import ConfigParser

from analytics import exec_node

__author__ = 'tmetsch'

config = ConfigParser.RawConfigParser()
config.read('app.conf')
# MongoDB connection
mongo = config.get('mongo', 'uri')
# Rabbit part
broker = config.get('rabbit', 'uri')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise AttributeError('please provide a tenant id for this execution '
                             'node as first argument!')

    user = sys.argv[1]
    pwd = sys.argv[2]
    exec_node.ExecNode(mongo, broker, user, pwd)
