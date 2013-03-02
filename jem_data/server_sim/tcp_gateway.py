import logging

from pymodbus.transaction import ModbusSocketFramer
from pymodbus.server.async import ModbusServerFactory
from pymodbus.internal.ptwisted import InstallManagementConsole

_log = logging.getLogger(__name__)

def start(context, identity=None, address=None, console=False):
    ''' Helper method to start the Modbus Async TCP server

    :param context: The server data context
    :param identify: The server identity to use (default empty)
    :param address: An optional (interface, port) to bind to.
    :param console: A flag indicating if you want the debug console
    '''
    from twisted.internet import reactor

    address = address or ("", 502)
    framer  = ModbusSocketFramer
    factory = ModbusServerFactory(context, framer, identity)
    if console: InstallManagementConsole({'factory': factory})

    _log.info("Starting Modbus TCP Server on %s:%s" % address)
    reactor.listenTCP(address[1], factory, interface=address[0])
    reactor.run()
