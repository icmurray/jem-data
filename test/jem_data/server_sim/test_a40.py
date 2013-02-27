from nose.tools import assert_equal

import jem_data.server_sim.a40 as a40

def test_a40_input_registers_are_initialized_to_zero_by_default():
    datablock = a40.A40InputRegistersDataBlock(dynamic=False)
    value = datablock.getValues(0xc550, 2)
    assert_equal(value, [0,0])

def test_a40_is_big_endian():
    initialData = {0xC550: 0xFF}
    datablock = a40.A40InputRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC550, 2)
    assert_equal(value, [0, 0xFF])

def test_a40_expands_2_word_values_into_the_next_register():
    initialData = {0xC550: 0x1234ABCD}
    datablock = a40.A40InputRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC550, 2)
    assert_equal(value, [0x1234, 0xABCD])

def test_a40_fails_on_registers_below_the_lowest_address():
    datablock = a40.A40InputRegistersDataBlock(dynamic=False)
    value = datablock.validate(0, 2)
    assert_equal(value, False)

