from nose.tools import assert_equal

import jem_data.server_sim.a40 as a40

def test_a40_input_registers_are_initialized_to_zero_by_default():
    datablock = a40.A40HoldingRegistersDataBlock(dynamic=False)
    value = datablock.getValues(0xc550, 2)
    assert_equal(value, [0,0])

def test_a40_is_big_endian():
    initialData = {0xC550: 0xFF}
    datablock = a40.A40HoldingRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC550, 2)
    assert_equal(value, [0, 0xFF])

def test_a40_expands_2_word_values_into_the_next_register():
    initialData = {0xC550: 0x0234ABCD}
    datablock = a40.A40HoldingRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC550, 2)
    assert_equal(value, [0x0234, 0xABCD])

def test_a40_leaves_negative_single_word_register_value_untouched():
    initialData = {0xC850: -32768}
    datablock = a40.A40HoldingRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC850, 1)
    assert_equal(value, [0x8000])

def test_a40_expands_2_word_negative_value():
    initialData = {0xC550: -2147483648}
    datablock = a40.A40HoldingRegistersDataBlock(initialData, dynamic=False)
    value = datablock.getValues(0xC550, 2)
    assert_equal(value, [0x8000, 0x0000])

def test_a40_fails_on_registers_below_the_lowest_address():
    datablock = a40.A40HoldingRegistersDataBlock(dynamic=False)
    value = datablock.validate(0, 2)
    assert_equal(value, False)

