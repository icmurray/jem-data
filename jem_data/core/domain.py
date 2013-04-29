# -*- coding: utf-8 -*-

"""
Definitions of domain models used by the system.
"""

import collections

DeviceId = collections.namedtuple(
        'DeviceId',
        'gateway_id unit')

