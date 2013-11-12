'''
Device configuration table for Diris products.
'''

import os.path

import jem_data.core.domain as domain
import jem_data.diris.registers as registers

try:
    import json
    _config_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'registers.json')
    _config = json.load(open(_config_file))
    _REGISTER_CONFIG = {}
    for device_type, config in _config.items():
        _REGISTER_CONFIG[device_type] = dict(
            (int(addr), reg) for (addr, reg) in config.items())

except:
    print "Unable to load register configuration."
    _REGISTER_CONFIG = {}

A40 = [
    domain.Table(
        id=i,
        label="Table %d" % i,
        registers=[
            domain.Register(
                addr,
                (_REGISTER_CONFIG.get('diris.a40',{})
                                 .get(addr,{})
                                 .get('label',hex(addr))),
                tuple((_REGISTER_CONFIG.get('diris.a40',{})
                                 .get(addr,{})
                                 .get('range',[-1000,1000]))),
                (_REGISTER_CONFIG.get('diris.a40',{})
                                 .get(addr,{})
                                 .get('unit_of_measurement', None)))
                    for addr in sorted(registers.TABLES[i-1].keys()) ]
    ) for i in xrange(1, 7) ]

ALL = {
    'diris.a40': A40
}
