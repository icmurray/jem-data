# -*- coding: utf-8 -*-

"""
Definitions of messages passed around the system.
"""

import collections

ReadTableMsg = collections.namedtuple(
        'ReadTableMsg',
        'table_id')

ResponseMsg = collections.namedtuple(
        'ResponseMsg',
        'table_id values timing_info error request_info')
