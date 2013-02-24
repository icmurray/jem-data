import pymodbus.datastore as datastore

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
           0xC550: 0x1234ABCD
        })
    )

_CT_AND_VT_REGISTERS = dict((addr, 2) for addr in range(0xC550, 0xC588, 2))
_ALL_REGISTERS = _CT_AND_VT_REGISTERS

class A40InputRegistersDataBlock(datastore.ModbusSparseDataBlock):

    def __init__(self, values=None):
        if values is None:
            values = {}
        assert set(values.keys()) <= set(_ALL_REGISTERS.keys())

        expanded_values = {}
        addrs = _ALL_REGISTERS.keys()
        for d in ( self._expand_register_value(addr, values.get(addr, 0)) \
                        for addr in addrs ):
            expanded_values.update(d)

        super(A40InputRegistersDataBlock, self).__init__(expanded_values)

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
