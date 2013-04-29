# -*- coding: utf-8 -*-

"""

"""

import contextlib
import time

import jem_data.diris as diris
import jem_data.core.messages as messages
import jem_data.core.modbus as modbus

def run(in_q, out_q, client):
    """
    Endlessly reads `ReadTableMsg` objects from a given `Queue`, performs the
    requests necessary to read the whole table, and writes the results back
    out to another (given) `Queue`.
    """

    with contextlib.closing(client) as conn:
        conn.connect()

        while True:
            msg = in_q.get()
            registers = diris.registers.TABLES[msg.table_id]
            for request in modbus.split_registers(registers):
                start_time = time.time()
                response = modbus.read_registers(conn,
                                                 registers=request,
                                                 unit=msg.device_id.unit)
                end_time = time.time()

                result = messages.ResponseMsg(
                        device_id = msg.device_id,
                        table_id = msg.table_id,
                        values = _read_values_from_response(response,
                                                            registers),
                        timing_info = (start_time, end_time),
                        error = None,
                        request_info = None)

                out_q.put(result)

def _read_values_from_response(response, requested_registers):
    """
    Returns a tuple of 2-tuples of (address, value) pairs.
    """

    return tuple( (addr, response.read_register(addr)) \
                        for addr in requested_registers.keys() )
