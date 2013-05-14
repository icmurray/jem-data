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
        client = ModbusClient(gateway.host, port=gateway.port)
        p = multiprocessing.Process(
                target = _run,
                args = (in_q, out_q, client))
        p.start()

def _run(in_q, out_q, client):
    """
    Endlessly reads `ReadTableMsg` objects from a given `Queue`, performs the
    requests necessary to read the whole table, and writes the results back
    out to another (given) `Queue`.
    """

    with contextlib.closing(client) as conn:

        while True:
            try:
                _read_table(in_q, out_q, conn)
            except jem_exceptions.JemException, e:
                print e
            except pymodbus.exceptions.ConnectionException:
                pass

def _read_table(in_q, out_q, conn):
    msg = in_q.get()

    for registers in _table_requests(msg.table_id.id):
        start_time = time.time()
        response = modbus.read_registers(conn,
                                         registers=registers,
                                         unit=msg.table_id.device_addr.unit)
        end_time = time.time()

        result = messages.ResponseMsg(
                table_id = msg.table_id,
                values = _read_values_from_response(response, registers),
                timing_info = domain.TimingInfo(start_time, end_time),
                error = None,
                request_info = None)

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
