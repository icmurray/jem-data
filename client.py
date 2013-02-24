from twisted.internet import reactor, protocol

from pymodbus.client.async import ModbusClientProtocol

from jem_data.core import requests
from jem_data.core import util

#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------# 
# helper method to test deferred callbacks
#---------------------------------------------------------------------------# 
def dassert(deferred, callback):
    def _assertor(value): assert(value)
    def _print_and_assert(r):
        print r
        _assertor(callback(r))
    def _print_and_fail(r):
        print r
        _assertor(False)
    deferred.addCallback(lambda r: _print_and_assert(r))
    deferred.addErrback(lambda  r: _print_and_fail(r))

def beginAsynchronousTest(client):

    registers = {
            0xC550: 2,
            0xC552: 2,
            0xC560: 2,
    }

    responseD = requests.read_registers(client, unit=0x01, registers=registers)
    responseD.addCallback(util.print_data)

    #-----------------------------------------------------------------------# 
    # close the client at some time later
    #-----------------------------------------------------------------------# 
    reactor.callLater(1, client.transport.loseConnection)
    reactor.callLater(2, reactor.stop)

defer = protocol.ClientCreator(reactor, ModbusClientProtocol
        ).connectTCP("localhost", 5020)
defer.addCallback(beginAsynchronousTest)
reactor.run()
