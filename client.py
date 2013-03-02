"""Low Level Dirus A40 Client

Just reads a set of registers from a Dirus A40, and measures how long the
request took to process

Usage:
    client.py [options]

Options
    --host=<host>       server host [default: 127.0.0.1]
    --port=<port>       server port [default: 5020]
    --delay=<delay>     the delay between requests (seconds) [default: 1.0]

"""

import docopt
import logging
import time

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

from jem_data.core import modbus

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

def main(host, port, delay):
    client = ModbusClient(host, port=port)
    client.connect()
    
    interested_registers = {
            0xC550: 2,
            0xC560: 2,
            0xC562: 2,
            0xC564: 2,
    }
    
    unit = 0x01
    
    min_response_time = 100
    max_response_time = 0
    sum_response_time = 0
    N = 0
    
    while True:
    
        start = time.time()
        ##response = modbus.read_registers(client,
        ##                                 registers=interested_registers,
        ##                                 unit=unit)
    
        response = client.read_holding_registers(0xc550, 4, unit=unit)
        response_time = time.time() - start
        #print response.read_register(0xc550)
    
        min_response_time = min(min_response_time, response_time)
        max_response_time = max(max_response_time, response_time)
        sum_response_time += response_time
        N += 1
    
        print"Min: %f\tMax: %f\tAvg: %f" % (min_response_time, max_response_time, (sum_response_time/N))
        print response
        print response.getRegister(0)
        ##print [ response.getRegister(addr) for addr in range(0, 125) ]
        ##print
        ##print response.getRegister(0)
        ##print response.getRegister(1)
        ##print response.getRegister(2)
        ##print response.getRegister(3)
        ##print "###############"
        ##print
    
        ##for addr in interested_registers:
        ##    print "[%x] %x : %d" % (unit, addr, response.read_register(addr))
    
        time.sleep(delay)
    client.close()

def _validate_args(raw_args):
    args = {}
    args['host'] = raw_args['--host']
    args['port'] = raw_args['--port']
    args['delay'] = float(raw_args['--delay'])
    return args

if __name__ == '__main__':
    args = _validate_args(docopt.docopt(__doc__))
    main(**args)
