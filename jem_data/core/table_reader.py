# -*- coding: utf-8 -*-

"""

"""

import contextlib
import multiprocessing
import time

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

import jem_data.diris as diris
import jem_data.core.domain as domain
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
        conn.connect()

        while True:
            _read_table(in_q, out_q, conn)

def _read_table(in_q, out_q, conn):
    msg = in_q.get()

    for request in _table_requests(msg.table_id):
        start_time = time.time()
        response = modbus.read_registers(conn,
                                         registers=request,
                                         unit=msg.device_id.unit)
        end_time = time.time()

        result = messages.ResponseMsg(
                device_id = msg.device_id,
                table_id = msg.table_id,
                values = _read_values_from_response(response, msg.table_id),
                timing_info = (start_time, end_time),
                error = None,
                request_info = None)

        out_q.put(result)

def _table_requests(table_id):
    registers = diris.registers.TABLES[table_id - 1]
    return modbus.split_registers(registers)

def _read_values_from_response(response, table_id):
    """
    Returns a tuple of 2-tuples of (address, value) pairs.
    """
    requested_registers = diris.registers.TABLES[table_id - 1]
    return tuple( (addr, response.read_register(addr)) \
                        for addr in requested_registers.keys() )
