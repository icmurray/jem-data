"""Measure performance characteristics of a given Dirus gateway.

Usage:
    performance.py [options]

Options
    --host=<host>       server host [default: 127.0.0.1]
    --port=<port>       server port [default: 5020]

"""
import collections
import logging
import random
import time

import docopt

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus

logging.basicConfig()
_log = logging.getLogger()
_log.setLevel(logging.INFO)

_REGISTERS = dict((addr, 2) for addr in range(0xC550, 0xC588, 2))
_MAX_NUMBER_OF_REGISTERS = len(_REGISTERS.keys())
_MIN_NUMBER_OF_REGISTERS = min(10, _MAX_NUMBER_OF_REGISTERS)

Measurement = collections.namedtuple('Measurement',
                                     'elapsed_time')

def _choose_random_registers():
    num_registers = random.randint(_MIN_NUMBER_OF_REGISTERS,
                                   _MAX_NUMBER_OF_REGISTERS)
    return random.sample(_REGISTERS.keys(), num_registers)

def _make_random_request(client):
    unit = 0x01
    registers = dict( (addr, 2) for addr in _choose_random_registers())
    start = time.time()
    response = modbus.read_registers(client, registers=registers, unit=unit)
    elapsed_time = time.time() - start
    #print response
    return Measurement(elapsed_time=elapsed_time)

def _benchmark(host, port, N=100, delay=0.1):
    client = ModbusClient(host, port=port)
    client.connect()

    measurements = []
    
    for i in xrange(N):
        measurements.append(_make_random_request(client))
        #time.sleep(delay)

    client.close()

    print sum(map(lambda m: m.elapsed_time, measurements)) / len(measurements)

def _validate_args(raw_args):
    args = {}
    args['host'] = raw_args['--host']
    args['port'] = raw_args['--port']
    return args

def main(host, port):
    _benchmark(host, port)

if __name__ == '__main__':
    args = _validate_args(docopt.docopt(__doc__))
    main(**args)
