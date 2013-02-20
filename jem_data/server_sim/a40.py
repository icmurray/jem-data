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
        ir = datastore.ModbusSequentialDataBlock(0xC550, [15]*100)
    )
