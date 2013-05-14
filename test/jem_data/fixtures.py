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

def _a40_tables():
    return [ 
        domain.Table(
            id=i,
            label=None,
            registers=[
                domain.Register(addr, None, (0,100)) \
                        for addr in sorted(registers.TABLES[i-1].keys()) ]
        ) for i in xrange(1, 7) ]
