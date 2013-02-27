import logging
import time

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

client = ModbusClient('localhost', port=5020)
client.connect()

interested_registers = {
        0xC550: 2,
        0xC560: 2,
        0xC562: 2,
        0xC564: 2,
}

units = range(0x20)

while True:

    for unit in units:

        response = modbus.read_registers(client,
                                         registers=interested_registers,
                                         unit=unit)

        for addr in interested_registers:
            print "[%x] %x : %d" % (unit, addr, response.read_register(addr))

    time.sleep(0.1)
client.close()
