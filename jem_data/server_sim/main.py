import logging

from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async import StartTcpServer

import a40

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

slaves = {
    0x01: a40.create(),
    0x02: a40.create(),
    0x03: a40.create()
}

context = ModbusServerContext(slaves=slaves, single=False)

identity = ModbusDeviceIdentification()
identity.VendorName  = 'Socomec'
identity.ProductName = 'Dirus'
identity.ModelName   = 'A40'

StartTcpServer(context, identity=identity, address=("localhost", 5020))
