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

ConfiguredGateway = collections.namedtuple(
        'ConfiguredGateway',
        'host port configured_devices')

ConfiguredDevice = collections.namedtuple(
        'ConfiguredDevice',
        'unit table_ids')

Recording = collections.namedtuple(
        'Recording',
        'id status configured_gateways start_time end_time')

class TimingInfo(collections.namedtuple('TimingInfo', 'start end')):
    __slots__ = ()

    @property
    def elapsed_time(self):
        self.end - self.start
