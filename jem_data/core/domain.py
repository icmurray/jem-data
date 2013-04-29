# -*- coding: utf-8 -*-

"""
Definitions of domain models used by the system.
"""

import collections

Device = collections.namedtuple(
        'Device',
        'gateway unit')

Gateway = collections.namedtuple(
        'Gateway',
        'host port')
