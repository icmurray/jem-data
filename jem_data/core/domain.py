# -*- coding: utf-8 -*-

"""
Definitions of domain models used by the system.
"""

import collections

Table = collections.namedtuple(
        'Table',
        'id label registers')

Device = collections.namedtuple(
        'Device',
        'gateway unit label tables')

Gateway = collections.namedtuple(
        'Gateway',
        'host port label')

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
