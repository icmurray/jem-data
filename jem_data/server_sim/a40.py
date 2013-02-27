import math
import logging
import time

import pymodbus.datastore as datastore

_log = logging.getLogger(__name__)

# Some of the registers that we simulate
_HOUR_METER = 0xC550
_PHASE_CURRENT_1 = 0xC560
_PHASE_CURRENT_2 = 0xC562
_PHASE_CURRENT_3 = 0xC564

def create():
    '''Create a new A40 slave

    For the timebeing this is just a stub.  But it does start the input registers
    at the correct address.
    '''
    return datastore.ModbusSlaveContext(
        di = datastore.ModbusSequentialDataBlock(0, [1]),
        co = datastore.ModbusSequentialDataBlock(0, [1]),
        hr = datastore.ModbusSequentialDataBlock(0, [1]),
        ir = A40InputRegistersDataBlock({
           _HOUR_METER: 0x0,
           _PHASE_CURRENT_1: 0x0,
           _PHASE_CURRENT_2: 0x0,
           _PHASE_CURRENT_3: 0x0,
        })
    )

_CT_AND_VT_REGISTERS = dict((addr, 2) for addr in range(0xC550, 0xC588, 2))
_ALL_REGISTERS = _CT_AND_VT_REGISTERS

class A40InputRegistersDataBlock(datastore.ModbusSparseDataBlock):
    '''A simulated datablock of registers for the Diris A40.

    A convenient subclass of a sparse data block, this transparantly handles
    the A40's multi-word registers upon initialization.

    It also dynamically updates its values using the twisted reactor.
    '''


    def __init__(self, values=None, dynamic=True):
        if values is None:
            values = {}
        assert set(values.keys()) <= set(_ALL_REGISTERS.keys())

        expanded_values = {}
        addrs = _ALL_REGISTERS.keys()
        for d in ( self._expand_register_value(addr, values.get(addr, 0)) \
                        for addr in addrs ):
            expanded_values.update(d)

        super(A40InputRegistersDataBlock, self).__init__(expanded_values)

        if dynamic:
            _log.debug("A40 Register Block initialised with dynamic updating")
            from twisted.internet import task
            self._start_time = time.time()
            l = task.LoopingCall(self._step)
            l.start(0.1)     # in seconds.

    def _expand_register_value(self, addr, value):
        '''Returns a dict of register addresses to register values.

        A40 registers can have register values greater than 2 bytes.  In which
        case the value is split across contiguous registers.

        This function takes a register address; looks up how wide it expects the
        value to be; and returns a mapping of register addresses to values.
        '''
        assert addr in _ALL_REGISTERS
        width = _ALL_REGISTERS[addr]
        assert width * 16 >= value.bit_length()
        mask = 0xFFFF

        to_return = {}
        for i in range(0,width):
            shift = i*16
            to_return[addr + width - i - 1] = (value & (mask << shift)) >> shift

        return to_return

    def _step(self):
        '''Step to the next set of values in this simulated datablock'''
        elapsed_time = time.time() - self._start_time
        
        # The A40 updates its hour meter every 1/100-th of an hour, ie
        # every 36 seconds.
        diris_time = int(elapsed_time / 36.0)
        self.setValues(_HOUR_METER, self._expand_register_value(_HOUR_METER, diris_time))
        
        self._update_sinusoidal_register(_PHASE_CURRENT_1, 240.0, 0.20, elapsed_time)
        self._update_sinusoidal_register(_PHASE_CURRENT_2, 120.0, 0.60, elapsed_time)
        self._update_sinusoidal_register(_PHASE_CURRENT_3, 100.0, 0.80, elapsed_time)

    def _update_sinusoidal_register(self, addr, amplitude, frequency, now):
        v = int(amplitude * math.sin(2.0 * math.pi * frequency * now) * 100.0) + int(amplitude * 100.0)
        self.setValues(addr, self._expand_register_value(addr, v))
