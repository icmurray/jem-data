# -*- coding: utf-8 -*-

"""

"""

import contextlib
import multiprocessing
import time

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import pymodbus.exceptions

import jem_data.diris.registers as diris_registers
import jem_data.core.domain as domain
import jem_data.core.exceptions as jem_exceptions
import jem_data.core.messages as messages
import jem_data.core.modbus as modbus

def start_readers(gateway, in_q, out_q, number_processes=4):
    """
    Create and start a pool of `Process`s connecting to the `gateway` device.
    """

    for i in xrange(number_processes):
        p = multiprocessing.Process(
                target = _run,
                args = (in_q, out_q, gateway.host, gateway.port))
        p.start()

def _run(in_q, out_q, host, port):
    """
    Endlessly reads `ReadTableMsg` objects from a given `Queue`, performs the
    requests necessary to read the whole table, and writes the results back
    out to another (given) `Queue`.
    """
    client = ModbusClient(host, port)
    with contextlib.closing(client) as conn:

        while True:
            try:
                msg = in_q.get()
                _read_table(msg, out_q, conn)
            except jem_exceptions.JemException, e:
                print "ERROR: %s : %s" % (msg, e)
            except pymodbus.exceptions.ConnectionException:
                pass

def _read_table(msg, out_q, conn):
    #msg = in_q.get()

    for registers in _table_requests(msg.table_addr.id):
        start_time = time.time()
        response = modbus.read_registers(conn,
                                         registers=registers,
                                         unit=msg.table_addr.device_addr.unit)
        end_time = time.time()

        result = messages.ResponseMsg(
                table_addr = msg.table_addr,
                values = _read_values_from_response(response, registers),
                timing_info = domain.TimingInfo(start_time, end_time),
                error = None,
                request_info = {'recording_id': msg.recording_id})

        print "SUCCESS: %s : %s" % (msg, result)
        out_q.put(result)

def _table_requests(table_id):
    registers = diris_registers.TABLES[table_id - 1]
    return modbus.split_registers(registers)

def _read_values_from_response(response, requested_registers):
    """
    Returns a tuple of 2-tuples of (address, value) pairs.
    """
    return tuple( (addr, response.read_register(addr)) \
                        for addr in requested_registers.keys() )
