"""Measure performance characteristics of a given Dirus gateway.

Usage:
    performance.py [--host=<host>]
                   [--port=<port>]
                   [--unit=<unit>]...
                   [--requests=<requests>]
                   [--delay=<delay>]...

Options
    --hostE<host>           server host [default: 127.0.0.1]
    --port=<port>           server port [default: 5020]
    --unit=<unit>...        units to test against [default: 0x1]
    --requests=<requests>   requests to make (per client)
    --delay=<delay>         a delay between requests (per client)
                            [default: 0.001, 0.01, 0.1]

"""
import collections
import logging
import Queue
import random
import threading
import time

import docopt

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus
import jem_data.core.exceptions as jem_exceptions

logging.basicConfig()
_log = logging.getLogger()
_log.setLevel(logging.INFO)

_REGISTERS = dict((addr, 2) for addr in range(0xC550, 0xC588, 2))
_MAX_NUMBER_OF_REGISTERS = len(_REGISTERS.keys())
_MIN_NUMBER_OF_REGISTERS = min(10, _MAX_NUMBER_OF_REGISTERS)

ClientMeasurements = collections.namedtuple(
    'ClientMeasurements', 'client_id measurements errors')
        
Result = collections.namedtuple('Result',
                                'concurrency client_id measurements errors')

def _choose_random_registers():
    num_registers = random.randint(_MIN_NUMBER_OF_REGISTERS,
                                   _MAX_NUMBER_OF_REGISTERS)
    return random.sample(_REGISTERS.keys(), num_registers)

def _make_random_request(client, units):
    unit = random.sample(units, 1)[0]
    registers = dict( (addr, 2) for addr in _choose_random_registers())
    start = time.time()
    response = modbus.read_registers(client, registers=registers, unit=unit)
    elapsed_time = time.time() - start
    #print response
    return elapsed_time

def _run_single_client(client_id, host, port, units, results, N, delay):
    client = ModbusClient(host, port=port)
    client.connect()

    _log.info('Client %d connected to %s (%s)', client_id, host, port)

    measurements = []
    errors = []
    for i in xrange(N):
        if N >= 1000 and i % (N/10) == 0 and i > 0:
            _log.info('Client %d %.0f%% complete', client_id, 100.0*i/N)
        try:
            measurements.append(_make_random_request(client, units))
        except jem_exceptions.JemException, e:
            errors.append(e)
            _log.warn('Client %d received error response: %s', client_id, e)
        finally:
            time.sleep(delay)

    client.close()
    _log.info('Client %d closed connection', client_id)
    results.put(ClientMeasurements(client_id=client_id,
                                   measurements=measurements,
                                   errors=errors))

def _benchmark_server(host, port, units, requests, delays):
    results = []
    for concurrency in xrange(1,5):
        _log.info('Starting benchmarking at concurrency level %d', concurrency)

        for delay in delays:
            _log.info('Starting benchmarking with delay %f', delay)

            client_results = Queue.Queue()
            ts = []
            for client_id in range(concurrency):
                args = (client_id, host, port, units, client_results, requests, delay)
                t = threading.Thread(target=_run_single_client, args = args)
                ts.append(t)
                t.start()

            for t in ts:
                t.join()

            while not client_results.empty():
                result = client_results.get()
                results.append(Result(
                    concurrency = concurrency,
                    client_id = result.client_id,
                    measurements = result.measurements,
                    errors = result.errors))

    return results

def _print_results(results):
    for result in results:
        print '[%d] Client %d: avg. response time %f' % (
                result.concurrency,
                result.client_id,
                sum(result.measurements) / len(result.measurements))

def _from_hex_string(s):
    return int(s, 16)

def _validate_args(raw_args):
    args = {}
    args['host'] = raw_args['--host']
    args['port'] = raw_args['--port']
    args['units'] = map(_from_hex_string, raw_args['--unit'])
    args['requests'] = int(raw_args['--requests'])
    args['delays'] = map(float, raw_args['--delay'])
    return args

def main(host, port, units, requests, delays):
    results = _benchmark_server(host, port, units, requests, delays)
    _print_results(results)

if __name__ == '__main__':
    args = _validate_args(docopt.docopt(__doc__))
    main(**args)
