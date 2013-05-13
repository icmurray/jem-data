import itertools
import random

import nose.tools as nose

import jem_data.util as util

def test_packing_and_unpacking():
    for width in [1,2]:
        min_value = -(2 ** (16 * width) / 2)
        max_value = -min_value - 1
        edge_cases = [min_value, max_value, -1, 0, 1]
        sample = random.sample(xrange(min_value, max_value), 10000)
        for i in itertools.chain(edge_cases, sample):
            packed = util.pack_value(i, width)
            unpacked = util.unpack_values(packed)
            nose.assert_equal(i, unpacked)
