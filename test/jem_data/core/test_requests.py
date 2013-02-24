import mock
from nose.tools import assert_equal

import jem_data.core.requests as requests

def test_read_registers_requests_the_correct_address_range():
    registers = {
        0xC550: 2,
        0xC552: 2,
        0xC556: 3
    }

    client = mock.Mock()
    requests.read_registers(client, unit=0x01, registers=registers)
    client.read_input_registers.assert_called_once_with(
            0xC550-1,
            0xC559-0xC550,
            unit=0x01)

def test_read_registers_checks_for_large_register_range():
    registers = {
        1: 1,
        126: 1,
    }

    client = mock.Mock()
    requests.read_registers(client, unit=0x01, registers=registers)
    assert_equal(client.read_input_registers.call_count, 0)

def test_read_registers_includes_word_size_when_calculating_range():
    registers = {
        1: 126
    }

    client = mock.Mock()
    requests.read_registers(client, unit=0x01, registers=registers)
    assert_equal(client.read_input_registers.call_count, 0)

def test_read_register_range_exactly_right_edge_case():
    registers = {
        1: 1,
        124: 2,
    }

    client = mock.Mock()
    requests.read_registers(client, unit=0x01, registers=registers)
    client.read_input_registers.assert_called_once_with(0, 125, unit=0x01)
