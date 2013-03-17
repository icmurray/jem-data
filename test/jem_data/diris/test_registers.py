import nose.tools as nose

import jem_data.diris.registers as registers

def test_register_addresses_do_not_overlap():

    accum = set()
    for t in registers.TABLES:
        t_set = set(t.keys())
        nose.assert_equal(set(), t_set.intersection(accum))
        accum = accum.union(t_set)
