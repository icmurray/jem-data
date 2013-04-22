# -*- coding: utf-8 -*-

"""Low Level Dirus A40 Client

Just reads a set of registers from a Dirus A40, and measures how long the
request took to process

Usage:
    client.py [options]

Options
    --host=<host>       server host [default: 127.0.0.1]
    --port=<port>       server port [default: 5020]
    --delay=<delay>     the delay between requests (seconds) [default: 1.0]
    --unit=<unit>       the unit address to request [default: 0x01]
    --table=<table>     the table to read [default: 1]

"""

import docopt
import logging
import time

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus
import jem_data.diris.registers as diris_registers

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

DEMO_REGISTERS = {

    # Table 1
    0xC550: u'Time',
    0xC55E: u'Frequency',
    0xC560: u'Phase Current 1',
    0xC566: u'Neutral Current',
    0xC568: u'𝚺 Active Power +/-',
    0xC56A: u'𝚺 Reactive Power +/-',
    0xC56C: u'𝚺 Apparant Power',

    # Table 2
    0xC650: u'Time',
    0xC652: u'Active Energy +',
    0xC654: u'Reactive Energy +',
    0xC656: u'Apparent apparente',
    0xC658: u'Active Energy -',
    0xC66A: u'Reactive Energy -',
    0xC65C: u'No. Compteurs d’Impulsions',

    # Table 3
    0xC75E: u'Avg I1',
    0xC766: u'Avg 𝚺 Active Power +',
    0xC768: u'Avg 𝚺 Active Power -',
    0xC77A: u'Avg 𝚺 Reactive Power +',
    0xC77C: u'Avg 𝚺 Reactive Power -',
    0xC76E: u'Avg 𝚺 Apparant Power',
    0xC77E: u'Max/Avg I1',

    # Table 6
    0xC956: u'THD I1',
    0xC95A: u'Max Rank',
    0xC95B: u'Harmonic I1 Row 3',
    0xC95F: u'Harmonic I1 Row 5',
    0xC963: u'Harmonic I1 Row 7',
    0xC967: u'Harmonic I1 Row 9',
    0xC96B: u'Harmonic I1 Row 11',
    0xC96F: u'Harmonic I1 Row 13',
    0xC973: u'Harmonic I1 Row 15',
    0xC977: u'Harmonic I1 Row 17',
    0xC97B: u'Harmonic I1 Row 19',
    0xC97F: u'Harmonic I1 Row 21',
}


def main(host, port, delay, unit, table_num):
    client = ModbusClient(host, port=port)
    client.connect()
    
    min_response_time = 100
    max_response_time = 0
    sum_response_time = 0
    N = 0

    register_widths = diris_registers.TABLES[table_num-1].copy()
    register_labels = DEMO_REGISTERS.copy()
    registers = dict((addr, register_widths[addr]) \
                        for addr in DEMO_REGISTERS.keys() \
                        if addr in register_widths)

    label_width = max([len(label) for label in DEMO_REGISTERS.values()]) + 1

    while True:
    
        start = time.time()
        response = modbus.read_registers(client,
                                         registers=registers,
                                         unit=unit)
    
        response_time = time.time() - start
    
        print "Request Times:"

        min_response_time = min(min_response_time, response_time)
        max_response_time = max(max_response_time, response_time)
        sum_response_time += response_time
        N += 1
    
        print "Min".rjust(label_width) + ": " + str(min_response_time)
        print "Max".rjust(label_width) + ": " + str(max_response_time)
        print "Avg".rjust(label_width) + ": " + str(sum_response_time/N)

        print "Response Values:"
        for addr in sorted(registers.keys()):
            print (u"{label:>" + str(label_width) + u"s}: {value:f}").format(
                    label=register_labels[addr],
                    value=response.read_register(addr))

        print
        time.sleep(delay)
    client.close()

def _validate_args(raw_args):
    args = {}
    args['host'] = raw_args['--host']
    args['port'] = raw_args['--port']
    args['delay'] = float(raw_args['--delay'])
    args['unit'] = int(raw_args['--unit'], 16)
    args['table_num'] = int(raw_args['--table'])
    return args

if __name__ == '__main__':
    args = _validate_args(docopt.docopt(__doc__))
    main(**args)
