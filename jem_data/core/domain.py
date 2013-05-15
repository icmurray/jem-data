# -*- coding: utf-8 -*-

"""
Definitions of domain models used by the system.
"""

import collections

#-----------------------------------------------------------------------------
# DeviceAddr and GatewayAddr model the minimum maount of information to be able
# to send a request to some device.  They are used in the message-passing part
# of the system, and are structured so that knowing a Device, one can find
# its Gateway.
#-----------------------------------------------------------------------------

TableAddr = collections.namedtuple(
        'TableAddr',
        'device_addr id')

DeviceAddr = collections.namedtuple(
        'DeviceAddr',
        'gateway_addr unit')

GatewayAddr = collections.namedtuple(
        'GatewayAddr',
        'host port')

#-----------------------------------------------------------------------------
# Gateway and Device are a super-set (*) of the above *Id data models.  They
# hold data pertaining to the configuration of a system.  They're structured
# in such a way that the Gateway is the root of a graph of domain models
# containing, amongst other things, the devices attached to each Gateway.
#
# (*) A GatewayAddr and list of DeviceAddrs can be derived from a Gateway, but
#     the relationships between the objects go in the other direction - ie
#     top-down as opposed to bottom-up.  This is because of the different
#     use-case of these richer objects.
#-----------------------------------------------------------------------------

Register = collections.namedtuple(
        'Register',
        'address label range')

Table = collections.namedtuple(
        'Table',
        'id label registers')

Device = collections.namedtuple(
        'Device',
        'unit label type tables')

Gateway = collections.namedtuple(
        'Gateway',
        'host port label devices')

Recording = collections.namedtuple(
        'Recording',
        'id status gateways start_time end_time')

class TimingInfo(collections.namedtuple('TimingInfo', 'start end')):
    __slots__ = ()

    @property
    def elapsed_time(self):
        self.end - self.start
