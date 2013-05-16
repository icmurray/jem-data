# -*- coding: utf-8 -*-

"""
Definitions of messages passed around the system.
"""

import collections

ReadTableMsg = collections.namedtuple(
        'ReadTableMsg',
        'table_addr')

ResponseMsg = collections.namedtuple(
        'ResponseMsg',
        'table_addr values timing_info error request_info')
