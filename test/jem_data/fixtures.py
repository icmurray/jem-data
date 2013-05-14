import jem_data.core.domain as domain
import jem_data.diris.registers as registers

def stub_gateways():
    devices = [
        [
            domain.Device(0x01, label=None, tables=_a40_tables()),
            domain.Device(0x02, label='Custom Label', tables=_a40_tables()),
        ],
        [
            domain.Device(0x01, label=None, tables=_a40_tables()),
            domain.Device(0x02, label=None, tables=_a40_tables()),
            domain.Device(0x03, label=None, tables=_a40_tables()),
        ]
    ]

    gateways = [
        domain.Gateway("127.0.0.1", 5020,
                       label='Gateway 1', devices=devices[0]),

        domain.Gateway("192.168.0.101", 502,
                       label=None, devices=devices[1])
    ]

    return gateways

def raw_gateway_data():
    return [
        {
            'host': '127.0.0.1',
            'port': 5020,
            'label': 'Gateway 1',
            'devices': [
                {'unit': 1, 'label': None, 'tables': _raw_a40_tables() },
                {'unit': 2, 'label': 'Custom Label', 'tables': _raw_a40_tables() },
            ],
        },
        {
            'host': '192.168.0.101',
            'port': 502,
            'label': None,
            'devices': [
                {'unit': 1, 'label': None, 'tables': _raw_a40_tables() },
                {'unit': 2, 'label': None, 'tables': _raw_a40_tables() },
                {'unit': 3, 'label': None, 'tables': _raw_a40_tables() },
            ],
        },
    ]

def _a40_tables():
    return [ 
        domain.Table(
            id=i,
            label=None,
            registers=[
                domain.Register(addr, None, (0,100)) \
                        for addr in sorted(registers.TABLES[i-1].keys()) ]
        ) for i in xrange(1, 7) ]

def _raw_a40_tables():
    return [
        {
            'id': i,
            'label': None,
            'registers': [{'address': addr, 'label': None, 'range': (0,100)} \
                        for addr in sorted(registers.TABLES[i-1].keys()) ]
        } for i in xrange(1, 7) ]
