import logging

from twisted.internet import defer

import pymodbus.pdu as pdu

import jem_data.core.exceptions as jem_exceptions

_log = logging.getLogger(__name__)

_VALID_REGISTER_RANGE = 125

def read_registers(client, unit, registers):
    '''Make a request for the given registers.

    :param client: the pymodbus client to send the request to.
    :param unit: the unit identifier if the client is a gateway.
    :param registers: a dict of register addresses to register value widths

    When using this function, you should address the registers as they are
    named on the device (and therefore in the device's specification), rather
    than the 0-indexed naming required by the modbus request message.  (Modbus
    defines the addresses to the 1-indexed when naming them on the device, but
    when constructing a modbus request, they need to be 0-indexed.  This
    function handles the 1-indexed form, in order to keep the interface
    uniform).

    The registers on the device may actually be wider than 1 register value.
    For example, the register named `0xC550` may actually have a value that
    is 32 bits wide.  This means the lower half of the value is stored in
    register `0xC551`.  And the next "meaningful" register address would be
    `0xC552`.  That is what the `registers` param is used for: the width of
    the register values can be specified, and this function will ensure that
    the correct range of registers is requested.  And will also (upon success)
    return the response in the form of a `RegisterResponse` object which
    will transparently read the required number of register values in order to
    contruct the composite value -- ie in the example above, when asked for
    the value of the register named `0xC550`, the response will transparently
    also read the value in `0xC551` and combine the two values.

    Returns a Deferred which contains the result of the request.
    '''

    if not registers:
        raise ValueError("Cannot request empty set of registers")

    if not isinstance(registers, dict):
        raise TypeError("registers argument must be a dict")

    min_register = min(registers.keys())
    max_register = max(registers.keys())
    register_range = max_register + registers[max_register] - min_register

    if register_range > _VALID_REGISTER_RANGE:
        raise InvalidModbusRangeException(register_range)

    # NOTE - the modbus PDU expects that requests for registers addressed as
    #        1 - 16 to be requested as 0 - 15.  This means that the first
    #        address below *should* be `min_register - 1`.  However, the
    #        Dirus A40 still expects the addresses 1 - 15.  This means that
    #        the following request is incorrect for any device that is not
    #        a Dirus A40.
    _log.debug('read_holding_registers: %x -> %x from %s [unit: %x]',
               min_register,
               min_register - 1 + register_range,
               str(client),
               unit)
    response = client.read_holding_registers(min_register,
                                             register_range,
                                             unit=unit)

    if isinstance(response, defer.Deferred):
        def callback(data):
            return RegisterResponse(data, registers)
        response.addCallback(callback)

    elif isinstance(response, pdu.ExceptionResponse):
        raise jem_exceptions._wrap_exception_response(response)

    else:
        response = RegisterResponse(response, registers)
    
    return response

def split_registers(registers):
    """
    Splits the given registers into multiple register dicts which all have
    a valid modbus register range (of <= 125).
    """

    for width in registers.values():
        if width > _VALID_REGISTER_RANGE:
            raise ValueError("Invalid register width: %d" % width)

    working_copy = registers.copy()
    valid_registers = []

    current_range_start = min(working_copy.keys())
    current_range_end   = current_range_start + _VALID_REGISTER_RANGE

    while working_copy:
        current_range = dict(
            (addr, width) for addr, width in working_copy.items() \
                if current_range_start <= addr and \
                   addr + width <= current_range_end
        )

        valid_registers.append(current_range)
        for addr in current_range:
            working_copy.pop(addr)

        if working_copy:
            current_range_start = min(working_copy.keys())
            current_range_end   = current_range_start + _VALID_REGISTER_RANGE

    return valid_registers


class RegisterResponse(object):
    '''Wraps a pymodbus response object to provide access to the registers
    with values more than 1 register wide.

    For example, it may be that the register named `0xC550` is actually stored
    across `0xC550` *and* `0xC551` on the device.  Knowing this, this response
    class can, when asked for the value of the register named `0xC550`,
    combine the two values.

    The most significant bytes are assumed to be stored in the lower address.
    '''

    def __init__(self, pymodbus_response, requested_registers):
        self._requested_registers = requested_registers
        self._response = pymodbus_response
        self._min_addr = min(self._requested_registers.keys())

    def read_register(self, addr):
        if addr not in self._requested_registers:
            raise IndexError('Unknown register address: %x' % addr)

        values = [ self._response.getRegister(addr + i - self._min_addr) \
                        for i in range(self._requested_registers[addr]) ]

        return reduce(lambda acc, x: (acc << 16) + x, values, 0)

#-----------------------------------------------------------------------------
# Exception definitions
#-----------------------------------------------------------------------------

class InvalidModbusRangeException(jem_exceptions.JemException):
    def __init__(self, range_size):
        super(InvalidModbusRangeException, self).__init__(
                'Modbus range too large: %d' % range_size)
