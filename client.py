from twisted.internet import reactor, protocol

from pymodbus.client.async import ModbusClientProtocol

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
    rr = client.read_input_registers(0xc550,8,unit=0x01)
    dassert(rr, lambda r: r.registers == [15]*8)      # test the expected value

    #-----------------------------------------------------------------------# 
    # close the client at some time later
    #-----------------------------------------------------------------------# 
    reactor.callLater(1, client.transport.loseConnection)
    reactor.callLater(2, reactor.stop)

defer = protocol.ClientCreator(reactor, ModbusClientProtocol
        ).connectTCP("localhost", 5020)
defer.addCallback(beginAsynchronousTest)
reactor.run()
