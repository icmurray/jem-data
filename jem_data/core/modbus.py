import logging

from twisted.internet import defer

_log = logging.getLogger(__name__)

def read_registers(client, unit, registers):
    '''Make a request for the given registers.

    Returns a Deferred which contains the result of the request.
    '''
    min_register = min(registers.keys())
    max_register = max(registers.keys())
    register_range = max_register + registers[max_register] - min_register

    if register_range > 125:
        return defer.fail(ValueError('Unable to create request of such a '
                                     'large range'))

    # The `- 1` is because the registers are *named* [1..n], but when making
    # a request they are reference as [0,n)
    d = client.read_input_registers(min_register - 1,
                                    register_range,
                                    unit=unit)

    # Map the result of the deferred to a more manageable response type.
    map_to_register_response(d, registers)

    return d

class RegisterResponse(object):
    '''Provides easier access to a request for a sparse array of registers.'''

    def __init__(self, pymodbus_response, requested_registers):
        self._requested_registers = requested_registers
        self._response = pymodbus_response
        self._min_addr = min(self._requested_registers.keys())

    def __str__(self):
        return str(dict( (addr, self.read_register(addr)) for addr in self._requested_registers.keys() ))

    def read_register(self, addr):
        assert addr in self._requested_registers
        values = [ self._response.getRegister(addr + i - self._min_addr) \
                        for i in range(self._requested_registers[addr]) ]
        return reduce(lambda acc, x: (acc << 16) + x, values, 0)

def map_to_register_response(d, requested_registers):
    def _f(response):
        return RegisterResponse(response, requested_registers)
    d.addCallback(_f)
