import logging

from twisted.internet import defer

import jem_data.core.response as response

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
    response.map_to_register_response(d, registers)

    return d
