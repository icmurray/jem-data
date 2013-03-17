"""Measure performance characteristics of a given Dirus gateway.

Usage:
    performance.py [--host=<host>]
                   [--port=<port>]
                   [--unit=<unit>]...
                   [--requests=<requests>]
                   [--delay=<delay>]...
                   [--with-throughput]
                   [--warmup=<warmup>]
                   [--target-dir=<target-dir>]

Options
    --host=<host>               server host [default: 127.0.0.1]
    --port=<port>               server port [default: 5020]
    --unit=<unit>...            units to test against [default: 0x1]
    --requests=<requests>       requests to make (per client)
                                [default: 1000]
    --delay=<delay>             a delay between requests (per client)
                                [default: 0 0.001 0.01 0.1]
    --with-throughput           record throughput -- runs a test with delay of 0
    --warmup=<warmup>           perform this numbe of requests before starting
                                to record response times.
                                [default: 500]
    --target-dir=<target-dir>   directory to write result files to
                                [default: ./results]

"""
import csv
import collections
import logging
import os
import Queue
import random
import sys
import threading
import time

import docopt

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus
import jem_data.core.exceptions as jem_exceptions

logging.basicConfig()
_log = logging.getLogger()
_log.setLevel(logging.INFO)

_REGISTERS = dict((addr, 2) for addr in range(0xC950, 51656, 1))
#_REGISTERS = dict((addr, 2) for addr in range(0xC550, 0xC588, 2))
_MAX_NUMBER_OF_REGISTERS = min(120, len(_REGISTERS.keys()))
_MIN_NUMBER_OF_REGISTERS = 120
#_MIN_NUMBER_OF_REGISTERS = min(_MAX_NUMBER_OF_REGISTERS, _MAX_NUMBER_OF_REGISTERS)

ClientMeasurements = collections.namedtuple(
    'ClientMeasurements', 'client_id measurements errors')
        
BenchmarkResult = collections.namedtuple(
    'BenchmarkResult', 'concurrency delay client_measurements total_time')

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
    return elapsed_time

def _run_single_client(client_id, host, port, units, results, N, delay, warmup):
    _log.info('Client %d connecting to %s (%s)', client_id, host, port)
    client = ModbusClient(host, port=port)
    client.connect()

    _log.info('Client %d connected to %s (%s)', client_id, host, port)

    measurements = []
    errors = []
    for i in xrange(N):
        if N >= 1000 and i % (N/10) == 0 and i > 0:
            _log.info('Client %d %.0f%% complete', client_id, 100.0*i/N)
        try:
            m = _make_random_request(client, units)
            if i >= warmup or N <= warmup:
                if i == warmup:
                    _log.info('Client %d warmup complete.', client_id)
                measurements.append(m)
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

def _benchmark_server(host, port, units, requests, delays, warmup):
    results = []
    for concurrency in xrange(1,5):
        _log.info('Starting benchmarking at concurrency level %d', concurrency)

        for delay in delays:
            _log.info('Starting benchmarking with delay %f', delay)

            client_results = Queue.Queue()
            ts = []
            for client_id in range(concurrency):
                args = (client_id,
                        host,
                        port,
                        units,
                        client_results,
                        requests,
                        delay,
                        warmup)
                t = threading.Thread(target=_run_single_client, args = args)
                ts.append(t)

            start = time.time()
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            total_time = time.time() - start

            client_measurements = []
            while not client_results.empty():
                client_measurements.append(client_results.get())

            results.append(BenchmarkResult(
                concurrency = concurrency,
                delay = delay,
                client_measurements = client_measurements,
                total_time = total_time))

    return results

def _write_results(results, target_dir):

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    time_string = time.strftime("%Y-%m-%d %H:%M:%S.csv", time.localtime())
    filename = "response_times " + time_string
    filepath = os.path.join(target_dir, filename)
    f_out = open(filepath, 'wb')
    csv_out = csv.writer(f_out)
    _log.info("Writing results to %s", filepath)
    csv_out.writerow(['delay', 'concurrency level', 'response time']) # header
    for result in results:
        ms = _get_all_measurements(result)
        for m in ms:
            row = [result.delay, result.concurrency, m]
            csv_out.writerow(row)
    f_out.flush()
    f_out.close()

    filename = "throughput " + time_string
    filepath = os.path.join(target_dir, filename)
    f_out = open(filepath, 'wb')
    csv_out = csv.writer(f_out)
    _log.info("Writing results to %s", filepath)
    csv_out.writerow(['delay', 'concurrency level', 'throughput']) # header
    for result in results:
        ms = _get_all_measurements(result)
        errors = _get_all_errors(result)
        throughput = (len(ms) + len(errors)) / result.total_time
        row = [result.delay, result.concurrency, throughput]
        csv_out.writerow(row)
    f_out.flush()
    f_out.close()

def _get_all_measurements(result):
    measurements = []
    for m in result.client_measurements:
        measurements.extend(m.measurements)
    return measurements

def _get_all_errors(result):
    errors = []
    for m in result.client_measurements:
        errors.extend(m.errors)
    return errors

def _print_results(results):
    print "******* RESULTS ********"
    for result in results:

        measurements = _get_all_measurements(result)
        errors = _get_all_errors(result)

        print('Concurrency: %d; delay: %f; Avg response time: %f, Throughput: %f/sec, Number of errors: %d' % (
                result.concurrency,
                result.delay,
                sum(measurements) / len(measurements),
                (len(measurements) + len(errors)) / result.total_time,
                len(errors)))

def _from_hex_string(s):
    return int(s, 16)

def _validate_args(raw_args):
    args = {}
    args['host'] = raw_args['--host']
    args['port'] = raw_args['--port']
    args['units'] = map(_from_hex_string, raw_args['--unit'])
    args['requests'] = int(raw_args['--requests'])
    args['delays'] = map(float, raw_args['--delay'])
    args['with_throughput'] = raw_args['--with-throughput']
    args['warmup'] = int(raw_args['--warmup'])
    args['target_dir'] = raw_args['--target-dir']
    return args

def main(host, port, units, requests, delays, with_throughput, warmup, target_dir):
    if with_throughput:
        delays = list(set(delays).union(set([0])))
    results = _benchmark_server(host, port, units, requests, delays, warmup)
    _print_results(results)
    _write_results(results, target_dir)

if __name__ == '__main__':
    args = _validate_args(docopt.docopt(__doc__))
    main(**args)
