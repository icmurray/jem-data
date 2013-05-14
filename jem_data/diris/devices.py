'''
Device configuration table for Diris products.
'''

import jem_data.core.domain as domain
import jem_data.diris.registers as registers

A40 = [
    domain.Table(
        id=i,
        label="Table %d" % i,
        registers=[
            domain.Register(addr, hex(addr), (0,100)) \
                    for addr in sorted(registers.TABLES[i-1].keys()) ]
    ) for i in xrange(1, 7) ]

ALL = {
    'diris.a40': A40
}
