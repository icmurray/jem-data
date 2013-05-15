import jem_data.core.domain as domain
import jem_data.diris.devices as devices
import jem_data.util as util

def stub_gateways():
    devices = [
        [
            domain.Device(0x01, label=None, type="diris.a40", tables=_a40_tables()),
            domain.Device(0x02, label='Custom Label', type="diris.a40", tables=_a40_tables()),
        ],
        [
            domain.Device(0x01, label=None, type="diris.a40", tables=_a40_tables()),
            domain.Device(0x02, label=None, type="diris.a40", tables=_a40_tables()),
            domain.Device(0x03, label=None, type="diris.a40", tables=_a40_tables()),
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
                {'unit': 1, 'label': None, 'type': 'diris.a40','tables': _raw_a40_tables() },
                {'unit': 2, 'label': 'Custom Label', 'type': 'diris.a40', 'tables': _raw_a40_tables() },
            ],
        },
        {
            'host': '192.168.0.101',
            'port': 502,
            'label': None,
            'devices': [
                {'unit': 1, 'label': None, 'type': 'diris.a40', 'tables': _raw_a40_tables() },
                {'unit': 2, 'label': None, 'type': 'diris.a40', 'tables': _raw_a40_tables() },
                {'unit': 3, 'label': None, 'type': 'diris.a40', 'tables': _raw_a40_tables() },
            ],
        },
    ]

def _a40_tables():
    return devices.A40

def _raw_a40_tables():
    return util.deep_asdict(devices.A40)
