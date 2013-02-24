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
        value = reduce(lambda acc, x: (acc << 16) + x, values, 0)
        return value

def map_to_register_response(d, requested_registers):
    def _f(response):
        return RegisterResponse(response, requested_registers)
    d.addCallback(_f)
